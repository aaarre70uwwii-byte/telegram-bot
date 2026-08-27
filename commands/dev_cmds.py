import os
import sys
from pyrogram import Client, filters
from pyrogram.types import (
    Message, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    CallbackQuery,
    ReplyKeyboardRemove
)

# قراءة أيدي المطور الرئيسي من متغيرات البيئة تلقائياً
MAIN_DEV_ID = int(os.getenv("DEV_ID", 0))

secondary_devs = set()       # قائمة المطورين الثانويين
dev_status = {}              # حالات تفعيل الميزات
general_replies = {}         # مخزن الردود العامة
cliches_db = {}              # كليشات القوائم
banned_global = set()        # قائمة الحظر العام
muted_global = set()         # قائمة الكتم العام

def is_dev(user_id: int) -> bool:
    return user_id == MAIN_DEV_ID or user_id in secondary_devs


# --- 1. كيبورد المطور العريض (Reply Keyboard) الذي يظهر في الخاص فقط محل كيبورد الهاتف ---
def get_dev_reply_keyboard():
    keyboard = [
        [KeyboardButton("إعدادات البوت ⚙️"), KeyboardButton("أوامر الإذاعة 📣"), KeyboardButton("قائمه العام 📊")],
        [KeyboardButton("تغيير المطور الاساسي 👑"), KeyboardButton("مسح المطورين 🧹")],
        [KeyboardButton("مسح اسم البوت 🗑️"), KeyboardButton("مسح قائمه العام ❌")],
        [KeyboardButton("تغيير اسم البوت ✏️"), KeyboardButton("مسح المطورين الثانويين 👥")],
        [KeyboardButton("تعطيل التواصل 📴"), KeyboardButton("جلب النسخه الاحتياطيه 📦")],
        [KeyboardButton("تفعيل التواصل 📲"), KeyboardButton("تحديث الملفات 🔄")],
        [KeyboardButton("تفعيل التفعيل التلقائي ✅"), KeyboardButton("تحديث السورس 🚀")],
        [KeyboardButton("تعطيل التفعيل التلقائي 🚫"), KeyboardButton("اخفاء + اظهار قائمه العام 👁️")],
        [KeyboardButton("تعطيل البوت الخدمي 🛑"), KeyboardButton("تفعيل البوت ⚡")],
        [KeyboardButton("تفعيل البوت الخدمي ▶️")],
        [KeyboardButton("• اظهار _ اخفاء • قائمة اعداد البوت ⚙️")],
        [KeyboardButton("اضف ترحيب 👋🏻")],
        [KeyboardButton("قناه تحديثات البوت 📢")],
        [KeyboardButton("• رجوع • الى قائمة البدء ↩️")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# --- 2. أزرار م5 الشفافة (Inline) التي تظهر للأعضاء والمطور داخل الجروبات عند طلب القائمة ---
def get_m5_inline_keyboard():
    buttons = [
        [
            InlineKeyboardButton("أوامر التواصل 📬", callback_data="dev_contact_cmds"),
            InlineKeyboardButton("الحظر والكتم العام 🚫", callback_data="dev_global_punish")
        ],
        [
            InlineKeyboardButton("إدارة الردود العامة 📝", callback_data="dev_replies_cmds"),
            InlineKeyboardButton("إعداد الكليشات ⚙️", callback_data="dev_cliches_cmds")
        ],
        [
            InlineKeyboardButton("أوامر التحديث والتحكم 🔄", callback_data="dev_system_cmds")
        ],
        [
            InlineKeyboardButton("إغلاق القائمة ✖️", callback_data="dev_close_menu")
        ]
    ]
    return InlineKeyboardMarkup(buttons)


# --- 3. معالج أوامر المطور (الخاص والجروبات) ---
@Client.on_message(filters.text, group=5)
async def dev_master_handler(client: Client, message: Message):
    cmd = message.text.strip()
    user_id = message.from_user.id if message.from_user else 0

    # أ. التعامل مع الجروبات (عرض أزرار م5 الشفافة)
    if message.chat.type != message.chat.type.PRIVATE:
        if cmd in ["م5", "اوامر م5"]:
            return await message.reply_text(
                text="⭐️ **أهلاً بك عزيزي في قائمة أوامر المطور (م5) الخاصة بالمجموعات:**\n\nإليك الأقسام المتاحة للمطورين برمجياً بالأسفل:",
                reply_markup=get_m5_inline_keyboard()
            )
        return

    # ب. التعامل مع الخاص (لوحة الكيبورد الثابتة للمطور محل كيبورد الهاتف)
    if not is_dev(user_id):
        return 

    try:
        # إذا فتح المطور الخاص وكتب "مطور" يتم تفعيل الكيبورد العريض
        if cmd in ["لوحة المطور", "المطور", "مطور", "/start"]:
            return await message.reply_text(
                text="🎛️ **تم تفعيل لوحة تحكم المطور بنجاح!**\n- الأزرار الآن مثبتة بالأسفل محل كيبورد الهاتف للتنفيذ السريع والمريح.",
                reply_markup=get_dev_reply_keyboard()
            )

        # تنفيذ الأوامر من خلال قراءة النص القادم من أزرار كيبورد الهاتف العريضة
        if cmd == "تحديث الملفات 🔄" or cmd in ["تحديث", "reload"]:
            await message.reply_text("🔄 جاري تحديث ملفات البوت من السورس وإعادة التشغيل... ⏳")
            os.execv(sys.executable, [sys.executable] + sys.argv)
            return

        elif cmd == "جلب النسخه الاحتياطيه 📦":
            return await message.reply_text("📦 جاري تجميع ملفات قاعدة البيانات وإرسال النسخة الاحتياطية لك فوراً...")

        elif cmd == "تفعيل البوت ⚡":
            return await message.reply_text("⚡ تم تفعيل وتشغيل كافة وظائف البوت الخدمية بنجاح.")

        elif cmd == "• رجوع • الى قائمة البدء ↩️":
            return await message.reply_text("↩️ تم إغلاق لوحة المطور وإخفاء الأزرار من الشاشة الحاليّة.", reply_markup=ReplyKeyboardRemove())

    except Exception as e:
        await message.reply_text(f"⚠️ حدث خطأ داخلي في نظام المطور: {str(e)}")


# --- 4. حماية ومعالجة الأزرار الشفافة لـ م5 في الجروبات ---
@Client.on_callback_query()
async def dev_inline_callback_handler(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data

    # التحقق من أن الضغطة تخص هذا الملف أولاً لعدم التداخل
    if not data.startswith("dev_"):
        return

    # الأزرار الشفافة في الجروبات تعمل فقط للمطورين
    if not is_dev(user_id):
        return await callback_query.answer("❌ عذراً، هذه الأزرار والوظائف الإدارية خاصة بمطوري البوت فقط!", show_alert=True)

    try:
        if data == "dev_contact_cmds":
            await callback_query.message.edit_text("📬 **أوامر التواصل للمطور:**\n\n• اضف رد تواصل\n• حذف رد تواصل\n• ردود التواصل\n• حظر/الغاء حظر بالرد للتواصل", reply_markup=get_m5_inline_keyboard())
        elif data == "dev_global_punish":
            await callback_query.message.edit_text("🚫 **أوامر الحظر والكتم العام:**\n\n• حظر عام - كتم عام\n• الغاء حظر عام - الغاء كتم عام\n• قائمه العام - مسح المحظورين عام", reply_markup=get_m5_inline_keyboard())
        elif data == "dev_replies_cmds":
            await callback_query.message.edit_text("📝 **إدارة الردود العامة:**\n\n• اضف رد عام\n• اضف رد متعدد عام\n• مسح الردود العامه", reply_markup=get_m5_inline_keyboard())
        elif data == "dev_cliches_cmds":
            await callback_query.message.edit_text("⚙️ **أوامر الكليشات:**\n\n• وضع كليشه م1 إلى م6\n• مسح كليشه م1 إلى م6", reply_markup=get_m5_inline_keyboard())
        elif data == "dev_system_cmds":
            await callback_query.message.edit_text("🔄 **أنظمة التحديث والتحكم بالبوت:**\n\n• تحديث السورس\n• تحديث الملفات\n• إعادة تشغيل - reload", reply_markup=get_m5_inline_keyboard())
        elif data == "dev_close_menu":
            await callback_query.message.delete()
            
        await callback_query.answer()  # إنهاء حالة التحميل على الزر
    except Exception:
        pass
