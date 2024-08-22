import time, asyncio, logging
import message_parser
from telebot.async_telebot import AsyncTeleBot
from dotenv import load_dotenv
from os import getenv
from tinydb import TinyDB, where, operations
from datetime import datetime
from croniter import croniter
from pytz import timezone

logger = logging.getLogger(__name__)

load_dotenv()

TOKEN = getenv('TOKEN')
MAX = int(getenv('MAX'))
DAD = int(getenv('DAD'))

parents = [int(getenv('DAD')), int(getenv('MAX'))]
children = ['MAX', 'STE', 'KSU', 'VAL']


name_to_id = {}
for child in children:
    name_to_id[child] = int(getenv(child))
    
id_to_name = {}
for child in children:
    id_to_name[name_to_id[child]] = child

start_message = message_parser.read_message_text('start_message')

info_message_parent = message_parser.read_message_text('info_message_parent')

info_message_child = message_parser.read_message_text('info_message_child')

add_chore_failure_format = message_parser.read_message_text('add_chore_failure_format')

add_chore_failure_child_name = message_parser.read_message_text('add_chore_failure_child_name')

add_chore_failure_no_access = message_parser.read_message_text('add_chore_failure_no_access')

add_chore_success = message_parser.read_message_text('add_chore_success')

delete_chore_failure_no_access = message_parser.read_message_text('delete_chore_failure_no_access')

change_chore_failure_no_access = message_parser.read_message_text('change_chore_failure_no_access')

change_chore_failure_format = message_parser.read_message_text('change_chore_failure_format')

lorem_ipsum = message_parser.read_message_text('lorem_ipsum')

DELAY = 10

bot = AsyncTeleBot(TOKEN, parse_mode=None)

uninit = TinyDB('db/uninit.json')


@bot.message_handler(commands=['start'])
async def introduce(message):
    logger.info('Entered introduce')
    await bot.reply_to(message, start_message)
    

@bot.message_handler(commands=['info'])
async def give_info(message):
    logger.info('Entered give_info')
    if message.from_user.id not in parents:
        await bot.reply_to(message, info_message_child)
    else:
        await bot.reply_to(message, info_message_parent, parse_mode='MarkdownV2')
        

@bot.message_handler(commands=['addchore'])
async def add_chore(message):
    logger.info('Entered add_chore') 
    # checking access rights
    if message.from_user.id not in parents:
        await bot.reply_to(message, add_chore_failure_no_access)
        return
    
    # breaking message into lines and checking time format
    try:
        args = message_parser.parse_add_chore(message)
    except:
        await bot.reply_to(message, add_chore_failure_format)
        return
    
    # checking child name
    if args[0] not in children:
        await bot.reply_to(message, add_chore_failure_child_name)
        return
    else:
        designated_child = name_to_id[args[0]]
    
    with open('db/id_counter', 'r') as f:
        _id_ = int(f.read())
        
    uninit.insert({'id': _id_, 'to': designated_child, 'from': message.from_user.id, 'desc': args[1], 'time': args[2], 'cron': args[3]})
    
    with open('db/id_counter', 'w') as f:
        f.write(str(_id_ + 1))
    
    await bot.reply_to(message, add_chore_success + str(_id_))
    

@bot.message_handler(commands=['delchore'])
async def delete_chore(message):
    logger.info('Entered delete_chore')
    if message.from_user.id not in parents:
        await bot.reply_to(message, delete_chore_failure_no_access)
        return
    
    args = list(message.text.split())
    if len(args) != 2:
        await bot.reply_to(message, 'Неправильный формат. Попробуйте еще раз.')
        return
    
    try:
        _id_ = int(args[1])
    except:
        await bot.reply_to(message, 'Что-то с ID. Попробуйте ещё раз.')
        return
    
    uninit.remove(where('id') == _id_)
    await bot.reply_to(message, f'Удалил задание с id {_id_}')

    
