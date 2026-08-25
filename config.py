import os

TOKEN = os.getenv("BOT_TOKEN")
DEV = int(os.getenv("DEV_ID", "0"))

ADMINS = os.getenv("ADMINS", "")
admins = [int(x) for x in ADMINS.split(",") if x]

# فحص سريع
if not TOKEN or DEV == 0:
    raise ValueError("❌ BOT_TOKEN or DEV_ID not set in Environment Variables")

print(f"✅ DEV: {DEV} | Admins: {admins}")
