cursor.execute("CREATE TABLE IF NOT EXISTS locks (chat_id INTEGER, lock_type TEXT, PRIMARY KEY(chat_id, lock_type))")
cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
