import os
import sys
import io
import random
import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from http.server import BaseHTTPRequestHandler, HTTPServer

# ---------- 🌐 خادم الويب لإبقاء البوت حي 24/7 ----------
class KeepAliveServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"TiA Bot is Alive 24/7")
    def log_message(self, *args): pass

def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), KeepAliveServer)
    threading.Thread(target=server.serve_forever, daemon=True).start()

# ---------- 🤖 إعدادات البوت ----------
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    print("❌ خطأ: BOT_TOKEN")
    sys.exit(1)

keep_alive()
bot = telebot.TeleBot(BOT_TOKEN)

user_codes = {}
group_settings = {}
bank_accounts = {}
group_responses = {}
custom_ranks = {"dev_basic": [], "dev_m": [], "owner_basic": {}, "owner": {}, "vip": {}}
DEVELOPER_ID = 7488375443

FUN_QUESTIONS = ["لو خيروك جزيرة لوحدك ولا مع شخص تكرهه؟", "اكره صفة في اللي قدامك؟", "لو معاك مليون دولار اول شي تسويه؟"]
JOKES = ["محش شاف ممنوع الوقوف انسدح!", "مرة نملة شافت عصير قالت البحر الاحمر!"]
WORD_GAME = ["تفاحة", "مدرسة", "برمجة", "تليجرام", "كمبيوتر"]

GROUP_MENU_TEXT = (
    "↢ اهلا فيك في قائمة 𝐓𝐢α الشاملة ✓\n━━━━━ 𝐓𝐢α ━━━━━\n\n"
    "↢ تفعيل الردود | تعطيل الردود\n"
    "↢ اضف ردي + الكلمة + الرد\n"
    "↢ تاك ↤ نداء جماعي\n"
    "↢ انشا حسابي بنكي | فلوسي | استثمار [المبلغ]\n"
    "↢ كشط | زوجني | كت | كلمات\n"
    "━━━━━ 𝐓𝐢α ━━━━━\n@eeccvu"
)

def is_admin(chat_id, user_id):
    if user_id == DEVELOPER_ID or user_id in custom_ranks["dev_basic"] or user_id in custom_ranks["dev_m"]: return True
    try: return bot.get_chat_member(chat_id, user_id).status in ['creator', 'administrator']
    except: return False

def init_group_settings(chat_id):
    if chat_id not in group_settings: group_settings[chat_id] = {"status": True, "responses_enabled": True}
    if chat_id not in group_responses: group_responses[chat_id] = {}
    for key in ["owner_basic", "owner", "vip"]:
        if chat_id not in custom_ranks[key]: custom_ranks[key][chat_id] = []
    return group_settings[chat_id]

def get_dev_main_keyboard():
    m = InlineKeyboardMarkup(row_width=2)
    m.add(InlineKeyboardButton("⌨️ كيبورد الرموز", callback_data="dev_open_kb"), InlineKeyboardButton("🚀 تشغيل", callback_data="dev_run_code"))
    m.add(InlineKeyboardButton("📋 عرض", callback_data="dev_show_code"), InlineKeyboardButton("🧹 مسح", callback_data="dev_clear_code"))
    return m

def get_dev_symbols_keyboard():
    m = InlineKeyboardMarkup(row_width=4)
    m.row(InlineKeyboardButton("{ }", "dev_add_{ }"), InlineKeyboardButton("[ ]", "dev_add_[ ]"), InlineKeyboardButton("( )", "dev_add_( )"), InlineKeyboardButton(":", "dev_add_:"))
    m.row(InlineKeyboardButton(";", "dev_add_;"), InlineKeyboardButton("=", "dev_add_="), InlineKeyboardButton("+", "dev_add_+"), InlineKeyboardButton("-", "dev_add_-"))
    m.row(InlineKeyboardButton("🔙 رجوع", "dev_main_menu"))
    return m

# ---------- 🔥 حفظ الكود من الخاص ----------
@bot.message_handler(func=lambda msg: msg.chat.type == "private" and not msg.text.startswith('/'))
def save_code(message):
    cid = message.chat.id
    user_codes.setdefault(cid, "")
    user_codes[cid] += message.text + "\n"
    bot.reply_to(message, "✅ تم حفظ السطر. اضغط `تشغيل`", parse_mode="Markdown")

# ---------- الرسائل ----------
@bot.message_handler(commands=['start', 'help', 'الاوامر', 'أوامر'])
def start(message):
    if message.chat.type == "private":
        user_codes.setdefault(message.chat.id, "")
        bot.send_message(message.chat.id, "💻 **لوحة المطور 𝐓𝐢α 24/7**\n\nارسل الكود هنا سطر سطر\nوبعدها اضغط زر `تشغيل`", reply_markup=get_dev_main_keyboard(), parse_mode="Markdown")
    else:
        init_group_settings(message.chat.id)
        bot.reply_to(message, GROUP_MENU_TEXT)

@bot.message_handler(func=lambda msg: msg.text in ['رفع مطور اساسي', 'تنزيل مطور اساسي', 'رفع m', 'تنزيل m'])
def dev_rank(message):
    if message.from_user.id!= DEVELOPER_ID or not message.reply_to_message: return
    tid = message.reply_to_message.from_user.id; name = message.reply_to_message.from_user.first_name
    if message.text == 'رفع مطور اساسي':
        if tid not in custom_ranks["dev_basic"]: custom_ranks["dev_basic"].append(tid)
        bot.reply_to(message, f"🛡️ تم رفع {name} مطور اساسي")
    elif message.text == 'تنزيل مطور اساسي':
        if tid in custom_ranks["dev_basic"]: custom_ranks["dev_basic"].remove(tid)
        bot.reply_to(message, f"✖️ تم تنزيل {name}")

