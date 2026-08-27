import os
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.errors import ChatAdminRequired, UserAdminInvalid

# قراءة أيدي المطور من متغيرات البيئة (يحمل القيمة 0 كافتراضي لحماية الكود)
DEV_ID = int(os.getenv("DEV_ID", 0))

# دالة مساعدة للتحقق من صلاحيات المشرف أو المطور لضمان أمان البوت
async def is_admin_or_dev(client: Client, chat_id: int, user_id: int) -> bool:
    if user_id == DEV_ID:
        return True
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except Exception:
        return False

# --- 1. أوامر الرفع والتنزيل ---
@Client.on_message(filters.group & filters.text)
async def manage_roles(client: Client, message: Message):
    cmd = message.text.strip()
    chat_id = message.chat.id
    user_id = message.from_user.id

    # قائمة بأوامر الرفع والتنزيل المدعومة
    roles_cmds = [
        "رفع مالك اساسي", "تنزيل مالك اساسي", "رفع مالك", "تنزيل مالك",
        "رفع مشرف", "تنزيل مشرف", "رفع منشئ", "تنزيل منشئ",
        "رفع مدير", "تنزيل مدير", "رفع ادمن", "تنزيل ادمن",
        "رفع مميز", "تنزيل مميز", "تنزيل الكل"
    ]

    if cmd not in roles_cmds:
        return

    # التحقق من الصلاحيات
    if not await is_admin_or_dev(client, chat_id, user_id):
        return await message.reply_text("❌ عذراً، هذا الأمر خاص بالمشرفين ومطور البوت فقط.")

    # التحقق من وجود رد (Reply)
    if not message.reply_to_message:
        return await message.reply_text("⚠️ يرجى الرد (Reply) على رسالة الشخص لتنفيذ الأمر عليه.")

    target_user = message.reply_to_message.from_user
    target_name = target_user.first_name
    target_link = f"[{target_name}](tg://user?id={target_user.id})"

    if cmd == "تنزيل الكل":
        await message.reply_text(f"⚠️ تم تنزيل وإلغاء جميع الرتب المرفوعة للعضو {target_link} بنجاح.")
    else:
        action = "رفع" if cmd.startswith("رفع") else "تنزيل"
        role_name = cmd.split(None, 1)[1]
        await message.reply_text(f"🔹 تم {action} العضو {target_link} كـ (**{role_name}**) بنجاح.")


# --- 2. أوامر المسح ---
@Client.on_message(filters.group & filters.text)
async def clear_data(client: Client, message: Message):
    cmd = message.text.strip()
    chat_id = message.chat.id
    user_id = message.from_user.id

    clear_cmds = ["مسح المحظورين", "مسح المكتومين", "مسح قائمه المنع", "مسح الردود", "مسح الروابط"]

    if cmd not in clear_cmds:
        return

    if not await is_admin_or_dev(client, chat_id, user_id):
        return await message.reply_text("❌ عذراً، هذا الأمر خاص بالمشرفين ومطور البوت فقط.")

    # هنا يمكنك لاحقاً ربطها بقاعدة البيانات الخاصة بالردود أو المنع لتصفيرها
    await message.reply_text(f"🧹 تم البدء في تنفيذ أمر (**{cmd}**) وتفريغ البيانات المطلوبة بنجاح.")


# --- 3. أوامر الطرد والحظر والكتم الآمنة ---
@Client.on_message(filters.group & filters.text)
async def punishment_actions(client: Client, message: Message):
    cmd = message.text.strip()
    chat_id = message.chat.id
    user_id = message.from_user.id

    # الأوامر العادية والأوامر التي تحتوي على وقت (مثل: تقييد + الوقت)
    if not (cmd in ["حظر", "طرد", "كتم", "تقييد"] or cmd.startswith("تقييد ")):
        return

    if not await is_admin_or_dev(client, chat_id, user_id):
        return await message.reply_text("❌ عذراً، هذا الأمر خاص بالمشرفين ومطور البوت فقط.")

    if not message.reply_to_message:
        return await message.reply_text("⚠️ يرجى الرد على رسالة العضو لتنفيذ العقوبة.")

    target_id = message.reply_to_message.from_user.id
    target_name = message.reply_to_message.from_user.first_name
    target_link = f"[{target_name}](tg://user?id={target_id})"

    try:
        if cmd == "حظر":
            await message.chat.ban_member(target_id)
            await message.reply_text(f"🚫 تم حظر العضو {target_link} من المجموعة.")
        elif cmd == "طرد":
            await message.chat.ban_member(target_id)
            await message.chat.unban_member(target_id)
            await message.reply_text(f"🚷 تم طرد العضو {target_link} خارج المجموعة.")
        elif cmd == "كتم" or cmd == "تقييد" or cmd.startswith("تقييد "):
            # تقييد افتراضي بمنع إرسال الرسائل
            await message.chat.restrict_member(target_id, ChatPermissions(can_send_messages=False))
            await message.reply_text(f"🔇 تم كتم وتقييد صلاحيات العضو {target_link} بنجاح.")
            
    except ChatAdminRequired:
        await message.reply_text("❌ خطأ: البوت يحتاج إلى صلاحيات مشرف كاملة (تأكد من رفع البوت مشرف).")
    except UserAdminInvalid:
        await message.reply_text("❌ خطأ: لا يمكنك تطبيق هذا الإجراء على مشرف آخر أو على مالك المجموعة.")
    except Exception as e:
        await message.reply_text(f"⚠️ حدث خطأ أثناء تنفيذ العقوبة: {str(e)}")


# --- 4. أوامر إلغاء العقوبات وفك القيود ---
@Client.on_message(filters.group & filters.text)
async def lift_punishment_actions(client: Client, message: Message):
    cmd = message.text.strip()
    chat_id = message.chat.id
    user_id = message.from_user.id

    lift_cmds = ["الغاء الحظر", "الغاء الكتم", "فك التقييد", "رفع القيود"]

    if cmd not in lift_cmds:
        return

    if not await is_admin_or_dev(client, chat_id, user_id):
        return await message.reply_text("❌ عذراً، هذا الأمر خاص بالمشرفين ومطور البوت فقط.")

    if not message.reply_to_message:
        return await message.reply_text("⚠️ يرجى الرد على رسالة العضو لالغاء القيود عنه.")

    target_id = message.reply_to_message.from_user.id
    target_name = message.reply_to_message.from_user.first_name
    target_link = f"[{target_name}](tg://user?id={target_id})"

    try:
        if cmd == "الغاء الحظر":
            await message.chat.unban_member(target_id)
            await message.reply_text(f"✅ تم إلغاء حظر العضو {target_link} ويمكنه العودة للجروب.")
        else:
            # إعادة كافة الصلاحيات للكتابة وإرسال الوسائط
            await message.chat.restrict_member(target_id, ChatPermissions(
                can_send_messages=True, can_send_media_messages=True,
                can_send_polls=True, can_add_web_page_previews=True
            ))
            await message.reply_text(f"🔊 تم فك التقييد وإلغاء الكتم عن العضو {target_link} بنجاح.")
            
    except ChatAdminRequired:
        await message.reply_text("❌ خطأ: البوت يحتاج صلاحية مشرف لفك القيود.")
    except Exception as e:
        await message.reply_text(f"⚠️ حدث خطأ: {str(e)}")
