import os
from auth import get_service
from dotenv import load_dotenv
from datetime import datetime, timezone
from logger import logger

load_dotenv()

TOPIC_NAME = os.getenv("TOPIC_NAME")

def register_watch(topic_name=TOPIC_NAME):
    service = get_service()
    request = {
        "topicName": topic_name,
        "labelIds": ["INBOX"],
    }
    
    response = service.users().watch(userId="me", body=request).execute()
    exp_ms = int(response["expiration"])
    exp_dt = datetime.fromtimestamp(exp_ms / 1000, tz=timezone.utc)

    logger.info(f"watch registered, expires at {exp_dt.isoformat()}")
    return response