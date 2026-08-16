import os

# Telegram API
API_ID = int(os.getenv("API_ID", 12345))
API_HASH = os.getenv("API_HASH", "your_api_hash")
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")

# Admin
ADMIN_ID = int(os.getenv("ADMIN_ID", 123456789))  # حط ايديك هنا
ADMINS = [ADMIN_ID]

# Download Settings
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloads")

# FFMPEG
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "ffmpeg")

# Music Settings
DURATION_LIMIT = int(os.getenv("DURATION_LIMIT", 60)) # دقايق
SONG_DOWNLOAD_DURATION = int(os.getenv("SONG_DOWNLOAD_DURATION", 10)) # دقايق

# اسم البوت
BOT_NAME = os.getenv("BOT_NAME", "MusicBot")

# لغة البوت
LANGUAGE = os.getenv("LANGUAGE", "ar")
