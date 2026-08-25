import os

TOKEN = os.getenv("BOT_TOKEN")
DEV = int(os.getenv("DEV_ID"))
ADMINS = os.getenv("ADMINS", "")
admins = [int(x) for x in ADMINS.split(",") if x]
