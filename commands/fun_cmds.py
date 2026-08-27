# -*- coding: utf-8 -*-
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

# قواعد بيانات مؤقتة في الذاكرة لتخزين الحالات ورتب التسلية
fun_status = {}
group_fun_roles = {}
global_fun_roles = {}
marriages = {}
votes = {}

# قائمة برتب التسلية الأساسية التي تظهر بالايدي
FUN_ROLES_MAP = {
    "هطف": "الهطوف", "بثر": "البثرين", "حمار": "الحمير", "كلب": "الكلاب",
    "كلبه": "الكلبات", "عتوي": "العتوين", "عتويه": "العتويات", "لحجي": "اللحوج",
    "لحجيه": "اللحجيات", "خروف": "الخرفان", "خفيفه": "الخفيفات", "خفيف": "الخفيفين",
    "بقلبي": "قلبي"
}

# --- 1. معالج أوامر الرفع والتنزيل (الرتب الافتراضية والاختيارية) ---
@Client.on_message(filters.group & filters.text)
async def fun_roles_handler(client: Client, message: Message):
    cmd = message.text.strip()
    chat_id = message.chat.id
    user_id = message.from_user.id

    # التحقق من أن التسلية ليست معطلة في الجروب
    if fun_status.get(chat_id, {}).get("التسليه") is False:
        return

    # أولاً: معالجة أوامر التنزيل
    if cmd.startswith("تنزيل "):
        if not message.reply_to_message:
            return await message.reply_text("⚠️ يرجى الرد على رسالة الشخص لتنزيل رتبته.")

        role_key = cmd.replace("تنزيل ", "", 1).strip()
        target_id = message.reply_to_message.from_user.id

        if role_key in FUN_ROLES_MAP:
            plural_name = FUN_ROLES_MAP[role_key]
            if chat_id in group_fun_roles and target_id in group_fun_roles[chat_id]:
                del group_fun_roles[chat_id][target_id]
            await message.reply_text(f"✅ تم تنزيل العضو من قائمة **{plural_name}**.")
        return

    elif cmd == "تنزيل من قلبي":
        if not message.reply_to_message: return
        target_id = message.reply_to_message.from_user.id
        if chat_id in group_fun_roles and target_id in group_fun_roles[chat_id]:
            del group_fun_roles[chat_id][target_id]
        await message.reply_text("💔 تم تنزيل العضو من قلبك بنجاح.")
        return

    # ثانياً: معالجة أوامر الرفع
    if cmd.startswith("رفع "):
        if not message.reply_to_message:
            return await message.reply_text("⚠️ يرجى الرد على رسالة الشخص لرفع رتبته.")

        role_key = cmd.replace("رفع ", "", 1).strip()

        # استثناء أمر "رفع عام" ليعالج في الفلتر الخاص به
        if role_key.startswith("عام "):
            return

        target_id = message.reply_to_message.from_user.id
        target_user = message.reply_to_message.from_user
        target_link = f"[{target_user.first_name}](tg://user?id={target_id})"

        if chat_id not in group_fun_roles:
            group_fun_roles[chat_id] = {}

        # أ. رفع رتبة تسلية افتراضية
        if role_key in FUN_ROLES_MAP:
            plural_name = FUN_ROLES_MAP[role_key]
            group_fun_roles[chat_id][target_id] = plural_name
            await message.reply_text(f"😂 تم رفع العضو {target_link} في قائمة **{plural_name}** بنجاح!")

        # ب. رفع رتبة بقلبي
        elif role_key == "بقلبي":
            group_fun_roles[chat_id][target_id] = "قلبي"
            await message.reply_text(f"❤️ تم رفع العضو {target_link} في قلبك بنجاح!")

        # ج. رفع رتبة اختيارية مخصصة للجروب (مثل: رفع كينج)
        else:
            group_fun_roles[chat_id][target_id] = role_key
            await message.reply_text(f"👑 تم رفع العضو رتبة جروب مخصصة: **{role_key}**")

# --- 2. أوامر رتب التسلية العامة والإدارية ---
@Client.on_message(filters.group & filters.text)
async def admin_fun_lists(client: Client, message: Message):
    cmd = message.text.strip()
    chat_id = message.chat.id
    user_id = message.from_user.id

    if fun_status.get(chat_id, {}).get("التسليه") is False:
        return

    # رفع رتبة تسلية عامة (خاص بالمطور فقط)
    if cmd.startswith("رفع عام "):
        if user_id!= DEV_ID:
            return await message.reply_text("❌ عذراً، هذا الأمر خاص بمطور البوت الرئيسي فقط للرتب العامة.")
        if not message.reply_to_message:
            return await message.reply_text("⚠️ يرجى الرد على رسالة الشخص لرفعه عام.")

        custom_role = cmd.replace("رفع عام ", "", 1).strip()
        target_id = message.reply_to_message.from_user.id
        global_fun_roles[target_id] = custom_role
        return await message.reply_text(f"🌍 تم رفع العضو رتبة عامة بالبوت: **{custom_role}**")

    # استعراض القوائم والمسح للمشرفين
    if cmd in ["رتب التسليه", "رتب التسليه عام", "مسح رتب التسليه"]:
        if not await is_admin_or_dev(client, chat_id, user_id):
            return await message.reply_text("❌ عذراً، هذا الأمر خاص بالإدارة والمشرفين فقط.")

        if cmd == "رتب التسليه":
            roles = group_fun_roles.get(chat_id, {})
            if not roles: return await message.reply_text("📭 لا توجد رتب تسلية في هذه المجموعة حالياً.")
            txt = "🎭 **رتب التسلية الحالية بالجروب:**\n\n"
            for u_id, r_name in roles.items():
                txt += f"👤 ID: `{u_id}` ◀️ رتبة: **{r_name}**\n"
            await message.reply_text(txt)

        elif cmd == "رتب التسليه عام":
            if not global_fun_roles: return await message.reply_text("📭 لا توجد رتب تسلية عامة مرفوعة بالبوت حالياً.")
            txt = "🌍 **رتب التسلية العامة المرفوعة بالبوت:**\n\n"
            for u_id, r_name in global_fun_roles.items():
                txt += f"👤 ID: `{u_id}` ◀️ رتبة: **{r_name}**\n"
            await message.reply_text(txt)

        elif cmd == "مسح رتب التسليه":
            if chat_id in group_fun_roles:
                group_fun_roles[chat_id] = {}
            await message.reply_text("🧹 تم تصفير ومسح رتب التسلية لهذه المجموعة بالكامل بنجاح.")

