from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_reg_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Регистрация")
    return kb.as_markup(resize_keyboard=True)


def get_reg_contact_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Поделиться контактом", request_contact=True)
    return kb.as_markup(resize_keyboard=True)


def get_reg_approve_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Подтвердить")
    kb.button(text="Изменить",)
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)
