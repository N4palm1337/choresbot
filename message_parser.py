import time, string


def parse_add_chore(message):
    ls = list(message.text.split('\n'))
    # todo
    # should return a list of 2 args:
    # desc -> string, self-explanatory
    # time -> integer, unix format in nanoseconds
    ls[3] = convert_to_unix_time(ls[3])
    return ls[1:4]


def convert_to_unix_time(time_str):
    time_struct = time.strptime(time_str, '%d/%m/%Y %H:%M')
    return int(time.mktime(time_struct) * 1000)