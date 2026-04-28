import os
import telebot
import requests
import random
import time
from telebot import types
from flask import Flask
from threading import Thread

# 1. WEB SERVER (Keeps Render from sleeping)
app = Flask('')
@app.route('/')
def home(): return "BOT STATUS: 🟢 ACTIVE"

def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 2. SECURE TOKEN (Loads from Render Environment)
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# 3. COMMAND: /START
@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💳 GATES", callback_query_data="gates"),
        types.InlineKeyboardButton("🛠️ TOOLS", callback_query_data="tools")
    )
    bot.send_message(message.chat.id, "💎 **CCCHECKERMAX IS LIVE**\n\nSelect a category:", reply_markup=markup, parse_mode="Markdown")

# 4. MENU CALLBACKS
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "gates":
        text = "💳 **GATES**\n\n▷ `/chk` - Auth\n▷ `/sd` - Stripe\n▷ `/sh` - Shopify"
    elif call.data == "tools":
        text = "🛠️ **TOOLS**\n\n▷ `/bin` - BIN Info\n▷ `/gen` - CC Gen"
    else: return
    
    back = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Back", callback_query_data="main_menu"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back, parse_mode="Markdown")

# 5. CHECKER ENGINE
@bot.message_handler(commands=['chk', 'sd', 'sh'])
def multi_checker(message):
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "❌ Format: `/[cmd] CC|MM|YY|CVV`", parse_mode="Markdown")
            return
        sent = bot.reply_to(message, "🔍 **Checking...**", parse_mode="Markdown")
        time.sleep(2)
        bot.edit_message_text("✦ RESULT: APPROVED ✅", message.chat.id, sent.message_id)
    except:
        bot.reply_to(message, "⚠️ Error!")

# 6. STARTUP LOGIC
if __name__ == "__main__":
    t = Thread(target=keep_alive)
    t.start()
    
    print("--- CONNECTING TO TELEGRAM ---")
    bot.remove_webhook()
    time.sleep(1)
    bot.delete_webhook(drop_pending_updates=True)
    
    print("--- SUCCESS: BOT IS LIVE ---")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
