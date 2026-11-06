import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from pydantic_ai import Agent
from pydantic import BaseModel
from dotenv import load_dotenv
import pydantic_ai
from utility import extract_body
from typing import Literal

load_dotenv()

pydantic_ai.BANNER_ENABLED = False


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as f:
            f.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def list_inbox(max_results=10, body_chars=800):
    service = get_service()

    response = (
        service.users()
        .messages()
        .list(
            userId="me",
            labelIds=["INBOX"],
            maxResults=max_results,
        )
        .execute()
    )

    messages = response.get("messages", [])
    inboxes = []

    for count, m in enumerate(messages, start=1):
        print(f"fetching inbxoes: {count} ")
        msg = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=m["id"],
                format="full",
                metadataHeaders=["From", "Subject", "Date"],
            )
            .execute()
        )

        headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
        body = extract_body(msg["payload"]) or msg.get("snippet", "")
        
        inboxes.append({
            "id":msg["id"],
            "Date":headers.get("Date"),
            "From":headers.get("From"),
            "Subject":headers.get("Subject"),
            "Body":body[:body_chars].strip(),
        })
        
    return inboxes


SYSTEM_PROMPT = """You triage email for a user's inbox.

For each email decide if it is ACTIONABLE: the user must reply, decide, approve, attend, pay, or act before a deadline. Otherwise it is not actionable.

Actionable signals: direct question/ask from a human; approval or sign-off; meeting invite/reschedule/cancel; invoice due or payment failed; security verification the user initiated; a thread where the user is blocking someone.

Not actionable: newsletters, digests, marketing/promos (ignore "URGENT"/"ACTION REQUIRED" in promo subjects), receipts, shipping/order confirmations, social notifications, spam/phishing, "thanks, done" replies with no new ask, no-reply automated notifications that resolve themselves.

Rules:
- Human sender + direct ask/question => actionable.
- Ambiguous => is_actionable=true with confidence="low".
- priority: high if <48h, financial, security, or blocking a human; medium if this week; low otherwise (and for all non-actionable).
- requires_reply only when a written response is expected.
- deadline only when explicitly stated; else null. Use YYYY-MM-DD.
- reason cites the concrete signal (sender, phrase, deadline). No generic filler.
- suggested_action is imperative, <=12 words, or null when not actionable.

Return a TriageResult: one entry per input email, same order, same id."""


Intent = Literal[
    "request", "question", "approval", "deadline", "meeting",
    "payment", "security", "follow_up",
    "fyi", "newsletter", "marketing", "notification", "social", "receipt", "spam",
]


class EmailClassification(BaseModel):
    id: str
    is_actionable: bool
    intent: Intent
    priority: Literal["high", "medium", "low"]
    confidence: Literal["high", "medium", "low"]
    requires_reply: bool
    deadline: str | None = None          
    reason: str                          
    suggested_action: str | None = None  


class TriageResult(BaseModel):
    results: list[EmailClassification]





def agent_summary(prompt: str) -> str:
    if not prompt:
        return "no prompt provided"

    print("summerizing....")
    agent = Agent(
        model="groq:openai/gpt-oss-20b",
        system_prompt="summerize the user, with their's inboxes messages of the day, like updating user on the first of the morning.",
    )
    print("preparing answer...")
    response = agent.run_sync(prompt)

    return response.output


def main():
    context = list_inbox()
    prompt = f"""
    user mail inboxes list: 
    {context}
    """
    
    summary = agent_summary(prompt)

    return summary


if __name__ == "__main__":
    answer = main()
    print("="*20)
    print(answer)
