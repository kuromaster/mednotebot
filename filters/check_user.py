from aiogram import types
from aiogram.filters import Filter, BaseFilter
from typing import Union


class IsSuIsRegMessage(BaseFilter):
    def __init__(self, user_id: Union[int, list]):
        self.user_id = user_id

    async def __call__(self, message: types.Message) -> bool:
        if isinstance(self.user_id, int):
            return message.from_user.id == self.user_id
        else:
            return message.from_user.id in self.user_id


class IsSuIsRegCallback(Filter):
    def __init__(self, user_id: Union[int, list]):
        self.user_id = user_id

    async def __call__(self, callback: types.CallbackQuery) -> bool:
        if isinstance(self.user_id, int):
            return callback.from_user.id == self.user_id
        else:
            return callback.from_user.id in self.user_id


class IsDoctorMessage(BaseFilter):
    def __init__(self, dict_doctors: dict):
        self.dict_doctors = dict_doctors

    async def __call__(self, message: types.Message) -> bool:
        for doctor in self.dict_doctors:
            # print(f"{doctor} {message.from_user.id} == {self.dict_doctors[doctor]['id']}")
            if message.from_user.id == self.dict_doctors[doctor]['id']:
                return True
        return False


            # class ChatTypeFilter(BaseFilter):
#     def __init__(self, chat_type: Union[str, list]):
#         self.chat_type = chat_type
#
#     async def __call__(self, message: types.Message) -> bool:
#         if isinstance(self.chat_type, str):
#             return message.chat.type == self.chat_type
#         else:
#             return message.chat.type in self.chat_type
