import os
import json
import base64
from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError
from gmail_reader import list_inbox
from triage import agent_summary, email_draft_agent


PROJECT_ID = os.getenv("PROJECT_ID")
SUBSCRIPTION_ID = os.getenv("SUBSCRIPTION_ID")

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)

last_history_id = None

def callback(message):
    global last_history_id
    
    try:
        data = base64.b64decode(message.data).decode("utf-8")
        notification = json.loads(data)
        new_history_id = notification.get("historyId")
        
        print(f"Received notification for historyId: {new_history_id}")

        if new_history_id == last_history_id:
            print("Duplicate notification, skipping.")
            message.ack()
            return

        print("Triggering LLM orchestration...")
        context = list_inbox(max_results=10) 
        result = agent_summary(context)
        
        actionable = [r for r in result.results if r.is_actionable]
        print(f"total={len(result.results)} actionable={len(actionable)}")
        
        message.ack()
        last_history_id = new_history_id
        
    except Exception as e:
        print(f"Error processing message: {e}")
        message.nack()

print(f"Listening for messages on {subscription_path}...")
streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)

try:
    streaming_pull_future.result()
except TimeoutError:
    streaming_pull_future.cancel()
    streaming_pull_future.result()