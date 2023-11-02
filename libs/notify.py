import calendar
from aiogram import types
from aiogram.utils.markdown import hlink

from config_reader import config, myvars, DEBUG
from libs.dictanotry_lib import to_ru_month2


async def notify_on_appt(year: int, month: int, day: int, doctor: str, hour: int, callback: types.CallbackQuery, customer_fio: str, appt_format: str, car_plate: str = None):
    # t = datetime(year=year, month=month, day=day, hour=hour, minute=0)
    # query = ''
    # pg_execute(query)
    # locale.setlocale(locale.LC_ALL, ('ru_RU', 'UTF-8'))
    url = f"https://docs.google.com/spreadsheets/d/{myvars.doctors[doctor]['spreadsheet_id']}"
    text = f'{hlink(title="[Новая запись]", url=url)}\n' + \
        '━━━━━━━━━━━━━━━\n' + \
        f'<b>Время</b>: {day} {to_ru_month2[calendar.month_name[month]]} {year} -- {hour}:00:00\n' + \
        f'<b>Врач:</b> <u>{doctor}</u>\n' +\
        f'<b>Формат</b>: {appt_format}\n' + \
        f'<b>Пациент:</b> {customer_fio}\n'
    if car_plate != 'online':
        text += f'<b>Номер машины:</b> {car_plate}'
    if DEBUG == 1:
        chat_id = config.maezztro_tid
    else:
        chat_id = int(myvars.doctors[doctor]['id']),
    await callback.message.bot.send_message(
        chat_id=chat_id,
        text=text
    )
