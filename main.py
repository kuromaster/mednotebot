#! /opt/mednotebot/venv/bin/python3

import asyncio
import logging
import traceback
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from middleware.apschedulermiddleware import SchedulerMiddleware

from handlers import cm_start, message_files
from handlers import registration
from handlers import appointment_menu
from handlers import superuser_menu
from handlers import docotor_menu
from handlers import administrator_menu
from handlers import services

from config_reader import config
from libs.load_vars import loadvars
from middleware.multiplefilemiddleware import MultipleFileMiddleware


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s",
    # filename="log/mednotebot.log",
    # filemode="w"
)

logger = logging.getLogger(__name__)


async def on_startup():
    logger.info("Запуск бота...")


# Запуск процесса поллинга новых апдейтов
async def main():
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

    try:
        await loadvars()
        # Объект бота
        bot = Bot(token=config.bot_token.get_secret_value(), parse_mode="HTML")

        # Диспетчер
        dp = Dispatcher()

        # Регистрация scheduler middleware в диспетчере
        dp.update.middleware.register(SchedulerMiddleware(scheduler))

        # Регистрация Фото/Файлы мидлваре
        dp.message.middleware.register(MultipleFileMiddleware())

        # Добавляем роуты в диспетчер
        dp.include_routers(cm_start.router)
        dp.include_routers(registration.router)
        dp.include_routers(services.router)
        dp.include_routers(message_files.router)
        dp.include_routers(appointment_menu.router, superuser_menu.router, administrator_menu.router, docotor_menu.router)

        # On startup
        dp.startup.register(on_startup)

        # Scheduler
        scheduler.start()

        # Не обрабатывать сообщение в ТГ присланные пока бот не работал
        await bot.delete_webhook(drop_pending_updates=True)

        # Запуск бота
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
    finally:
        logger.info('Выключение бота...')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info('Бот выключен.')
