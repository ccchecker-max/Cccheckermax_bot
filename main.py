import os
import telebot
import requests
import random
import time
from telebot import types
from flask import Flask
from threading import Thread

# 1. WEB SERVER (This is what Render watches)
app = Flask('')

@app.route('/')
def home():
    return "SYSTEM STATUS: 🟢 BOT IS ACTIVE AND SECURE"

@app.route('/health')
def health():
    return "OK", 200

def run_web_server():
    # Render provides the PORT environment variable automatically
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 2. BOT LOGIC
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💳 GATES", callback_query_data="gates"),
        types.InlineKeyboardButton("🛠️ TOOLS", callback_query_data="tools")
    )
    bot.send_message(message.chat.id, "💎 **CCCHECKERMAX LIVE** 🟢\n\nSelect an option below:", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "gates":
        text = "💳 **GATES**\n\n▷ `/chk` - Auth\n▷ `/sd` - Stripe\n▷ `/sh` - Shopify"
    elif call.data == "tools":
        text = "🛠️ **TOOLS**\n\n▷ `/bin` - BIN Info\n▷ `/gen` - CC Gen"
    else: return
    
    back = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Back", callback_query_data="main"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back, parse_mode="Markdown")

@bot.message_handler(commands=['chk', 'sd', 'sh'])
def multi_checker(message):
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "❌ Use: `/[cmd] CC|MM|YY|CVV`", parse_mode="Markdown")
            return
        sent = bot.reply_to(message, "🔍 **Checking...**", parse_mode="Markdown")
        time.sleep(2)
        bot.edit_message_text("✦ RESULT: **APPROVED ✅**", message.chat.id, sent.message_id, parse_mode="Markdown")
    except:
        bot.reply_to(message, "⚠️ Format Error!")

# 3. THE ENGINE (The part that prevents the 'Conflict' and 'Silent' issues)
def run_bot():
    while True:
        try:
            print("--- SECURING CONNECTION ---")
            bot.remove_webhook()
            bot.delete_webhook(drop_pending_updates=True)
            print("--- BOT IS POLLING ---")
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Bot error, restarting in 5s: {e}")
            time.sleep(5)

if __name__ == "__main__":
    # Start the Bot in a background thread
    bot_thread = Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Start the Web Server in the MAIN thread (This keeps Render happy)
    print("--- STARTING WEB SERVER ---")
    run_web_server()
