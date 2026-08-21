import os
import sys
import time
import io
import random
import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPrivileges
from http.server import BaseHTTPRequestHandler, HTTPServer

# ---------- 🌐 خادم الويب المدمج لإبقاء البوت حياً ----------
class KeepAliveServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write("🟢 سورس 𝐓𝐢α الخارق نشط ويعمل بنجاح 24/7 مع أنظمة الحماية والردود المتقدمة والتاك!".encode('utf-8'))

    def log_message(self, format, *args):
        # تعطيل طباعة سجلات الويب العشوائية في الترمينال للحفاظ على نظافة الـ Logs
        return

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), KeepAliveServer)
    server.serve_forever()

def keep_alive():
    """تشغيل الخادم في خلفية منفصلة لتأمين استمرار البوت"""
    t = threading.Thread(target=run_web_server)
    t.daemon = True
    t.start()

# ---------- 🤖 إعدادات البوت والتوكن والتعريفات ----------
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    print("❌ خطأ: لم يتم العثور على متغير البيئة 'BOT_TOKEN'. يرجى إضافته في منصة الاستضافة.")
    sys.exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

user_codes = {}
group_settings = {}
secret_whispers = {}
custom_commands = {}
bank_accounts = {}

# قواميس لحفظ الردود المخصصة التلقائية (لكل جروب)
group_responses = {}

custom_ranks = {
    "dev_basic": [],   # مطور اساسي
    "dev_m": [],       # مطور m
    "owner_basic": {}, 
    "owner": {},       
    "vip": {}          
}

DEVELOPER_ID = 7488375443  # آيدي المطور الأساسي الثابت والمحمي

FUN_QUESTIONS = ["لو خيروك تعيش في جزيرة لوحدك أو مع شخص تكرهه؟", "صفة مستحيل تتحملها بالشخص اللي قدامك؟"]
JOKES = ["محشش شاف إشارة ممنوع الوقوف، قام انسدح!", "مرة نملة شافت عصير فراولة قالت: واو أخيراً شفت البحر الأحمر!"]
WORD_GAME = ["تفاحة", "مدرسة", "برمجة", "تليجرام", "سيرفر", "كمبيوتر"]

GROUP_MENU_TEXT = (
    "↢ أهلاً يا حلو ♡\n"
    "• قائمة اوامر 𝐓𝐢α الشاملة والحماية\n\n"
    "- أنظمة الردود والتاك والبنك المدمجة:\n"
    "↢ تفعيل الردود | تعطيل الردود\n"
    "↢ اضف ردي + الكلمة + الرد (بالرد أو سطر واحد)\n"
    "↢ تاك ↤ لعمل نداء جماعي للأعضاء\n"
    "↢ انشا حسابي بنكي | فلوسي | استثمار\n"
    "↢ كشط | زوجني | كت | كلمات\n\n"
    "تحديثات السورس الحصرية: « 𝐓𝐢α »  @eeccvu"
)

# ---------- دالات فحص الهوية والتهيئة ----------

def is_admin(chat_id, user_id):
    if user_id == DEVELOPER_ID or user_id in custom_ranks["dev_basic"] or user_id in custom_ranks["dev_m"]: return True
    if chat_id in custom_ranks["owner_basic"] and user_id in custom_ranks["owner_basic"][chat_id]: return True
    if chat_id in custom_ranks["owner"] and user_id in custom_ranks["owner"][chat_id]: return True
    try:
        chat_member = bot.get_chat_member(chat_id, user_id)
        return chat_member.status in ['creator', 'administrator']
    except Exception: return False

