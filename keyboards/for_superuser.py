from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config_reader import myvars


async def get_kb_main_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='Сервисы', callback_data='cb_superuser_service_list')
    kb.button(text='Управление', callback_data='cb_superuser_manage')
    kb.button(text='Администратор', callback_data='cb_superuser_administrator')
    kb.button(text='Врач', callback_data='cb_superuser_doctor')
    kb.button(text='Пациент', callback_data='cb_superuser_customer')
    kb.button(text='Debug', callback_data='cb_superuser_debug')
    kb.button(text='Скрыть меню', callback_data='cb_superuser_remove_menu')
    kb.adjust(1)
    return kb.as_markup()


async def get_kb_debug_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='test google', callback_data='cb_debug_test_google')
    kb.button(text='test vars', callback_data='cb_debug_test_vars')
    kb.button(text='Назад', callback_data='cb_superuser_mainmenu')
    kb.button(text='Скрыть меню', callback_data='cb_superuser_remove_menu')
    kb.adjust(1)
    return kb.as_markup()


async def get_kb_debug_test_vars() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='set var', callback_data='cb_debug_test_vars_set')
    kb.button(text='get vars', callback_data='cb_debug_test_vars_get')
    kb.button(text='Назад', callback_data='cb_superuser_mainmenu')
    kb.button(text='Скрыть меню', callback_data='cb_superuser_remove_menu')
    kb.adjust(1)
    return kb.as_markup()


async def get_kb_superuser_manage_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='Назначить superuser-а', callback_data='cb_superuser_set_superuser')
    kb.button(text='Назначить врача', callback_data='cb_superuser_set_doctor')
    kb.button(text='Назначить администратора', callback_data='cb_superuser_set_administrator')
    kb.button(text='Присвоить врачу spreadsheet_id', callback_data='cb_superuser_set_doctor_spreadsheet_id')
    kb.button(text='Назад', callback_data='cb_superuser_mainmenu')
    kb.button(text='Скрыть меню', callback_data='cb_superuser_remove_menu')
    kb.adjust(1)
    return kb.as_markup()


async def get_kb_superuser_search_user_result(state: FSMContext) -> InlineKeyboardMarkup:
    user_data = await state.get_data()
    kb = InlineKeyboardBuilder()

    for user in user_data['search_user'].keys():
        text = f"[{user}] {user_data['search_user'][user]['lastname']} {user_data['search_user'][user]['name']} {user_data['search_user'][user]['surname']}"
        kb.add(types.InlineKeyboardButton(text=text, callback_data=f"cb_su_search_user_result_{user_data['role']}_{user}"))

    kb.button(text='Назад', callback_data='cb_superuser_manage')
    kb.button(text='Скрыть меню', callback_data='cb_superuser_remove_menu')

    kb.adjust(1)
    return kb.as_markup()


async def get_kb_superuser_approve_user_role() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.button(text='Назначить', callback_data='cb_su_approve_user_role')
    kb.button(text='Снять роль', callback_data='cb_su_rm_user_role')
    kb.button(text='Назад', callback_data='cb_superuser_manage')
    kb.button(text='Скрыть меню', callback_data='cb_superuser_remove_menu')

    kb.adjust(1)
    return kb.as_markup()


async def get_kb_su_doctor_list(state: FSMContext) -> InlineKeyboardMarkup:
    user_data = await state.get_data()
    kb = InlineKeyboardBuilder()

    for doctor in user_data['doctors'].keys():
        text = f"[{user_data['doctors'][doctor]['id']}] {doctor}"
        kb.add(types.InlineKeyboardButton(text=text, callback_data=f"cb_su_doctor_selected_{user_data['doctors'][doctor]['id']}_{doctor}"))

    kb.button(text='Назад', callback_data='cb_superuser_manage')
    kb.button(text='Скрыть меню', callback_data='cb_superuser_remove_menu')

    kb.adjust(1)
    return kb.as_markup()


async def get_kb_su_approve_spreadsheet_id():
    kb = InlineKeyboardBuilder()

    kb.button(text='Применить', callback_data='cb_su_approve_spreadsheet_id')
    kb.button(text='Назад', callback_data='cb_superuser_manage')
    kb.button(text='Скрыть меню', callback_data='cb_superuser_remove_menu')

    kb.adjust(1)
    return kb.as_markup()