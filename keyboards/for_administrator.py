import calendar

from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from datetime import datetime, timedelta

from config_reader import myvars
from libs.dictanotry_lib import to_ru_month


async def get_kb_administrator_menu(state: FSMContext) -> InlineKeyboardMarkup:
    user_data = await state.get_data()

    kb = InlineKeyboardBuilder()
    kb.button(text='График приёма', callback_data='cb_adm_doctors_appt')
    kb.button(text='Пациенты', callback_data='cb_administrator_patients')
    kb.button(text='Регистрация', callback_data='cb_admin_registration_patients')
    if user_data['user_tid'] in myvars.superuser:
        await state.update_data(role='administrator')
        await state.update_data(selected_user=myvars.administrator[user_data['admin']]['tid'])
        kb.button(text='Удалить роль', callback_data='cb_su_rm_user_role')
        kb.button(text='Назад', callback_data='cb_superuser_mainmenu')
    kb.button(text='Скрыть меню', callback_data='cb_superuser_remove_menu')

    kb.adjust(1)
    return kb.as_markup()


async def get_kb_adm_doctors_appt() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for doctor in myvars.doctors.keys():
        kb.button(text=doctor, url=f"https://docs.google.com/spreadsheets/d/{myvars.doctors[doctor]['spreadsheet_id']}/")

    kb.button(text='Назад', callback_data='cb_superuser_administrator')
    kb.button(text='Скрыть меню', callback_data='cb_superuser_remove_menu')

    kb.adjust(1)
    return kb.as_markup()


async def get_kb_admin_search_user_result(state: FSMContext):
    user_data = await state.get_data()
    kb = InlineKeyboardBuilder()

    for user in user_data['search_user'].keys():
        text = f"[{user}] {user_data['search_user'][user]['lastname']} {user_data['search_user'][user]['name']} {user_data['search_user'][user]['surname']}"
        kb.add(
            types.InlineKeyboardButton(text=text, callback_data=f"cb_admin_search_user_result_{user}"))

    kb.button(text='Назад', callback_data='cb_superuser_administrator')
    kb.button(text='Скрыть меню', callback_data='cb_superuser_remove_menu')

    kb.adjust(1)
    return kb.as_markup()


async def get_kb_admin_selected_patient() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.button(text='📝 Новая запись', callback_data='cb_admin_select_doctor')
    kb.button(text='🗒 Записи', callback_data='cb_admin_appointments_patient')
    kb.button(text='Главное меню', callback_data='cb_superuser_administrator')
    kb.button(text='Скрыть меню', callback_data='cb_superuser_remove_menu')

    kb.adjust(1)
    return kb.as_markup()