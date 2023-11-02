from aiogram import Router
from aiogram import types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from keyboards.for_doctor import get_kb_doctor_menu
from keyboards.for_reg import get_reg_kb
from keyboards.for_appointment import get_appointment_kb
from keyboards.for_superuser import get_kb_main_menu
from config_reader import myvars
from filters.permission import check_permission
# from filters.check_user import IsSuIsRegMessage, IsDoctorMessage
# from libs.load_vars import update_superuser, update_registred, update_administrator, update_doctor

router = Router()

# update_superuser()
# update_registred()
# update_administrator()
# update_doctor()
#
#
# @router.message(IsSuIsRegMessage(user_id=update_superuser()), Command("start"))
# async def cmd_start_su(message: types.Message):
#     await message.answer("Добрый день, superuser. Для вызова меню используйте /start", reply_markup=ReplyKeyboardRemove())
#     await message.answer("Главное меню:", reply_markup=await get_kb_main_menu())
#
#
# @router.message(IsDoctorMessage(dict_doctors=myvars.doctors), Command("start"))
# async def cm_start_doctor(message: types.Message, state: FSMContext):
#     await state.update_data(user_tid=message.from_user.id)
#     await message.answer("Добрый день. Для вызова меню используйте /start", reply_markup=ReplyKeyboardRemove())
#     await message.answer("Меню:", reply_markup=await get_kb_doctor_menu(state))
#
#
# @router.message(IsSuIsRegMessage(user_id=myvars.registred_users), Command("start"))
# async def cmd_start_reg(message: types.Message):
#     await message.answer("Добрый день, уважаемый пациент", reply_markup=get_appointment_kb())


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.update_data(user_tid=message.from_user.id)

    is_superuser = await check_permission(myvars.superuser, message)
    # print(f'is_superuser: {is_superuser}, list_su: {myvars.superuser}')
    if is_superuser:
        await message.answer("Добрый день, superuser. Для вызова меню используйте /start",
                             reply_markup=ReplyKeyboardRemove())
        await message.answer("Главное меню:", reply_markup=await get_kb_main_menu())
        return

    is_doctor = await check_permission(myvars.doctors, message)
    if is_doctor:
        await message.answer("Добрый день. Для вызова меню используйте /start", reply_markup=ReplyKeyboardRemove())
        await message.answer("Меню:", reply_markup=await get_kb_doctor_menu(state))
        return

    is_registred = await check_permission(myvars.registred_users, message)
    if is_registred:
        await message.answer("Добрый день, уважаемый пациент", reply_markup=get_appointment_kb())
    else:
        await message.answer("Доброго времени суток. Для записи к врачу, пожалуйста, пройдите регистрацию.",
                             reply_markup=get_reg_kb())
