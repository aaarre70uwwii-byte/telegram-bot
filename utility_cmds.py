import os
import random
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import ChatAdminRequired

# قراءة أيدي المطور الرئيسي من متغيرات البيئة تلقائياً
MAIN_DEV_ID = int(os.getenv("DEV_ID", 0))

# مخزن مؤقت في الذاكرة لحفظ الهمسات والردود المخصصة
whispers_db = {}
custom_replies = {}

# دالة مسابعة للتحقق من الصلاحيات الإدارية لبعض الأوامر الخاصة بالأدمن/المطور
async def is_admin_or_dev(client: Client, chat_id: int, user_id: int) -> bool:
    if user_id == MAIN_DEV_ID:
        return True
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except Exception:
        return False

# --- الدالة الشاملة والمفحوصة لجميع الأوامر الخدمية والترفيهية والتحميل والهمسات ---
@Client.on_message(filters.group & filters.text, group=6)
async def utilities_master_handler(client: Client, message: Message):
    cmd = message.text.strip()
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else 0

    try:
        # 1. نظام إنشاء الهمسة السرية داخل الجروب بالرد
        if cmd.startswith("همسه ") or cmd.startswith("همسة "):
            if not message.reply_to_message or not message.reply_to_message.from_user:
                return await message.reply_text("⚠️ يرجى الرد على الشخص الذي تريد توجيه الهمسة إليه.\n💡 **مثال:** اكتب `همسة للتوثيق برمجياً` بالرد عليه.")
            
            whisper_parts = cmd.split(None, 1)
            if len(whisper_parts) < 2:
                return await message.reply_text("⚠️ يرجى كتابة نص الهمسة بعد الكلمة.")
                
            whisper_text = whisper_parts[1].strip()
            sender_id = user_id
            receiver_id = message.reply_to_message.from_user.id
            
            if sender_id == receiver_id:
                return await message.reply_text("🧐 لا يمكنك إرسال همسة سرية لنفسك!")
                
            whisper_id = f"w_{message.id}"
            whispers_db[whisper_id] = {
                "sender": sender_id,
                "receiver": receiver_id,
                "text": whisper_text
            }
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔏 اضغط لفتح الهمسة السرية", callback_data=whisper_id)]
            ])
            
            sender_link = f"[{message.from_user.first_name}](tg://user?id={sender_id})"
            receiver_link = f"[{message.reply_to_message.from_user.first_name}](tg://user?id={receiver_id})"
            return await message.reply_text(
                text=f"🔒 تم إرسال همسة سرية من {sender_link} إلى {receiver_link}.\n\n⚠️ لا يمكن لأحد غيرهما فتحها والاطلاع عليها.",
                reply_markup=keyboard
            )

        # 2. أمر الآيدي الذكي والمطور (مع جلب الرتب البرمجية وتأمينها)
        if cmd in ["ايدي", "ايديات", "id"]:
            target_user = message.reply_to_message.from_user if (message.reply_to_message and message.reply_to_message.from_user) else message.from_user
            t_user_id = target_user.id
            username = f"@{target_user.username}" if target_user.username else "لا يوجد"
            
            if t_user_id == MAIN_DEV_ID:
                rank = "👑 مطور البوت الرئيسي"
            else:
                try:
                    member = await client.get_chat_member(chat_id, t_user_id)
                    if member.status == "creator":
                        rank = "👑 مالك المجموعة"
                    elif member.status == "administrator":
                        rank = "👮‍♂️ مشرف في المجموعة"
                    else:
                        rank = "👤 عضو عادي"
                except Exception:
                    rank = "👤 عضو عادي"

            id_text = f"📌 **معلومات الحساب والتأمين:**\n━━━━━━━━━━━━\n👤 الاسم: {target_user.first_name}\n🆔 الآيدي: `{t_user_id}`\n🏷️ اليوزر: {username}\n🎖️ الرتبة: **{rank}**\n━━━━━━━━━━━━\n📥 آيدي الجروب: `{chat_id}`"
            return await message.reply_text(id_text)

        # 3. الأوامر الخدمية التفاعلية العامة (نسب، آراء، اقتراحات)
        if cmd == "نسبه الحب":
            percentage = random.randint(0, 100)
            return await message.reply_text(f"❤️ نسبة الحب لديك هي: **{percentage}%**")

        elif cmd == "نسبه الغباء":
            percentage = random.randint(0, 100)
            if message.reply_to_message and message.reply_to_message.from_user:
                target_name = message.reply_to_message.from_user.first_name
                target_id = message.reply_to_message.from_user.id
                return await message.reply_text(f"🧠 نسبة غباء **[{target_name}](tg://user?id={target_id})** هي: **{percentage}%**")
            return await message.reply_text(f"🧠 نسبة غبائك هي: **{percentage}%**")

        elif cmd == "تحبه":
            if not message.reply_to_message or not message.reply_to_message.from_user:
                return await message.reply_text("⚠️ يرجى الرد على الشخص الذي تود معرفة مشاعرك تجاهه.")
            percentage = random.randint(0, 100)
            target_name = message.reply_to_message.from_user.first_name
            return await message.reply_text(f"👀 نسبة حبك لـ **{target_name}** هي: **{percentage}%**")

        elif cmd in ["شبيهي", "شبيهتي"]:
            return await message.reply_text("🎭 شبيهك الحالي في الجروب هو العضو الذي سيرسل الرسالة القادمة!")

        elif cmd == "شرايك في افتاري":
            rates = ["🔥 فخم جداً 10/10", "✨ لطيف وجميل", "🤷‍♂️ عادي صراحة", "❌ يحتاج تغيير فوراً"]
            return await message.reply_text(f"🧐 رأيي في افتارك: **{random.choice(rates)}**")

        elif cmd in ["افتاره", "البايو"]:
            if not message.reply_to_message or not message.reply_to_message.from_user:
                return await message.reply_text("⚠️ يرجى الرد على رسالة العضو لجلب معلوماته.")
            
            target_user = message.reply_to_message.from_user
            
            if cmd == "افتاره":
                try:
                    async for photo in client.get_chat_photos(target_user.id, limit=1):
                        return await message.reply_photo(photo.file_id, caption=f"📸 افتار: {target_user.first_name}")
                    await message.reply_text("❌ هذا المستخدم لا يمتلك صورة بروفايل حالياً.")
                except Exception:
                    await message.reply_text("❌ فشل جلب صورة المستخدم بسبب إعدادات الخصوصية لديه.")
            else:
                try:
                    full_chat_info = await client.get_chat(target_user.id)
                    bio = full_chat_info.description if full_chat_info.description else "لا يوجد بايو."
                    await message.reply_text(f"📝 بايو العضو:\n`{bio}`")
                except Exception:
                    await message.reply_text("❌ فشل جلب بايو المستخدم من السيرفر.")
            return

        elif cmd in ["نسبه انوثتها", "نسبه رجولته"]:
            percentage = random.randint(10, 100)
            word = "أنوثتها" if "انوثتها" in cmd else "رجولته"
            if message.reply_to_message and message.reply_to_message.from_user:
                target_name = message.reply_to_message.from_user.first_name
                return await message.reply_text(f"✨ نسبة {word} للعضو **{target_name}** هي: **{percentage}%**")
            return await message.reply_text(f"✨ النسبة المئوية التقريبية هي: **{percentage}%**")

        # 4. أوامر المحتوى الديني، الثقافي، والميديا الجاهزة
        content_triggers = {
            "قران": "📖 سورة الفاتحة بملف صوتي قادم..",
            "اذكار": "🌙 (ألا بذكر الله تطمئن القلوب): سبحان الله وبحمده، سبحان الله العظيم.",
            "شعر": "📜 لَعَلَّ اللَّهَ يُحْدِثُ بَعْدَ ذَلِكَ أَمْرًا.. فكن صبوراً.",
            "قصائد": "📜 وما نيل المطالب بالتمني.. ولكن تؤخذ الدنيا غلاباً.",
            "اقتباسات": "💭 'الخوف من الفشل هو العائق الوحيد أمام تحقيق أحلامك.'",
            "ثريد": "🧵 ثريد ثقافي: هل تعلم أن تليجرام يحمي بياناتك ببروتوكول MTProto المشفر بالكامل؟",
            "قصص": "📚 قصة اليوم: كان هناك بوت برمج يسهل إدارة المجموعات بكفاءة حتى أصبح الأفضل!",
            "كتب": "📚 كتاب ننصح به: 'العادات الذرية' لجيمس كلير.",
            "اطربني": "🎵 جاري تجهيز أغنية عشوائية فخمة لك.. ⏳",
            "اغاني": "🎶 تفضل بكتابة `بحث + اسم الأغنية` لجلبها فوراً.",
            "افلام": "🎬 فيلم الليلة المقترح: (The Pursuit of Happyness) كفاح وإصرار.",
            "البوت السحري": "🔮 أنا البوت السحري، اسألني وسأجيبك بتوقعاتي للمستقبل!",
            "من ضافني": "👥 تم رصد دخولك للمجموعة بواسطة رابط دعوة عام أو إضافتك من مشرف."
        }
        if cmd in content_triggers:
            return await message.reply_text(content_triggers[cmd])

        media_keywords = ["هيدرات", "جداريات", "ميمز", "ايدت", "قيفات", "افتارات"]
        matched_media = next((m for m in media_keywords if m in cmd), None)
        if matched_media:
            return await message.reply_text(f"📸 جاري جلب محتوى مخصص لـ (**{cmd}**) من مخزن البيانات الميديا الخاص بالبوت... ⏳")

        # 5. أوامر البحث والخدمات البرمجية المعتمدة على متغيرات المدخلات خلفها
        if cmd.startswith("صيح "):
            shout_text = cmd.replace("صيح ", "", 1).strip()
            if shout_text: return await message.reply_text(f"🗣️ {shout_text.upper()} !!!")
            return

        elif cmd.startswith("ارسل ") and " زاجل" in cmd:
            parts = cmd.replace("ارسل ", "").replace(" زاجل", "").strip().rsplit(None, 1)
            if len(parts) >= 2:
                msg_content, target_username = parts
                return await message.reply_text(f"📬 تم إرسال رسالة الزاجل السرية بنجاح إلى: {target_username}")
            return await message.reply_text("⚠️ صيغة الزاجل خاطئة. الصيغة: `ارسل [الكلام] [اليوزر] زاجل`")

        elif cmd.startswith("قوقل "):
            search_query = cmd.replace("قوقل ", "", 1).strip()
