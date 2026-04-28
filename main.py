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

# 2. SECURE BOT LOGIC
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# --- FIXED WELCOME FUNCTION ---
@bot.message_handler(commands=['start'])
def welcome(message):
    markup = telebot.types.InlineKeyboardMarkup()
    # Fixed: Inline buttons MUST have a callback_query_data or a url
    btn = telebot.types.InlineKeyboardButton(text="💳 GATES", callback_query_data="gt")
    markup.add(btn)
    
    bot.send_message(
        message.chat.id, 
        "💎 **CCCHECKERMAX IS READY**\n\nClick the button below to see gates:", 
        reply_markup=markup, 
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: True)
def cb(call):
    if call.data == "gt":
        # Fixed: Simplified response
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="💳 **GATES AVAILABLE**\n\n▷ `/chk` - Auth\n▷ `/sd` - Stripe",
            parse_mode="Markdown"
        )

# --- ENGINE ---
def start_bot():
    print("--- ATTEMPTING TO START POLLING ---")
    while True:
        try:
            bot.remove_webhook()
            # Clear backlog so it doesn't crash on start
            bot.delete_webhook(drop_pending_updates=True)
            print("--- SUCCESS: BOT IS POLLING ---")
            bot.polling(none_stop=True, timeout=20)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    # Start web server
    t = Thread(target=run_web)
    t.daemon = True
    t.start()
    
    # Run bot
    start_bot()
