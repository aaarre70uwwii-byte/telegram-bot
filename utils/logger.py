import datetime
import os

LOG_FILE = "logs.txt"

def log_action(action: str, admin_id: int, target_id: int, chat_id: int):
    """حفظ كل اجراء في ملف logs.txt"""
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_text = f"[{time}] ACTION: {action} | ADMIN: {admin_id} | TARGET: {target_id} | CHAT: {chat_id}\n"

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_text)
