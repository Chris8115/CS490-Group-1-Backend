import os

GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
CRAZE_SECRET_KEY   = os.getenv("CRAZE_SECRET_KEY")

if not GMAIL_APP_PASSWORD or not CRAZE_SECRET_KEY:
    raise RuntimeError("Missing required secret(s) in environment")
