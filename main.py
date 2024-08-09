import telebot
from dotenv import load_dotenv
from os import getenv
# from tinydb import TinyDB, Query
import messagetexts, message_parser

load_dotenv()

TOKEN = getenv('TOKEN')
DAD = int(getenv('DAD'))
MAX = int(getenv('MAX'))
STE = int(getenv('STE'))
KSU = int(getenv('KSU'))
VAL = int(getenv('VAL'))

bot = telebot.TeleBot(TOKEN, parse_mode=None)

@bot.message_handler(commands=['start'])
def introduce(message):
    bot.reply_to(message, messagetexts.start_message)

@bot.message_handler(commands=['info'])
def give_info(message):
    bot.reply_to(message, messagetexts.info_message)


@bot.message_handler(commands=['addchore'])
def add_chore(message):
    if message.from_user.id != DAD and message.from_user.id != MAX:
        bot.reply_to(message, messagetexts.add_chore_message_no_access)
        print(message.from_user.id)
    else:
        try:
            args = message_parser.parse_add_chore(message)
        except:
            bot.reply_to(message, messagetexts.add_chore_failure_format)
            return
        
        # tinyDB.insert({'id': id, 'desc': args[0], 'to': args[1], 'time': args[2]})
        # id += 1
        bot.reply_to(message, messagetexts.add_chore_success)




@bot.message_handler(func= lambda msg: True)
def reply(message):
    bot.reply_to(message, "hairy")


bot.infinity_polling()