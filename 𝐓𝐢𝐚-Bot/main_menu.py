import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# سحب المتغيرات تلقائيًا من منصة Railway
TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

# التحقق من وجود التوكن لتفادي توقف البوت عند التشغيل
if not TOKEN:
    raise ValueError("⚠️ خطأ: لم يتم العثور على متغير BOT_TOKEN في إعدادات Railway!")

bot = telebot.TeleBot(TOKEN)

# نص القائمة الرئيسية
MAIN_MENU_TEXT = """- ‌‌‏أهلاً بك عزيزي في قائمة الاوامر :
━━━━━━━━━━━━
◂ م1 : اوامر الادمنيه
◂ م2 : اوامر الاعدادات
◂ م3 : اوامر القفل - الفتح
◂ م4 : اوامر التسليه
◂ م5 : اوامر Dev
◂ م6 : الاوامر الخدميه 
━━━━━━━━━━━━"""

# نصوص الصفحات من 1 إلى 6
PAGES_TEXT = {
    "1": "◂ **اوامر الادمنيه:**\n\nهنا تضع أوامر الإدارة (طرد، حظر، كتم...)",
    "2": "◂ **اوامر الاعدادات:**\n\nهنا تضع أوامر إعدادات المجموعة أو البوت",
    "3": "◂ **اوامر القفل - الفتح:**\n\nهنا تضع أوامر قفل وفتح الميديا، الروابط الخ...",
    "4": "◂ **اوامر التسليه:**\n\nهنا تضع ألعاب وأوامر التسلية والترفيه",
    "5": "◂ **اوامر Dev:**\n\nأوامر خاصة بمطور البوت فقط",
    "6": "◂ **الاوامر الخدميه:**\n\nهنا تضع الأوامر العامة والخدمية للمستخدمين"
}

# دالة إنشاء لوحة الأزرار الديناميكية
def create_keyboard(current_page=None):
    markup = InlineKeyboardMarkup()
    
    # تصميم الأزرار الرقمية
    btn1 = InlineKeyboardButton("1", callback_data="page_1")
    btn2 = InlineKeyboardButton("2", callback_data="page_2")
    btn3 = InlineKeyboardButton("3", callback_data="page_3")
    btn4 = InlineKeyboardButton("4", callback_data="page_4")
    btn5 = InlineKeyboardButton("5", callback_data="page_5")
    btn6 = InlineKeyboardButton("6", callback_data="page_6")
    
    markup.row(btn1)
    markup.row(btn2, btn3, btn4, btn5, btn6)
    
    # أزرار التنقل (التالي، السابق، القائمة الرئيسية)
    if current_page:
        try:
            current_num = int(current_page)
            prev_num = 6 if current_num == 1 else current_num - 1
            next_num = 1 if current_num == 6 else current_num + 1
            
            btn_prev = InlineKeyboardButton("⬅️ السابق", callback_data=f"page_{prev_num}")
            btn_main = InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")
            btn_next = InlineKeyboardButton("التالي ➡️", callback_data=f"page_{next_num}")
            
            markup.row(btn_prev, btn_main, btn_next)
        except ValueError:
            pass
            
    # زر الاشتراك/التحديثات مع إخفاء اليوزر داخل الرابط
    btn_channel = InlineKeyboardButton("تحديثات 𝐓𝐢𝐚", url="https://t.me")
    markup.row(btn_channel)
    
    # أزرار فاضية بدون شيء للتصميم
    btn_empty1 = InlineKeyboardButton(" 🔘 ", callback_data="empty")
    btn_empty2 = InlineKeyboardButton(" 🔘 ", callback_data="empty")
    markup.row(btn_empty1, btn_empty2)
    
    return markup

# 1. الاستجابة لأمر "الاوامر" في المجموعات والخاص
@bot.message_handler(func=lambda message: message.text == "الاوامر")
def send_commands_group(message):
    markup = create_keyboard()
    bot.reply_to(message, MAIN_MENU_TEXT, reply_markup=markup, parse_mode="Markdown")

# 2. الاستجابة لأمر "الاوامر" في القنوات
@bot.channel_post_handler(func=lambda message: message.text == "الاوامر")
def send_commands_channel(message):
    markup = create_keyboard()
    bot.send_message(message.chat.id, MAIN_MENU_TEXT, reply_markup=markup, parse_mode="Markdown")

# 3. أمر التفعيل (يرد "تم تفعيل بنجاح") للمجموعات والقنوات
@bot.message_handler(func=lambda message: message.text == "تفعيل")
@bot.channel_post_handler(func=lambda message: message.text == "تفعيل")
def activate_cmd(message):
    try:
        bot.reply_to(message, "تم تفعيل بنجاح")
    except Exception:
        try:
            bot.send_message(message.chat.id, "تم تفعيل بنجاح")
        except Exception:
            pass

# 4. أمر إخفاء الاوامر بدون أخطاء
@bot.message_handler(func=lambda message: message.text == "اخفاء الاوامر")
@bot.channel_post_handler(func=lambda message: message.text == "اخفاء الاوامر")
def hide_commands(message):
    try:
        if message.reply_to_message:
            bot.delete_message(message.chat.id, message.reply_to_message.message_id)
        bot.delete_message(message.chat.id, message.message_id)
    except Exception:
        pass

# 5. معالجة الضغط على الأزرار (تم تصحيح الـ split والـ index هنا)
@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    try:
        if call.data == "main_menu":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                                  text=MAIN_MENU_TEXT, reply_markup=create_keyboard(), parse_mode="Markdown")
            bot.answer_callback_query(call.id)
            
        elif call.data.startswith("page_"):
            # تصحيح: استخراج النص الرقمي فقط عبر تحديد الـ index الثاني [1]
            page_num = call.data.split("_")[1]
            page_text = PAGES_TEXT.get(page_num, "قسم فارغ")
            
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                                  text=page_text, reply_markup=create_keyboard(current_page=page_num), parse_mode="Markdown")
            bot.answer_callback_query(call.id)
            
        elif call.data == "empty":
            bot.answer_callback_query(call.id, text="هذا الزر فارغ مخصص للتصميم فقط!", show_alert=False)
            
    except Exception as e:
        print(f"Error in callback: {e}")

# تشغيل البوت
print("البوت جاهز ومفحوص ويعمل على منصة Railway...")
bot.infinity_polling()
