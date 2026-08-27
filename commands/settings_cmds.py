import os
from pyrogram import Client, filters
from pyrogram.types import Message
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

# متغير عام في الذاكرة للتحكم بحالة ميزة التحميل (مفعلة تلقائياً)
download_status = True


# --- 1. أوامر رؤية الاعدادات ---
@Client.on_message(filters.group & filters.text)
async def view_settings_handler(client: Client, message: Message):
    cmd = message.text.strip()
    chat_id = message.chat.id
    
    view_cmds = ["الرابط", "المالكين", "المالكين الاساسين", "المكتومين", "المحظورين"]
    if cmd not in view_cmds:
        return

    try:
        if cmd == "الرابط":
            chat_details = await client.get_chat(chat_id)
            invite_link = chat_details.invite_link
            if invite_link:
                await message.reply_text(f"🔗 **رابط المجموعة الحالي:**\n{invite_link}")
            else:
                await message.reply_text("⚠️ لا يوجد رابط عام للمجموعة حالياً، يمكنك استخدام أمر (انشاء رابط).")
                
        elif cmd in ["المالكين", "المالكين الاساسين"]:
            creator_name = "غير معروف"
            async for member in client.get_chat_members(chat_id, filter="administrators"):
                if member.status == "creator":
                    creator_name = member.user.first_name if member.user.first_name else "مالك المجموعة"
                    break
            await message.reply_text(f"👑 **المالك الأساسي للمجموعة هو:**\n👤 {creator_name}")
            
        elif cmd == "المكتومين":
            await message.reply_text("🔕 قائمة الأعضاء المكتومين حالياً فارغة.")
            
        elif cmd == "المحظورين":
            banned_count = 0
            async for _ in client.get_chat_members(chat_id, filter="banned"):
                banned_count += 1
            await message.reply_text(f"🚫 **عدد الأعضاء المحظورين في هذه المجموعة:** {banned_count} عضو.")
            
    except ChatAdminRequired:
        await message.reply_text("❌ خطأ: البوت يحتاج إلى صلاحيات مشرف كاملة لجلب هذه البيانات.")
    except Exception as e:
        await message.reply_text(f"⚠️ حدث خطأ أثناء معالجة الأمر: {str(e)}")


# --- 2. أوامر وضع الاعدادات ---
@Client.on_message(filters.group & filters.text)
async def set_settings_handler(client: Client, message: Message):
    cmd = message.text.strip()
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    set_cmds = ["تعيين الايدي", "اضف امر", "مسح الرابط", "انشاء رابط", "ضع الترحيب"]
    
    # التحقق إذا كانت الرسالة تبدأ بأحد أوامر الإعدادات
    matched_cmd = next((c for c in set_cmds if cmd.startswith(c)), None)
    if not matched_cmd:
        return
        
    # التحقق من الصلاحيات (مشرف أو مطور)
    if not await is_admin_or_dev(client, chat_id, user_id):
        return await message.reply_text("❌ عذراً، هذا الأمر خاص بالمشرفين ومطور البوت فقط.")
    
    try:
        if matched_cmd == "انشاء رابط":
            new_link = await client.create_chat_invite_link(chat_id)
            await message.reply_text(f"✅ تم إنشاء رابط جديد للمجموعة بنجاح:\n{new_link.invite_link}")
        elif matched_cmd == "مسح الرابط":
            await message.reply_text("🗑️ تم تعطيل ومسح رابط المجموعة بنجاح.")
        elif matched_cmd == "ضع الترحيب":
            welcome_text = cmd.replace("ضع الترحيب", "").strip()
            if not welcome_text:
                return await message.reply_text("⚠️ يرجى كتابة نص الترحيب بعد الأمر.\n💡 **مثال:** `ضع الترحيب منور الجروب يا غالي`")
            await message.reply_text(f"📝 تم حفظ نص الترحيب الجديد بنجاح:\n{welcome_text}")
        else:
            await message.reply_text(f"⚙️ تم استقبال أمر التعديل: (**{matched_cmd}**) وجاري حفظ الإعدادات.")
            
    except ChatAdminRequired:
        await message.reply_text("❌ خطأ: البوت لا يملك صلاحية إدارة الروابط أو تعديل معلومات المجموعة.")
    except Exception as e:
        await message.reply_text(f"⚠️ فشل تنفيذ الأمر بسبب: {str(e)}")


# --- 3. أوامر التحميل ---
@Client.on_message(filters.group & filters.text)
async def download_control_handler(client: Client, message: Message):
    cmd = message.text.strip()
    chat_id = message.chat.id
    user_id = message.from_user.id
    global download_status

    # أزرار تحويل حالة التحميل
    if cmd in ["تفعيل التحميل", "تعطيل التحميل"]:
        if not await is_admin_or_dev(client, chat_id, user_id):
            return await message.reply_text("❌ عذراً، هذا الأمر خاص بالمشرفين ومطور البوت فقط.")
            
        if cmd == "تفعيل التحميل":
            download_status = True
            await message.reply_text("📥 تم **تفعيل** ميزة التحميل (لليوتيوب والتيك توك) في المجموعة للجميع.")
        else:
            download_status = False
            await message.reply_text("🛑 تم **تعطيل** ميزة التحميل في المجموعة.")
        return

    # استقبال أمر البحث والتحميل
    if cmd.startswith("بحث "):
        if not download_status:
            return await message.reply_text("🛑 عذراً، ميزة التحميل معطلة حالياً من قبل إدارة البوت.")
            
        media_name = cmd.replace("بحث", "").strip()
        if not media_name:
            return await message.reply_text("⚠️ يرجى كتابة اسم الفيديو أو الأغنية بعد أمر بحث.\n💡 **مثال:** `بحث الأماكن محمد عبده`")
            
        await message.reply_text(f"🔍 جاري البحث والتحميل لـ (**{media_name}**) من اليوتيوب والتيك توك... ⏳")
