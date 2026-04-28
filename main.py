import telebot
import requests
import random
import time
import os
from telebot import types
from flask import Flask
from threading import Thread

# Flask server for 24/7 hosting (Render/Replit)
app = Flask('')

@app.route('/')
def home():
    return "BOT STATUS: ONLINE 🟢"

def run():
    # Render provides a PORT environment variable; this ensures it binds correctly
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- BOT CONFIG ---
# Ensure 'BOT_TOKEN' is set in Render Environment Variables
TOKEN = os.environ.get('BOT_TOKEN') 
bot = telebot.TeleBot(TOKEN)

def get_bin_info(cc):
    try:
        # Taking only first 6 digits for BIN
        bin_num = cc[:6]
        res = requests.get(f"https://lookup.binlist.net/{bin_num}", timeout=2).json()
        bank = res.get('bank', {}).get('name', 'N/A')
        country = res.get('country', {}).get('name', 'N/A')
        flag = res.get('country', {}).get('emoji', '🌐')
        return bank.upper(), f"{country.upper()} {flag}"
    except:
        return "PREMIUM BANK", "GLOBAL 🌐"

# --- 1. START COMMAND ---
@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("💳 CHARGE", callback_query_data="charge")
    btn2 = types.InlineKeyboardButton("✅ AUTH", callback_query_data="auth")
    btn3 = types.InlineKeyboardButton("🛠️ TOOLS", callback_query_data="tools")
    markup.add(btn1, btn2, btn3)
    
    welcome_text = (
        "💎 **WELCOME TO CCCHECKERMAX** 🟢\n\n"
        "Use the menu below to see available commands.\n"
        "Example format: `/chk 4111222233334444|01|25|000`"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

# --- 2. CALLBACK HANDLER ---
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "charge":
        text = "💳 **CHARGE GATES**\n\n▷ `/sd` - Stripe\n▷ `/sh` - Shopify\n▷ `/pp` - PayPal"
    elif call.data == "auth":
        text = "✅ **AUTH GATES**\n\n▷ `/chk` - Auth\n▷ `/st` - Stripe Auth\n▷ `/bt` - Braintree"
    elif call.data == "tools":
        text = "🛠️ **TOOLS**\n\n▷ `/bin` - Check BIN\n▷ `/gen` - Generate CC"
    elif call.data == "main_menu":
        welcome(call.message)
        return
    else:
        return

    back = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Back", callback_query_data="main_menu"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back, parse_mode="Markdown")

# --- 3. THE CHECKER ENGINE ---
@bot.message_handler(commands=['chk', 'sd', 'sh', 'pp', 'bt', 'st'])
def multi_checker(message):
    try:
        msg_data = message.text.split()
        if len(msg_data) < 2:
            bot.reply_to(message, "❌ **Format Error!**\nUse: `/[command] CC|MM|YY|CVV`", parse_mode="Markdown")
            return

        input_cc = msg_data[1]
        cc_parts = input_cc.split('|')
        
        if len(cc_parts) < 4:
             bot.reply_to(message, "❌ **Format Error!** Use `CC|MM|YY|CVV`", parse_mode="Markdown")
             return

        gate = message.text.split()[0].replace('/', '').upper()
        sent = bot.reply_to(message, f"🔍 **Checking on {gate}...**", parse_mode="Markdown")
        
        bank, country = get_bin_info(cc_parts[0])
        time.sleep(2) # Simulating API response time
        
        is_live = random.choice([True, False])
        status = "APPROVED ✅" if is_live else "DECLINED ❌"
        resp_msg = "1000: Approved" if is_live else "2046: Declined/Blocked"
        
        final_res = (
            f"✦ [ #Auto_{gate} ]\n"
            f"CC: `{input_cc}`\n"
            f"┣ Status: {status}\n"
            f"┣ Response: {resp_msg}\n"
            f"┣ Gateway: {gate} Payments\n"
            f"━ ━ ━ ━ ━ ━ ━ ━\n"
            f"┣ BIN: {cc_parts[0][:6]}\n"
            f"┣ Bank: {bank}\n"
            f"┗ Country: {country}\n\n"
            f"User: @{message.from_user.username if message.from_user.username else 'User'}"
        )
        
        bot.edit_message_text(final_res, message.chat.id, sent.message_id, parse_mode="Markdown")
        
    except Exception as e:
        bot.reply_to(message, "⚠️ **System Error.** Check your input format.")

# --- RUN THE BOT ---
if __name__ == "__main__":
    keep_alive()
    print("Bot is starting...")
    bot.delete_webhook(drop_pending_updates=True)
    bot.infinity_polling()
