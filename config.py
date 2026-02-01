import os

# 🔐 Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")

# 👑 Админы
ADMINS = {int(os.getenv("ADMIN_ID"))}

# 📊 Google Sheets
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME")
SHEET_INDEX = int(os.getenv("SHEET_INDEX", 5))

# 👥 Группа и тема
GROUP_ID = int(os.getenv("GROUP_ID"))
TOPIC_ID = int(os.getenv("TOPIC_ID"))
