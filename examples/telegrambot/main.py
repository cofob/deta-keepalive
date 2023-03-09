from deta_keepalive import Pinger
import telebot
import deta
import os

bot = telebot.TeleBot("your token here")
pinger = Pinger(deta.Deta(os.environ["DETA_PROJECT_KEY"]))


@bot.message_handler(commands=["start"])
def start(m):
    bot.send_message(m.chat.id, f"Hello from Deta!")


def app(event):
    pinger.run()
    bot.polling(none_stop=True, interval=0)
