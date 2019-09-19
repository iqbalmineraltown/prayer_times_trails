import os
import re
import json
import requests
from datetime import datetime, timedelta, date, time

cityname = 'jakarta'
jsonurl = f'http://muslimsalat.com/{cityname}.json'
username = 'Haji Oval'
emojicon = ':kaaba:'
webhookurl = 'https://hooks.slack.com/services/<secret>'

advminutes = 10
start_message = f'Hai, {username} akan membantu mengingatkan jadwal sholat sekitar {advminutes} menit sebelum waktu adzan berkumandang.\nBerikut jadwal sholat untuk {cityname} hari ini:\n'


def slack_sender(name: str, time: datetime):
    message = f'Sholat {name} sekitar {advminutes} menit lagi'
    time_str = time.strftime('%H:%M')
    payloaddict = {
        'username': username,
        'text': message,
        'icon_emoji': emojicon
    }
    json_dump = json.dumps(payloaddict)

    command = f'curl -X POST {webhookurl} -d \'{json_dump}\''
    f = open(f'{name}.sh', 'w+')
    f.write(command)
    f.close()
    os.system(f'chmod +x {name}.sh')

    print(time_str)
    os.system(f'at -f {name}.sh {time_str}')
    pass


def convert_prayer_name(name: str) -> str:

    if name == 'fajr':
        name = 'Subuh'
    elif name == 'dhuhr':
        name = 'Zuhur'
    elif name == 'asr':
        name = 'Ashar'
    elif name == 'isha':
        name = 'Isya'
    else:
        name = name.title()

    return name
    pass


def reminder_prayertime(name: str, time: str):
    time_sched = substract_10_mins(time)
    today = datetime.today()
    today_date = datetime(today.year, today.month, today.day,
                          time_sched.hour, time_sched.minute)

    name = convert_prayer_name(name)
    time_prayer = time_sched.strftime('%H:%M')
    global start_message
    start_message += f'{name} {time_prayer}\n'

    slack_sender(name, today_date)
    pass


def fetch_prayertimes():
    os.system('for i in `atq | awk \'{print $1}\'`;do atrm $i;done')

    resjson = json.loads(requests.get(jsonurl).text)

    for key, val in resjson['items'][0].items():
        if not (key == 'date_for' or key == 'shurooq'):
            reminder_prayertime(key, val)

    global start_message
    payloaddict = {
        'username': username,
        'text': start_message,
        'icon_emoji': emojicon
    }
    json_dump = json.dumps(payloaddict)

    os.system(f'curl -X POST {webhookurl} -d \'{json_dump}\'')

    pass


def substract_10_mins(time_str: str) -> time:
    datetime_obj = datetime.strptime(time_str, '%I:%M %p')
    datetime_obj -= timedelta(minutes=advminutes)

    return datetime_obj
    pass


fetch_prayertimes()
