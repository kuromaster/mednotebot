from aiogram import Bot
from aiogram.fsm.context import FSMContext

from config_reader import config, myvars
from keyboards.for_services import get_kb_job_appt_approve
from libs.db_lib import pg_select_one_column as pg_soc, pg_select, pg_execute


async def send_message_time(bot: Bot):
    await bot.send_message(chat_id=config.maezztro_tid, text='Проверка шедулера')


async def send_message_sc_notify(bot: Bot, state: FSMContext):
    # user_data
    query = f"SELECT tid, appt_date FROM tb_appointments " \
            "WHERE is_approved=0 and date(notify_date)=date(CURRENT_TIMESTAMP) and is_notified=0"
    rows = pg_select(query)
    # print(rows)
    for row in rows:
        await state.update_data(job_date=row[1])
        await state.update_data(job_tid=row[0])
        query = f"UPDATE tb_appointments SET is_notified=1 " \
                f"WHERE is_approved=0 and appt_date='{row[1]}'::timestamp and tid={row[0]}"
        # print(query)
        pg_execute(query)
        text = f"Добрый день, подтвердите свою запись на {row[1]}"
        await bot.send_message(chat_id=row[0], text=text, reply_markup=await get_kb_job_appt_approve(state))


async def send_message_sc_notify_admin(bot: Bot):
    query = f"SELECT ap.tid, appt_date, lastname, name, surname " \
            "FROM tb_appointments as ap " \
            "LEFT JOIN tb_customers as cu " \
            "ON ap.tid = cu.tid " \
            "WHERE is_approved=0 and date(notify_date)=date(CURRENT_TIMESTAMP) and is_notified=1"
    rows = pg_select(query)

    for row in rows:
        text = f"<b>[Запись не подтверждена]</b>\n" \
               f"━━━━━━━━━━━━━━━\n" \
               f"Время: {row[1]}\n" \
               f"Пациент: <u>{row[2]} {row[3]} {row[4]}</u>"
        query = f"UPDATE tb_appointments SET is_notified=2 " \
                f"WHERE is_approved=0 and appt_date='{row[1]}'::timestamp and tid={row[0]}"
        # print(query)
        pg_execute(query)
        for admin_id in myvars.administrator:
            print(f'admin_id: {admin_id}')
            await bot.send_message(chat_id=admin_id, text=text)


# async def send_message_sc_notify(bot: Bot, chat_id: int, text: str = None):
#     await bot.send_message(chat_id=chat_id, text=text)
