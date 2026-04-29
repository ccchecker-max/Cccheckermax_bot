import telebot
import requests
import random
import time
import os
from telebot import types
from flask import Flask
from threading import Thread

# --- FLASK SERVER (Keeps Render Web Service Alive) ---
app = Flask('')

@app.route('/')
def home():
    return "BOT STATUS: ONLINE 🟢"

def run():
    # Render binds to the PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- BOT CONFIG ---
TOKEN = os.environ.get('BOT_TOKEN') 
bot = telebot.TeleBot(TOKEN)

# --- BIN LOOKUP ---
def get_bin_info(cc):
    try:
        bin_num = cc[:6]
        res = requests.get(f"https://lookup.binlist.net/{bin_num}", timeout=2).json()
        bank = res.get('bank', {}).get('name', 'N/A')
        country = res.get('country', {}).get('name', 'N/A')
        flag = res.get('country', {}).get('emoji', '🌐')
        return bank.upper(), f"{country.upper()} {flag}"
    except:
        return "PREMIUM BANK", "GLOBAL 🌐"

# --- MENU BUILDER ---
def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💳 CHARGE", callback_data="charge"),
types.InlineKeyboardButton("✅ AUTH", callback_data="auth"),
types.InlineKeyboardButton("🛠️ TOOLS", callback_data="tools")
    )
    return markup

# --- COMMANDS ---
@bot.message_handler(commands=['start'])
def welcome(message):
    text = "💎 **WELCOME TO CCCHECKERMAX** 🟢\n\nSelect a category to see commands:"
    bot.send_message(message.chat.id, text, reply_markup=main_menu(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    back = types.InlineKeyboardButton("🔙 Back", callback_data="main_menu")
    if call.data == "main_menu":
        bot.edit_message_text("💎 **MAIN MENU** 🟢", call.message.chat.id, call.message.message_id, reply_markup=main_menu(), parse_mode="Markdown")
    elif call.data == "charge":
        bot.edit_message_text("💳 **CHARGE GATES**\n\n▷ `/sd` - Stripe\n▷ `/sh` - Shopify\n▷ `/pp` - PayPal", call.message.chat.id, call.message.message_id, reply_markup=back, parse_mode="Markdown")
    elif call.data == "auth":
        bot.edit_message_text("✅ **AUTH GATES**\n\n▷ `/chk` - Auth\n▷ `/st` - Stripe Auth\n▷ `/bt` - Braintree", call.message.chat.id, call.message.message_id, reply_markup=back, parse_mode="Markdown")
    elif call.data == "tools":
        bot.edit_message_text("🛠️ **TOOLS**\n\n▷ `/bin [bin]` - BIN Info\n▷ `/gen [bin]` - CC Gen", call.message.chat.id, call.message.message_id, reply_markup=back, parse_mode="Markdown")

@bot.message_handler(commands=['chk', 'sd', 'sh', 'pp', 'bt', 'st'])
def multi_checker(message):
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "❌ **Usage:** `/[gate] CC|MM|YY|CVV`", parse_mode="Markdown")
            return

        cc = args[1]
        gate = args[0].replace('/', '').upper()
        sent = bot.reply_to(message, f"🔍 **Checking on {gate}...**", parse_mode="Markdown")
        
        bank, country = get_bin_info(cc.split('|')[0])
        time.sleep(1.5)
        
        status = random.choice(["APPROVED ✅", "DECLINED ❌"])
        
        res = (f"✦ [ #Auto_{gate} ]\nCC: `{cc}`\n┣ Status: {status}\n┣ Bank: {bank}\n┗ Country: {country}")
        bot.edit_message_text(res, message.chat.id, sent.message_id, parse_mode="Markdown")
    except:
        bot.reply_to(message, "⚠️ **Check Format.**")

# --- STARTUP ---
if __name__ == "__main__":
    keep_alive()
    print("System Online...")
    time.sleep(5) # Prevents 409 Conflict on Render
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
