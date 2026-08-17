import re
import time
from config import BANNED_WORDS, MAX_FLOOD, FLOOD_TIME

user_messages = {} # لتخزين وقت الرسائل {user_id: [time1, time2]}

def has_link(text: str) -> bool:
    """التحقق من وجود رابط"""
    if not text:
        return False
    pattern = r'(https?://|www\.|t\.me/|telegram\.me/|@[\w\d_]{5,})'
    return bool(re.search(pattern, text, re.IGNORECASE))

def has_banned_word(text: str) -> tuple:
    """التحقق من الكلمات الممنوعة. يرجع True والكلمة"""
    if not text:
        return False, None
    text_lower = text.lower()
    for word in BANNED_WORDS:
        if word in text_lower:
            return True, word
    return False, None

def check_flood(user_id: int) -> bool:
    """التحقق من السبام"""
    now = time.time()
    if user_id not in user_messages:
        user_messages[user_id] = []

    user_messages[user_id].append(now)
    # احذف الرسائل اللي اقدم من FLOOD_TIME
    user_messages[user_id] = [t for t in user_messages[user_id] if now - t < FLOOD_TIME]

    return len(user_messages[user_id]) > MAX_FLOOD
