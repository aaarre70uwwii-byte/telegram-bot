import os

# ===== 1. بيانات البوت الاساسية - من المتغيرات =====
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# ===== 2. الصلاحيات =====
ADMINS = [7488375443] # انت المطور
SUDO_USERS = [8871846057] # المساعد
ALL_ADMINS = ADMINS + SUDO_USERS # عشان نستخدمها في فلتر الاوامر

# ===== 3. معلومات البوت =====
BOT_NAME = "ProProtectBot"
BOT_USERNAME = "حط_يوزر_بوتك_هنا" # اختياري
COMMAND_PREFIX = ["/", "!"]

# ===== 4. مجلدات وملفات =====
DOWNLOAD_DIR = "downloads" # مجلد تحميل الاغاني
MAX_SONG_DURATION = 10 # اقصى مدة للاغنية بالدقايق

# ===== 5. اعدادات الحماية =====
PROTECTION = {
    "delete_links": True, # حذف الروابط
    "delete_bad_words": True, # حذف السب
    "anti_flood": True, # منع التكرار
    "flood_limit": 5, # 5 رسائل في 5 ثواني = كتم
    "anti_spam": True, # منع الكبتل والايموجي الزايد
    "welcome": True, # رسالة الترحيب
}

BAD_WORDS = [
    "كلمة1", "كلمة2", "سب", "شتم" # ضيف كلماتك الممنوعة هنا
]

WELCOME_MSG = """
اهلا {user} نورت {chat} ❤️
اقرا قوانين المجموعة قبل ما تبدا
"""

# ===== 6. رسائل النظام =====
MESSAGES = {
    "no_admin": "🚫 هذا الامر للادمن فقط",
    "user_banned": "✅ تم حظر {user}",
    "user_muted": "✅ تم كتم {user} لمدة {time}",
    "song_not_found": "❌ ما لقيت الاغنية",
    "downloading": "جاري التحميل 🎵 انتظر..."
}
