import traceback

from aiogram import Router, F
from aiogram import types
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta

from config_reader import myvars, DEBUG
from filters.permission import check_permission
from handlers.superuser_menu import InputData
from keyboards.for_doctor import run_calendar, get_kb_doctor_menu, get_kb_doctor_selected_day, \
    get_kb_doctor_selected_patient
from libs.db_lib import pg_select_one_column as pg_soc, pg_execute, pg_select
from libs.dictanotry_lib import to_ru_dayofweek, to_ru_month3
from libs.google_ss import update_cell, google_get_vars
from libs.load_vars import update_appointments
from main import logger


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
    await state.update_data(user_tid=callback.from_user.id)

    temp_date = datetime(int(year), int(month), 1)
    if action == 'PREV-MONTH':
        prev_date = temp_date - timedelta(days=31)
        await callback.message.edit_reply_markup(reply_markup=await run_calendar(year=int(prev_date.year), month=int(prev_date.month)))
    if action == 'NEXT-MONTH':
        next_date = temp_date + timedelta(days=31)
        await callback.message.edit_reply_markup(reply_markup=await run_calendar(year=int(next_date.year), month=int(next_date.month)))
    if action == "SELECTED":
        query = f"SELECT id FROM tb_appointments WHERE date(appt_date) = date('{year}-{month}-{day}') and is_closed = 1"
        res = pg_soc(query)
        # status_apt = ''
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
        await callback.message.answer(text=text, reply_markup=await get_kb_doctor_selected_day(state))
        await callback.answer("Успешно")
    if action == "BACK":
        await callback.message.delete()
        await callback.message.answer(f'Меню', reply_markup=await get_kb_doctor_menu(state))
        await state.clear()
        await callback.answer('')
    if action == "IGNORE":
        await callback.answer('Выберите число')


@router.callback_query(F.data.startswith("cb_doctor_close_appt_exec"))
async def doctor_close_appt(callback: types.CallbackQuery, state: FSMContext):
    user_data = await get_user_data(callback, state)

    try:
        user_data['spreadsheet_id'] = myvars.doctors[user_data['doctor']]['spreadsheet_id']
        service, sheets, title = await google_get_vars(user_data, callback)

        for hour in user_data['hours']:
            appt_date = datetime(year=int(user_data['year']), month=int(user_data['month']), day=int(user_data['day']), hour=hour)

            # Проверка существует ли запись на этот день и время
            query = f"SELECT EXISTS (SELECT cid FROM tb_appointments WHERE appt_date = '{appt_date}'::timestamp)"
            res = pg_soc(query)[0]
            if res:
                query = f"UPDATE tb_appointments SET is_closed = 1 WHERE appt_date = '{appt_date}'::timestamp"
                pg_execute(query)
            else:
                query = f"INSERT INTO tb_appointments (is_closed, cid, doctor_id, appt_format, appt_date) " + \
                        f"SELECT 1, id, {int(user_data['doctor_id'])}, '{user_data['appt_format']}', '{appt_date}' " \
                        f"FROM tb_customers WHERE tid = {int(user_data['doctor_id'])}"
                pg_execute(query)

            await callback.answer('БД обновлена. Обновляется Google таблица', cache_time=35)

            if DEBUG == 0:
                await update_cell(myvars.doctors[user_data['doctor']]['spreadsheet_id'], int(hour),
                                  int(user_data['month']), int(user_data['year']),
                                  int(user_data['day']), user_data['appt_format'], service, sheets, title)
            else:
                await update_cell(myvars.doctors['Соболевский В.А.']['spreadsheet_id'], int(hour),
                                  int(user_data['month']), int(user_data['year']),
                                  int(user_data['day']), user_data['appt_format'], service, sheets, title)

        await update_appointments()
        await callback.message.delete()
        # await callback.answer('Успешно')

    except Exception as e:
        logger.error(f"exception: {e} traceback: {traceback.format_exc()}")


@router.callback_query(F.data.startswith("cb_doctor_open_appt_exec"))
async def doctor_open_appt(callback: types.CallbackQuery, state: FSMContext):
    user_data = await get_user_data(callback, state)

    try:
        user_data['spreadsheet_id'] = myvars.doctors[user_data['doctor']]['spreadsheet_id']
        service, sheets, title = await google_get_vars(user_data, callback)

        for hour in user_data['hours']:
            appt_date = datetime(year=int(user_data['year']), month=int(user_data['month']), day=int(user_data['day']),
                                 hour=hour)

            # Проверка существует ли запись на этот день и время от пациента
            query = f"SELECT EXISTS (SELECT cid FROM tb_appointments " \
                    f"WHERE appt_date = '{appt_date}'::timestamp and " \
                    f"cid  != (SELECT id FROM tb_customers WHERE tid = doctor_id))"
            print(query)
            res = pg_soc(query)[0]
            value = None
            if res:
                query = "SELECT lastname, name, surname, appt_format FROM tb_customers as cu " \
                        "LEFT JOIN tb_appointments as ap ON cu.id = ap.cid " \
                        f"WHERE (appt_date = '{appt_date}'::timestamp)"
                rows = pg_select(query)
                for row in rows:
                    value = f"openedФИО: {row[0]} {row[1]} {row[2]}\n Формат: {row[3]}"
                query = f"UPDATE tb_appointments SET is_closed = 0 " \
                        f"WHERE appt_date = '{appt_date}'::timestamp and " \
                        f"cid  != (SELECT id FROM tb_customers WHERE tid = doctor_id)"
                pg_execute(query)
            else:
                value = "opened"
                query = f"DELETE FROM tb_appointments " \
                        f"WHERE appt_date = '{appt_date}'::timestamp and is_closed=1"
                pg_execute(query)

            await callback.answer('БД обновлена. Обновляется Google таблица', cache_time=35)
            if DEBUG == 1:
                await update_cell(myvars.doctors['Соболевский В.А.']['spreadsheet_id'], int(hour),
                                  int(user_data['month']), int(user_data['year']),
                                  int(user_data['day']),
                                  value, service, sheets, title)
            else:
                await update_cell(myvars.doctors[user_data['doctor']]['spreadsheet_id'], int(hour),
                                  int(user_data['month']), int(user_data['year']),
                                  int(user_data['day']), value, service, sheets, title)

        await update_appointments()
        await callback.message.delete()
        # await callback.answer('Успешно')

    except Exception as e:
        logger.error(f"exception: {e} traceback: {traceback.format_exc()}")


@router.callback_query(F.data == "cb_doctor_patients")
async def set_doctor(callback: types.CallbackQuery, state: FSMContext):
    is_superuser = await check_permission(myvars.superuser, callback=callback)
    is_doctor = await check_permission(myvars.doctors, callback=callback)

    if is_superuser or is_doctor:
        await state.update_data(role="patient")
        await callback.message.delete()
        await callback.message.answer("Введите фамилию или её часть для поиска:")
        await callback.answer("")
        await state.set_state(InputData.lastname)
    else:
        await callback.message.delete()
        await callback.answer("")


@router.callback_query(F.data.startswith("cb_doctor_search_user_result_"))
async def manage_seleted_patient(callback: types.CallbackQuery, state: FSMContext):
    is_superuser = await check_permission(myvars.superuser, callback=callback)
    is_doctor = await check_permission(myvars.doctors, callback=callback)
    if is_superuser or is_doctor:
        role = callback.data.split("_")[5]
        tid = int(callback.data.split("_")[6])
        await state.update_data(selected_user=tid)
        user_data = await state.get_data()

        await callback.message.delete()
        text = f"<b>Пациент</b>\n" \
               f"━━━━━━━━━━━━━━━\n" \
               f"<b>{[tid]} {user_data['search_user'][tid]['lastname']} " \
               f"{user_data['search_user'][tid]['name']} {user_data['search_user'][tid]['surname']}</b>"

        await callback.message.answer(text=text, reply_markup=await get_kb_doctor_selected_patient())
        await callback.answer("")
    else:
        await callback.message.delete()
        await callback.answer("")


@router.callback_query(F.data == "cb_doctor_get_patient_files")
async def set_doctor(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    tid = user_data['selected_user']

    # media_group_photo = []
    # media_group_doc = []
    query = f"SELECT file_id, file_type " \
            f"FROM tb_files as f " \
            f"LEFT JOIN tb_customers as cu " \
            f"ON cu.id = f.cid " \
            f"WHERE cu.tid={tid} " \
            f"ORDER BY created DESC"
    print(query)
    rows = pg_select(query)
    for row in rows:
        if row[1] == 'photo':
            # media_group_photo.append(InputMediaPhoto(media=row[0]))
            # await callback.message.answer_media_group(media_group)
            await callback.message.answer_photo(photo=row[0])
        elif row[1] == 'document':
            # media_group_doc.append(InputMediaDocument(media=row[0]))
            await callback.message.answer_document(document=row[0])
        elif row[1] == 'audio':
            await  callback

    # await callback.message.answer_media_group(media_group_photo)
    # await callback.message.answer_media_group(media_group_doc)
    # await callback.message.do answer_media_group(media_group_doc)
    await callback.message.answer("Загрузка завершена")
    await callback.answer("Успешно")