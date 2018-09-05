import os
import telegram
from flask import Flask, request
from telegram.ext import Updater

app = Flask(__name__)

os.environ["HTTPS_PROXY"] = 'https://125.141.200.45:80'

global bot
with open('token.txt') as token_txt:
    token = token_txt.read()

    bot = telegram.Bot(token=token)



@app.route('/HOOK', methods=['POST'])
def webhook_handler():
    if request.method == "POST":
        # retrieve the message in JSON and then transform it to Telegram object
        update = telegram.Update.de_json(request.get_json(force=True))

        chat_id = update.message.chat.id

        # Telegram understands UTF-8, so encode text for unicode compatibility
        text = update.message.text.encode('utf-8')

        # repeat the same message back (echo)
        bot.sendMessage(chat_id=chat_id, text=text)

    return 'ok'


@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('https://http://127.0.0.1:5000/')
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


@app.route('/')
def index():
    return '.'

