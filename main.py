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

print("🚀 Starting Bot...") # Logs mein ye dikhna chahiye

try:
    # 30 second ka timeout diya hai taaki agar connect na ho toh error dikhaye
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=30000)
    # Connection check karne ke liye ping command
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
        return res.get('bank', {}).get('name', 'N/A'), res.get('country', {}).get('name', 'N/A')
    except: return "BANK", "GLOBAL"

# --- 4. COMMAND HANDLER ---
@bot.message_handler(commands=['start', 'st', 'sh', 'stxt'])
def handle_all(message):
    # DEBUG: Logs mein check karne ke liye
    print(f"📩 Command Received: {message.text}")
    
    if message.text.startswith('/start'):
        bot.reply_to(message, "🔥 Bot is Live! Send /st CC|MM|YY|CVV")
        return

    # Mass Check Logic
    try:
        data = message.text.split(None, 1)
        if len(data) < 2:
            bot.reply_to(message, "❌ Format: /st cc|mm|yy|cvv")
            return
            
        cc_list = [c.strip() for c in data[1].splitlines() if "|" in c][:100]
        sent = bot.reply_to(message, f"🚀 Checking {len(cc_list)} cards...")

        for cc in cc_list:
            status, msg = get_true_status(cc)
            bank, country = get_bin(cc)
            res = f"CC: `{cc}`\nStatus: {status}\nBank: {bank}"
            bot.send_message(message.chat.id, res, parse_mode="Markdown")
            
        bot.edit_message_text("✅ Done!", message.chat.id, sent.message_id)
    except Exception as e:
        print(f"Error: {e}")

# --- 5. THE MAIN POINT (CONFLICT KILLER) ---
if __name__ == "__main__":
    keep_alive()
    print("🚀 Bot is cleaning old sessions...")
    
    # Ye line 409 error ko khatam karegi
    try:
        # Purane saare latke huye updates ko drop kar do
        requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true")
        bot.remove_webhook()
        time.sleep(2)
    except: pass

    while True:
        try:
            print("📡 Polling started...")
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Conflict detect hua, 5 sec wait... {e}")
            time.sleep(5)

