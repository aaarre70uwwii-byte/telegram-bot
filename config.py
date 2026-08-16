import os

# === الحماية ===
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
ADMIN_ID = int(os.getenv("ADMIN_ID"))
ALLOWED_USERS = [OWNER_ID, ADMIN_ID] # بس انت والادمن

# === اعدادات البوت ===
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloads")
MAX_SONG_DURATION = int(os.getenv("MAX_SONG_DURATION", "60"))
MESSAGE_DUPLICATE_LIMIT = int(os.getenv("MESSAGE_DUPLICATE_LIMIT", "2"))
NIXPACKS_PACKAGES = os.getenv("NIXPACKS_PACKAGES", "ffmpeg")
