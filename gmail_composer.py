from email.mime.text import MIMEText
import base64


def create_draft(service, to, subject, body, thread_id=None):
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    
    draft_body = {"message":{"raw":raw}}
    if thread_id:
        draft_body["message"]["threadId"] = thread_id
    
    draft = service.users().drafts().create(userId="me", body=draft_body).execute()
    print("draft created with id: ", draft["id"])
    return draft

def send_draft(service, draft_id):
    sent_message = service.users().drafts().send(
        userId="me",
        body={
            "id":draft_id
        }
    ).execute()
    print(f"email sent, message id: ", sent_message["id"])
    return sent_message
