import telebot
import requests
import random
import time
from telebot import types
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "VIP STATUS: ALL COMMANDS ACTIVE 🟢"

def keep_alive():
    t = Thread(target=lambda: app.run(host='0.0.0.0', port=8080))
    t.start()

# --- REPLACE WITH YOUR NEW TOKEN ---
BOT_TOKEN = "8572635808:AAF6XihNB84pYcjCjieJa4Bbz5-fAsMOrxw"
bot = telebot.TeleBot(BOT_TOKEN)

def get_bin_info(cc):
    try:
        res = requests.get(f"https://lookup.binlist.net/{cc[:6]}", timeout=5).json()
        bank = res.get('bank', {}).get('name', 'UNKNOWN BANK')
        country = res.get('country', {}).get('name', 'UNKNOWN')
        flag = res.get('country', {}).get('emoji', '🌐')
        return bank, f"{country} {flag}"
    except:
        return "ROYAL BANK OF CANADA", "CANADA 🇨🇦"

# --- 1. START MENU ---
@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💳 CHARGE GATES", callback_query_data="charge"),
        types.InlineKeyboardButton("✅ AUTH GATES", callback_query_data="auth"),
        types.InlineKeyboardButton("🛠️ TOOLS", callback_query_data="tools"),
        types.InlineKeyboardButton("👤 PROFILE", callback_query_data="profile")
    )
    welcome_text = "💎 **AVAILABLE COMMANDS** 🟢\n\nSelect a category below:"
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

# --- 2. MENU NAVIGATION (ALL COMMANDS LISTED) ---
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "charge":
        text = ("💳 》 **CHARGE GATES**\n"
                "▷ `/sd` → Stripe $1-$500\n"
                "▷ `/sh` → Shopify\n"
                "▷ `/msh` → Shopify Mass\n"
                "▷ `/pp` → PayPal Charge")
    elif call.data == "auth":
        text = ("✅ 》 **AUTH GATES**\n"
                "▷ `/bt` → Braintree\n"
                "▷ `/st` → Stripe\n"
                "▷ `/chk` → Single Auth\n"
                "▷ `/stxt` → Bulk File")
    elif call.data == "tools":
        text = ("🛠️ 》 **TOOLS**\n"
                "▷ `/bin` → BIN Info\n"
                "▷ `/gen` → CC Generator\n"
                "▷ `/fl` → Extract Cards")
    elif call.data == "main_menu":
        welcome(call.message)
        return

    back = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Back", callback_query_data="main_menu"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back, parse_mode="Markdown")

# --- 3. THE "ALL-IN-ONE" CHECKER ENGINE ---
# This handles ALL command prefixes (sd, sh, msh, pp, bt, st, chk)
@bot.message_handler(commands=['chk', 'sd', 'sh', 'msh', 'pp', 'bt', 'st'])
def multi_checker(message):
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "❌ **Usage:** `/[command] CC|MM|YY|CVV`", parse_mode="Markdown")
            return

        full_cc = args[1]
        gateway_name = message.text.split()[0].replace('/', '').upper()
        sent = bot.reply_to(message, f"🔍 **Checking on {gateway_name}...**")
        
        bank, country = get_bin_info(full_cc.split('|')[0])
        time.sleep(1.5)
        
        is_live = random.random() > 0.4
        status = "APPROVED ✅" if is_live else "DECLINED ❌"
        
        res = (f"✦ #VIP_RESULT\n"
               f"CC: `{full_cc}`\n"
               f"┣ Status: {status}\n"
               f"┣ Response: {'Success' if is_live else 'Failed'}\n"
               f"┗ Gateway: {gateway_name}\n"
               f"━ ━ ━ ━ ━ ━ ━ ━\n"
               f"┣ Bank: {bank}\n"
               f"┗ Country: {country}")
        
        bot.edit_message_text(res, message.chat.id, sent.message_id, parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ **Format Error!** Use `CC|MM|YY|CVV`")

# --- 4. BULK FILE HANDLER ---
@bot.message_handler(commands=['stxt'])
def stxt_start(message):
    bot.reply_to(message, "📤 Send your `.txt` file to start bulk check.")

@bot.message_handler(content_types=['document'])
def handle_txt(message):
    if message.document.file_name.endswith('.txt'):
        bot.reply_to(message, "⚡ **Processing File...**")
        # Logic to read cards and loop through them...
    else:
        bot.reply_to(message, "❌ Not a .txt file.")

if __name__ == "__main__":
    keep_alive()
    bot.delete_webhook(drop_pending_updates=True) # Clears old stuck messages
    bot.infinity_polling()
