from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram import types
from config_reader import myvars
from datetime import datetime, timedelta
import calendar

from aiogram.filters.callback_data import CallbackData

from libs.dictanotry_lib import to_ru_month

# picked_date = None


def get_appointment_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Записаться к врачу")
    kb.button(text="Отменить запись")
    kb.button(text="Добавить историю болезни(файлы)")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def get_doctor_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    # kb.button()
    # print(f'doctor keys: {myvars.doctors.keys()}')
    for doctor in myvars.doctors.keys():
        kb.add(types.InlineKeyboardButton(text=doctor, callback_data=f"callback_select_doctor_{doctor}"))

    kb.adjust(1)
    return kb.as_markup()


class CalendarCallback(CallbackData, prefix="callback_calendar"):
    action: str
    # ddate: Optional[str]
    year: int
    month: int
    day: int


# def start_calendar(
#     year: int = datetime.now().year,
#     month: int = datetime.now().month
# ) -> InlineKeyboardMarkup:
#     ikb = InlineKeyboardBuilder()
#     ignore_callback = CalendarCallback(action="IGNORE", year=year, month=month, day=0)
#     btn1 = types.InlineKeyboardButton(text="test1", callback_data=ignore_callback.pack())
#     btn2 = types.InlineKeyboardButton(text="test2", callback_data="test")
#     btn3 = types.InlineKeyboardButton(text="test3", callback_data="test")
#     btn4 = types.InlineKeyboardButton(text='4', callback_data='3')
#     btn5 = types.InlineKeyboardButton(text='5', callback_data='3')
#     btn6 = types.InlineKeyboardButton(text='6', callback_data='3')
#     btn7 = types.InlineKeyboardButton(text='7', callback_data='3')
#     for num in range(1, 10):
#         ikb.button(text=str(num), callback_data=ignore_callback)
#     ikb.adjust(7)
#     btns_row = [btn1, btn2, btn3, btn4, btn5]
#     ikb.row(*btns_row, width=3)
#
#     return ikb.as_markup()

async def check_appt_day(year:int, month: int, day: int):
    check_date = datetime(year=year, month=month, day=day)
    i = 0
    for key in myvars.appointments.keys():
        # print(f'{year}-{month}-{day}  ----  {key.date()}')
        # print(f'{check_date}  ----  {key.date()}')
        if check_date.date() == key.date():
            i += 1
    # print(i)
    return i


async def start_calendar(
        year: int = datetime.now().year,
        month: int = datetime.now().month
) -> InlineKeyboardMarkup:
    """
    Creates an inline keyboard with the provided year and month
    :param int year: Year to use in the calendar, if None the current year is used.
    :param int month: Month to use in the calendar, if None the current month is used.
    :return: Returns InlineKeyboardMarkup object with the calendar.
    """

    curday_id = 0
    border_id = 0
    i = 0

    now = datetime.now()
    # now = datetime(year=2023, month=10, day=26)
    border_dt = now + timedelta(days=13)
    curday = now.day
    # curyear = now.year
    curmonth = now.month
    inline_kb = InlineKeyboardBuilder()
    ignore_callback = CalendarCallback(action="IGNORE", year=year, month=month, day=0)  # for buttons with no answer

    # First row - Month and Year
    if curmonth != month:
        inline_kb.button(
            text="⬅",
            callback_data=CalendarCallback(action="PREV-MONTH", year=year, month=month, day=1)
        )
    inline_kb.button(
        text=f'{to_ru_month[calendar.month_name[month]]} {str(year)}',
        callback_data=ignore_callback
    )
    if curmonth == month:
        if border_dt.month != curmonth:
            inline_kb.button(
                text="➡",
                callback_data=CalendarCallback(action="NEXT-MONTH", year=year, month=month, day=1)
            )
    inline_kb.adjust(5)

    # Second row - Week Days
    btns_day = []
    # for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]:
    for day in ["Пн", "Вт", "Ср", "Чт", "Пт"]:
        btns_day.append(types.InlineKeyboardButton(text=day, callback_data=ignore_callback.pack()))

    inline_kb.row(*btns_day, width=5)
    # Calendar rows - Days of month
    month_calendar = calendar.monthcalendar(year, month)
    btns_week = []
    for week in month_calendar:
        counter = 0
        for day in week:
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

            appt_count = await check_appt_day(year, month, day)
            if appt_count < 7:
                btns_week.append(types.InlineKeyboardButton(
                    text=f'{str(day)}',
                    callback_data=CalendarCallback(action="SELECTED", year=year, month=month, day=day).pack()
                ))
            else:
                btns_week.append(types.InlineKeyboardButton(text=' ', callback_data=ignore_callback.pack()))

            i += 1
            counter += 1

    c = None

    # print(f'curday_id: {curday_id}')
    # print(f'check id: {btns_week[curday_id].text}')
    # print(f'len btns_week: {len(btns_week)}')
    if curmonth == month:
        for i in range(4, len(btns_week)-1, 5):
            # print(i)
            if btns_week[i].text == ' ' and i < curday_id:
                c = i + 1
    # print(f'border_id: {border_id}')
    if curmonth != month:
        for i in range(len(btns_week)-1, -1, -5):
            # print(i)
            if btns_week[i].text == ' ' and i >= border_id:
                # print(f'next c: {i}')
                c = i+1

    # print({btns_week[9]})
    if c is not None and curmonth == month:
        btns_week = btns_week[c:]
    if c is not None and curmonth != month:
        btns_week = btns_week[:c]

    inline_kb.row(*btns_week, width=5)
    # Last row - Buttons
    btns_pag = [
        types.InlineKeyboardButton(
            text="Назад", callback_data=CalendarCallback(action="BACK", year=year, month=month, day=day).pack()
        )
        # types.InlineKeyboardButton(
        #     text="В начало", callback_data=CalendarCallback(action="PICK-DOCTOR", year=year, month=month, day=day).pack()
        # )
    ]
    inline_kb.row(*btns_pag, width=1)

    return inline_kb.as_markup()


