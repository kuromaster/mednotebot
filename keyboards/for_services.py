from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def get_kb_services() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='Сервис уведомлений', callback_data='cb_service_notify')
    kb.button(text='Назад', callback_data='cb_superuser_mainmenu')
    kb.button(text='Скрыть меню', callback_data='cb_superuser_remove_menu')

    kb.adjust(1)
    return kb.as_markup()


async def get_kb_manage_sc_notify() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='Запустить', callback_data='cb_service_notify_start')
    kb.button(text='Остановить', callback_data='cb_service_notify_stop')
    kb.button(text='Назад', callback_data='cb_superuser_service_list')
    kb.button(text='Главное меню', callback_data='cb_superuser_mainmenu')
    kb.button(text='Скрыть меню', callback_data='cb_superuser_remove_menu')

    kb.adjust(1)
    return kb.as_markup()


async def get_kb_sc_notify_start_stop() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='Назад', callback_data='cb_service_notify')
    kb.button(text='Главное меню', callback_data='cb_superuser_mainmenu')
    kb.button(text='Скрыть меню', callback_data='cb_superuser_remove_menu')

    kb.adjust(1)
    return kb.as_markup()


async def get_kb_job_appt_approve(state: FSMContext) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    user_data = await state.get_data()
    kb.button(text="Подвердить", callback_data=f"cb_service_appt_approve_{user_data['job_date']}_{user_data['job_tid']}")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)