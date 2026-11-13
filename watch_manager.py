import os
from auth import get_service
from dotenv import load_dotenv

load_dotenv()

TOPIC_NAME = os.getenv("TOPIC_NAME")

def register_watch(topic_name=TOPIC_NAME):
    service = get_service()
    request = {
        "topicName": topic_name,
        "labelsIds": ["INBOX"],
    }
    
    response = service.users().watch(userId="me", body=request).execute()
    print(f"watch registered, expiration: {response["expiration"]}")
    return response