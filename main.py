import os
import telebot
import time
from flask import Flask
from threading import Thread

# 1. WEB SERVER (Keeps Render 'Live')
app = Flask('')
@app.route('/')
def home(): return "BOT STATUS: 🟢 LIVE & SECURE"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 2. SECURE BOT LOGIC
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    # FIXED: Uses proper InlineKeyboardButton
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text="💳 GATES", callback_query_data="gt"))
    bot.send_message(message.chat.id, "💎 **READY**\nClick below:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def cb(call):
    if call.data == "gt":
        bot.edit_message_text("💳 `/chk` | `/sd`", call.message.chat.id, call.message.message_id)

# 3. THE ENGINE
def start_bot():
    while True:
        try:
            print("Cleaning old connections...")
            bot.remove_webhook()
            # This drops the 'stuck' messages causing the crash
            bot.delete_webhook(drop_pending_updates=True) 
            print("--- SUCCESS: BOT IS POLLING ---")
            bot.polling(none_stop=True, timeout=20)
        except Exception as e:
            print(f"Connection Error: {e}. Restarting...")
            time.sleep(5)

if __name__ == "__main__":
    t = Thread(target=run_web)
    t.daemon = True
    t.start()
    start_bot()
