import os
from dotenv import load_dotenv

load_dotenv()

# للحساب المساعد (يمكنك جلبها من my.telegram.org)
API_ID = int(os.getenv("API_ID", "123456"))
API_HASH = os.getenv("API_HASH", "abcdef1234567890abcdef1234567890")

# توكن البوت الأساسي وآيدي المطور
BOT_TOKEN = os.getenv("BOT_TOKEN", "1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ")
OWNER_ID = int(os.getenv("OWNER_ID", "123456789"))
