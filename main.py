import os
import sys
import logging
from telegram.ext import Application, CommandHandler

# استدعاء دوال الربط من الملفات الفرعية
from dev_panel import start as dev_start, register_dev_handlers
from menu import register_menu_handlers

# إعدادات المراقبة والسجلات لمنع تعليق السورس
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

# 🌐 قراءة المتغيرات تلقائياً من لوحة تحكم Railway الفعالة في صورتك
TOKEN = os.getenv('TOKEN')
OWNER_ID = os.getenv('OWNER_ID')

# التحقق من وجود المتغيرات الهامة لمنع توقف البوت عند الإقلاع
if not TOKEN:
    print("❌ [خطأ]: لم يتم العثور على متغير TOKEN في إعدادات Railway!")
    sys.exit(1)

def main():
    # بناء تطبيق البوت الموحد باستخدام التوكن المستدعى من الاستضافة
    application = Application.builder().token(TOKEN).build()

    # 1. ربط أمر /start الأساسي
    application.add_handler(CommandHandler("start", dev_start))

    # 2. استدعاء وربط مستمعات أزرار المطور بالخاص من ملف dev_panel.py
    register_dev_handlers(application)

    # 3. استدعاء وربط مستمعات أوامر المجموعات والكيبورد الأخضر من ملف menu.py
    register_menu_handlers(application)

    # بدء تشغيل البوت الموحد بنجاح
    print(f"⚡ [النظام]: تم جلب البيانات بنجاح من Railway.")
    print(f"👑 [OWNER_ID]: {OWNER_ID}")
    print("🚀 [main.py] يعمل الآن على الاستضافة بنجاح ودون تعليق.")
    application.run_polling()

if __name__ == '__main__':
    main()
