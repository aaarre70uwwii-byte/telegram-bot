import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ")
OWNER_ID = int(os.getenv("OWNER_ID", "123456789"))
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", "-100123456789"))
