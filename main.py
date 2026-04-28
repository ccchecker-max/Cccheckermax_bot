import telebot
import requests
from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def home():
    return "Bot is Running 24/7!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Fixed Token and Key
BOT_TOKEN = "8572635808:AAERJ8lmiRaMYHS6i52C2-gtQSav1VdKiY"
STRIPE_SK = "sk_test_51TRF6rKHmpSuzHmu1RC7yZ02ipVZ228CdiqkuhB1NF7EogFJ6KaPLW6gzGy0O1usfuWBr2RtSk43jVVbceISS97K00p9lZ0r8C"

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "Welcome Wasim! Use `/chk CC|MM|YY|CVV` format.", parse_mode="Markdown")

@bot.message_handler(commands=['chk'])
def check_card(message):
    try:
        input_data = message.text.split()[1]
        cc, mm, yy, cvv = input_data.split('|')
        sent = bot.reply_to(message, "🔍 Checking...")

        r = requests.post(
            "https://api.stripe.com/v1/tokens",
            headers={"Authorization": f"Bearer {STRIPE_SK}"},
            data={"card[number]": cc, "card[exp_month]": mm, "card[exp_year]": yy, "card[cvc]": cvv}
        )
        res = r.json()

        if "id" in res:
            result = "✅ **LIVE**"
        else:
            msg = res.get('error', {}).get('message', 'Error')
            result = f"❌ **DEAD**\n📝 {msg}"
            
        bot.edit_message_text(f"Card: `{cc}`\n{result}", message.chat.id, sent.message_id, parse_mode="Markdown")
    except Exception:
        bot.reply_to(message, "Format: `/chk CC|MM|YY|CVV`")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
