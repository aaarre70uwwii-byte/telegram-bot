from pyrogram import filters, enums
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import ChatAdminRequired, UserAdminInvalid
from config import app, ADMIN_ID, db
from buttons import roz_keyboard, admin_keyboard, lock_keyboard
import random, io
from PIL import Image, ImageDraw, ImageFont

def is_admin(user_id):
    return user_id == ADMIN_ID

async def is_user_admin(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
    except:
        return False

# دالة انشاء صورة الايدي
def create_id_photo(user, chat_title):
    img = Image.new('RGB', (600, 320), color = '#1a1a2e')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 32)
        font2 = ImageFont.truetype("arial.ttf", 26)
    except:
        font = ImageFont.load_default()
        font2 = ImageFont.load_default()
    
    draw.text((30, 25), f"『𝐓𝐢𝐚』 معلومات العضو", fill='#e94560', font=font)
    draw.text((30, 85), f"الاسم: {user.first_name}", fill='white', font=font2)
    draw.text((30, 125), f"اليوزر: @{user.username if user.username else 'لا يوجد'}", fill='white', font=font2)
    draw.text((30, 165), f"الايدي: {user.id}", fill='#00ff88', font=font2)
    draw.text((30, 205), f"القروب: {chat_title}", fill='white', font=font2)
    draw.text((30, 260), f"بواسطة: بوت 𝐓𝐢𝐚", fill='#a9a9a9', font=font2)
    
    bio = io.BytesIO()
    bio.name = 'id.png'
    img.save(bio, 'PNG')
    bio.seek(0)
    return bio

# امر الاوامر
@app.on_message(filters.command("اوامر") | filters.command("start"))
async def tia_commands(client, message: Message):
    db["users"].add(message.from_user.id)
    text =
