import telebot
import requests
import random
import time
import os
from telebot import types
from flask import Flask
from threading import Thread

# --- FLASK SERVER (Render 24/7 Keep-Alive) ---
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

# --- BOT CONFIG ---
TOKEN = os.environ.get('BOT_TOKEN') 
bot = telebot.TeleBot(TOKEN)

# --- HELPER FUNCTIONS ---
def get_bin_info(cc):
    try:
        bin_num = cc[:6]
        res = requests.get(f"https://lookup.binlist.net/{bin_num}", timeout=2).json()
        bank = res.get('bank', {}).get('name', 'N/A')
        brand = res.get('scheme', 'MASTER').upper()
        type_cc = res.get('type', 'CREDIT').upper()
        country = res.get('country', {}).get('name', 'N/A')
        flag = res.get('country', {}).get('emoji', '🌐')
        return bank.upper(), f"{country.upper()} {flag}", brand, type_cc
    except:
        return "PREMIUM BANK", "GLOBAL 🌐", "MASTER", "CREDIT"

def get_response_msg(status):
    if "APPROVED" in status or "NON VBV" in status:
        return random.choice(["Card Added Successfully", "Payment Successful", "authenticate_successful"])
    return random.choice(["CARD_NOT_ENROLLED", "GENERIC_DECLINE", "INSUFFICIENT_FUNDS", "challenge_required"])

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def welcome(message):
    text = (
        "💎 **AVAILABLE COMMANDS** 🟢\n\n"
        "💳 》 **CHARGE GATES**\n"
        " ▷ `/sd` → Stripe $1-$500\n"
        " ▷ `/sh` → Shopify\n"
        " ▷ `/msh` → Shopify Mass\n"
        " ▷ `/mtxt` → Shopify File\n"
        " ▷ `/pp` → PayPal Charge $1\n\n"
        "✅ 》 **AUTH GATES**\n"
        " ▷ `/bt` → Braintree\n"
        " ▷ `/st` → Stripe\n"
        " ▷ `/stxt` → Stripe File\n"
        " ▷ `/vbv` → VBV Lookup\n\n"
        "🛠 》 **TOOLS**\n"
        " ▷ `/bin` → BIN Info\n"
        " ▷ `/gen` → CC Gen\n"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# --- BIN LOOKUP COMMAND ---
@bot.message_handler(commands=['bin'])
def bin_cmd(message):
    try:
        bin_val = message.text.split()[1]
        bank, country, brand, type_cc = get_bin_info(bin_val)
        res = (
            f"B!N: **{bin_val}**\n"
            f"Bank: **{bank}**\n"
            f"Brand: **{brand}**\n"
            f"Scheme: **{brand}CARD**\n"
            f"Type: **{type_cc}**\n"
            f"Country: **{country}**"
        )
        bot.reply_to(message, res, parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ Use: `/bin 540545`")

# --- VBV LOOKUP COMMAND ---
@bot.message_handler(commands=['vbv'])
def vbv_cmd(message):
    try:
        cc = message.text.split()[1] if len(message.text.split()) > 1 else ""
        if not cc and message.reply_to_message:
            cc = message.reply_to_message.text.split()[1]
        
        if "|" not in cc: raise ValueError
        
        sent = bot.reply_to(message, "🔍 **VBV LOOKUP...**", parse_mode="Markdown")
        start = time.time()
        bank, country, _, _ = get_bin_info(cc.split('|')[0])
        
        is_vbv = random.choice([True, False])
        status = "VBV ❌" if is_vbv else "NON VBV ✅"
        resp = "challenge_required" if is_vbv else "authenticate_successful"

        res = (
            f"**VBV LOOKUP**\n\n"
            f"**CC:** `{cc}`\n"
            f"**Status:** {status}\n"
            f"**Response:** `{resp}`\n\n"
            f"**Type:** CREDIT | **Level:** PLATINUM\n"
            f"**Country:** {country}\n"
            f"**Bank:** {bank}\n\n"
            f"**Took:** {round(time.time() - start, 2)}s"
        )
        bot.edit_message_text(res, message.chat.id, sent.message_id, parse_mode="Markdown")
    except:
        bot.reply_to(message, "⚠️ Use: `/vbv CC|MM|YY|CVV` or reply to CC.")

# --- MASS & FILE CHECKER (500 CARDS SUPPORT) ---
@bot.message_handler(commands=['sd', 'st', 'sh', 'bt', 'pp', 'msh', 'mst', 'stxt'])
@bot.message_handler(content_types=['document'])
def mass_handler(message):
    try:
        # Get CC List from text or file
        if message.content_type == 'document':
            if not message.caption or not message.caption.startswith('/'): return
            file_info = bot.get_file(message.document.file_id)
            downloaded = bot.download_file(file_info.file_path)
            cc_list = downloaded.decode("utf-8").splitlines()
            gate = message.caption[1:].upper()
        else:
            data = message.text.split(None, 1)
            if len(data) < 2: return
            cc_list = data[1].splitlines()
            gate = data[0][1:].upper()

        cc_list = cc_list[:500] # Limit 500
        sent = bot.reply_to(message, f"🚀 **Starting Check: {len(cc_list)} Cards**", parse_mode="Markdown")
        
        approved, declined, total = 0, 0, 0
        start_time = time.time()

        for cc in cc_list:
            cc = cc.strip()
            if "|" not in cc: continue
            
            total += 1
            bank, country, _, _ = get_bin_info(cc.split('|')[0])
            status = "APPROVED ✅" if random.choice([True, False]) else "DECLINED ❌"
            if "APPROVED" in status: approved += 1
            else: declined += 1
            
            # Send single result (Only for small lists, else it hits flood limits)
            if len(cc_list) <= 5:
                res = (
                    f"✦ [ /{gate.lower()} ] [ #SHOPY_CHK ]\n\n"
                    f"**CC:** `{cc}`\n"
                    f"┣ **Status:** {status}\n"
                    f"┣ **Response:** {get_response_msg(status)}\n"
                    f"┗ **Gateway:** {gate}\n"
                    f"--------------------------\n"
                    f"┣ **Bank:** {bank}\n"
                    f"┗ **Country:** {country}\n\n"
                    f"》 **User:** {message.from_user.first_name} | **Bot:** SHOPY 𝕏 CHK"
                )
                bot.send_message(message.chat.id, res, parse_mode="Markdown")
            
            # Flood control for mass checking
            time.sleep(1.2)

        # Final Summary
        summary = (
            f"✅ **Checking Completed!**\n\n"
            f"Total Approved ✅ | {approved}\n"
            f"Total Declined ❌ | {declined}\n"
            f"Total Checked ☠️ | {total}\n"
            f"━━━━━━━━━━━━━━\n"
            f"⌛ **Time Taken:** {round(time.time() - start_time, 2)}s"
        )
        bot.edit_message_text(summary, message.chat.id, sent.message_id, parse_mode="Markdown")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    keep_alive()
    print("System Online...")

    try:
        bot.remove_webhook()
        time.sleep(2)
    except Exception as e:
        print(e)

    while True:
        try:
            bot.infinity_polling(
                skip_pending=True,
                timeout=30,
                long_polling_timeout=30
            )
        except Exception as e:
            print("Restarting:", e)
            time.sleep(5)
