import telebot
from dotenv import load_dotenv
from os import getenv
from tinydb import TinyDB, Query
import messagetexts, message_parser

load_dotenv()

TOKEN = getenv("TOKEN")
DAD = getenv("DAD")

bot = telebot.TeleBot(TOKEN, parse_mode=None)

@bot.message_handler(commands=['start'])
def introduce(message):
    bot.reply_to(message, messagetexts.start_message)

@bot.message_handler(commands=['info'])
def give_info(message):
    bot.reply_to(message, messagetexts.info_message)


@bot.message_handler(commands=['addchore'])
def add_chore(message):
    if message.from_user.username != DAD:
        bot.reply_to(message, messagetexts.add_chore_message_no_access)
    else:
        args = message_parser.parse_add_chore(message)
        

@bot.message_handler(func= lambda msg: True)
def reply(message):
    bot.reply_to(message, "hairy")


bot.infinity_polling()