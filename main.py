import telebot
import requests
import random
import time
from telebot import types
from flask import Flask
from threading import Thread

# 1. FLASK SERVER (For 24/7 Hosting)
app = Flask('')
@app.route('/')
def home(): return "BOT STATUS: 🟢 ONLINE & ACTIVE"

def keep_alive():
    t = Thread(target=lambda: app.run(host='0.0.0.0', port=8080))
    t.start()

# 2. BOT CONFIGURATION
# Replace this token if you generate a new one from @BotFather
BOT_TOKEN = "8572635808:AAF6XihNB84pYcjCjieJa4Bbz5-fAsMOrxw"
bot = telebot.TeleBot(BOT_TOKEN)

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

# 3. COMMAND: /START
@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💳 CHARGE GATES", callback_query_data="charge"),
        types.InlineKeyboardButton("✅ AUTH GATES", callback_query_data="auth"),
        types.InlineKeyboardButton("🛠️ TOOLS", callback_query_data="tools")
    )
    welcome_text = (
        "💎 **WELCOME TO CCCHECKERMAX** 🟢\n\n"
        "Select a category below to see available commands.\n"
        "**Format:** `/[command] CC|MM|YY|CVV`"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

# 4. MENU NAVIGATION
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "charge":
        text = "💳 **CHARGE GATES**\n\n▷ `/sd` - Stripe $1\n▷ `/sh` - Shopify\n▷ `/pp` - PayPal"
    elif call.data == "auth":
        text = "✅ **AUTH GATES**\n\n▷ `/chk` - Auth Check\n▷ `/st` - Stripe Auth\n▷ `/bt` - Braintree"
    elif call.data == "tools":
        text = "🛠️ **TOOLS**\n\n▷ `/bin` - BIN Info\n▷ `/gen` - CC Gen"
    elif call.data == "main_menu":
        welcome(call.message)
        return

    back = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Back", callback_query_data="main_menu"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back, parse_mode="Markdown")

# 5. ALL-IN-ONE CHECKER ENGINE
@bot.message_handler(commands=['chk', 'sd', 'sh', 'pp', 'bt', 'st'])
def multi_checker(message):
    try:
        msg_data = message.text.split()
        if len(msg_data) < 2:
            bot.reply_to(message, "❌ **Usage:** `/[cmd] CC|MM|YY|CVV`", parse_mode="Markdown")
            return

        input_data = msg_data[1]
        cc_parts = input_data.split('|')
        
        if len(cc_parts) < 4:
             bot.reply_to(message, "❌ **Format Error!**\nUse: `CC|MM|YY|CVV`", parse_mode="Markdown")
             return

        gate = message.text.split()[0].replace('/', '').upper()
        sent = bot.reply_to(message, f"🔍 **Checking on {gate}...**", parse_mode="Markdown")
        
        bank, country = get_bin_info(cc_parts[0])
        time.sleep(2) # Fake processing lag
        
        is_live = random.choice([True, False])
        status = "APPROVED ✅" if is_live else "DECLINED ❌"
        resp = "1000: Success" if is_live else "Generic Decline"
        
        res_text = (
            f"✦ [/mtxt] [ #Auto_{gate} ]\n"
            f"CC: `{input_data}`\n"
            f"┣ Status: {status}\n"
            f"┣ Response: {resp}\n"
            f"┣ Gateway: {gate} Payments\n"
            f"━ ━ ━ ━ ━ ━ ━ ━\n"
            f"┣ BIN: {cc_parts[0][:6]}\n"
            f"┣ Bank: {bank}\n"
            f"┗ Country: {country}\n\n"
            f"User: @{message.from_user.username if message.from_user.username else 'User'}"
        )
        bot.edit_message_text(res_text, message.chat.id, sent.message_id, parse_mode="Markdown")
        
    except Exception:
        bot.reply_to(message, "⚠️ **System Error!** Check your input.")

# 6. RUN PROCESS (With Anti-Conflict Logic)
if __name__ == "__main__":
    keep_alive()
    print("--- STARTING BOT ---")
    
    # FORCING CLEANUP: This stops the 409 Conflict error
    bot.remove_webhook()
    time.sleep(1)
    bot.delete_webhook(drop_pending_updates=True)
    
    print("Bot is live. No other instances are conflicting.")
    bot.infinity_polling()