@bot.message_handler(func=lambda msg: msg.chat.type!= "private" and msg.text in ['تفعيل الردود', 'تعطيل الردود'] or msg.text.startswith("اضف ردي "))
def responses(message):
    if not is_admin(message.chat.id, message.from_user.id): return
    s = init_group_settings(message.chat.id)
    if message.text == 'تفعيل الردود': s["responses_enabled"] = True; bot.reply_to(message, "🟢 تم تفعيل الردود")
    elif message.text == 'تعطيل الردود': s["responses_enabled"] = False; bot.reply_to(message, "🔴 تم تعطيل الردود")
    elif message.text.startswith("اضف ردي "):
        try: k, v = message.text.replace("اضف ردي ", "").split(" ", 1); group_responses[message.chat.id][k] = v; bot.reply_to(message, f"📝 تم اضافة رد: `{k}`", parse_mode="Markdown")
        except: bot.reply_to(message, "⚠️ اكتب: اضف ردي هلا هلا والله")

@bot.message_handler(func=lambda msg: msg.chat.type!= "private" and msg.text == "تاك")
def tag(message):
    if not is_admin(message.chat.id, message.from_user.id): return
    admins = bot.get_chat_administrators(message.chat.id)
    tag = "📣 **نداء جماعي:**\n" + " ".join([f"[{a.user.first_name}](tg://user?id={a.user.id})" for a in admins[:20] if not a.user.is_bot])
    bot.send_message(message.chat.id, tag, parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.chat.type!= "private" and msg.text)
def games(message):
    cid, uid, text = message.chat.id, message.from_user.id, message.text
    s = init_group_settings(cid)
    if s["responses_enabled"] and text in group_responses.get(cid, {}): return bot.reply_to(message, group_responses[cid][text])

    if text == 'انشا حسابي بنكي':
        bank_accounts.setdefault(uid, {"balance": 500, "invested": 0}); bot.reply_to(message, "💳 تم انشاء حسابك +500$ هدية")
    elif text == 'فلوسي':
        if uid not in bank_accounts: return bot.reply_to(message, "⚠️ سوي حساب اول: انشا حسابي بنكي")
        b = bank_accounts[uid]; bot.reply_to(message, f"💰 **رصيدك:** `{b['balance']}$`\n📈 **مستثمر:** `{b['invested']}$`", parse_mode="Markdown")
    elif text.startswith("استثمار "):
        if uid not in bank_accounts: return bot.reply_to(message, "⚠️ سوي حساب اول")
        try:
            amt = int(text.split()[1])
            if amt <= 0 or amt > bank_accounts[uid]["balance"]: return bot.reply_to(message, "❌ المبلغ غلط او رصيدك ما يكفي")
            bank_accounts[uid]["balance"] -= amt; bank_accounts[uid]["invested"] += amt
            profit = int(amt * 0.2); bank_accounts[uid]["balance"] += amt + profit
            bot.reply_to(message, f"📈 استثمرت `{amt}$` وربحت `{profit}$`\nرصيدك: `{bank_accounts[uid]['balance']}$`", parse_mode="Markdown")
        except: bot.reply_to(message, "⚠️ مثال: استثمار 100")
    elif text == 'كشط':
        if uid not in bank_accounts: return bot.reply_to(message, "⚠️ سوي حساب")
        win = random.randint(50, 300); bank_accounts[uid]["balance"] += win; bot.reply_to(message, f"🎰 فزت `{win}$`")
    elif text == 'زوجني': bot.reply_to(message, f"💍 تم تزويجك لعضو عشوائي 😂")
    elif text == 'كت': bot.reply_to(message, f"🎯 كت تويت: {random.choice(FUN_QUESTIONS)}")
    elif text == 'كلمات': w = random.choice(WORD_GAME); bot.reply_to(message, f"⌨️ رتب الكلمة: `{''.join(random.sample(w, len(w)))}`", parse_mode="Markdown")

# ---------- الازرار - مصلحة من خطأ 409 ----------
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    cid = call.message.chat.id
    mid = call.message.message_id # التعديل المهم هنا
    data = call.data
    bot.answer_callback_query(call.id)

    if data == "dev_main_menu":
        bot.edit_message_text("💻 لوحة التحكم", cid, mid, reply_markup=get_dev_main_keyboard())
    elif data == "dev_open_kb":
        bot.edit_message_text("⌨️ اختار الرموز:", cid, mid, reply_markup=get_dev_symbols_keyboard())
    elif data.startswith("dev_add_"):
        user_codes.setdefault(cid, "")
        user_codes[cid] += data.replace("dev_add_", "") + "\n"
        bot.answer_callback_query(call.id, "تمت الاضافة ✅")
    elif data == "dev_show_code":
        code = user_codes.get(cid, 'فاضي')
        bot.send_message(cid, f"📋 كودك:\n```\n{code}\n```", parse_mode="Markdown")
    elif data == "dev_clear_code":
        user_codes[cid] = ""
        bot.answer_callback_query(call.id, "تم المسح 🧹")
    elif data == "dev_run_code":
        code = user_codes.get(cid, "")
        if not code:
            return bot.answer_callback_query(call.id, "الكود فاضي!", show_alert=True)
        try:
            old, new = sys.stdout, io.StringIO()
            sys.stdout = new
            exec(code, {})
            sys.stdout = old
            result = new.getvalue()
            bot.send_message(cid, f"✅ النتيجة:\n```\n{result if result else 'تم التنفيذ'}\n```", parse_mode="Markdown")
        except Exception as e:
            bot.send_message(cid, f"❌ خطأ:\n`{e}`", parse_mode="Markdown")

print("✅ البوت 𝐓𝐢α شغال 24/7")
bot.infinity_polling(none_stop=True, skip_pending=True, long_polling_timeout=30)
