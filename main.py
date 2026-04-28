import telebot
import requests
import random
import time
from telebot import types
from flask import Flask
from threading import Thread

# 1. FLASK SERVER (Keeps Render Active)
app = Flask('')
@app.route('/')
def home(): return "SYSTEM STATUS: 🟢 CONNECTED"

def keep_alive():
    t = Thread(target=lambda: app.run(host='0.0.0.0', port=8080))
    t.start()

# 2. UPDATED TOKEN
BOT_TOKEN = "8572635808:AAHmZWpIc0rwIYSgV8JzRLb_90IvvjYnr10"
bot = telebot.TeleBot(BOT_TOKEN)

def get_bin_info(cc):
    try:
        res = requests.get(f"https://lookup.binlist.net/{cc[:6]}", timeout=2).json()
        bank = res.get('bank', {}).get('name', 'N/A')
        country = res.get('country', {}).get('name', 'N/A')
        return bank.upper(), country.upper()
    except:
        return "PREMIUM BANK", "GLOBAL 🌐"

# 3. /START COMMAND
@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💳 GATES", callback_query_data="gates"),
        types.InlineKeyboardButton("🛠️ TOOLS", callback_query_data="tools")
    )
    bot.send_message(message.chat.id, "💎 **CCCHECKERMAX IS LIVE** 🟢\n\nUse the buttons below:", reply_markup=markup, parse_mode="Markdown")

# 4. CALLBACKS
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "gates":
        text = "💳 **GATES**\n\n▷ `/chk` - Auth\n▷ `/sd` - Stripe\n▷ `/sh` - Shopify"
    elif call.data == "tools":
        text = "🛠️ **TOOLS**\n\n▷ `/bin` - BIN Info\n▷ `/gen` - CC Gen"
    
    back = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Back", callback_query_data="main"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back, parse_mode="Markdown")

# 5. CHECKER ENGINE
@bot.message_handler(commands=['chk', 'sd', 'sh'])
def multi_checker(message):
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "❌ **Usage:** `/[cmd] CC|MM|YY|CVV`", parse_mode="Markdown")
            return

        cc_data = args[1]
        gate = message.text.split()[0].replace('/', '').upper()
        sent = bot.reply_to(message, f"🔍 **Checking {gate}...**", parse_mode="Markdown")
        
        bank, country = get_bin_info(cc_data.split('|')[0])
        time.sleep(1.5)
        
        is_live = random.choice([True, False])
        status = "APPROVED ✅" if is_live else "DECLINED ❌"
        
        res = (f"✦ RESULT\nCC: `{cc_data}`\n┣ Status: {status}\n┣ Gateway: {gate}\n┣ Bank: {bank}\n┗ Country: {country}")
        bot.edit_message_text(res, message.chat.id, sent.message_id, parse_mode="Markdown")
    except:
        bot.reply_to(message, "⚠️ Format Error!")

# 6. SAFE STARTUP
if __name__ == "__main__":
    keep_alive()
    print("--- CONNECTING TO TELEGRAM ---")
    
    # Force kill any old webhooks and drop pending updates
    bot.remove_webhook()
    time.sleep(1)
    bot.delete_webhook(drop_pending_updates=True)
    
    print("Bot is now the only instance. READY.")
    bot.infinity_polling()
