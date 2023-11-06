from aiogram import Router, F
from aiogram import types

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove

from handlers.appointment_menu import is_phonenumber
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
    approve = State()


@router.message(F.text.lower() == "регистрация")
async def reg_start(message: types.Message, state: FSMContext):
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
        text="Нажмите кнопку поделиться контактом",
        reply_markup=get_reg_contact_kb())
    await state.set_state(AwaitMessages.phone_add)


@router.message(AwaitMessages.phone_add)
async def set_phone(message: types.Message, state: FSMContext):
    global tid, name, surname, lastname, phonenumber
    if hasattr(message.contact, 'phone_number'):
        await state.update_data(phone=message.contact.phone_number)
        user_data = await state.get_data()
        tid = message.from_user.id
        name = user_data["name"]
        surname = user_data["surname"]
        lastname = user_data["lastname"]
        phonenumber = user_data["phone"][1:]
        await message.answer(
            text=f'tid: <code>{str(tid)}</code>\nИмя: {name}\nОтчество: {surname}\nФамилия: {lastname}\nНомер тел: {phonenumber}\n',
            reply_markup=get_reg_approve_kb())
        await state.set_state(AwaitMessages.approve)
    else:
        user_data = await state.get_data()
        if "admin_reg_patient" in user_data.keys():
            phone = message.text
            if len(phone) == 11:
                if phone.isnumeric():
                    await state.update_data(phone=phone)
                    name = user_data["name"]
                    surname = user_data["surname"]
                    lastname = user_data["lastname"]
                    await message.answer(
                        text=f'tid: <code>0</code>\n'
                             f'Имя: {name}\n'
                             f'Отчество: {surname}\n'
                             f'Фамилия: {lastname}\n'
                             f'Номер тел: {phone}\n',
                        reply_markup=get_reg_approve_kb())
                    await state.set_state(AwaitMessages.approve)
                else:
                    await message.answer("Пожалуйста введите правильно номер. Номер не должен содержать буквы.\nПример: 79161112233",
                                         reply_markup=get_reg_contact_kb())
                    await state.set_state(AwaitMessages.phone_add)
            else:
                await message.answer("Пожалуйста введите правильно номер.\nПример: 79161112233", reply_markup=get_reg_contact_kb())
                await state.set_state(AwaitMessages.phone_add)
        else:
            await message.answer("Пожалуйста поделитесь контактом", reply_markup=get_reg_contact_kb())
            await state.set_state(AwaitMessages.phone_add)


@router.message(AwaitMessages.approve)
@router.message(F.text.lower() == "подтвердить")
async def reg_approve(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if "admin_reg_patient" in user_data.keys():
        query = f"INSERT INTO tb_customers (name, surname, lastname, phonenumber) " \
                f"VALUES ('{user_data['name']}','{user_data['surname']}','{user_data['lastname']}','{user_data['phone']}') " \
                f"ON CONFLICT (phonenumber) DO NOTHING"
    else:
        query = f"INSERT INTO tb_customers (tid, name, surname, lastname, phonenumber) " \
                f"VALUES ('{message.from_user.id}','{user_data['name']}','{user_data['surname']}','{user_data['lastname']}','{user_data['phone']}') " \
                f"ON CONFLICT (phonenumber) DO NOTHING"
    pg_execute(query)

    query = "SELECT tid FROM tb_customers"
    myvars.registred_users = pg_soc(query)
    await state.clear()

    await message.answer(text="Спасибо за регистрацию!", reply_markup=get_appointment_kb())


@router.message(F.text.lower() == "изменить")
async def reg_edit(message: types.Message, state: FSMContext):
    await message.answer("Введите имя", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AwaitMessages.name_add)
