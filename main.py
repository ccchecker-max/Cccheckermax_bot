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

# Environment variables se data uthayega
BOT_TOKEN = os.environ.get('8572635808:AAERJ8lmiRaYMYHS6i52C2-gtQSav1VdKiY')
STRIPE_SK = os.environ.get('sk_test_51TRF6rKHmp5uzHmulRC7yZ82ipVZ228CdiqkLhBiNF7EogFJ6KoPLW6qzGyDOlusfuWBn2RtSk43jYVbcoIS597K00BoJj91An')

bot = telebot.TeleBot(8572635808:AAERJ8lmiRaYMYHS6i52C2-gtQSav1VdKiY)

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "Welcome Wasim! `/chk CC|MM|YY|CVV` format use karein.", parse_mode="Markdown")

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
            result = f"❌ **DEAD**\n📝 {res.get('error', {}).get('message', 'Error')}"
            
        bot.edit_message_text(f"💳 Card: `{cc}`\n{result}", message.chat.id, sent.message_id, parse_mode="Markdown")
    except:
        bot.reply_to(message, "Format: `/chk CC|MM|YY|CVV`")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
