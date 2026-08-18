import os
import re
import random
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Secure environment compilation integration
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("CRITICAL ERROR: 'BOT_TOKEN' environment variable is missing!")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# ==========================================
# 📊 VOLATILE MEMORY DATABASE STORAGE (MOCK)
# ==========================================
FUN_SYSTEM_ENABLED = True
MUTE_VOTE_ENABLED = True
MARRIAGE_ENABLED = True
DEDICATION_SYSTEM_ENABLED = True

group_fun_db = {}
global_fun_db = {}
marriage_db = {}

FUN_PLURAL_MAP = {
    "هطف": "الهطوف", "بثر": "البثرين", "حمار": "الحمير", "كلب": "الكلاب",
    "كلبه": "الكلبات", "عتوي": "العتوين", "عتويه": "العتويات", "لحجي": "اللحوج",
    "لحجيه": "اللحجيات", "خروف": "الخرفان", "خفيفه": "الخفيفات", "خفيف": "الخفيفين",
    "بقلبي": "قلب الإدارة"
}

QUOTES_POOL = ["لا تيأس، المبرمج العظيم واجه أخطاءً أكثر مما تتخيل.", "النجاح هو الانتقال من فشل إلى فشل دون فقدان الحماس."]
POEMS_POOL = ["ألا ليت الشباب يعود يوماً... فأخبره بما فعل المشيب", "على قدر أهل العزم تأتي العزائم... وتأتي على قدر الكرام المكارم"]
STORIES_POOL = ["كتاب: مقدمة ابن خلدون الباب الأول", "رواية ليلى والذئب - الفصل الأول تنزيل كامل."]
SONGS_POOL = ["🎵 جاري تشغيل شيلة حماسية...", "🎵 جاري عزف مقام بياتي هادئ..."]

# ==========================================
# 🎛️ PROFESSIONAL KEYBOARD INTERFACES
# ==========================================

def get_main_dashboard_markup():
    """Generates the primary 1-6 categorized grid system."""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("1️⃣ أوامر الرفع والمنع والمسح", callback_data="menu_1"),
        InlineKeyboardButton("2️⃣ قائمة وعرض الإعدادات", callback_data="menu_2")
    )
    markup.add(
        InlineKeyboardButton("3️⃣ أوامر القفل والفتح والتعطيل", callback_data="menu_3"),
        InlineKeyboardButton("4️⃣ ميزة الإهداءات الصوتية", callback_data="menu_4")
    )
    markup.add(
        InlineKeyboardButton("5️⃣ أوامر التسلية والارتباط", callback_data="menu_5"),
        InlineKeyboardButton("6️⃣ الأوامر الخدمية والتحميل", callback_data="menu_6")
    )
    # Bottom structural dynamic canvas commands
    markup.add(InlineKeyboardButton("❌ إخفاء اللوحة", callback_data="hide_dashboard"))
    markup.add(InlineKeyboardButton("🦦 تحديثات 𝐓𝐢𝐚 @eeccvu", url="https://t.me"))
    return markup

