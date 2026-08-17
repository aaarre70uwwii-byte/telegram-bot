import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
DB_NAME = "protection_bot.db"

BANNED_WORDS = ["كسمك", "احا", "شرموط"]
MAX_FLOOD = 5
FLOOD_TIME = 3
MAX_WARNS = 3