async def check_apt_hour(hour, picked_date):
    f = False
    for key in myvars.appointments.keys():
        # if myvars.picked_date.date() == key.date():
        if picked_date.date() == key.date():
            # print(f'{hour} --- {key.hour}')
            if hour == key.hour:
                f = True
    return f


async def time_picker(state: FSMContext) -> InlineKeyboardMarkup:
    hours = [10, 11, 12, 13, 14, 15, 16]
    btns_hour = []
    user_data = await state.get_data()

    kb = InlineKeyboardBuilder()

    for hour in hours:
        flag = await check_apt_hour(int(hour), user_data['picked_date'])
        # print(f'{myvars.picked_date.date()} {hour} -- {key}')
        # print(f'flag1: {flag}')
        if not flag:
            # print(f'flag2: {flag}')
            btns_hour.append(types.InlineKeyboardButton(text=f'{hour}.00-{hour}.40', callback_data=f'time_picker_{hour}'))

    kb.row(*btns_hour, width=1)
    kb.button(text='Назад', callback_data='time_picker_back')
    kb.button(text='В начало', callback_data='time_picker_pickdoctor')
    kb.adjust(1)
    return kb.as_markup()


def kb_appt_state() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='онлайн/удаленно', callback_data='appt_state_online')
    kb.button(text='оффлайн/в поликлинике', callback_data='appt_state_offline')
    kb.button(text='Назад', callback_data='appt_state_back')
    kb.button(text='В начало', callback_data='appt_state_pickdoctor')
    kb.adjust(1)
    return kb.as_markup()


# def kb_car_plate() -> InlineKeyboardMarkup:
#     kb = InlineKeyboardBuilder()
#     kb.button(text='Подтвердить', callback_data='appt_state_approve')
#     kb.button(text='оффлайн/в поликлинике', callback_data='appt_state_offline')
#     kb.button(text='Назад', callback_data='appt_state_back')
#     kb.button(text='В начало', callback_data='appt_state_pickdoctor')
#     kb.adjust(1)
#     return kb.as_markup()


async def kb_appt_approve() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='Подтвердить', callback_data='appt_approve_approve')
    kb.button(text='Назад', callback_data='appt_approve_back')
    kb.button(text='В начало', callback_data='appt_approve_pickdoctor')
    kb.adjust(1)
    return kb.as_markup()


async def get_kb_appt_cancel(state: FSMContext) -> InlineKeyboardMarkup:
    user_data = await state.get_data()

    kb = InlineKeyboardBuilder()
    # kb.button()
    # print(f'doctor keys: {myvars.doctors.keys()}')
    for date in myvars.appointments.keys():
        # print(f'date: {date.year}_{date.month}_{date.day}_{date.hour}')
        if myvars.appointments[date]['tid'] == user_data['user_tid']:
            kb.add(types.InlineKeyboardButton(text=str(date),
                                              callback_data=f"callback_appt_close_{date.year}_{date.month}_{date.day}_{date.hour}_00_00"))
    kb.adjust(1)
    return kb.as_markup()


async def get_kb_appt_cancel_approve() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='Подтвердить', callback_data='cb_appt_close_approve')
    kb.button(text='Назад', callback_data='cb_appt_close_menu')

    kb.adjust(1)
    return kb.as_markup()
