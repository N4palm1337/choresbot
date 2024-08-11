import telebot, threading, time
from dotenv import load_dotenv
from os import getenv
# import tinydb
import message_texts, message_parser

load_dotenv()

TOKEN = getenv('TOKEN')
DAD = int(getenv('DAD'))
MAX = int(getenv('MAX'))

DELAY = 30

bot = telebot.TeleBot(TOKEN, parse_mode=None)

# uninit = tinydb.TinyDB('db/uninit.json')

@bot.message_handler(commands=['start'])
def introduce(message):
    bot.reply_to(message, message_texts.start_message)

@bot.message_handler(commands=['info'])
def give_info(message):
    if message.from_user.id != DAD and message.from_user.id != MAX:
        bot.reply_to(message, message_texts.info_message_child)
    else:
        bot.reply_to(message, message_texts.info_message_parent)


@bot.message_handler(commands=['addchore'])
def add_chore(message): 
    # checking access rights
    if message.from_user.id != DAD and message.from_user.id != MAX:
        bot.reply_to(message, message_texts.add_chore_message_no_access)
        return
        # print(message.from_user.id)
    
    # breaking message into lines and checking time format
    try:
        args = message_parser.parse_add_chore(message)
    except:
        bot.reply_to(message, message_texts.add_chore_failure_format)
        return
    
    # checking child name
    try:
        designated_child = int(getenv(args[0], default='nuhuh'))
    except:
        bot.reply_to(message, message_texts.add_chore_failure_child_name)
        return
    
    with open('db/id_counter', 'r') as f:
        _id_ = int(f.read())
        
    # uninit.insert({'id': _id_, 'to': designated_child, 'desc': args[1], 'time': args[2]})
    
    with open('db/id_counter', 'w') as f:
        f.write(str(_id_ + 1))
    
    bot.reply_to(message, message_texts.add_chore_success)


def send_reminder():
    while True:
        # send reminders (todo)
        time.sleep(DELAY)
        


reminder_thread = threading.Thread(target=send_reminder)
reminder_thread.start()


while True:
    try:
        bot.infinity_polling()
    except:
        time.sleep(10)