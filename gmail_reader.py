from auth import get_service
from utility import extract_body


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
            "threadId":msg.get("threadId")
            "Date":headers.get("Date"),
            "From":headers.get("From"),
            "Subject":headers.get("Subject"),
            "Body":body[:body_chars].strip(),
        })
        
    return inboxes
