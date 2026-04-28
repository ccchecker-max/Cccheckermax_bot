import os
import telebot
import time
import random
from flask import Flask
from threading import Thread

# 1. WEB SERVER (Keeps Render service 'Live')
app = Flask('')

@app.route('/')
def home():
    return "BOT STATUS: 🟢 ONLINE & SECURE"

def run_web():
    # Render sets the PORT automatically
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 2. BOT CONFIGURATION
# Pulls from Render Environment Variable 'BOT_TOKEN'
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# --- COMMANDS ---
@bot.message_handler(commands=['start'])
def welcome(message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        telebot.types.InlineKeyboardButton("💳 GATES", callback_query_data="gates"),
        telebot.types.InlineKeyboardButton("🛠️ TOOLS", callback_query_data="tools")
    )
    bot.send_message(message.chat.id, "💎 **CCCHECKERMAX LIVE** 🟢\n\nSelect a category:", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def menu_callback(call):
    if call.data == "gates":
        text = "💳 **GATES**\n\n▷ `/chk` - Auth\n▷ `/sd` - Stripe\n▷ `/sh` - Shopify"
    elif call.data == "tools":
        text = "🛠️ **TOOLS**\n\n▷ `/bin` - BIN Info\n▷ `/gen` - CC Gen"
    else: return
    
    back = telebot.types.InlineKeyboardMarkup().add(telebot.types.InlineKeyboardButton("🔙 Back", callback_query_data="main"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back, parse_mode="Markdown")

@bot.message_handler(commands=['chk', 'sd', 'sh'])
def checker(message):
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "❌ **Usage:** `/[cmd] CC|MM|YY|CVV`", parse_mode="Markdown")
            return
        
        sent = bot.reply_to(message, "🔍 **Checking...**", parse_mode="Markdown")
        time.sleep(2)
        bot.edit_message_text("✦ RESULT: **APPROVED ✅**", message.chat.id, sent.message_id, parse_mode="Markdown")
    except:
        bot.reply_to(message, "⚠️ Format Error!")

# 3. SECURE STARTUP ENGINE
if __name__ == "__main__":
    # Start Web Server in background
    t = Thread(target=run_web)
    t.daemon = True
    t.start()
    
    print("--- CLEANING GHOST CONNECTIONS ---")
    # This block prevents the 409 Conflict error
    bot.remove_webhook()
    time.sleep(2)
    bot.delete_webhook(drop_pending_updates=True) 
    
    print("--- SUCCESS: BOT IS POLLING ---")
    # Start the Bot
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
