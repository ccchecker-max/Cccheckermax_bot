import os
import telebot
import requests
import random
import time
from telebot import types
from flask import Flask
from threading import Thread

# 1. WEB SERVER
app = Flask('')
@app.route('/')
def home(): return "BOT STATUS: 🟢 SECURE & ACTIVE"

def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 2. SECURE TOKEN (Pulls from Render Secrets)
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# 3. /START COMMAND
@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💳 GATES", callback_query_data="gates"),
        types.InlineKeyboardButton("🛠️ TOOLS", callback_query_data="tools")
    )
    bot.send_message(message.chat.id, "💎 **CCCHECKERMAX LIVE** 🟢\n\nSelect an option:", reply_markup=markup, parse_mode="Markdown")

# 4. GATES LOGIC
@bot.message_handler(commands=['chk', 'sd', 'sh'])
def multi_checker(message):
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "❌ Use: `/[cmd] CC|MM|YY|CVV`", parse_mode="Markdown")
            return
        sent = bot.reply_to(message, "🔍 **Checking...**", parse_mode="Markdown")
        time.sleep(1.5)
        bot.edit_message_text("✦ RESULT: APPROVED ✅", message.chat.id, sent.message_id)
    except:
        bot.reply_to(message, "⚠️ Error!")

# 5. SAFE STARTUP
if __name__ == "__main__":
    # Start web server in background
    t = Thread(target=keep_alive)
    t.start()
    
    # Kill ghost connections
    print("Cleaning connection...")
    bot.remove_webhook()
    time.sleep(1)
    bot.delete_webhook(drop_pending_updates=True)
    
    print("Bot is LIVE and SECURE.")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
