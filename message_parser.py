import time
from croniter import croniter
from datetime import datetime
from pytz import timezone


def parse_add_chore(message):
    ls = list(message.text.split('\n'))
    if len(ls) != 4:
        raise ValueError('Wrong format in add_chore: message has to have 4 lines')
    
    if croniter.is_valid(ls[3]):
        ls.append(ls[3])
        ls[3] = (croniter(ls[3], datetime.now(tz=timezone('Europe/Moscow')))).get_next()
    else:
        ls.append(None)
        ls[3] = convert_to_unix_time(ls[3])
    
    return ls[1:5]

def parse_change_chore_description(message):
    ls = list(message.text.split('\n'))
    if len(ls) != 3:
        raise ValueError('Wrong format in change_chore_description: message has to have 3 lines')
    
    try:
        ls[1] = int(ls[1])
    except:
        raise ValueError('Wrong format in change_chore_description: first argument must be an integer')
    
    return ls[1:3]


def parse_change_chore_time(message):
    ls = list(message.text.split('\n'))
    if len(ls) != 3:
        raise ValueError('Wrong format in change_chore_time: message has to have 3 lines')
    
    try:
        ls[1] = int(ls[1])
    except:
        raise ValueError('Wrong format in change_chore_time: first argument must be an integer')
    
    if croniter.is_valid(ls[2]):
        ls.append(ls[2])
        ls[2] = (croniter(ls[2], datetime.now(tz=timezone('Europe/Moscow')))).get_next()
    else:
        ls.append(None)
        ls[2] = convert_to_unix_time(ls[2])
    
    return ls[1:4]
    
    
# accepts messages from bot only
# returns id of chore if message is a reminder, and -1 otherwise
def check_if_message_is_a_reminder(message) -> int: 
    lines = list(message.text.split('\n'))
    try:
        lines[0] = int(lines[0])
        return lines[0]
    except:
        return -1
    
    

def convert_to_unix_time(time_str):
    return time.mktime(time.strptime(time_str, '%d/%m/%Y %H:%M'))

def read_message_text(name: str):
    with open(f'message_texts/{name}', 'r') as f:
        return f.read()
