from aiogram import Router, F
from aiogram.types import Message, InputMediaPhoto, InputMedia, ContentType as CT
from aiogram import types

from config_reader import config


router = Router()


# пример отправки тех же данных в виде медиагруппы
@router.message(F.content_type.in_([CT.PHOTO, CT.VIDEO, CT.AUDIO, CT.DOCUMENT]))
async def handle_albums(message: Message, album: list[Message]):
    media_group = []
    file_id_list = []
    file_type_list = []
    print(f'album: {album}')
    for msg in album:
        if msg.photo:
            file_id = msg.photo[-1].file_id
            media_group.append(InputMediaPhoto(media=file_id))
            file_id_list.append(msg.photo[-1].file_id)
            file_type_list.append(msg.content_type)
        else:
            obj_dict = msg.model_dump()
            file_id = obj_dict[msg.content_type]['file_id']
            media_group.append(InputMedia(media=file_id))
            file_id_list.append(obj_dict[msg.content_type]['file_id'])
            file_type_list.append(msg.content_type)

    # await message.answer_media_group(media_group)
    i=0
    text = ""
    for file_id in file_id_list:
        text += f"file_id: {file_id} type: {file_type_list[i]}\n"
        i += 1
    await message.answer(text=text)
