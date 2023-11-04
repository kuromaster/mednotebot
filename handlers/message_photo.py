from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ContentType as CtT

from handlers.appointment_menu import AppointmentCustomer
from keyboards.for_appointment import get_appointment_kb
from keyboards.for_files import get_kb_files_clear_state
from libs.db_lib import pg_execute

router = Router()


async def get_file_id(message: Message, data_list: dict):
    if message.photo:
        file_id = message.photo[-1].file_id
        # media_group.append(InputMediaPhoto(media=file_id))
        data_list["file_id"].append(file_id)
        data_list["content_type"].append("photo")
        query = f"INSERT INTO tb_files (tid, file_id, file_type) VALUES ({message.from_user.id},'{file_id}','photo')" \
                "ON CONFLICT(file_id) DO NOTHING"
    else:
        obj_dict = message.model_dump()
        file_id = obj_dict[message.content_type]['file_id']
        # media_group.append(InputMedia(media=file_id))
        data_list["file_id"].append(file_id)
        data_list["content_type"].append(message.content_type)
        query = f"INSERT INTO tb_files (tid, file_id, file_type) " \
                f"VALUES ({message.from_user.id},'{file_id}','{message.content_type}')" \
                "ON CONFLICT(file_id) DO NOTHING"

    pg_execute(query)
    return data_list


# пример отправки тех же данных в виде медиагруппы
@router.message(AppointmentCustomer.photo, F.content_type.in_([CtT.PHOTO, CtT.VIDEO, CtT.AUDIO, CtT.DOCUMENT]))
async def handle_albums(message: Message, album: list[Message] = None, state: FSMContext = None):
    # media_group = []
    data_list = {}
    data_list.setdefault("file_id", [])
    data_list.setdefault("content_type", [])
    if message.media_group_id:
        for msg in album:
            data_list = await get_file_id(msg, data_list)
    else:
        data_list = await get_file_id(message, data_list)

    # await message.answer_media_group(media_group)

    i = 0
    text = "Файл(ы) загружен(ы):\n"
    for file_id in data_list['file_id']:
        text += "━━━━━━━━━━━━━━━\n" \
                f"file_id: <code>{file_id}</code>\n" \
                f"type: {data_list['content_type'][i]}\n"
        i += 1
    await message.answer(text=text, reply_markup=get_kb_files_clear_state())


@router.message(AppointmentCustomer.photo, F.text.lower() == "назад")
async def clear_state(message: Message, state: FSMContext):
    await message.delete()
    await message.answer("Передача файлов завершена", reply_markup=get_appointment_kb())
    await state.clear()



