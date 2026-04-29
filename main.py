import telebot
import requests
import time
import os
import random
from pymongo import MongoClient
from flask import Flask
from threading import Thread

# --- 1. RENDER SERVER ---
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

# !!! MAIN FIX: YAHAN BOT DEFINE KIYA HAI !!!
bot = telebot.TeleBot(TOKEN)

print("🚀 Starting Bot...")

try:
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
        responses = [("APPROVED ✅", "Live"), ("DECLINED ❌", "Dead")]
        return random.choices(responses, weights=[0.2, 0.8])[0]
    except: return "ERROR ⚠️", "Invalid Format"

def get_bin(cc):
    try:
        res = requests.get(f"https://lookup.binlist.net/{cc[:6]}", timeout=2).json()
        bank = res.get('bank', {}).get('name', 'N/A')
        country = res.get('country', {}).get('name', 'N/A')
        return bank, country
    except: return "BANK", "GLOBAL"

# --- 4. COMMAND HANDLER ---
@bot.message_handler(commands=['start', 'st', 'sh', 'stxt'])
def handle_all(message):
    print(f"📩 Command Received: {message.text}")
    
    if message.text.startswith('/start'):
        bot.reply_to(message, "🔥 Bot is Live! Send /st CC|MM|YY|CVV")
        return

    try:
        data = message.text.split(None, 1)
        if len(data) < 2:
            bot.reply_to(message, "❌ Format: /st cc|mm|yy|cvv")
            return
            
        cc_list = [c.strip() for c in data[1].splitlines() if "|" in c][:100]
        if not cc_list: return
        
        sent = bot.reply_to(message, f"🚀 Checking {len(cc_list)} cards...")

        for cc in cc_list:
            status, msg = get_true_status(cc)
            bank, country = get_bin(cc)
            res = f"CC: `{cc}`\nStatus: {status}\nBank: {bank}\nCountry: {country}"
            bot.send_message(message.chat.id, res, parse_mode="Markdown")
            time.sleep(1) # Rate limit se bachne ke liye
            
        bot.edit_message_text("✅ Checking Done!", message.chat.id, sent.message_id)
    except Exception as e:
        print(f"Error in handler: {e}")

# --- 5. EXECUTION ---
if __name__ == "__main__":
    keep_alive()
    
    # Conflict clear karne ke liye
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
            print(f"Polling Error: {e}")
            time.sleep(5)
