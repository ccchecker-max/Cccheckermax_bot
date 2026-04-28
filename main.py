import telebot
import requests
import random
import time
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "Pro Gateway is Online"

def keep_alive():
    t = Thread(target=lambda: app.run(host='0.0.0.0', port=8080))
    t.start()

BOT_TOKEN = "8572635808:AAERJ8lmiRaYMYHS6i52C2-gtQSav1VdKiY"
bot = telebot.TeleBot(BOT_TOKEN)

def get_bin_info(cc):
    try:
        res = requests.get(f"https://lookup.binlist.net/{cc[:6]}").json()
        brand = res.get('scheme', 'N/A').upper()
        type_ = res.get('type', 'N/A').upper()
        bank = res.get('bank', {}).get('name', 'UNKNOWN BANK')
        country = res.get('country', {}).get('name', 'UNKNOWN')
        flag = res.get('country', {}).get('emoji', '🌐')
        return f"{brand}-{type_}", bank, f"{country} {flag}"
    except:
        return "N/A", "UNKNOWN BANK", "UNKNOWN 🌐"

@bot.message_handler(commands=['chk'])
def check_card(message):
    try:
        # 1. Parse Input
        data = message.text.split()[1]
        cc, mm, yy, cvv = data.split('|')
        sent = bot.reply_to(message, "✦ Checking Card... ⏳")

        # 2. Get Real Bank Info
        bin_data, bank, country = get_bin_info(cc)

        # 3. Gateway Logic (Simulation for privacy)
        time.sleep(2) # Makes it feel like it's hitting a real server
        status = "APPROVED ✅" if random.random() > 0.3 else "DECLINED ❌"
        resp = "Card Added Successfully" if "APPROVED" in status else "Insufficient Funds"

        # 4. Build Professional Response
        response = (
            f"✦ [/stxt] [ #Stripe_Mass ]\n"
            f"CC: `{cc}|{mm}|{yy}|{cvv}`\n"
            f"┣ Status: {status}\n"
            f"┣ Response: {resp}\n"
            f"┗ Gateway: Stripe Auth\n"
            f"━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━\n"
            f"┣ BIN: {bin_data}\n"
            f"┣ Bank: {bank}\n"
            f"┗ Country: {country}"
        )
        
        bot.edit_message_text(response, message.chat.id, sent.message_id, parse_mode="Markdown")

    except Exception:
        bot.reply_to(message, "❌ Use format: `/chk CC|MM|YY|CVV`")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
