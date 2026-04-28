import os
import telebot
import time
from flask import Flask
from threading import Thread

# 1. WEB SERVER (Keeps Render 'Live')
app = Flask('')
@app.route('/')
def home(): return "BOT STATUS: 🟢 ONLINE"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 2. SECURE BOT LOGIC
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    # CRITICAL FIX: We ONLY use InlineKeyboardMarkup with InlineKeyboardButton
    markup = telebot.types.InlineKeyboardMarkup()
    btn1 = telebot.types.InlineKeyboardButton(text="💳 GATES", callback_data="gt")
    btn2 = telebot.types.InlineKeyboardButton(text="🛠️ TOOLS", callback_data="tl")
    markup.add(btn1, btn2)
    
    bot.send_message(
        message.chat.id, 
        "💎 **CCCHECKERMAX IS READY**\n\nChoose an option:", 
        reply_markup=markup, 
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_menu(call):
    if call.data == "gt":
        bot.edit_message_text("💳 **GATES**\n\n▷ `/chk` - Auth\n▷ `/sd` - Stripe", call.message.chat.id, call.message.message_id)
    elif call.data == "tl":
        bot.edit_message_text("🛠️ **TOOLS**\n\n▷ `/bin` - BIN Info", call.message.chat.id, call.message.message_id)

# 3. THE "ZOMBIE KILLER" ENGINE
def start_bot():
    while True:
        try:
            print("Cleaning old sessions...")
            bot.remove_webhook()
            # This drops the old 'stuck' messages causing the 400 error
            bot.delete_webhook(drop_pending_updates=True) 
            print("--- SUCCESS: BOT IS POLLING ---")
            bot.polling(none_stop=True, timeout=20)
        except Exception as e:
            print(f"Error: {e}. Restarting...")
            time.sleep(5)

if __name__ == "__main__":
    t = Thread(target=run_web)
    t.daemon = True
    t.start()
    start_bot()
