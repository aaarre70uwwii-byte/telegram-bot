import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
المطور_الاساسي = int(os.getenv("DEVELOPER_ID", "7488375443")) # حط ايديك هنا
اسم_البوت = os.getenv("BOT_NAME", "𝐓𝐢𝐚")
admins = [] # بنضيف مشرفين لاحقا

# متغيرات الحماية
MAINTENANCE = os.getenv("MAINTENANCE", "False") == "True"
