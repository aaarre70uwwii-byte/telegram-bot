import os
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.errors import ChatAdminRequired

# قراءة أيدي المطور من متغيرات البيئة تلقائياً
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

# قواعد بيانات مؤقتة في الذاكرة لتخزين الحالات
locks_db = {}
features_db = {}

# القائمة المعتمدة والمدققة لأوامر القفل والفتح
LOCKABLE_ITEMS = [
    "جمثون", "السب", "الايرانيه", "الكتابه", "الاباحي", "تعديل الميديا",
    "التعديل", "الفيديو", "الصور", "الملصقات", "المتحركه", "الدردشه",
    "الروابط", "التاك", "البوتات", "المعرفات", "الكلايش", "التكرار",
    "التوجيه", "الانلاين", "الجهات", "الكل", "الدخول", "الصوت",
    "التوجيه بالتقييد", "الروابط بالتقييد", "المتحركه بالتقييد",
    "الصور بالتقييد", "الفيديو بالتقييد", "البوتات بالطرد"
]

# القائمة المعتمدة والمدققة لأوامر التفعيل والتعطيل
TOGGLE_FEATURES = [
    "ضافني", "الاذكار", "الذكار", "الثنائي", "افتاري", "التسليه", "الكت", "الترحيب",
    "الردود", "الانذار", "التحذير", "الايدي", "الرابط", "اطردني", "الحظر",
    "الرفع", "التنزيل", "التحويل", "الحمايه", "المنشن", "وضع الاقتباسات",
    "الخدميه", "اليوتيوب", "الايدي بالصوره", "التحقق", "ردود السورس"
]

# --- 1. معالج أوامر القفل والفتح ---
@Client.on_message(filters.group & filters.text)
async def lock_unlock_handler(client: Client, message: Message):
    cmd = message.text.strip()
    chat_id = message.chat.id
    user_id = message.from_user.id

    action = None
    target_item = None

    if cmd.startswith("قفل "):
        action = "lock"
        target_item = cmd.replace("قفل ", "", 1).strip()
    elif cmd.startswith("فتح "):
        action = "unlock"
        target_item = cmd.replace("فتح ", "", 1).strip()

    if not action or target_item not in LOCKABLE_ITEMS:
        return

    if not await is_admin_or_dev(client, chat_id, user_id):
        return await message.reply_text("❌ عذراً، هذا الأمر خاص بالمشرفين ومطور البوت فقط.")

    if chat_id not in locks_db:
        locks_db[chat_id] = {}

    try:
        # جلب الصلاحيات الحالية للجروب لتجنب تصفيرها أو قفل الجروب بالكامل بالخطأ
        chat_obj = await client.get_chat(chat_id)
        current_perms = chat_obj.permissions or ChatPermissions()
        
        status = False if action == "lock" else True

        # تعديل صلاحيات تليجرام المباشرة بناء على العنصر المستهدف بدقة
        if target_item in ["الكتابه", "الدردشه", "الكل"]:
            new_perms = ChatPermissions(
                can_send_messages=status,
                can_send_media_messages=status,
                can_send_polls=status,
                can_send_other_messages=status,
                can_add_web_page_previews=status,
                can_change_info=current_perms.can_change_info,
                can_invite_users=current_perms.can_invite_users,
                can_pin_messages=current_perms.can_pin_messages
            )
            await client.set_chat_permissions(chat_id, new_perms)
            
        elif target_item in ["الصور", "الفيديو", "الملصقات", "المتحركه", "الصوت"]:
            new_perms = ChatPermissions(
                can_send_messages=current_perms.can_send_messages,
                can_send_media_messages=status if target_item in ["الصور", "الفيديو"] else current_perms.can_send_media_messages,
                can_send_other_messages=status if target_item in ["الملصقات", "المتحركه"] else current_perms.can_send_other_messages,
                can_send_polls=current_perms.can_send_polls,
                can_add_web_page_previews=current_perms.can_add_web_page_previews,
                can_change_info=current_perms.can_change_info,
                can_invite_users=current_perms.can_invite_users,
                can_pin_messages=current_perms.can_pin_messages
            )
            await client.set_chat_permissions(chat_id, new_perms)

        # حفظ الحالة البرمجية في الذاكرة لجميع الأوامر (بما فيها الحماية الداخلية)
        locks_db[chat_id][target_item] = (action == "lock")
        
        emoji = "🔒" if action == "lock" else "🔓"
        word = "قفل" if action == "lock" else "فتح"
        await message.reply_text(f"{emoji} تم **{word}** ({target_item}) في المجموعة بنجاح.")

    except ChatAdminRequired:
        await message.reply_text("❌ خطأ: البوت يحتاج صلاحية (تغيير معلومات المجموعة ودمج القيود) ليعمل نظام القفل المباشر.")
    except Exception as e:
        await message.reply_text(f"⚠️ حدث خطأ أثناء تعديل الأقفال: {str(e)}")


