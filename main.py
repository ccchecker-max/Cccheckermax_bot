import os
import telebot
import time
from flask import Flask
from threading import Thread

# 1. WEB SERVER
app = Flask('')
@app.route('/')
def home(): return "BOT STATUS: 🟢 LIVE"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 2. BOT
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("💳 GATES", callback_query_data="gt"))
    bot.send_message(message.chat.id, "💎 **READY**", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def cb(call):
    if call.data == "gt":
        bot.edit_message_text("💳 `/chk` | `/sd`", call.message.chat.id, call.message.message_id)

# 3. ENGINE
def start_bot():
    while True:
        try:
            bot.remove_webhook()
            bot.delete_webhook(drop_pending_updates=True)
            print("--- BOT IS POLLING ---")
            bot.polling(none_stop=True)
        except:
            time.sleep(5)

if __name__ == "__main__":
    # Start web server first
    t = Thread(target=run_web)
    t.daemon = True
    t.start()
    
    # Run bot
    start_bot()
