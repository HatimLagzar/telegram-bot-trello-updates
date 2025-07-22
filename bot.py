import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
TRELLO_TOKEN = os.getenv('TRELLO_TOKEN')
TRELLO_BOARD_ID = os.getenv('TRELLO_BOARD_ID')

def get_multiple_lists_status(list_names):
    url = f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/lists"
    params = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_TOKEN
    }
    response = requests.get(url, params=params)

    if response.status_code != 200:
        return f"❌ Failed to fetch lists: {response.status_code}"

    all_lists = response.json()
    output = []

    for name in list_names:
        trello_list = next((lst for lst in all_lists if lst['name'].lower() == name.lower()), None)
        if not trello_list:
            output.append(f"⚠️ List '{name}' not found.\n")
            continue

        list_id = trello_list['id']
        card_url = f"https://api.trello.com/1/lists/{list_id}/cards"
        card_resp = requests.get(card_url, params=params)

        if card_resp.status_code != 200:
            output.append(f"❌ Failed to fetch cards for '{name}': {card_resp.status_code}\n")
            continue

        cards = card_resp.json()
        card_lines = "\n".join([f"• {card['name']}" for card in cards]) if cards else "✅ No cards."
        output.append(f"📌 {name}\n{card_lines}\n")

    return "\n".join(output)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    list_names = [
        "Current Feature",
        "In Progress",
        "In Testing | Waiting for Production"
    ]
    await update.message.reply_text("📋 Fetching Trello list status...")
    result = get_multiple_lists_status(list_names)
    await update.message.reply_text(result, parse_mode="Markdown")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("status", status))
    print("🤖 Bot is running...")
    app.run_polling()