# --- 2. معالج أوامر التفعيل والتعطيل ---
@Client.on_message(filters.group & filters.text)
async def toggle_features_handler(client: Client, message: Message):
    cmd = message.text.strip()
    chat_id = message.chat.id
    user_id = message.from_user.id

    action = None
    target_feature = None

    if cmd.startswith("تفعيل "):
        action = "enable"
        target_feature = cmd.replace("تفعيل ", "", 1).strip()
    elif cmd.startswith("تعطيل "):
        action = "disable"
        target_feature = cmd.replace("تعطيل ", "", 1).strip()

    if not action or target_feature not in TOGGLE_FEATURES:
        return

    if not await is_admin_or_dev(client, chat_id, user_id):
        return await message.reply_text("❌ عذراً، هذا الأمر خاص بالمشرفين ومطور البوت فقط.")

    if chat_id not in features_db:
        features_db[chat_id] = {}

    # توحيد المسمى الإملائي للأذكار
    if target_feature == "الذكار":
        target_feature = "الاضكار"

    features_db[chat_id][target_feature] = (action == "enable")
    
    emoji = "⚙️" if action == "enable" else "🛑"
    word = "تفعيل" if action == "enable" else "تعطيل"
    await message.reply_text(f"{emoji} تم **{word}** ميزة ({target_feature}) للجروب بنجاح.")


# --- 3. فحص ومراقبة الرسائل لتطبيق الأقفال البرمجية خلف الكواليس ---
@Client.on_message(filters.group & ~filters.me, group=2)
async def monitor_locks_and_filters(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else None

    if not user_id or chat_id not in locks_db:
        return

    if await is_admin_or_dev(client, chat_id, user_id):
        return

    chat_locks = locks_db[chat_id]
    text = message.text or message.caption or ""

    # 1. فحص قفل الروابط / الروابط بالتقييد
    if (chat_locks.get("الروابط") or chat_locks.get("الروابط بالتقييد")) and ("t.me/" in text or "http" in text or ".com" in text):
        try:
            await message.delete()
            if chat_locks.get("الروابط بالتقييد"):
                await message.chat.restrict_member(user_id, ChatPermissions(can_send_messages=False))
        except Exception:
            pass
        return

    # 2. فحص قفل التوجيه / التوجيه بالتقييد
    if (chat_locks.get("التوجيه") or chat_locks.get("التوجيه بالتقييد")) and message.forward_date:
        try:
            await message.delete()
            if chat_locks.get("التوجيه بالتقييد"):
                await message.chat.restrict_member(user_id, ChatPermissions(can_send_messages=False))
        except Exception:
            pass
        return

    # 3. فحص قفل المعرفات (Usernames)
    if chat_locks.get("المعرفات") and "@" in text:
        try:
            await message.delete()
        except Exception:
            pass
        return

    # 4. فحص قفل البوتات بالطرد أو الحظر المباشر
    if message.new_chat_members:
        for member in message.new_chat_members:
            if member.is_bot:
                if chat_locks.get("البوتات") or chat_locks.get("البوتات بالطرد"):
                    try:
                        await message.chat.ban_member(member.id)
                    except Exception:
                        pass
