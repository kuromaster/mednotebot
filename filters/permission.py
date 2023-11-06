from aiogram.types import CallbackQuery, Message
from typing import Union


async def check_permission(customers: Union[list, dict], message: Message = None, callback: CallbackQuery = None) -> bool:
    vvar = None
    if message is not None:
        vvar = message
    elif callback is not None:
        vvar = callback

    if isinstance(customers, list):
        return vvar.from_user.id in customers
    else:
        for user in customers:
            if vvar.from_user.id == customers[user]['tid']:
                return True

    return False
