from aiogram import Router, F
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

# from filters.check_user import IsSuIsRegCallback
from keyboards.for_appointment import get_appointment_kb
from keyboards.for_doctor import get_kb_doctor_menu, get_kb_doctor_search_user_result
from keyboards.for_superuser import get_kb_debug_menu, get_kb_main_menu, get_kb_superuser_manage_menu, \
    get_kb_superuser_search_user_result, get_kb_debug_test_vars, get_kb_superuser_approve_user_role, \
    get_kb_su_doctor_list, get_kb_su_approve_spreadsheet_id
from keyboards.for_services import get_kb_services
from libs.db_lib import pg_select, pg_execute
from libs.google_ss import google_main, update_cell
from config_reader import config, myvars
from libs.load_vars import update_superuser, update_administrator, update_doctor
from filters.permission import check_permission

router = Router()


class InputData(StatesGroup):
    lastname = State()
    spreadsheet_id = State()
    test_vars = State()


@router.callback_query(F.data == "cb_debug_test_vars")
async def debug_test_vars(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(f'test vars action:', reply_markup=await get_kb_debug_test_vars())
    await callback.answer("Успешно")


@router.callback_query(F.data == "cb_debug_test_vars_get")
async def debug_test_vars_get(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    await callback.message.delete()
    await callback.message.answer(f'test_vars: {user_data["lastname"]}', reply_markup=await get_kb_debug_test_vars())
    await state.set_state(InputData.test_vars)
    await callback.answer("Успешно")


@router.callback_query(F.data == "cb_debug_test_vars_set")
async def debug_test_vars_set(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(f'Введите test_vars', reply_markup=await get_kb_debug_test_vars())
    await state.set_state(InputData.test_vars)
    await callback.answer("Успешно")


@router.message(InputData.test_vars)
async def set_test_vars(message: types.Message, state: FSMContext):
    await state.update_data(lastname=message.text)
    myvars.test_var = message.text
    await message.answer("Переменная установлена", reply_markup=await get_kb_debug_test_vars())


@router.callback_query(F.data == "cb_superuser_debug")
async def pick_debug(callback: types.CallbackQuery):
    is_superuser = await check_permission(myvars.superuser, callback=callback)
    if is_superuser:
        await callback.message.delete()
        await callback.message.answer(f'Debug menu:', reply_markup=await get_kb_debug_menu())
        await callback.answer("Успешно")
    else:
        await callback.message.delete()
        await callback.answer("")


@router.callback_query(F.data == "cb_debug_test_google")
async def debug_btn1(callback: types.CallbackQuery):
    await callback.message.answer(f'Выполняется...')
    # await google_main(callback)
    await update_cell(config.spreadsheet_id, hour=int(12), month=int(10), year=int(2023), day=int(30),
                      value='some text', callback=callback)
    await callback.answer("Успешно")


@router.callback_query(F.data == "cb_superuser_mainmenu")
async def go_to_main_menu(callback: types.CallbackQuery):
    is_superuser = await check_permission(myvars.superuser, callback=callback)
    if is_superuser:
        await callback.message.delete()
        await callback.message.answer("Main menu", reply_markup=await get_kb_main_menu())
        await callback.answer("")
    else:
        await callback.message.delete()
        await callback.answer("")


@router.callback_query(F.data == "cb_superuser_remove_menu")
async def remove_menu(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.answer("")


@router.callback_query(F.data == "cb_superuser_service_list")
async def menu_services(callback: types.CallbackQuery):
    is_superuser = await check_permission(myvars.superuser, callback=callback)
    if is_superuser:
        await callback.message.delete()
        await callback.message.answer("Сервисы:", reply_markup=await get_kb_services())
        await callback.answer("")
    else:
        await callback.message.delete()
        await callback.answer("")


@router.callback_query(F.data == "cb_superuser_customer")
async def menu_patients(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("Добрый день, уважаемый пациент", reply_markup=get_appointment_kb())
    await callback.answer("")


@router.callback_query(F.data == "cb_superuser_doctor")
async def menu_doctors(callback: types.CallbackQuery, state: FSMContext):
    is_superuser = await check_permission(myvars.superuser, callback=callback)
    if is_superuser:
        user_data = await state.get_data()
        await callback.message.delete()
        if user_data['user_tid'] in myvars.superuser:
            await callback.message.answer("Меню врача:", reply_markup=await get_kb_doctor_menu(state))
        else:
            await callback.message.answer("Меню:", reply_markup=await get_kb_doctor_menu(state))
        await callback.answer("")
    else:
        await callback.message.delete()
        await callback.answer("")


@router.callback_query(F.data == "cb_superuser_manage")
async def menu_manager(callback: types.CallbackQuery):
    is_superuser = await check_permission(myvars.superuser, callback=callback)
    if is_superuser:
        await callback.message.delete()
        await callback.message.answer("Управление:", reply_markup=await get_kb_superuser_manage_menu())
        await callback.answer("")
    else:
        await callback.message.delete()
        await callback.answer("")


@router.callback_query(F.data == "cb_superuser_set_superuser")
async def set_superuser(callback: types.CallbackQuery, state: FSMContext):
    is_superuser = await check_permission(myvars.superuser, callback=callback)
    if is_superuser:
        await state.update_data(role="su")
        await callback.message.delete()
        await callback.message.answer("Введите фамилию или её часть для поиска:")
        await callback.answer("")
        await state.set_state(InputData.lastname)
    else:
        await callback.message.delete()
        await callback.answer("")


async def add_search_user_to_dict(message: types.Message, state: FSMContext):
    lastname = message.text
    query = f"SELECT lastname, name, surname, tid, is_doctor, is_administrator, is_superuser " \
            f" FROM tb_customers WHERE lower(lastname) LIKE '%{lastname.lower()}%'"
    rows = pg_select(query)
    my_search_user = {}

    for row in rows:
        my_search_user[row[3]] = {'lastname': row[0], 'name': row[1], 'surname': row[2],
                                  'is_doctor': row[4], 'is_administrator': row[5], 'is_superuser': row[6]}

    await state.update_data(search_user=my_search_user)


@router.message(InputData.lastname)
async def search_user(message: types.Message, state: FSMContext):
    is_superuser = await check_permission(myvars.superuser, message)
    is_doctor = await check_permission(myvars.doctors, message)
    if is_superuser:
        await add_search_user_to_dict(message, state)
        await message.answer("Результат: ", reply_markup=await get_kb_superuser_search_user_result(state))
    elif is_doctor:
        await add_search_user_to_dict(message, state)
        await message.answer("Результат: ", reply_markup=await get_kb_doctor_search_user_result(state))
    else:
        await message.delete()


@router.callback_query(F.data == "cb_superuser_set_doctor")
async def set_doctor(callback: types.CallbackQuery, state: FSMContext):
    is_superuser = await check_permission(myvars.superuser, callback=callback)
    if is_superuser:
        await state.update_data(role="doctor")
        await callback.message.delete()
        await callback.message.answer("Введите фамилию или её часть для поиска:")
        await callback.answer("")
        await state.set_state(InputData.lastname)
    else:
        await callback.message.delete()
        await callback.answer("")


@router.callback_query(F.data == "cb_superuser_set_administrator")
async def set_administrator(callback: types.CallbackQuery, state: FSMContext):
    is_superuser = await check_permission(myvars.superuser, callback=callback)
    if is_superuser:
        await state.update_data(role="administrator")
        await callback.message.delete()
        await callback.message.answer("Введите фамилию или её часть для поиска:")
        await callback.answer("")
        await state.set_state(InputData.lastname)
    else:
        await callback.message.delete()
        await callback.answer("")


@router.callback_query(F.data == "cb_superuser_set_doctor_spreadsheet_id")
async def set_doctor_spreadsheet_id(callback: types.CallbackQuery, state: FSMContext):
    is_superuser = await check_permission(myvars.superuser, callback=callback)
    if is_superuser:
        await state.update_data(doctors=myvars.doctors)
        await callback.message.delete()
        await callback.message.answer("Выбирете доктора:", reply_markup=await get_kb_su_doctor_list(state))
        await callback.answer("")
    else:
        await callback.message.delete()
        await callback.answer("")


@router.callback_query(F.data.startswith("cb_su_doctor_selected_"))
async def selected_doctor(callback: types.CallbackQuery, state: FSMContext):
    is_superuser = await check_permission(myvars.superuser, callback=callback)
    if is_superuser:
        tid = int(callback.data.split("_")[4])
        doctor = callback.data.split("_")[5]
        await state.update_data(selected_doctor_tid=tid)
        await state.update_data(selected_doctor=doctor)
        await state.set_state(InputData.spreadsheet_id)
        await callback.message.delete()
        await callback.message.answer("Введите <b>SPREADSHEET_ID</b>")
        await callback.answer("")
    else:
        await callback.message.delete()
        await callback.answer("")


@router.message(InputData.spreadsheet_id)
async def input_spreadsheet_id(message: types.Message, state: FSMContext):
    is_superuser = await check_permission(myvars.superuser, message)
    if is_superuser:
        spreadsheet_id = message.text
        await state.update_data(spreadsheet_id=spreadsheet_id)
        user_data = await state.get_data()
        text = f"<b>[Назначить SPREADSHEET_ID]</b>\n" \
               f"━━━━━━━━━━━━━━━\n" \
               f"Врач: <u>{user_data['selected_doctor']}</u>\n" \
               f"SPREADSHEET_ID: <code>{spreadsheet_id}</code>"
        await message.answer(text=text, reply_markup=await get_kb_su_approve_spreadsheet_id())
    else:
        await message.delete()


@router.callback_query(F.data == "cb_su_approve_spreadsheet_id")
async def set_doctor_spreadsheet_id(callback: types.CallbackQuery, state: FSMContext):
    is_superuser = await check_permission(myvars.superuser, callback=callback)
    if is_superuser:
        user_data = await state.get_data()
        query = f"UPDATE tb_customers SET spreadsheet_id = '{user_data['spreadsheet_id']}' " \
                f"WHERE tid = {user_data['selected_doctor_tid']}"
        pg_execute(query)
        myvars.doctors[user_data['selected_doctor']]['spreadsheet_id'] = user_data['spreadsheet_id']
        await callback.message.delete()
        await callback.message.answer("<b>SPREADSHEET_ID</b> успешно обновлён.")
        await callback.answer("")
    else:
        await callback.message.delete()
        await callback.answer("")


@router.callback_query(F.data.startswith("cb_su_search_user_result_"))
async def approve_selected_user_role(callback: types.CallbackQuery, state: FSMContext):
    is_superuser = await check_permission(myvars.superuser, callback=callback)
    if is_superuser:
        role = callback.data.split("_")[5]
        tid = int(callback.data.split("_")[6])
        await state.update_data(selected_user=tid)
        user_data = await state.get_data()

        await callback.message.delete()
        text = f"<b>Назначить роль: {role}</b>\n" \
               f"<b>{[tid]} {user_data['search_user'][tid]['lastname']} " \
               f"{user_data['search_user'][tid]['name']} {user_data['search_user'][tid]['surname']}</b>\n" \
               f"━━━━━━━━━━━━━━━\n" \
               f"Текущие роли:\n" \
               f"<u>is_superuser</u>: {user_data['search_user'][tid]['is_superuser']}\n" \
               f"<u>is_doctor</u>: {user_data['search_user'][tid]['is_doctor']}\n" \
               f"<u>is_administrator</u>: {user_data['search_user'][tid]['is_administrator']}"
        await callback.message.answer(text=text, reply_markup=await get_kb_superuser_approve_user_role())
        await callback.answer("")
    else:
        await callback.message.delete()
        await callback.answer("")


async def user_role_action_set_rm(action: int, state: FSMContext):
    user_data = await state.get_data()
    tid = user_data['selected_user']
    query = None
    if user_data['role'] == 'su':
        query = f"UPDATE tb_customers SET is_superuser={action} WHERE tid={tid}"
        pg_execute(query)
        update_superuser()
    elif user_data['role'] == 'administrator':
        query = f"UPDATE tb_customers SET is_administrator={action} WHERE tid={tid}"
        pg_execute(query)
        update_administrator()
    elif user_data['role'] == 'doctor':
        query = f"UPDATE tb_customers SET is_doctor={action} WHERE tid={tid}"
        pg_execute(query)
        update_doctor()

    ico = None
    if action == 1:
        action = 'назначена'
        ico = "✅"
    else:
        action = 'удалена'
        ico = "❌"

    text = f"{ico} Роль <b>{user_data['role']}</b> успешно <b>{action}</b> пользователю <u>{user_data['search_user'][tid]['lastname']} " \
           f"{user_data['search_user'][tid]['name']} {user_data['search_user'][tid]['surname']}</u>"
    return text


@router.callback_query(F.data == "cb_su_approve_user_role")
async def approve_user_role(callback: types.CallbackQuery, state: FSMContext):
    is_superuser = await check_permission(myvars.superuser, callback=callback)
    if is_superuser:
        text = await user_role_action_set_rm(1, state)
        await callback.message.delete()

        await callback.message.answer(text=text)
        await state.clear()
        await callback.answer("Успешно")
    else:
        await callback.message.delete()
        await callback.answer("")


@router.callback_query(F.data == "cb_su_rm_user_role")
async def rm_user_role(callback: types.CallbackQuery, state: FSMContext):
    is_superuser = await check_permission(myvars.superuser, callback=callback)
    if is_superuser:
        text = await user_role_action_set_rm(0, state)
        await callback.message.delete()

        await callback.message.answer(text=text)
        await state.clear()
        await callback.answer("Успешно")
    else:
        await callback.message.delete()
        await callback.answer("")
