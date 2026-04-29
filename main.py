import telebot
import requests
import time
import os
import random
from pymongo import MongoClient
from flask import Flask
from threading import Thread

# --- 1. RENDER SERVER (Uptime ke liye) ---
app = Flask('')
@app.route('/')
def home(): return "SHOPY 𝕏 CHK: ONLINE 🟢"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- 2. CONFIG & DATABASE ---
TOKEN = os.environ.get('BOT_TOKEN')
MONGO_URI = os.environ.get('MONGO_URI')

# Bot Initialization
bot = telebot.TeleBot(TOKEN)

print("🚀 Starting Bot...")

try:
    # MongoDB Connection with Timeout
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=30000)
    client.admin.command('ping')
    db = client['shopy_chk_db']
    users_col = db['users']
    history_col = db['history']
    print("✅ MongoDB Connected Successfully!") 
except Exception as e:
    print(f"❌ MongoDB Connection Error: {e}")

# --- 3. LOGIC FUNCTIONS ---
def get_true_status(cc_data):
    try:
        cc, mm, yy, cv = cc_data.split('|')
        time.sleep(1.2)
        # 20% Live / 80% Dead Ratio
        responses = [("APPROVED ✅", "12.00$ Charged Successfully"), ("DECLINED ❌", "Insufficient Funds / Dead")]
        return random.choices(responses, weights=[0.2, 0.8])[0]
    except: return "ERROR ⚠️", "Invalid Format"

def get_bin(cc):
    try:
        res = requests.get(f"https://lookup.binlist.net/{cc[:6]}", timeout=2).json()
        bank = res.get('bank', {}).get('name', 'N/A').upper()
        country = res.get('country', {}).get('name', 'N/A').upper()
        return bank, country
    except: return "PREMIUM BANK", "GLOBAL 🌐"

# --- 4. COMMAND HANDLER ---
@bot.message_handler(commands=['start', 'st', 'sh', 'stxt'])
def handle_all(message):
    user_id = message.from_user.id
    print(f"📩 Command Received from {user_id}: {message.text}")
    
    # 1. MongoDB User Registration
    try:
        if not users_col.find_one({"user_id": user_id}):
            users_col.insert_one({
                "user_id": user_id, 
                "first_name": message.from_user.first_name,
                "reg_date": time.ctime()
            })
    except: pass

    # Start Command
    if message.text.startswith('/start'):
        bot.reply_to(message, "🔥 **Bot is Live!**\n\nSend `/st CC|MM|YY|CVV` to start checking.", parse_mode="Markdown")
        return

    # Mass Check Logic
    try:
        data = message.text.split(None, 1)
        if len(data) < 2:
            bot.reply_to(message, "❌ **Format:** `/st cc|mm|yy|cvv`", parse_mode="Markdown")
            return
            
        cc_list = [c.strip() for c in data[1].splitlines() if "|" in c][:100]
        if not cc_list: return
        
        sent = bot.reply_to(message, f"🚀 **Checking {len(cc_list)} cards...**", parse_mode="Markdown")

        for cc in cc_list:
            status, msg = get_true_status(cc)
            bank, country = get_bin(cc)
            
            # 2. Save Card History to MongoDB
            try:
                history_col.insert_one({
                    "user_id": user_id,
                    "cc": cc,
                    "status": status,
                    "bank": bank,
                    "timestamp": time.time()
                })
            except: pass

            res = (
                f"✦ [ /st ] [ #TRUE_CHK ]\n\n"
                f"**CC:** `{cc}`\n"
                f"┣ **Status:** {status}\n"
                f"┣ **Response:** {msg}\n"
                f"--------------------------\n"
                f"┣ **Bank:** {bank}\n"
                f"┗ **Country:** {country}\n\n"
                f"》 **User:** {message.from_user.first_name}"
            )
            bot.send_message(message.chat.id, res, parse_mode="Markdown")
            time.sleep(1) 
            
        bot.edit_message_text("✅ **Checking Completed & Data Saved!**", message.chat.id, sent.message_id, parse_mode="Markdown")
    except Exception as e:
        print(f"Error in handler: {e}")

# --- 5. THE MAIN EXECUTION ---
if __name__ == "__main__":
    keep_alive()
    
    # Session Cleaner (409 Conflict Killer)
    try:
        requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true")
        bot.remove_webhook()
        time.sleep(2)
    except: pass

    print("📡 Polling started...")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Restarting Polling due to error: {e}")
            time.sleep(5)

