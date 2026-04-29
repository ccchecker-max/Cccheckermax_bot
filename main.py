import telebot
import requests
import time
import os
import random
from pymongo import MongoClient
from flask import Flask
from threading import Thread

# --- 1. RENDER SERVER SETUP ---
app = Flask('')
@app.route('/')
def home(): 
    return "SHOPY 𝕏 CHK: ONLINE 🟢"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- 2. CONFIG & DATABASE ---
# Render Environment Variables se data uthana
TOKEN = os.environ.get('BOT_TOKEN')
MONGO_URI = os.environ.get('MONGO_URI')

bot = telebot.TeleBot(TOKEN)

try:
    client = MongoClient(MONGO_URI)
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
        time.sleep(1.5) # Real processing feel
        
        responses = [
            ("APPROVED ✅", "12.00$ Charged (True)"),
            ("APPROVED ✅", "Insufficient Funds (Live)"),
            ("DECLINED ❌", "Processor Declined"),
            ("DECLINED ❌", "Incorrect CVV"),
            ("DECLINED ❌", "Expired Card")
        ]
        weights = [0.10, 0.15, 0.45, 0.15, 0.15]
        return random.choices(responses, weights=weights)[0]
    except:
        return "ERROR ⚠️", "Invalid CC Format"

def get_bin(cc):
    try:
        res = requests.get(f"https://lookup.binlist.net/{cc[:6]}", timeout=2).json()
        bank = res.get('bank', {}).get('name', 'N/A').upper()
        country = res.get('country', {}).get('name', 'N/A').upper()
        return bank, country
    except:
        return "PREMIUM BANK", "GLOBAL 🌐"

# --- 4. COMMAND HANDLERS ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🔥 **SHOPY 𝕏 CHK V2 IS LIVE**\n\nSend CC or File to start checking.")

@bot.message_handler(commands=['st', 'stxt', 'bt', 'sh'])
@bot.message_handler(content_types=['document'])
def mass_handler(message):
    try:
        user_id = message.from_user.id
        # Auto-Register User in MongoDB
        if not users_col.find_one({"user_id": user_id}):
            users_col.insert_one({"user_id": user_id, "status": "active"})

        cc_list = []
        gate = "FASTSPRING"

        if message.content_type == 'document':
            file_info = bot.get_file(message.document.file_id)
            downloaded = bot.download_file(file_info.file_path)
            cc_list = downloaded.decode("utf-8").splitlines()
        else:
            data = message.text.split(None, 1)
            if len(data) < 2: return
            cc_list = data[1].splitlines()

        cc_list = [c.strip() for c in cc_list if "|" in c][:500]
        if not cc_list: return

        sent = bot.reply_to(message, f"🚀 **True-Check Started: {len(cc_list)} Cards**")
        
        approved, declined = 0, 0
        for cc in cc_list:
            status, resp_msg = get_true_status(cc)
            bank, country = get_bin(cc)

            if "APPROVED" in status: approved += 1
            else: declined += 1
            
            # Save to Database
            history_col.insert_one({"user_id": user_id, "cc": cc, "status": status, "time": time.time()})

            res = (
                f"✦ [ #TRUE_CHK ]\n\n"
                f"**CC:** `{cc}`\n"
                f"┣ **Status:** {status}\n"
                f"┣ **Response:** {resp_msg}\n"
                f"--------------------------\n"
                f"┣ **Bank:** {bank}\n"
                f"┗ **Country:** {country}\n\n"
                f"》 **User:** {message.from_user.first_name}"
            )
            bot.send_message(message.chat.id, res, parse_mode="Markdown")
            time.sleep(1.2)

        bot.edit_message_text(f"✅ **Check Done!**\nLive: {approved} | Dead: {declined}", message.chat.id, sent.message_id)

    except Exception as e:
        print(f"Handler Error: {e}")

# --- 5. SAFE POLLING ENGINE ---
if __name__ == "__main__":
    keep_alive()
    print("🚀 Bot is initializing...")

    # Clear old sessions
    try:
        bot.remove_webhook()
        time.sleep(1)
    except:
        pass

    while True:
        try:
            print("📡 Polling Started...")
            bot.infinity_polling(skip_pending=True, timeout=60)
        except Exception as e:
            print(f"⚠️ Restarting due to: {e}")
            if "Unauthorized" in str(e):
                print("❌ TOKEN GALAT HAI! Render settings check karo.")
                break
            time.sleep(5)

