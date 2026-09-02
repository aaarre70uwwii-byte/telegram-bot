# اسم الملف: main.py
import os
import sys
import logging
from telegram import Update  # <-- مهم عشان allowed_updates
from telegram.ext import Application, CommandHandler
from dev_panel import start, register_dev_handlers
from menu import register_menu_handlers

# إعدادات المراقبة والسجلات لمنع تعليق السورس
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

# 🌐 قراءة المتغيرات تلقائياً من Railway
TOKEN = os.getenv('TOKEN')
OWNER_ID = os.getenv('OWNER_ID')

# التحقق من وجود المتغيرات الهامة
if not TOKEN:
    print("❌ [خطأ]: لم يتم العثور على متغير TOKEN في إعدادات Railway!")
    sys.exit(1)
if not OWNER_ID:
    print("❌ [خطأ]: لم يتم العثور على OWNER_ID في إعدادات Railway!")
    sys.exit(1)

def main():
    # بناء تطبيق البوت الموحد باستخدام التوكن
    application = Application.builder().token(TOKEN).build()

    # 1. ربط أمر /start الأساسي
    application.add_handler(CommandHandler("start", start))

    # 2. ربط لوحة المطور
    register_dev_handlers(application)

    # 3. ربط قائمة الجروبات
    register_menu_handlers(application)

    # بدء تشغيل البوت الموحد
    print(f"⚡ [النظام]: تم جلب البيانات بنجاح من Railway.")
    print(f"👑 [OWNER_ID]: {OWNER_ID}")
    print("🚀 [main.py] يعمل الآن على الاستضافة بنجاح ودون تعليق.")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == '__main__':
    main()
