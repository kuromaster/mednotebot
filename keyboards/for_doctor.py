import calendar

from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from datetime import datetime, timedelta

from config_reader import myvars
from libs.dictanotry_lib import to_ru_month


async def get_kb_doctor_menu(state: FSMContext) -> InlineKeyboardMarkup:
    user_data = await state.get_data()
    spreadsheet_id = None

    if user_data['user_tid'] in myvars.superuser:
        spreadsheet_id = myvars.doctors[user_data['doctor']]['spreadsheet_id']
    else:
        for doctor in myvars.doctors.keys():
            if myvars.doctors[doctor]['tid'] == user_data['user_tid']:
                spreadsheet_id = myvars.doctors[doctor]['spreadsheet_id']

    kb = InlineKeyboardBuilder()
    kb.button(text='График приёма(google)', url=f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/")
    kb.button(text='Приёмные дни', callback_data='cb_doctor_workday_appt')
    kb.button(text='Пациенты', callback_data='cb_doctor_patients')
    if user_data['user_tid'] in myvars.superuser:
        await state.update_data(role='doctor')
        await state.update_data(selected_user=myvars.doctors[user_data['doctor']]['tid'])
        kb.button(text='Удалить роль', callback_data='cb_su_rm_user_role')
        kb.button(text='Назад', callback_data='cb_superuser_mainmenu')
    kb.button(text='Скрыть меню', callback_data='cb_superuser_remove_menu')

    kb.adjust(1)
    return kb.as_markup()


class CalendarCallbackDoctor(CallbackData, prefix="callback_doctor_calendar"):
    action: str
    year: int
    month: int
    day: int


async def run_calendar(
        year: int = datetime.now().year,
        month: int = datetime.now().month
) -> InlineKeyboardMarkup:

    curday_id = 0
    border_id = 0
    i = 0

    now = datetime.now()
    border_dt = now + timedelta(days=31)

    curday = now.day
    curmonth = now.month
    kb_calendar = InlineKeyboardBuilder()
    ignore_callback = CalendarCallbackDoctor(action="IGNORE", year=year, month=month, day=0)

    # First row - Month and Year
    if curmonth != month:
        kb_calendar.button(
            text="⬅",
            callback_data=CalendarCallbackDoctor(action="PREV-MONTH", year=year, month=month, day=1)
        )
    kb_calendar.button(
        text=f'{to_ru_month[calendar.month_name[month]]} {str(year)}',
        callback_data=ignore_callback
    )
    if curmonth == month:
        if border_dt.month != curmonth:
            kb_calendar.button(
                text="➡",
                callback_data=CalendarCallbackDoctor(action="NEXT-MONTH", year=year, month=month, day=1)
            )
    kb_calendar.adjust(5)

    # Second row - Week Days
    btns_day = []
    # for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]:
    for day in ["Пн", "Вт", "Ср", "Чт", "Пт"]:
        btns_day.append(types.InlineKeyboardButton(text=day, callback_data=ignore_callback.pack()))

    kb_calendar.row(*btns_day, width=5)
    # Calendar rows - Days of month
    month_calendar2 = calendar.monthcalendar(year, month)
    btns_week = []
    for week2 in month_calendar2:
        counter = 0
        for day in week2:
            if day == curday:
                curday_id = i
            if day == border_dt.day:
                border_id = i
            if counter in (5, 6):
                counter += 1
                continue
            if curmonth == month:
                if day == 0 or day < curday:
                    btns_week.append(types.InlineKeyboardButton(text=' ', callback_data=ignore_callback.pack()))
                    counter += 1
                    i += 1
                    continue
                if curmonth == border_dt.month:
                    if day > border_dt.day:
                        btns_week.append(types.InlineKeyboardButton(text=' ', callback_data=ignore_callback.pack()))
                        counter += 1
                        i += 1
                        continue
            if curmonth != month:
                if day == 0 or day > border_dt.day:
                    btns_week.append(types.InlineKeyboardButton(text=' ', callback_data=ignore_callback.pack()))
                    counter += 1
                    i += 1
                    continue

            btns_week.append(types.InlineKeyboardButton(
                text=f'{str(day)}',
                callback_data=CalendarCallbackDoctor(action="SELECTED", year=year, month=month, day=day).pack()
            ))

            i += 1
            counter += 1

    c = None

    # Обрезание пустых строк с кнопками
    if curmonth == month:
        for i in range(4, len(btns_week)-1, 5):
            if btns_week[i].text == ' ' and i < curday_id:
                c = i + 1

    if curmonth != month:
        for i in range(len(btns_week)-1, -1, -5):

            if btns_week[i].text == ' ' and i >= border_id:
                c = i+1

    if c is not None and curmonth == month:
        btns_week = btns_week[c:]
    if c is not None and curmonth != month:
        btns_week = btns_week[:c]

    kb_calendar.row(*btns_week, width=5)

    # Last row - Buttons
    btns_pag = [
        types.InlineKeyboardButton(
            text="Назад", callback_data=CalendarCallbackDoctor(action="BACK", year=year, month=month, day=day).pack()
        )
        # types.InlineKeyboardButton(
        #     text="В начало", callback_data=CalendarCallback(action="PICK-DOCTOR", year=year, month=month, day=day).pack()
        # )
    ]
    kb_calendar.row(*btns_pag, width=1)

    return kb_calendar.as_markup()


async def get_kb_doctor_selected_day(state: FSMContext):
    user_data = await state.get_data()

    kb = InlineKeyboardBuilder()
    kb.button(text='Закрыть приём', callback_data='cb_doctor_close_appt_exec')
    kb.button(text='Открыть прием', callback_data='cb_doctor_open_appt_exec')
    kb.button(text='Назад', callback_data='cb_doctor_workday_appt')
    if user_data['user_tid'] in myvars.superuser:
        kb.button(text='Главное меню', callback_data='cb_superuser_mainmenu')
    else:
        kb.button(text='Главное меню', callback_data='callback_doctor_calendar:BACK:2023:1:1')

    kb.button(text='Скрыть меню', callback_data='cb_superuser_remove_menu')

    kb.adjust(1)
    return kb.as_markup()


async def get_kb_doctor_search_user_result(state: FSMContext):
    user_data = await state.get_data()
    kb = InlineKeyboardBuilder()

    for user in user_data['search_user'].keys():
        text = f"[{user}] {user_data['search_user'][user]['lastname']} {user_data['search_user'][user]['name']} {user_data['search_user'][user]['surname']}"
        kb.add(
            types.InlineKeyboardButton(text=text, callback_data=f"cb_doctor_search_user_result_{user_data['role']}_{user}"))

    kb.button(text='Назад', callback_data='callback_doctor_calendar:BACK:2023:1:1')
    kb.button(text='Скрыть меню', callback_data='cb_superuser_remove_menu')

    kb.adjust(1)
    return kb.as_markup()


async def get_kb_doctor_selected_patient() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.button(text='Загрузить историю болезни(файлы)', callback_data='cb_doctor_get_patient_files')
    kb.button(text='Главное меню', callback_data='callback_doctor_calendar:BACK:2023:1:1')
    kb.button(text='Скрыть меню', callback_data='cb_superuser_remove_menu')

    kb.adjust(1)
    return kb.as_markup()