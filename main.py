# -*- coding: utf-8 -*-
import os
import sys
import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import Message

# 1. جلب متغيرات البيئة المحمية الخاصة بالسيرفر
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
DEV_ID = os.getenv("DEV_ID")

# فحص تأميني إلزامي لمنع تشغيل البوت ببيانات فارغة تسبب انهيار الـ Client
if not all([API_ID, API_HASH, BOT_TOKEN, DEV_ID]):
    print("❌ خطأ حرج: يرجى التأكد من إدخال المتغيرات الأربعة (API_ID, API_HASH, BOT_TOKEN, DEV_ID) في إعدادات السيرفر أولاً!")
    sys.exit(1)

# 2. تهيئة العقل المدبر وتفعيل ميزة التوجيه التلقائي للمجلد commands
app = Client(
    "MyShieldBot",
    api_id=int(API_ID),
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="commands")  # يربط م1، م2، م3، م4، م5، م6 تلقائياً وبأمان
)

# 3. أمر عرض القائمة الرئيسية (الاوامر) داخل المجموعات والخاص
@app.on_message(filters.command(["الاوامر", "help", "اوامري"]))
async def main_menu_handler(client: Client, message: Message):
    menu_text = """
- ‌‌‏أهلاً بك عزيزي في قائمة الاوامر :
━━━━━━━━━━━━
◂ م1 : اوامر الادمنيه 👮‍♂️
◂ م2 : اوامر الاعدادات ⚙️
◂ م3 : اوامر القفل - الفتح 🔒
◂ م4 : اوامر التسليه 😂
◂ م5 : اوامر Dev 👑
◂ م6 : الاوامر الخدميه 🛠️
━━━━━━━━━━━━
💡 _لفتح أي قائمة، فقط اكتب الرمز الخاص بها في الجروب (مثال: م1)_
"""
    await message.reply_text(text=menu_text)

# 4. دالة الإقلاع والمحافظة على استمرارية البوت وضغط الرسائل العالي
async def main():
    print("⚡ جاري تهيئة وفحص ملفات الحماية والـ Plugins...")
    await app.start()
    bot_info = await app.get_me()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"✅ تم تشغيل البوت بنجاح واكتمل ربط الملفات الستة المحدثة!")
    print(f"🤖 اسم البوت: {bot_info.first_name}")
    print(f"🆔 معرف البوت: @{bot_info.username}")
    print(f"👑 آيدي المطور الرئيسي المعتمد: {DEV_ID}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    await idle()  # المحافظة على استقبال الرسائل والهمسات بانتظام دون توقف فجائي
    await app.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 تم إيقاف تشغيل البوت بنجاح من التيرمنال.")