def get_user_rank(chat_id, user_id):
    if user_id == DEVELOPER_ID: return "مطور السورس الأساسي 👑"
    if user_id in custom_ranks["dev_basic"]: return "مطور اساسي بالسورس 🛡️"
    if user_id in custom_ranks["dev_m"]: return "مطور m معتمد ⚡"
    try:
        member = bot.get_chat_member(chat_id, user_id)
        if member.status == 'creator': return "المالك الأساسي للمجموعة 💎"
        elif member.status == 'administrator': return "مشرف الجروب 👮‍♂️"
        else: return "عضو محترم 👤"
    except Exception: return "عضو 👤"

def init_group_settings(chat_id):
    if chat_id not in group_settings:
        group_settings[chat_id] = {
            "status": True, 
            "welcome": True, 
            "welcome_msg": "أهلاً بك يا قلبي في المجموعة!", 
            "lock_links": False,
            "lock_photos": False,
            "responses_enabled": True  
        }
    if chat_id not in group_responses:
        group_responses[chat_id] = {}
    for key in custom_ranks.keys():
        if key not in ["dev_basic", "dev_m"] and chat_id not in custom_ranks[key]: custom_ranks[key][chat_id] = []
    return group_settings[chat_id]

# ---------- 💬 قسم استقبال الرسائل والأوامر النصية ----------

@bot.message_handler(commands=['start', 'help', 'الاوامر', 'أوامر', 'اوامر'])
def handle_start_and_commands(message):
    chat_id = message.chat.id
    if message.chat.type == "private":
        bot.send_message(chat_id, "💻 **مرحباً بك في لوحة كيبورد المطور 24/7!**", reply_markup=get_dev_main_keyboard())
    else:
        init_group_settings(chat_id)
        bot.reply_to(message, GROUP_MENU_TEXT)

# أوامر الرفع للمطورين والأمور الإدارية الخارقة
@bot.message_handler(func=lambda msg: msg.text in ['رفع مطور اساسي', 'تنزيل مطور اساسي', 'رفع m', 'تنزيل m'])
def handle_developer_promotions(message):
    if message.from_user.id != DEVELOPER_ID: return
    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ يرجى الرد على العضو المقصود!")
        return
    target_id = message.reply_to_message.from_user.id
    target_name = message.reply_to_message.from_user.first_name
    
    if message.text == 'رفع مطور اساسي':
        if target_id not in custom_ranks["dev_basic"]: custom_ranks["dev_basic"].append(target_id)
        bot.reply_to(message, f"🛡️ تم رفع **{target_name}** مطور اساسي للسورس بنجاح!")
    elif message.text == 'تنزيل مطور اساسي':
        if target_id in custom_ranks["dev_basic"]: custom_ranks["dev_basic"].remove(target_id)
        bot.reply_to(message, f"✖️ تم تنزيل المطور الاساسي **{target_name}**.")
    elif message.text == 'رفع m':
        if target_id not in custom_ranks["dev_m"]: custom_ranks["dev_m"].append(target_id)
        bot.reply_to(message, f"⚡ تم رفع **{target_name}** مطور m معتمد!")
    elif message.text == 'تنزيل m':
        if target_id in custom_ranks["dev_m"]: custom_ranks["dev_m"].remove(target_id)
        bot.reply_to(message, f"✖️ تم تنزيل المطور m **{target_name}**.")

