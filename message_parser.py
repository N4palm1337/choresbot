import time
from croniter import croniter
from datetime import datetime
from pytz import timezone


def parse_add_chore(message):
    ls = list(message.text.split('\n'))
    if croniter.is_valid(ls[3]):
        ls.append(ls[3])
        ls[3] = (croniter(ls[3], datetime.now(tz=timezone('Europe/Moscow')))).get_next()
    else:
        ls.append(None)
        ls[3] = convert_to_unix_time(ls[3])
    return ls[1:5]


def convert_to_unix_time(time_str):
    time_str = time_str.rstrip() + ' MSK'
    return time.mktime(time.strptime(time_str, '%d/%m/%Y %H:%M %Z'))

def read_message_text(name: str):
    with open(f'message_texts/{name}', 'r') as f:
        return f.read()
