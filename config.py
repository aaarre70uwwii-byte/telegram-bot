import os

TOKEN = os.getenv('TOKEN') or os.getenv('TELEGRAM_TOKEN')
DEV = int(os.getenv('DEV', 0))
admins = [DEV]