# نظام تفعيل/تعطيل الردود وإضافة ردود مخصصة بالجروب (اضف ردي)
@bot.message_handler(func=lambda msg: msg.chat.type != "private" and msg.text and (msg.text in ['تفعيل الردود', 'تعطيل الردود'] or msg.text.startswith("اضف ردي ")))
def handle_response_settings(message):
    chat_id = message.chat.id
    if not is_admin(chat_id, message.from_user.id): return
    settings = init_group_settings(chat_id)
    text = message.text

    if text == 'تفعيل الردود':
        settings["responses_enabled"] = True
        bot.reply_to(message, "🟢 تم تفعيل ردود الأعضاء والردود التلقائية بالجروب بنجاح.")
    elif text == 'تعطيل الردود':
        settings["responses_enabled"] = False
        bot.reply_to(message, "🔴 تم تعطيل وقفل ردود الأعضاء في هذه المجموعة.")
    elif text.startswith("اضف ردي "):
        content = text.replace("اضف ردي ", "").strip()
        parts = content.split(" ", 1)
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ طريقة الاستخدام خطأ! اكتب كالتالي:\n`اضف ردي` + الكلمة المفتاحية + الرد المطلوب عليها\nمثال: `اضف ردي هلا هيلين نورت الجروب`", parse_mode="Markdown")
            return
        trigger_word = parts[0].strip()
        reply_val = parts[1].strip()
        
        group_responses[chat_id][trigger_word] = reply_val
        bot.reply_to(message, f"📝 **تم إضافة الرد التلقائي المخصص بنجاح!**\n• الكلمة: `{trigger_word}`\n• الرد: `{reply_val}`", parse_mode="Markdown")

# نظام التاك الجماعي والنداء التلقائي لجميع الأعضاء والمشرفين
@bot.message_handler(func=lambda msg: msg.chat.type != "private" and msg.text == "تاك")
def handle_group_tag_all(message):
    chat_id = message.chat.id
    if not is_admin(chat_id, message.from_user.id): return
    
    try:
        admins = bot.get_chat_administrators(chat_id)
        tag_text = "📣 **نداء جماعي تلقائي عاجل لجميع الأعضاء والمشرفين بالتفاعل!**\n━━━━━ 𝐓𝐢α ━━━━━\n"
        
        for admin in admins[:10]: 
            if not admin.user.is_bot:
                tag_text += f"↤ [{admin.user.first_name}](tg://user?id={admin.user.id}) \n"
        
        tag_text += "━━━━━ 𝐓𝐢α ━━━━━\n💡 الرجاء التواجد والتفاعل بالجروب يا حلوين حياكم!"
        bot.send_message(chat_id, tag_text, parse_mode="Markdown")
    except Exception:
        bot.reply_to(message, "📣 تواجدوا يا حلوين بالشات نبي تفاعل فخم اليوم! 🔥")

# نظام البنك المالي والألعاب الجماعية التفاعلية وردود الهيبة
@bot.message_handler(func=lambda msg: msg.chat.type != "private" and msg.text)
def handle_bank_games_and_responses(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    text = message.text
    settings = init_group_settings(chat_id)

    if settings.get("responses_enabled") and text in group_responses.get(chat_id, {}):
        bot.reply_to(message, group_responses[chat_id][text])
        return

    if 'مطور' in text or 'المطور' in text:
        dev_replies = ["تاج راسي المطور وغالينا، تبي منه شيء؟ 😎", "المطور مشغول حالياً ببرمجة أكواد خارقة مثلي، لا تزعجه 💻✨"]
        if user_id != DEVELOPER_ID: bot.reply_to(message, random.choice(dev_replies))
        return

    if text == 'انشا حسابي بنكي':
        if user_id in bank_accounts: bot.reply_to(message, "⚠️ حسابك البنكي نشط بالفعل ولديك أموال!")
        else:
            bank_accounts[user_id] = {"balance": 500, "invested": 0}
            bot.reply_to(message, f"💳 **تم إنشاء حسابك البنكي بنجاح في سورس 𝐓𝐢α!**\n💰 تم إيداع هدية ترحيبية: `500$` في رصيدك الحالي.", parse_mode="Markdown")
    elif text == 'فلوسي':
        if user_id not in bank_accounts:
            bot.reply_to(message, "⚠️ ليس لديك حساب بنكي حالياً! اكتب (انشا حسابي بنكي) للبدء.")
            return
        bot.reply_to(message, f"💰 **كشف حسابك المالي الحالي:**\n• الرصيد المتاح: `{bank_accounts[user_id]['balance']}$`", parse_mode="Markdown")
    elif text.startswith("استثمار "):
        if user_id not in bank_accounts: return
        try:
