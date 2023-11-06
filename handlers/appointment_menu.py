import traceback
from aiogram import Router, F
from aiogram import types
from datetime import datetime, timedelta

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove

from keyboards.for_appointment import time_picker, get_doctor_kb, start_calendar, kb_appt_state, kb_appt_approve, \
    get_kb_appt_cancel, get_kb_appt_cancel_approve
from libs.dictanotry_lib import to_ru_dayofweek, to_ru_month3
from libs.load_vars import update_appointments
from libs.notify import notify_on_appt
from libs.db_lib import pg_select, pg_execute, pg_select_one_column as pg_soc
from config_reader import config, myvars
from libs.google_ss import update_cell, google_get_vars

router = Router()


class AppointmentCustomer(StatesGroup):
    doctor = State()
    year = State()
    month = State()
    day = State()
    time = State()
    appt_state = State()
    car_plate = State()
    photo = State()


@router.message(F.text.lower() == "📝 записаться к врачу")
async def appt_start(message: types.Message):
    await message.delete()
    await message.answer("Выберите врача:", reply_markup=get_doctor_kb())


@router.callback_query(F.data.startswith("callback_select_doctor_"))
async def pick_doctor(callback: types.CallbackQuery, state: FSMContext):
    doctor = callback.data.split("_")[3]
    await state.update_data(doctor=doctor)
    await callback.message.delete()
    await callback.message.answer(f'Выберите дату', reply_markup=await start_calendar())
    await callback.answer("Успешно")


@router.callback_query(F.data.startswith("callback_calendar"))
async def pick_date(callback: types.CallbackQuery, state: FSMContext):
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
        await callback.message.edit_reply_markup(
            reply_markup=await start_calendar(year=int(prev_date.year), month=int(prev_date.month)))
    if action == 'NEXT-MONTH':
        next_date = temp_date + timedelta(days=31)
        await callback.message.edit_reply_markup(
            reply_markup=await start_calendar(year=int(next_date.year), month=int(next_date.month)))
    if action == "SELECTED":
        # myvars.picked_date = datetime(year=int(year), month=int(month), day=int(day))
        await state.update_data(picked_date=datetime(year=int(year), month=int(month), day=int(day)))
        await callback.message.delete()
        await callback.message.answer(f'Выберите время', reply_markup=await time_picker(state))
        # await callback.message.delete()
        await callback.answer("Успешно")
    if action == "BACK":
        await state.clear()
        await callback.message.delete()
        await callback.message.answer(f'Выберите врача', reply_markup=get_doctor_kb())
        await callback.answer('')
    if action == "IGNORE":
        await callback.answer('Выберите число')


@router.callback_query(F.data.startswith("time_picker"))
async def pick_time(callback: types.CallbackQuery, state: FSMContext):
    hour = callback.data.split("_")[2]
    await state.update_data(hour=hour)

    if hour == 'back':
        await callback.message.delete()
        await callback.message.answer(f'Выберите дату', reply_markup=await start_calendar())
    elif hour == 'pickdoctor':
        await state.clear()
        await callback.message.delete()
        await callback.message.answer(f'В начало', reply_markup=get_doctor_kb())
    else:
        await callback.message.delete()
        await callback.message.answer(f'Выберите вид консультации', reply_markup=kb_appt_state())

    await callback.answer('Успешно')


@router.callback_query(F.data.startswith("appt_state"))
async def pick_appt_state(callback: types.CallbackQuery, state: FSMContext):
    appt_state = callback.data.split("_")[2]
    await state.update_data(appt_state=appt_state)
    user_data = await state.get_data()

    await callback.message.delete()
    if appt_state == 'offline':
        await callback.message.answer(
            f'Введите номер автомобиля, если планируете заезжать на машине или отправьте <i>без машины</i>')
        await state.set_state(AppointmentCustomer.car_plate)
    if appt_state == 'online':
        # await callback.message.delete()
        await callback.message.answer(
            f'Подвердите запись\n\n' +
            f'Врач:       <b>{user_data["doctor"]}</b>\n' +
            f'Дата:       {user_data["day"]}.{user_data["month"]}.{user_data["year"]}\n' +
            f'Время:    {user_data["hour"]}.00 -- {user_data["hour"]}.40\n',
            reply_markup=await kb_appt_approve())
    if appt_state == 'back':
        # await callback.message.delete()
        await callback.message.answer(f'Выберите вид консультации',
                                      reply_markup=kb_appt_state())
    if appt_state == 'pickdoctor':
        # await callback.message.delete()
        await state.clear()
        await callback.message.answer(f'Выберите врача',
                                      reply_markup=get_doctor_kb())

    await callback.answer('Успешно')


@router.message(AppointmentCustomer.car_plate)
async def set_name(message: types.Message, state: FSMContext):
    await state.update_data(car_plate=message.text)
    user_data = await state.get_data()
    await message.answer('Подвердите запись\n\n' +
                         f'Врач:       <b>{user_data["doctor"]}</b>\n' +
                         f'Дата:       {user_data["day"]}.{user_data["month"]}.{user_data["year"]}\n' +
                         f'Время:    {user_data["hour"]}.00 -- {user_data["hour"]}.40\n' +
                         f'Номер:    {user_data["car_plate"]}\n',
                         reply_markup=await kb_appt_approve())


async def is_phonenumber(state: FSMContext):
    user_data = await state.get_data()
    if 'selected_user' in user_data.keys():
        if user_data["selected_user"] == int(user_data["search_user"][user_data["selected_user"]]["phonenumber"]):
            return True, True
        return True, False
    return False, False


@router.callback_query(F.data.startswith("appt_approve"))
async def appt_approve(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    action = callback.data.split("_")[2]
    if action == 'back':
        await callback.message.delete()
        await callback.message.answer(f'Выберите вид консультации',
                                      reply_markup=kb_appt_state())
    elif action == 'pickdoctor':
        await state.clear()
        await callback.message.delete()
        await callback.message.answer(f'Выберите врача',
                                      reply_markup=get_doctor_kb())
    elif action == 'approve':
        try:
            year = user_data['year']
            month = user_data['month']
            day = user_data['day']
            hour = user_data['hour']
            doctor = user_data['doctor']
            user_data['spreadsheet_id'] = myvars.doctors[doctor]['spreadsheet_id']
            # print(user_data)
            car_plate = None
            if 'car_plate' in user_data:
                if user_data['car_plate'].lower() != 'без машины':
                    car_plate = user_data['car_plate']
                else:
                    car_plate = 'Без машины'
            else:
                car_plate = 'online'
            appt_format = user_data['appt_state']
            appt_date = datetime(year=int(year), month=int(month), day=int(day), hour=int(hour), minute=0, second=0,
                                 microsecond=0)
            delta_hour = int(hour) - 10
            notify_date = appt_date - timedelta(days=1, hours=delta_hour)
            doctor_id = myvars.doctors[doctor]['tid']

            # print(f'tid: {callback.message.chat.id}')
            is_admin_mode, is_phone = await is_phonenumber(state)

            query = None
            value = None
            customer_fio = []

            if not is_phone:
                # tid = None
                if is_admin_mode:
                    tid = user_data['selected_user']
                else:
                    tid = callback.message.chat.id
                query = f"SELECT lastname, name, surname FROM tb_customers WHERE tid={tid}"
                rows = pg_select(query)

                for row in rows:
                    customer_fio.append(f'{row[0]} {row[1]} {row[2]}')

                if appt_format == 'online':
                    query = f"INSERT INTO tb_appointments (cid, doctor_id, appt_format, appt_date, notify_date) " \
                            f"SELECT id, {doctor_id}, '{appt_format}', '{appt_date}', '{notify_date}' " \
                            f"FROM tb_customers WHERE tid = {tid}"
                    value = f'{customer_fio[0]}\nФормат: {appt_format}'
                else:
                    query = f"INSERT INTO tb_appointments (cid, doctor_id, appt_format, description, appt_date, notify_date) " \
                            f"SELECT id, {doctor_id}, '{appt_format}', 'Номер: {car_plate}', '{appt_date}', '{notify_date}'" \
                            f"FROM tb_customers WHERE tid = {tid}"
                    value = f'{customer_fio[0]}\nФормат: {appt_format}\nНомер: {car_plate}'
            else:
                # phonenumber = user_data[user_data['selected_user']]["phonenumber"]
                phonenumber = user_data["selected_user"]

                query = f"SELECT lastname, name, surname FROM tb_customers WHERE phonenumber='{phonenumber}'"
                rows = pg_select(query)

                for row in rows:
                    customer_fio.append(f'{row[0]} {row[1]} {row[2]}')

                if appt_format == 'online':
                    query = f"INSERT INTO tb_appointments (cid, doctor_id, appt_format, appt_date, notify_date) " \
                            f"SELECT id, {doctor_id}, '{appt_format}', '{appt_date}', '{notify_date}' " \
                            f"FROM tb_customers WHERE phonenumber = '{phonenumber}'"
                    value = f'{customer_fio[0]}\nФормат: {appt_format}'
                else:
                    query = f"INSERT INTO tb_appointments (cid, doctor_id, appt_format, description, appt_date, notify_date) " \
                            f"SELECT id, {doctor_id}, '{appt_format}', 'Номер: {car_plate}', '{appt_date}', '{notify_date}'" \
                            f"FROM tb_customers WHERE phonenumber = '{phonenumber}'"
                    value = f'{customer_fio[0]}\nФормат: {appt_format}\nНомер: {car_plate}'

            # print(f'appt_men:222: {query}')
            pg_execute(query)
            # print(f'query: {query}')
            # print(f'month: {month}')
            # print(f"appt_close_approve user_data: {user_data}")
            service, sheets, title = await google_get_vars(user_data, callback)
            await update_cell(myvars.doctors[doctor]['spreadsheet_id'], int(hour), int(month), int(year), int(day),
                              value, service, sheets, title)
            await update_appointments()

            await notify_on_appt(
                callback=callback,
                year=int(year),
                month=int(month),
                day=int(day),
                hour=int(hour),
                car_plate=car_plate,
                doctor=doctor,
                customer_fio=customer_fio[0],
                appt_format=appt_format
            )
            await callback.message.delete()
            await state.clear()
            await callback.message.answer('Вы успешно записаны')
        except Exception as e:
            text = f'[{str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}] [Ошибка записи]\nmessage.id: {callback.message.message_id}\ntid: {callback.message.chat.id}\n{traceback.format_exc()}'
            print(text)
            print(f'myerror: {str(e)}')
            await callback.message.delete()
            await state.clear()
            if 'duplicate key value violates unique constraint' in str(e):
                await callback.message.answer('Кто-то уже занял это время. Попробуйте выбрать другое.',
                                              reply_markup=get_doctor_kb())
            else:
                await callback.message.bot.send_message(chat_id=config.maezztro_tid, text=text)
                await callback.message.answer(
                    'Ой, что-то пошло не так, но мы уже работаем над исправлением. Приносим свои извинения. Попробуйте позже. ')

    await callback.answer('Успешно')


@router.message(F.text.lower() == "🗒 записи")
async def appt_close(message: types.Message, state: FSMContext):
    is_admin_mode, is_phone = await is_phonenumber(state)
    user_data = await state.get_data()
    query = None
    if not is_phone:
        tid = None
        if is_admin_mode:
            tid = user_data['selected_user']
        else:
            tid = message.from_user.id
        await state.update_data(user_tid=tid)

        query = f"SELECT count(ap.id) " \
                f"FROM tb_appointments as ap " \
                f"LEFT JOIN tb_customers as cu " \
                f"ON ap.cid = cu.id " \
                f"WHERE tid={tid} and appt_date > CURRENT_TIMESTAMP"
    else:
        phonenumber = user_data['selected_user']
        query = f"SELECT count(ap.id) " \
                f"FROM tb_appointments as ap " \
                f"LEFT JOIN tb_customers as cu " \
                f"ON ap.cid = cu.id " \
                f"WHERE phonenumber='{phonenumber}' and appt_date > CURRENT_TIMESTAMP"

    await message.delete()
    count = int(pg_soc(query)[0])

    if count == 0:
        await message.answer("Записей нет")
    else:
        # await message.answer("Выберите врача:", reply_markup=ReplyKeyboardRemove())
        await message.answer("Выберите запись:", reply_markup=await get_kb_appt_cancel(state))


async def get_user_data(callback: types.CallbackQuery, state: FSMContext):
    year = callback.data.split("_")[3]
    month = callback.data.split("_")[4]
    day = callback.data.split("_")[5]
    hour = callback.data.split("_")[6]

    appt_date = datetime(year=int(year), month=int(month), day=int(day), hour=int(hour))

    query = f"SELECT spreadsheet_id FROM tb_customers AS cu " \
            f"LEFT JOIN tb_appointments AS ap " \
            f"ON ap.doctor_id = cu.tid " \
            f"WHERE appt_date = '{appt_date}'::timestamp"

    spreadsheet_id = pg_soc(query)[0]

    await state.update_data(year=year)
    await state.update_data(month=month)
    await state.update_data(day=day)
    await state.update_data(hour=hour)
    await state.update_data(appt_date=appt_date)
    await state.update_data(spreadsheet_id=spreadsheet_id)
    user_data = await state.get_data()
    return user_data


@router.callback_query(F.data.startswith("callback_appt_close_"))
async def pick_doctor(callback: types.CallbackQuery, state: FSMContext):
    user_data = await get_user_data(callback, state)

    await callback.message.delete()
    text = f"<b>{to_ru_dayofweek[user_data['appt_date'].weekday()]}</b>\n" \
           "━━━━━━━━━━━━━━━\n" \
           f"<b>{user_data['day']} {to_ru_month3[int(user_data['month'])]} {user_data['year']} {user_data['hour']}:00:00</b>\n"
    await callback.message.answer(text=text, reply_markup=await get_kb_appt_cancel_approve())
    await callback.answer("Успешно")


@router.callback_query(F.data == "cb_appt_close_menu")
async def appt_close_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(user_tid=callback.message.chat.id)
    await callback.message.delete()
    await callback.message.answer("Выберите запись:", reply_markup=await get_kb_appt_cancel(state))
    await state.clear()
    await callback.answer("")


@router.callback_query(F.data == "cb_appt_close_approve")
async def appt_close_approve(callback: types.CallbackQuery, state: FSMContext):
    try:
        user_data = await state.get_data()
        appt_date = datetime(year=int(user_data['year']),
                             month=int(user_data['month']),
                             day=int(user_data['day']),
                             hour=int(user_data['hour']))

        if 'phonenumber' in user_data.keys():

            query = f"DELETE FROM tb_appointments " \
                    f"WHERE appt_date = '{appt_date}'::timestamp and " \
                    f"cid=(SELECT id FROM tb_customers WHERE phonenumber={user_data['phonenumber']})"
        else:
            query = f"DELETE FROM tb_appointments " \
                    f"WHERE appt_date='{appt_date}'::timestamp and " \
                    f"cid=(SELECT id FROM tb_customers WHERE tid={user_data['user_tid']})"
        # print(query)
        pg_execute(query)

        value = "appt_cancel"
        # print(f"appt_close_approve user_data: {user_data}")

        service, sheets, title = await google_get_vars(user_data, callback)
        await update_cell(user_data['spreadsheet_id'],
                          int(user_data['hour']),
                          int(user_data['month']),
                          int(user_data['year']),
                          int(user_data['day']),
                          value,
                          service, sheets, title)

        await update_appointments()
        await callback.message.delete()
        # await message.answer("Выберите врача:", reply_markup=ReplyKeyboardRemove())
        await callback.message.answer("Запись отменена")
        await state.clear()
        await callback.answer("Успешно")
    except Exception as e:
        print(f"Exception: {e}\nTraceback: {traceback.format_exc()}")
        await callback.message.delete()
        await callback.message.answer("Попробуйте ещё раз /start")


@router.message(F.text.lower() == "➕ добавить историю болезни(файлы)")
async def appt_add_files(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer("Бот ожидает приём файлов", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AppointmentCustomer.photo)
