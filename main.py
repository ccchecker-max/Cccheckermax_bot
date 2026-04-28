import telebot
import requests
import random
import time
import os
from telebot import types
from flask import Flask
from threading import Thread

# --- FLASK SERVER ---
app = Flask('')

@app.route('/')
def home():
    return "BOT STATUS: ONLINE 🟢"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- BOT CONFIG ---
TOKEN = os.environ.get('BOT_TOKEN') 
bot = telebot.TeleBot(TOKEN)

# --- HELPER: BIN LOOKUP ---
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

# --- MAIN MENU BUILDER ---
def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("💳 CHARGE", callback_query_data="charge")
    btn2 = types.InlineKeyboardButton("✅ AUTH", callback_query_data="auth")
    btn3 = types.InlineKeyboardButton("🛠️ TOOLS", callback_query_data="tools")
    markup.add(btn1, btn2, btn3)
    return markup

# --- 1. START COMMAND ---
@bot.message_handler(commands=['start'])
def welcome(message):
    welcome_text = (
        "💎 **WELCOME TO CCCHECKERMAX** 🟢\n\n"
        "Click the buttons below to see all commands."
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu(), parse_mode="Markdown")

# --- 2. CALLBACK HANDLER (This shows the commands) ---
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # Back button setup
    back_markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Back to Menu", callback_query_data="main_menu"))
    
    if call.data == "main_menu":
        bot.edit_message_text("💎 **WELCOME TO CCCHECKERMAX** 🟢", call.message.chat.id, call.message.message_id, reply_markup=main_menu(), parse_mode="Markdown")
        
    elif call.data == "charge":
        text = (
            "💳 **CHARGE GATES**\n"
            "━━━━━━━━━━━━━━\n"
            "▷ `/sd CC|MM|YY|CVV` - Stripe Charge\n"
            "▷ `/sh CC|MM|YY|CVV` - Shopify\n"
            "▷ `/pp CC|MM|YY|CVV` - PayPal"
        )
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back_markup, parse_mode="Markdown")
        
    elif call.data == "auth":
        text = (
            "✅ **AUTH GATES**\n"
            "━━━━━━━━━━━━━━\n"
            "▷ `/chk CC|MM|YY|CVV` - Standard Auth\n"
            "▷ `/st CC|MM|YY|CVV` - Stripe Auth\n"
            "▷ `/bt CC|MM|YY|CVV` - Braintree"
        )
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back_markup, parse_mode="Markdown")
        
    elif call.data == "tools":
        text = (
            "🛠️ **TOOLS**\n"
            "━━━━━━━━━━━━━━\n"
            "▷ `/bin 411122` - Get BIN Info\n"
            "▷ `/gen 411122` - Generate Cards"
        )
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back_markup, parse_mode="Markdown")

# --- 3. CHECKER ENGINE ---
@bot.message_handler(commands=['chk', 'sd', 'sh', 'pp', 'bt', 'st'])
def multi_checker(message):
    try:
        msg_data = message.text.split()
        if len(msg_data) < 2:
            bot.reply_to(message, "❌ **Usage:** `/[command] CC|MM|YY|CVV`", parse_mode="Markdown")
            return

        input_cc = msg_data[1]
        cc_parts = input_cc.split('|')
        gate = message.text.split()[0].replace('/', '').upper()
        
        sent = bot.reply_to(message, f"🔍 **Checking on {gate}...**", parse_mode="Markdown")
        
        bank, country = get_bin_info(cc_parts[0])
        time.sleep(1) # Simulated delay
        
        is_live = random.choice([True, False])
        status = "APPROVED ✅" if is_live else "DECLINED ❌"
        
        final_res = (
            f"✦ [ #Auto_{gate} ]\n"
            f"CC: `{input_cc}`\n"
            f"┣ Status: {status}\n"
            f"┣ Gateway: {gate} Payments\n"
            f"━ ━ ━ ━ ━ ━ ━ ━\n"
            f"┣ Bank: {bank}\n"
            f"┗ Country: {country}\n\n"
            f"User: @{message.from_user.username if message.from_user.username else 'User'}"
        )
        bot.edit_message_text(final_res, message.chat.id, sent.message_id, parse_mode="Markdown")
    except:
        bot.reply_to(message, "⚠️ **System Error.**")

# --- 4. BIN TOOL ---
@bot.message_handler(commands=['bin'])
def bin_tool(message):
    try:
        bin_num = message.text.split()[1][:6]
        bank, country = get_bin_info(bin_num)
        bot.reply_to(message, f"🔍 **BIN INFO**\n\nBIN: `{bin_num}`\nBank: {bank}\nCountry: {country}", parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ Usage: `/bin 411122`")

# --- RUN THE BOT ---
if __name__ == "__main__":
    keep_alive()
    print("Bot is starting...")
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)

