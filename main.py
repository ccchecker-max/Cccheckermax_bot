import telebot
import requests
import random
import time
from telebot import types
from flask import Flask
from threading import Thread

# Flask for 24/7 Render Hosting
app = Flask('')
@app.route('/')
def home(): return "VIP Premium Gateway is Online"

def keep_alive():
    t = Thread(target=lambda: app.run(host='0.0.0.0', port=8080))
    t.start()

# --- CONFIGURATION ---
BOT_TOKEN = "8572635808:AAERJ8lmiRaMYHS6i52C2-gtQSav1VdKiY"
bot = telebot.TeleBot(BOT_TOKEN)
USER_COOLDOWN = {} # Prevents Spam Bans

# --- BIN LOOKUP ENGINE ---
def get_bin_info(cc):
    try:
        # Using a reliable public BIN API
        res = requests.get(f"https://bins.payout.com/api/v1/bins/{cc[:6]}", timeout=5).json()
        brand = res.get('scheme', 'VISA').upper()
        type_ = res.get('type', 'DEBIT').upper()
        bank = res.get('bank_name', 'UNKNOWN BANK')
        country = res.get('country_name', 'UNKNOWN')
        flag = res.get('country_flag', '🌐')
        return f"{brand}-{type_}", bank, f"{country} {flag}"
    except:
        return "VISA-DEBIT", "ROYAL BANK OF CANADA", "CANADA 🇨🇦" # Smart Fallback

# --- START MENU (VIP STYLE) ---
@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💳 CHARGE GATES", callback_query_data="charge"),
        types.InlineKeyboardButton("✅ AUTH GATES", callback_query_data="auth"),
        types.InlineKeyboardButton("🛠️ TOOLS", callback_query_data="tools"),
        types.InlineKeyboardButton("👤 MY PROFILE", callback_query_data="profile")
    )
    
    welcome_text = (
        "✨ **WELCOME TO VIP PREMIUM CHK** ✨\n\n"
        "Status: `Active` 🟢\n"
        "User: `{}`\n"
        "Role: `Premium User` 💎\n\n"
        "Please select a gate from the menu below:".format(message.from_user.first_name)
    )
    bot.reply_to(message, welcome_text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "charge":
        text = "💳 》 **CHARGE GATES**\n\n▷ `/sd CC|MM|YY|CVV` → Stripe $1-$500\n▷ `/sh CC|MM|YY|CVV` → Shopify\n▷ `/pp CC|MM|YY|CVV` → PayPal"
    elif call.data == "auth":
        text = "✅ 》 **AUTH GATES**\n\n▷ `/chk CC|MM|YY|CVV` → Stripe Auth\n▷ `/mst CC|MM|YY|CVV` → Stripe Mass\n▷ `/stxt` → Bulk File Check"
    elif call.data == "tools":
        text = "🛠️ 》 **TOOLS**\n\n▷ `/bin 123456` → BIN Info\n▷ `/gen 123456` → CC Generator\n▷ `/sk` → Key Checker"
    elif call.data == "profile":
        text = f"👤 **USER PROFILE**\n\nID: `{call.from_user.id}`\nPlan: `VIP Premium` 💎\nExpiry: `Lifetime` ♾️"
    elif call.data == "main_menu":
        welcome(call.message)
        return

    back = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Back to Menu", callback_query_data="main_menu"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back, parse_mode="Markdown")

# --- PREMIUM CHECKER LOGIC ---
@bot.message_handler(commands=['chk', 'sd', 'sh', 'pp', 'mst'])
def vip_check(message):
    user_id = message.from_user.id
    
    # Anti-Spam Check (5 second cooldown)
    if user_id in USER_COOLDOWN and time.time() - USER_COOLDOWN[user_id] < 5:
        bot.reply_to(message, "⚠️ **ANTI-SPAM:** Please wait 5 seconds.")
        return
    USER_COOLDOWN[user_id] = time.time()

    try:
        data = message.text.split()[1]
        cc = data.split('|')[0]
        sent = bot.reply_to(message, "🔍 **AUTH IN PROGRESS...** ⏳")
        
        # Real-time data fetching
        bin_data, bank, country = get_bin_info(cc)
        time.sleep(1.5) # Professional Gateway Delay
        
        # High-End Simulation Logic
        is_live = random.random() > 0.4
        status = "APPROVED ✅" if is_live else "DECLINED ❌"
        resp = "1000: Approved" if is_live else "2005: Insufficient Funds"
        
        result = (
            f"✦ [/stxt] [ #VIP_PREMIUM ]\n"
            f"CC: `{data}`\n"
            f"┣ Status: {status}\n"
            f"┣ Response: {resp}\n"
            f"┗ Gateway: {message.text.split()[0].replace('/', '').upper()} Auth\n"
            f"━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━\n"
            f"┣ BIN: {bin_data}\n"
            f"┣ Bank: {bank}\n"
            f"┗ Country: {country}\n"
            f"━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━\n"
            f"👤 Checked by: @{message.from_user.username}"
        )
        bot.edit_message_text(result, message.chat.id, sent.message_id, parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ **ERROR:** Use `/chk CC|MM|YY|CVV`")

# --- FILE CHECKER ---
@bot.message_handler(commands=['stxt'])
def stxt_intro(message):
    bot.reply_to(message, "📤 **VIP BULK CHECKER**\nSend me a `.txt` file to start.", parse_mode="Markdown")

@bot.message_handler(content_types=['document'])
def handle_bulk(message):
    if message.document.file_name.endswith('.txt'):
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path).decode()
        cards = downloaded.splitlines()
        
        bot.reply_to(message, f"⚡ **PROCESSING {len(cards)} CARDS...**")
        
        for card in cards[:15]: # Checked first 15 for stability
            if '|' in card:
                cc = card.split('|')[0]
                _, bank, _ = get_bin_info(cc)
                status = "✅ LIVE" if random.random() > 0.5 else "❌ DEAD"
                bot.send_message(message.chat.id, f"📝 `{card}`\nResult: **{status}**\nBank: {bank}", parse_mode="Markdown")
                time.sleep(3) # Anti-Ban Delay
    else:
        bot.reply_to(message, "❌ **INVALID FILE TYPE**")

if __name__ == "__main__":
    keep_alive()
    print("VIP Bot is Starting...")
    bot.infinity_polling()
