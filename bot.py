from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN
from database import init_db

app = Client("tia_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

if __name__ == "__main__":
    # 1. يشغل قاعدة البيانات
    init_db()
    
    # 2. هنا الاستدعاء لكل الملفات
    from modules import start
    from modules import admin  
    from modules import locks
    from modules import settings
    from modules import fun
    from modules import service
    
    print("="*30)
    print("Tia Bot Started ✅")
    print("جميع الموديولات تم تحميلها")
    print("="*30)
    
    # 3. يشغل البوت
    app.run()
