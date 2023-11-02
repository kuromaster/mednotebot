from aiogram import Router, F
from aiogram import types

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove

from keyboards.for_reg import get_reg_contact_kb, get_reg_approve_kb
from keyboards.for_appointment import get_appointment_kb
from keyboards.for_superuser import get_kb_main_menu
from libs.db_lib import pg_execute
from libs.db_lib import pg_select_one_column as pg_soc
from config_reader import myvars

tid: int
phonenumber: int
name: str
surname: str
lastname: str

router = Router()


class AwaitMessages(StatesGroup):
    name_add = State()
    lastname_add = State()
    surname_add = State()
    phone_add = State()


@router.message(F.text.lower() == "регистрация")
async def reg_start(message: types.Message, state: FSMContext):
    # await message.answer("Отличный выбор!", reply_markup=get_reg_fio_kb())
    if message.from_user.id in myvars.registred_users:
        if message.from_user.id in myvars.superuser:
            await message.answer("Добрый день, superuser", reply_markup=ReplyKeyboardRemove())
            await message.answer("Главное меню:", reply_markup=await get_kb_main_menu())
        else:
            await message.answer("Добрый день, уважаемый пациент", reply_markup=get_appointment_kb())
    else:
        await message.answer("Введите имя")
        await state.set_state(AwaitMessages.name_add)


@router.message(AwaitMessages.name_add)
async def set_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(text="Введите отчество")
    await state.set_state(AwaitMessages.surname_add)


@router.message(AwaitMessages.surname_add)
async def set_surname(message: types.Message, state: FSMContext):
    await state.update_data(surname=message.text)
    await message.answer(text="Введите фамилию")
    await state.set_state(AwaitMessages.lastname_add)


@router.message(AwaitMessages.lastname_add)
async def set_lastname(message: types.Message, state: FSMContext):
    await state.update_data(lastname=message.text)
    await message.answer(
        text="Нажмите кнопку поделиться контактом или введите ваш номер телефона.\nПример: 79161234567",
        reply_markup=get_reg_contact_kb())
    await state.set_state(AwaitMessages.phone_add)


@router.message(AwaitMessages.phone_add)
async def set_phone(message: types.Message, state: FSMContext):
    global tid, name, surname, lastname, phonenumber
    if hasattr(message.contact, 'phone_number'):
        await state.update_data(phone=message.contact.phone_number)
    else:
        await state.update_data(phone=message.text)
    user_data = await state.get_data()
    tid = message.chat.id
    name = user_data["name"]
    surname = user_data["surname"]
    lastname = user_data["lastname"]
    phonenumber = user_data["phone"]

    await message.answer(
        text=f'tid: {str(tid)}\nИмя: {name}\nОтчество: {surname}\nФамилия: {lastname}\nНомер тел: {phonenumber}\n',
        # text=f'Имя: {user_data["name"]}\nОтчество: {user_data["surname"]}\nФамилия: {user_data["lastname"]}\nНомер тел: {user_data["phone"]}\n',
        reply_markup=get_reg_approve_kb())
    await state.clear()


@router.message(F.text.lower() == "подтвердить")
async def reg_approve(message: types.Message):
    query = f"INSERT INTO tb_customers (tid, name, surname, lastname, phonenumber) VALUES ('{tid}', '{name}','{surname}','{lastname}','{phonenumber}') ON CONFLICT (tid) DO NOTHING"
    pg_execute(query)

    query = "SELECT tid FROM tb_customers"
    myvars.registred_users = pg_soc(query)

    await message.answer(text="Спасибо за регистрацию!", reply_markup=get_appointment_kb())


@router.message(F.text.lower() == "изменить")
async def reg_edit(message: types.Message, state: FSMContext):
    await message.answer("Введите имя", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AwaitMessages.name_add)

# @router.callback_query(F.data == "reg_name")
# async def reg_answer_name(callback: types.CallbackQuery):
#     await callback.answer(text="Принято")