@bot.message_handler(commands=['changedesc'])
async def change_chore_description(message):
    logger.info('Entered change_chore_description')
    if message.from_user.id not in parents:
        await bot.reply_to(message, change_chore_failure_no_access)
        return
    
    try:
        args = message_parser.parse_change_chore_description(message)
    except:
        await bot.reply_to(message, change_chore_failure_format)
        return
    
    uninit.update(operations.set('desc', args[1]), where('id') == args[0])
    await bot.reply_to(message, f'Изменил описание задания с id {args[0]}')
    

@bot.message_handler(commands=['changetime'])
async def change_chore_time(message):
    logger.info('Entered change_chore_time')
    if message.from_user.id not in parents:
        await bot.reply_to(message, change_chore_failure_no_access)
        return
    
    try:
        args = message_parser.parse_change_chore_time(message)
    except:
        await bot.reply_to(message, change_chore_failure_format)
        return
    
    uninit.update(operations.set('time', args[1]), where('id') == args[0])
    uninit.update(operations.set('cron', args[2]), where('id') == args[0])
    await bot.reply_to(message, f'Изменил время задания с id {args[0]}')


@bot.message_handler(commands=['list'])
async def list_chores(message):
    logger.info('Entered list_chores')
    args = message.text.split()
    if len(args) > 2:
        await bot.reply_to(message, 'Команда принимает 0 или 1 аргумент(-ов).')
        return
    
    result_message = ''
    if len(args) == 2 and message.from_user.id in parents:
        if args[1] not in children:
            try:
                args[1] = int(args[1])
            except:
                await bot.reply_to(message, 'Проверьте аргумент!')
                return
        
        if type(args[1]) == int:
            tasks = uninit.search(where('id') == args[1])
        else:
            args[1] = name_to_id[args[1]]
            tasks = uninit.search(where('to') == args[1])
        for task in tasks:
            result_message += f"id задания: {task['id']}. \nОписание: '{task['desc']}'. \nБлижайшее время: {time.ctime(task['time'])}.\n"
            if task['cron'] is not None:
                result_message += f"Текущий cron: {task['cron']} \n\n"
            else:
                result_message += '\n'
        
        if len(result_message) > 0:
            await bot.reply_to(message, result_message)
        else:
            await bot.reply_to(message, 'Нету запланированных заданий.')
            
    elif len(args) == 2:
        try:
            args[1] = int(args[1])
        except:
            await bot.reply_to(message, 'Проверьте id!')
            return
        
        tasks = uninit.search(where('id') == args[1])
        for task in tasks:
            result_message += f"id: {task['id']} \n {task['desc']}. \nБлижайшее время: {time.ctime(task['time'])}.\n\n"
        
        if len(result_message) > 0:
            await bot.reply_to(message, result_message)
        else:
            await bot.reply_to(message, 'Нету запланированных заданий.')
            
    elif message.from_user.id not in parents:
        args.append(message.from_user.id)
        
        tasks = uninit.search(where('to') == args[1])
        for task in tasks:
            result_message += f"id: {task['id']} \n {task['desc']}. \nБлижайшее время: {time.ctime(task['time'])}.\n\n"
        
        if len(result_message) > 0:
            await bot.reply_to(message, result_message)
        else:
            await bot.reply_to(message, 'Нету запланированных заданий.')
        
    else:
        tasks = uninit.search(lambda m: True)
        for task in tasks:
            result_message += f"id задания: {task['id']}. Ребенок: {id_to_name[task['to']]}. \n"
            result_message += f"Описание: '{task['desc']}'. \nБлижайшее время: {time.ctime(task['time'])}. \n"
            if task['cron'] is not None:
                result_message += f"Текущий cron: {task['cron']} \n\n"
            else:
                result_message += '\n'
        
        if len(result_message) > 0:
            await bot.reply_to(message, result_message)
        else:
            await bot.reply_to(message, 'Нету запланированных заданий.')
        

