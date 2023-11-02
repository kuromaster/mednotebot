from aiogram import Router, F
from aiogram import types
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from datetime import datetime

# from keyboards.
# from config_reader import config

from keyboards.for_services import get_kb_manage_sc_notify, get_kb_sc_notify_start_stop
from libs.db_lib import pg_execute
from schedulers.jobs import send_message_sc_notify, send_message_sc_notify_admin

router = Router()


@router.callback_query(F.data == "cb_service_notify")
async def manage_sc_notify(callback: types.CallbackQuery, apscheduler: AsyncIOScheduler):
    sc_status = 'остановлен'
    if apscheduler.get_job('send_message_sc_notify') is not None:
        sc_status = 'запущен'

    await callback.message.delete()
    await callback.message.answer('<b>[Cервис уведомлений]</b>\n' +
                                  '━━━━━━━━━━━━━━━\n' +
                                  f'Статус:    <u>{sc_status}</u>',
                                  reply_markup=await get_kb_manage_sc_notify())
    await callback.answer("Успешно")


@router.callback_query(F.data == "cb_service_notify_start")
async def sc_notify_start(callback: types.CallbackQuery, apscheduler: AsyncIOScheduler, bot: Bot, state: FSMContext):
    # text = 'some text for test'
    apscheduler.add_job(
        send_message_sc_notify,
        trigger='cron',
        start_date=datetime.now(),
        hour=10,
        minute=5,
        id='send_message_sc_notify',
        kwargs={'bot': bot, 'state': state})
        # kwargs={'bot': bot, 'chat_id': config.maezztro_tid, 'text': text})
    apscheduler.add_job(
        send_message_sc_notify_admin,
        trigger='cron',
        start_date=datetime.now(),
        hour=14,
        minute=5,
        id='send_message_sc_notify_admin',
        kwargs={'bot': bot})
    # print(apscheduler.get_job('send_message_sc_notify'))
    await callback.message.delete()
    await callback.message.answer('Запускаем сервис оповещений...',
                                  reply_markup=await get_kb_sc_notify_start_stop())
    await callback.answer("Успешно")


@router.callback_query(F.data == "cb_service_notify_stop")
async def sc_notify_start(callback: types.CallbackQuery, apscheduler: AsyncIOScheduler, bot: Bot):
    apscheduler.remove_job('send_message_sc_notify')
    apscheduler.remove_job('send_message_sc_notify_admin')
    # apscheduler.add_job(send_message_sc_notify, trigger='interval', seconds=10, kwargs={'bot': bot, 'chat_id': config.maezztro_tid, 'text': text})
    await callback.message.delete()
    await callback.message.answer('Выключаем сервис оповещений...',
                                  reply_markup=await get_kb_sc_notify_start_stop())
    await callback.answer("Успешно")


@router.callback_query(F.data.startswith("cb_service_appt_approve_"))
async def patient_appt_approve(callback: types.CallbackQuery, state: FSMContext):
    appt_date = callback.data.split("_")[4]
    tid = int(callback.data.split("_")[5])
    query = f"UPDATE tb_appointments SET is_approved=1 " \
            f"WHERE is_approved=0 and appt_date='{appt_date}'::timestamp and tid={tid}"
    pg_execute(query)
    await callback.message.delete()
    await callback.message.answer('Спасибо. Ждём вас.')
    await callback.answer("")
