from aiogram import Router, F
from aiogram import types
from aiogram.fsm.context import FSMContext

# from config_reader import myvars
# from filters.permission import check_permission
from config_reader import myvars
from filters.permission import check_permission
from handlers.appointment_menu import is_phonenumber
from handlers.registration import AwaitMessages
from handlers.superuser_menu import InputData
from keyboards.for_administrator import get_kb_adm_doctors_appt, get_kb_admin_selected_patient
from keyboards.for_appointment import get_doctor_kb, get_kb_appt_cancel
from libs.db_lib import pg_select_one_column as pg_soc

router = Router()


@router.callback_query(F.data == "cb_adm_doctors_appt")
async def menu_administrator(callback: types.CallbackQuery, state: FSMContext):

    await callback.message.delete()
    await callback.message.answer("График работы врачей(google):", reply_markup=await get_kb_adm_doctors_appt())
    await callback.answer("")


@router.callback_query(F.data == "cb_administrator_patients")
async def set_doctor(callback: types.CallbackQuery, state: FSMContext):
    is_superuser = await check_permission(myvars.superuser, callback=callback)
    is_administrator = await check_permission(myvars.administrator, callback=callback)

    if is_superuser or is_administrator:
        # await state.update_data(role="")
        await callback.message.delete()
        await callback.message.answer("Введите фамилию или её часть для поиска:")
        await callback.answer("")
        await state.set_state(InputData.lastname)
    else:
        await callback.message.delete()
        await callback.answer("")


@router.callback_query(F.data.startswith("cb_admin_search_user_result_"))
async def admin_manage_seleted_patient(callback: types.CallbackQuery, state: FSMContext):
    is_superuser = await check_permission(myvars.superuser, callback=callback)
    is_administrator = await check_permission(myvars.administrator, callback=callback)

    if is_superuser or is_administrator:
        value = int(callback.data.split("_")[5])

        await state.update_data(selected_user=value)
        user_data = await state.get_data()

        await callback.message.delete()
        text = f"<b>Пациент</b>\n" \
               f"━━━━━━━━━━━━━━━\n" \
               f"<b>{[value]} {user_data['search_user'][value]['lastname']} " \
               f"{user_data['search_user'][value]['name']} {user_data['search_user'][value]['surname']}</b>"

        await callback.message.answer(text=text, reply_markup=await get_kb_admin_selected_patient())
        await callback.answer("")
    else:
        await callback.message.delete()
        await callback.answer("")


@router.callback_query(F.data == "cb_admin_select_doctor")
async def admin_patien_select_doctor(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer("Выберите врача:", reply_markup=get_doctor_kb())


@router.callback_query(F.data == "cb_admin_appointments_patient")
async def admin_appts_patient(callback: types.CallbackQuery, state: FSMContext):
    is_admin_mode, is_phone = await is_phonenumber(state)
    user_data = await state.get_data()
    query = None
    if not is_phone:
        tid = None
        if is_admin_mode:
            tid = user_data['selected_user']
        else:
            tid = callback.from_user.id
        await state.update_data(user_tid=tid)

        query = f"SELECT count(ap.id) " \
                f"FROM tb_appointments as ap " \
                f"LEFT JOIN tb_customers as cu " \
                f"ON ap.cid = cu.id " \
                f"WHERE tid={tid} and appt_date > CURRENT_TIMESTAMP"
    else:
        phonenumber = user_data['selected_user']
        query = f"SELECT count(ap.id) " \
                f"FROM tb_appointments as ap " \
                f"LEFT JOIN tb_customers as cu " \
                f"ON ap.cid = cu.id " \
                f"WHERE phonenumber='{phonenumber}' and appt_date > CURRENT_TIMESTAMP"

    await callback.message.delete()
    count = int(pg_soc(query)[0])

    if count == 0:
        await callback.message.answer("Записей нет")
    else:
        # await message.answer("Выберите врача:", reply_markup=ReplyKeyboardRemove())
        await callback.message.answer("Выберите запись:", reply_markup=await get_kb_appt_cancel(state))


@router.callback_query(F.data == "cb_admin_registration_patients")
async def admin_registration_patient(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(admin_reg_patient=True)
    await callback.message.answer("Введите имя")
    await state.set_state(AwaitMessages.name_add)
