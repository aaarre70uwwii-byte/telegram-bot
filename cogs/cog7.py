from telebot import types
import config

def setup(bot, المطور_الاساسي, admins):
    
    # الكيبورد الرئيسي
    @bot.message_handler(commands=['start','الاوامر'])
    def الاوامر(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        
        markup.add("1","2","3")
        markup.add("اوامر التسليه","اوامر Dev")
        markup.add("اوامر خدميه")
        
        bot.send_message(message.chat.id, f"""<b>AISED
الاوامر
- أهلاً بك عزي في قائمة الاوامر :

━━━━━━━━━━━━
◂ 1م : اوامر الادمنيه
◂ 2م : اوامر الاعدادات
◂ 3م : اوامر القفل - الفتح
◂ 4م : اوامر التسليه
◂ 5م : اوامر Dev
◂ 6م : الاوامر الخدميه
━━━━━━━━━━━━</b>""", reply_markup=markup, parse_mode="HTML")

    # ربط الازرار بباقي الملفات
    @bot.message_handler(content_types=['text'])
    def ربط_الازرار(message):
        text = message.text
        
        if text == "1" or text == "م1":
            م1(message)  # نفس الملف
        elif text == "2" or text == "م2":
            from cogs import cog2
            cog2.م2(message)
        elif text == "3" or text == "م3":
            from cogs import cog3
            cog3.م3(message)
        elif text == "اوامر التسليه" or text == "4" or text == "م4":
            from cogs import cog4
            cog4.م4(message)
        elif text == "اوامر Dev" or text == "5" or text == "م5":
            from cogs import cog5
            cog5.م5(message)
        elif text == "اوامر خدميه" or text == "6" or text == "م6":
            from cogs import cog6
            cog6.م6(message)

    # قائمة 1
    @bot.message_handler(commands=['م1'])
    def م1(message): 
        bot.reply_to(message, f"<b>• أهلاً بك في قائمة اوامر الادمنيه\n━━━━━━━━━━━━\nسيتم اضافتها لاحقا\n━━━━━━━━━━━━</b>")
