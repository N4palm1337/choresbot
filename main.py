import time, asyncio
import message_parser
from telebot.async_telebot import AsyncTeleBot
from dotenv import load_dotenv
from os import getenv
from tinydb import TinyDB, where, operations
from datetime import datetime
from croniter import croniter
from pytz import timezone

load_dotenv()

TOKEN = getenv('TOKEN')
DAD = int(getenv('DAD'))
MAX = int(getenv('MAX'))


name_to_id = {}
for child in ['MAX', 'STE', 'KSU', 'VAL']:
    name_to_id[child] = int(getenv(child))

start_message = message_parser.read_message_text('start_message')

info_message_parent = message_parser.read_message_text('info_message_parent')

info_message_child = message_parser.read_message_text('info_message_child')

add_chore_failure_format = message_parser.read_message_text('add_chore_failure_format')

add_chore_failure_child_name = message_parser.read_message_text('add_chore_failure_child_name')

add_chore_failure_no_access = message_parser.read_message_text('add_chore_failure_no_access')

add_chore_success = message_parser.read_message_text('add_chore_success')

DELAY = 10

bot = AsyncTeleBot(TOKEN, parse_mode=None)

uninit = TinyDB('db/uninit.json')

@bot.message_handler(commands=['start'])
async def introduce(message):
    await bot.reply_to(message, start_message)

@bot.message_handler(commands=['info'])
async def give_info(message):
    if message.from_user.id != DAD and message.from_user.id != MAX:
        await bot.reply_to(message, info_message_child)
    else:
        await bot.reply_to(message, info_message_parent, parse_mode='MarkdownV2')

@bot.message_handler(commands=['addchore'])
async def add_chore(message): 
    # checking access rights
    if message.from_user.id != DAD and message.from_user.id != MAX:
        await bot.reply_to(message, add_chore_failure_no_access)
        # print(message.from_user.id)
    
    # breaking message into lines and checking time format
    try:
        args = message_parser.parse_add_chore(message)
    except:
        await bot.reply_to(message, add_chore_failure_format)
        return
    
    # checking child name
    if args[0] not in ['MAX', 'STE', 'KSU', 'VAL']:
        await bot.reply_to(message, add_chore_failure_child_name)
        return
    else:
        designated_child = name_to_id[args[0]]
    
    with open('db/id_counter', 'r') as f:
        _id_ = int(f.read())
        
    uninit.insert({'id': _id_, 'to': designated_child, 'desc': args[1], 'time': args[2], 'cron': args[3]})
    
    with open('db/id_counter', 'w') as f:
        f.write(str(_id_ + 1))
    
    await bot.reply_to(message, add_chore_success + str(_id_))


async def send_reminder():
    while True:
        tasks = uninit.search(where('time') <= time.time())
        
        for task in tasks:
            await bot.send_message(task['to'], task['desc'])
            await bot.send_message(DAD, f"sent reminder to {task['to']} about task with id {task['id']}")
            if task['cron'] is not None:
                uninit.update(operations.set('time', (croniter(task['cron'], 
                                                               datetime.now(tz=timezone('Europe/Moscow')))).get_next()), where('id') == task['id'])
            else:
                uninit.remove(where('id') == task['id'])
        
        await asyncio.sleep(DELAY)


async def main():
    fetch_task = asyncio.create_task(bot.infinity_polling())
    send_task = asyncio.create_task(send_reminder())
    
    await fetch_task
    await send_task


if __name__ == '__main__':
    asyncio.run(main())