# --- 3. نظام محاكاة الزواج والطلاق والتعطيل التابع لها ---
@Client.on_message(filters.group & filters.text)
async def marriage_system_handler(client: Client, message: Message):
    cmd = message.text.strip()
    chat_id = message.chat.id
    user_id = message.from_user.id

    if fun_status.get(chat_id, {}).get("التسليه") is False or fun_status.get(chat_id, {}).get("زوجني") is False:
        return

    if cmd == "تتزوجني":
        if not message.reply_to_message:
            return await message.reply_text("⚠️ يرجى الرد على الشخص الذي تود التقدم للزواج منه.")
        target_id = message.reply_to_message.from_user.id
        if user_id == target_id:
            return await message.reply_text("🧐 لا يمكنك طلب الزواج من نفسك!")

        if chat_id not in marriages: marriages[chat_id] = {}
        marriages[chat_id][user_id] = target_id
        marriages[chat_id][target_id] = user_id
        await message.reply_text(f"💍 ألف مبروك! تم إعلان الزواج بنجاح بينكما في المجموعة.")

    elif cmd in ["زوجي", "زوجتي"]:
        partner = marriages.get(chat_id, {}).get(user_id)
        if not partner:
            return await message.reply_text("💔 وضعك الحالي (أعزب)، قم بالرد على أحدهم واكتب (تتزوجني) لطلب يدّه.")
        await message.reply_text(f"❤️ شريك حياتك المسجل في نظام البوت هو صاحب الآيدي الحالي: `{partner}`")

    elif cmd == "طلاق":
        if chat_id in marriages and user_id in marriages[chat_id]:
            partner = marriages[chat_id][user_id]
            del marriages[chat_id][user_id]
            if partner in marriages[chat_id]:
                del marriages[chat_id][partner]
            await message.reply_text("💔 تم الانفصال رسمياً، عدت إلى قائمة العزاب مجدداً.")
        else:
            await message.reply_text("🧐 أنت لست متزوجاً لتقوم بطلب الطلاق!")

# --- 4. ميزة تصويت الكتم (اكتموه) وأزرار التفعيل والتعطيل للمشرفين ---
@Client.on_message(filters.group & filters.text)
async def features_control_and_vote(client: Client, message: Message):
    cmd = message.text.strip()
    chat_id = message.chat.id
    user_id = message.from_user.id

    # معالجة أوامر التفعيل والتعطيل للميزات
    control_cmds = ["تعطيل التسليه", "تفعيل التسليه", "تعطيل اكتموه", "تفعيل اكتموه", "تعطيل زوجني", "تفعيل زوجني"]
    if cmd in control_cmds:
        if not await is_admin_or_dev(client, chat_id, user_id):
            return await message.reply_text("❌ عذراً، هذا التحكم خاص بالمشرفين ومطور البوت فقط.")

        feature = "التسليه" if "التسليه" in cmd else ("اكتموه" if "اكتموه" in cmd else "زوجني")
        status = True if "تفعيل" in cmd else False

        if chat_id not in fun_status:
            fun_status[chat_id] = {}

        fun_status[chat_id][feature] = status
        word = "تفعيل" if status else "تعطيل"
        return await message.reply_text(f"⚙️ تم **{word}** ميزة ({feature}) في المجموعة بنجاح.")

    # نظام التصويت الذكي (اكتموه) بالرد
    if cmd == "اكتموه":
        if fun_status.get(chat_id, {}).get("التسليه") is False or fun_status.get(chat_id, {}).get("اكتموه") is False:
            return
        if not message.reply_to_message:
            return await message.reply_text("⚠️ يرجى الرد على رسالة الشخص الذي تريد كتمه بالتصويت.")

        target_id = message.reply_to_message.from_user.id
        target_name = message.reply_to_message.from_user.first_name

        vote_key = f"{chat_id}_{target_id}"
        if vote_key not in votes:
            votes[vote_key] = set()

        votes[vote_key].add(user_id)
        current_votes = len(votes[vote_key])

        await message.reply_text(f"🔇 تصويت كتم على {target_name}: {current_votes}/3")

        # عند اكتمال 3 أصوات يتم تنفيذ الكتم المباشر بعضو الجروب
        if current_votes >= 3:
            try:
                await client.restrict_chat_member(chat_id, target_id, ChatPermissions())
                await message.reply_text(f"🔇 تم كتم {target_name} بنجاح بعد اكتمال التصويت")
                del votes[vote_key]
            except ChatAdminRequired:
                await message.reply_text("❌ ليس لدي صلاحية الكتم")
            except Exception:
                await message.reply_text("❌ حدث خطأ اثناء الكتم")
