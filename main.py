import dotenv
import pydantic_ai
from auth import get_service
from gmail_reader import list_inbox
from gmail_composer import create_draft, send_draft
from triage import agent_summary, email_draft_agent

dotenv.load_dotenv()
pydantic_ai.BANNER_ENABLED = False


def main():
    context = list_inbox(max_results=10)
    result = agent_summary(context)

    actionable = [r for r in result.results if r.is_actionable]
    
    print("=" * 20)
    print(f"total={len(result.results)} actionable={len(actionable)}")
    
    if not actionable:
        print("No actionable emails to process.")
        return result

    service = get_service()
    
    for r in actionable:
        print(f"[{r.priority}] {r.intent} — {r.suggested_action}  ({r.reason})")
                
        
        original_email = next(
            (e for e in context if e["id"] == r.id), None
        )
        
        if original_email is None:
            print(f"Skipping {r.id}: original email not found")
            continue
        
        prompt = f"""
            Draft a reply to this email.

            Original email:
            From: {original_email.get('From', 'Unknown')}
            Subject: {original_email.get('Subject', '')}

            Email content:
            {original_email.get('Body', original_email.get('Snippet', ''))}

            Requested action:
            {r.suggested_action}

            Intent:
            {r.intent}

            Reason:
            {r.reason}

            Write a concise, professional reply.
        """
        
        response = email_draft_agent(prompt)
        draft_response = (
            f"Hi,\n\n"
            # f"Regarding: {r.intent}\n\n"
            f"{response.body}\n\n"
            f"Best,\nDarshan Pandey"
        )        
        print(f"replying to: {original_email['From']} — {original_email['Subject']}")           
        
        recipient = original_email["From"] if original_email else "unknown@example.com"
        subject = response.subject or f"Re: {original_email.get('Subject', '')}"


        print("\n--- DRAFT FOR YOUR REVIEW ---")
        print(f"To: {recipient}")
        print(f"Subject: {subject}")
        print(f"Body:\n{draft_response}")
        print("-----------------------------")

        approval = input("Send this draft? (y/n): ").strip().lower()

        if approval == "y":
            draft = create_draft(
                service=service,
                to=recipient,
                subject=subject,
                body=draft_response,
                thread_id=original_email.get("threadId") if original_email else None,
            )
            send_draft(service, draft["id"])
            print("Draft approved and sent.")
        else:
            print("send cancelled.")

    return result

if __name__ == "__main__":
    main()