@bot.message_handler(commands=['logout'])
async def log_out(message):
    logger.info('Entered log_out')
    if message.from_user.id != MAX:
        await bot.reply_to(message, 'Я Вас не понял. Попробуйте ещё раз.')
        return
    
    await bot.reply_to(message, 'logging out')
    await bot.log_out()
    exit(0)
    
@bot.message_handler(commands=['error'])
async def raise_error(message):
    logger.info('Entered raise_error')
    raise ValueError('Error on purpose - checking infinite loop wrapping')


@bot.message_handler(content_types=['photo', 'video'])
async def resend_photo_proof(message):
    logger.info('Entered resend_photo_proof')
    
    if message.from_user.id in parents and message.from_user.id != MAX:
        await bot.reply_to(message, 'Я вас не понял. Попробуйте ещё раз.')
        return
    
    if message.reply_to_message is None:
        await bot.reply_to(message, 'Я вас не понял. Попробуйте ещё раз.')
        return
    
    replied_to = message.reply_to_message
    id_of_chore = message_parser.check_if_message_is_a_reminder(replied_to)
    
    if id_of_chore != -1:
        logger.info('About to resend messages')
        try:
            whom_to_forward = uninit.search(where('id') == id_of_chore)[0]['from']
        except:
            whom_to_forward = DAD
        
        logger.info(whom_to_forward)
        await bot.forward_message(chat_id=whom_to_forward, from_chat_id=replied_to.chat.id, message_id=replied_to.message_id)
        await bot.forward_message(chat_id=whom_to_forward, from_chat_id=message.chat.id, message_id=message.message_id)
        await bot.reply_to(message, 'Отправил на проверку.')
    else:
        await bot.reply_to(message, 'Я вас не понял. Попробуйте ещё раз. Скорее всего, вы хотите ответить на другое сообщение.')
    
    
@bot.message_handler(commands=['text'])
async def send_lorem_ipsum(message):
    logger.info('Entered send_lorem_ipsum')
    await bot.reply_to(message, lorem_ipsum)

@bot.message_handler(func=lambda message: True)
async def unknown_command(message):
    logger.info('Entered unknown_command')
    await bot.reply_to(message, 'Я вас не понял. Попробуйте ещё раз.')
    return

    
# ^ | command reactions 
# ---------------------------------------------------
# v | remiders & asyncio wrap


async def send_reminder():
    logger.info('Entered send_reminder')
    while True:
        # logger.info('Entered send_reminder loop')
        
        tasks = uninit.search(where('time') <= time.time())
        
        for task in tasks:
            await bot.send_message(task['to'], str(task['id']) + '\n' + task['desc']) # id in the beginning to distinguish reminders from other things
            await bot.send_message(DAD, f"sent reminder to {id_to_name[task['to']]} about task with id {task['id']} and description '{task['desc']}'")
            logger.info(f"sent reminder to {task['to']} about task with id {task['id']}")
            if task['cron'] is not None:
                uninit.update(operations.set('time', (croniter(task['cron'], 
                                                               datetime.now(tz=timezone('Europe/Moscow')))).get_next()), where('id') == task['id'])
            else:
                uninit.remove(where('id') == task['id'])
        
        await asyncio.sleep(DELAY)


async def main():
    logger.info('Entered main')
    fetch_task = asyncio.create_task(bot.infinity_polling())
    send_task = asyncio.create_task(send_reminder())
    try:
        await fetch_task
        await send_task
    except Exception as e:
        logger.error(f'Exception in await wrap: {e}')
        asyncio.sleep(10)


if __name__ == '__main__':
    logging.basicConfig(
        filename='logs/bot.log',
        encoding='utf-8',
        filemode='a',
        format='{asctime} - {levelname} - {message}',
        style='{',
        datefmt='%d/%m/%Y %H:%M:%S',
        level=logging.INFO
    )
    logger.info('---------------------------')
    logger.info('About to enter main')
    asyncio.run(main())