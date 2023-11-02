from aiogram import Router, F
from aiogram import types
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta

from config_reader import myvars, DEBUG
from keyboards.for_doctor import run_calendar, get_kb_doctor_menu, get_kb_doctor_selected_day
from libs.db_lib import pg_select_one_column as pg_soc, pg_execute, pg_select
from libs.dictanotry_lib import to_ru_dayofweek, to_ru_month3
from libs.google_ss import update_cell
from libs.load_vars import update_appointments

router = Router()


async def get_user_data(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    user_data['doctor_id'] = callback.message.chat.id
    user_data['appt_format'] = 'closed'
    user_data['hours'] = [10, 11, 12, 13, 14, 15, 16]
    for key in myvars.doctors.keys():
        if myvars.doctors[key]['id'] == callback.message.chat.id:
            user_data['doctor'] = key
    return user_data


@router.callback_query(F.data == "cb_doctor_workday_appt")
async def doctor_workday_appt(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("Выбор дня:", reply_markup=await run_calendar())
    await callback.answer("")


@router.callback_query(F.data.startswith("callback_doctor_calendar"))
async def pick_doctor_date(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split(":")[1]
    year = callback.data.split(":")[2]
    month = callback.data.split(":")[3]
    day = callback.data.split(":")[4]

    await state.update_data(year=year)
    await state.update_data(month=month)
    await state.update_data(day=day)

    # return_data = (False, None)
    temp_date = datetime(int(year), int(month), 1)
    if action == 'PREV-MONTH':
        prev_date = temp_date - timedelta(days=31)
        await callback.message.edit_reply_markup(reply_markup=await run_calendar(year=int(prev_date.year), month=int(prev_date.month)))
    if action == 'NEXT-MONTH':
        next_date = temp_date + timedelta(days=31)
        await callback.message.edit_reply_markup(reply_markup=await run_calendar(year=int(next_date.year), month=int(next_date.month)))
    if action == "SELECTED":
        # myvars.picked_date = datetime(year=int(year), month=int(month), day=int(day))
        query = f"SELECT id FROM tb_appointments WHERE date(appt_date) = date('{year}-{month}-{day}') and is_closed = 1"
        res = pg_soc(query)
        status_apt = ''
        if len(res) > 0:
            status_apt = 'закрыта'
        else:
            status_apt = 'открыта'
        day_of_week = to_ru_dayofweek[datetime(year=int(year), month=int(month), day=int(day)).weekday()]
        text = f'<b> {day_of_week}</b>\n' + \
            f'<b>{day} {to_ru_month3[int(month)]} {year}</b>\n' + \
            '━━━━━━━━━━━━━━━\n' + \
            f'Запись: <u>{status_apt}</u>'
        await callback.message.delete()
        await callback.message.answer(text=text, reply_markup=await get_kb_doctor_selected_day())
        await callback.answer("Успешно")
    if action == "BACK":
        await state.clear()
        await callback.message.delete()
        await callback.message.answer(f'Выберите врача', reply_markup=await get_kb_doctor_menu(state))
        await callback.answer('')
    if action == "IGNORE":
        await callback.answer('Выберите число')


@router.callback_query(F.data.startswith("cb_doctor_close_appt_exec"))
async def doctor_close_appt(callback: types.CallbackQuery, state: FSMContext):
    user_data = await get_user_data(callback, state)

    for hour in user_data['hours']:
        appt_date = datetime(year=int(user_data['year']), month=int(user_data['month']), day=int(user_data['day']), hour=hour)

        # Проверка существует ли запись на этот день и время
        query = f"SELECT EXISTS (SELECT tid FROM tb_appointments WHERE appt_date = '{appt_date}'::timestamp)"
        res = pg_soc(query)[0]
        if res:
            query = f"UPDATE tb_appointments SET is_closed = 1 WHERE appt_date = '{appt_date}'::timestamp"
            pg_execute(query)
        else:
            query = f"INSERT INTO tb_appointments (is_closed, tid, doctor_id, appt_format, appt_date) " + \
                    f"VALUES (1, {int(user_data['doctor_id'])}, {int(user_data['doctor_id'])}, '{user_data['appt_format']}', '{appt_date}')"
            pg_execute(query)

        await callback.answer('БД обновлена. Обновляется Google таблица')

        if DEBUG == 0:
            await update_cell(myvars.doctors[user_data['doctor']]['spreadsheet_id'], int(hour),
                              int(user_data['month']), int(user_data['year']),
                              int(user_data['day']), user_data['appt_format'], callback)
        else:
            await update_cell(myvars.doctors['Соболевский В.А.']['spreadsheet_id'], int(hour),
                              int(user_data['month']), int(user_data['year']),
                              int(user_data['day']), user_data['appt_format'], callback)

    await update_appointments()
    await callback.message.delete()
    await callback.answer('Успешно')


@router.callback_query(F.data.startswith("cb_doctor_open_appt_exec"))
async def doctor_open_appt(callback: types.CallbackQuery, state: FSMContext):
    user_data = await get_user_data(callback, state)

    for hour in user_data['hours']:
        appt_date = datetime(year=int(user_data['year']), month=int(user_data['month']), day=int(user_data['day']),
                             hour=hour)

        # Проверка существует ли запись на этот день и время от пациента
        query = f"SELECT EXISTS (SELECT tid FROM tb_appointments WHERE appt_date = '{appt_date}'::timestamp and doctor_id != tid)"
        res = pg_soc(query)[0]
        value = None
        if res:
            query = "SELECT lastname, name, surname, appt_format FROM tb_customers as cu " \
                    "LEFT JOIN tb_appointments as ap ON cu.tid = ap.tid " \
                    f"WHERE (appt_date = '{appt_date}'::timestamp)"
            rows = pg_select(query)
            for row in rows:
                value = f"openedФИО: {row[0]} {row[1]} {row[2]}\n Формат: {row[3]}"
            query = f"UPDATE tb_appointments SET is_closed = 0 WHERE appt_date = '{appt_date}'::timestamp and doctor_id != tid"
            pg_execute(query)
        else:
            value = "opened"
            query = f"DELETE FROM tb_appointments " \
                    f"WHERE appt_date = '{appt_date}'::timestamp and is_closed=1"
            pg_execute(query)

        await callback.answer('БД обновлена. Обновляется Google таблица')
        if DEBUG == 1:
            await update_cell(myvars.doctors['Соболевский В.А.']['spreadsheet_id'], int(hour),
                              int(user_data['month']), int(user_data['year']),
                              int(user_data['day']), value, callback)
        else:
            await update_cell(myvars.doctors[user_data['doctor']]['spreadsheet_id'], int(hour),
                              int(user_data['month']), int(user_data['year']),
                              int(user_data['day']), value, callback)

    await update_appointments()
    await callback.message.delete()
    await callback.answer('Успешно')