@bot.message_handler(regexp=r"^(الاوامر|أوامر البوت|لوحة التحكم|الاوامر بالازرار)$")
def send_control_panel(message):
    welcome_text = (
        "👑 **أهلاً بك في لوحة تحكم وإعدادات بوت سديم المتكاملة**\n\n"
        "الرجاء اختيار أحد الأقسام المرتبة بالتسلسل (1-6) من الأزرار التفاعلية أدناه لمراجعة طريقة كتابة الأوامر المتطابقة:"
    )
    bot.reply_to(message, welcome_text, reply_markup=get_main_dashboard_markup(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_menu_navigation(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id  # <-- تم التعديل هنا فقط
    
    if call.data == "hide_dashboard":
        bot.delete_message(chat_id, message_id)
        bot.answer_callback_query(call.id, "📥 تم إخفاء لوحة التحكم بنجاح.")
        return

    back_button = InlineKeyboardMarkup().add(InlineKeyboardButton("⬅️ العودة للوحة الرئيسية", callback_data="main_menu"))
    
    if call.data == "main_menu":
        welcome_text = (
            "👑 **أهلاً بك في لوحة تحكم وإعدادات بوت سديم المتكاملة**\n\n"
            "الرجاء اختيار أحد الأقسام المرتبة بالتسلسل (1-6) من الأزرار التفاعلية أدناه لمراجعة طريقة كتابة الأوامر المتطابقة:"
        )
        bot.edit_message_text(welcome_text, chat_id, message_id, reply_markup=get_main_dashboard_markup(), parse_mode="Markdown")
        
    elif call.data == "menu_1":
        text = (
            "🔱 **1️⃣ قسم أوامر الرفع والمنع والمسح الإداري:**\n━━━━━━━━━━━━\n"
            "• `رفع / تنزيل` [مالك اساسي | منشئ | مالك | مدير | ادمن | مشرف | مميز]\n"
            "• `تنزيل الكل` | `طرد المحذوفين`\n"
            "• `حظر` | `كتم` | `تقييد` | `طرد` | `الغاء الحظر` | `الغاء الكتم` | `فك التقييد` | `رفع القيود`\n"
            "• `منع بالرد` | `الغاء منع بالرد`\n"
            "• `تقييد + الوقت` (مثال: تقييد 10 دقائق)\n"
            "• `مسح + عدد الرسائل` (مثال: مسح 50)\n"
            "• `مسح` [الكل | المنشئين | المالكين | المدراء | الادمنيه | المميزين | المحظورين | المكتومين | قائمه المنع | الردود | الاوامر المضافه | بالرد | الايدي | الترحيب | الرابط]"
        )
        bot.edit_message_text(text, chat_id, message_id, reply_markup=back_button, parse_mode="Markdown")
        
    elif call.data == "menu_2":
        text = (
            "⚙️ **2️⃣ قسم عرض ووضع إعدادات المجموعة:**\n━━━━━━━━━━━━\n"
            "• **أوامر العرض الاستقرائي:**\n"
            "  `الرابط` | `المالكين الاساسين` | `المالكين` | `المنشئين` | `المدراء` | `الادمنيه` | `المميزين` | `المحظورين` | `المكتومين` | `القوانين` | `معلوماتي` | `الحمايه` | `الاعدادت` | `المجموعه`\n\n"
            "• **أوامر ضبط وتهيئة المتغيرات:**\n"
            "  `مسح الرابط` | `انشاء رابط`\n"
            "  `ضع الترحيب` [النص] | `ضع قوانين` [النص] | `ضـع رابط` [الرابط] | `اضف امر` [النص] | `تعيين الايدي` [النص]\n"
            "  `اضف قناه` [اليوزر أو الايدي] | `حذف قناه` [اليوزر أو الايدي]"
        )
        bot.edit_message_text(text, chat_id, message_id, reply_markup=back_button, parse_mode="Markdown")
        
    elif call.data == "menu_3":
        text = (
            "🔒 **3️⃣ قسم أوامر القفل والفتح والتعطيل:**\n━━━━━━━━━━━━\n"
            "• **صيغ القفل والفتح المتاحة:**\n"
            "  `قفل / فتح` [جمثون | السب | الايرانيه | الكتابه | التعديل | الفيديو | الصور | الملصقات | المتحركه | الدردشه | الروابط | التاك | البوتات | المعرفات | الكلايش | التكرار | التوجيه | الانلاين | الجهات | الكل | الدخول | الصوت]\n"
            "• `قفل البوتات بالطرد`\n\n"
            "• **أنظمة التفعيل والتعطيل التامة:**\n"
            "  `تفعيل / تعطيل` [ضافني | الاذكار | الثنائي | افتاري | التسليه | الكت | الترحيب | الردود | الانذار | التحذير | الايدي | الرابط | اطردني | الحظر | الرفع | التنزيل | التحويل | الحمايه | المنشن | وضع الاقتباسات | الخدميه | الايدي بالصوره | التحقق]"
        )
        bot.edit_message_text(text, chat_id, message_id, reply_markup=back_button, parse_mode="Markdown")
        
    elif call.data == "menu_4":
        text = (
            "🎙️ **4️⃣ قسم ميزة الإهداءات الصوتية المبتكرة لحساب سديم:**\n━━━━━━━━━━━━\n"
            "• **طريقة الإهداء:** بالرد على أي مقطع صوتي في المجموعة أو القناة واكتب:\n"
            "  `اهداء + معرف الشخص` (مثال: اهداء @un112)\n\n"
            "• **التحكم والتحويل في الإرسال وبث الصوت البيني:**\n"
            "  `ايقاف` | `وقف` | `سديم وقفي` | `تخطي` | `ايقاف الاهداءات`\n"
            "• **التحكم والتعطيل الإداري:**\n"
            "  `تعطيل الاهداءات` | `تفعيل الاهداءات`"
        )
        bot.edit_message_text(text, chat_id, message_id, reply_markup=back_button, parse_mode="Markdown")
        
    elif call.data == "menu_5":
        text = (
            "🎪 **5️⃣ قسم أوامر التسلية والارتباط والتصويت الديمقراطي:**\n━━━━━━━━━━━━\n"
            "• **رتب التسلية (بالتوجيه والرد):**\n"
            "  `رفع / تنزيل` [هطف | بثر | حمار | كلب | كلبه | عتوي | عتويه | لحجي | لحجيه | خروف | خفيفه | خفيف]\n"
            "• `رفع بقلبي` | `تنزيل من قلبي`\n"
            "• `رفع + اسم اختياري` | `رفع عام + اسم اختياري`\n"
            "• `رتب التسليه` | `رتب التسليه عام` | `مسح رتب التسليه`\n"
            "• `تعطيل التسليه`\n\n"
            "• **نظام العلاقات والارتباط الزوجي:**\n"
            "  `طلاق` | `زواج` | `زوجي` | `زوجتي` | `تتزوجني` | `تفعيل / تعطيل زوجني`\n\n"
            "• **محاكي الاقتراع التلقائي:**\n"
            "  `اكتموه` (فتح تصويت فوري بالرد) | `تفعيل / تعطيل اكتموه`"
        )
        bot.edit_message_text(text, chat_id, message_id, reply_markup=back_button, parse_mode="Markdown")
        
    elif call.data == "menu_6":
        text = (
            "🛠️
