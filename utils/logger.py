import datetime
import os

LOG_FILE = os.getenv("ASSISTANT_LOG", "assistant.log")

def log_event(event: str):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.datetime.now()}] {event}\n")
