from pyrogram import Client
from pyrogram.types import ChatPermissions
from config import OWNER_ID
from database import cursor

ranks = {"member": 0, "special": 1, "mod": 2, "owner": 3, "sudo": 4}
rank_names = {"sudo": "المطور", "owner": "المالك", "mod": "المدير", "special": "المميز", "member": "عضو"}

def get_rank(chat_id, user_id):
    if user_id == OWNER_ID: return "sudo"
    cursor.execute("SELECT rank FROM admins WHERE chat_id=? AND user_id=?", (chat_id, user_id))
    r = cursor.fetchone()
    return r[0] if r else "member"

def set_rank(chat_id, user_id, rank):
    if rank == "member":
        cursor.execute("DELETE FROM admins WHERE chat_id=? AND user_id=?", (chat_id, user_id))
    else:
        cursor.execute("INSERT OR REPLACE INTO admins VALUES (?,?,?)", (chat_id, user_id, rank))
    conn.commit()

async def has_permission(app: Client, chat_id, user_id, need_rank):
    user_rank = get_rank(chat_id, user_id)
    member = await app.get_chat_member(chat_id, user_id)
    if member.status in ["creator", "administrator"]: return True
    return ranks[user_rank] >= ranks[need_rank]

async def can_action(app, chat_id, user_id, target_id):
    if user_id == target_id: return False
    if ranks[get_rank(chat_id, user_id)] <= ranks[get_rank(chat_id, target_id)]:
        return False
    return True
