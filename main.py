import asyncio
import logging
import datetime

from regular_check import scheduler, schedule_jobs

from aiogram import Bot, Dispatcher, executor
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from app.config import TOKEN
from app.handlers.common_callbacks import register_callback_handlers
from app.handlers.common_commands import register_handlers_common
from app.handlers.inline_mode import register_inline_mode_handlers
from app.handlers.reg_order import register_reg_order_handlers
from app.handlers.reg_customer_profil import register_reg_customer_profil_handlers
from app.handlers.reg_executor_profil import register_reg_executor_profil_handlers
from app.handlers.start_reg import register_start_reg_handlers
from app.handlers.complete import register_complete_handlers
from app.handlers.complete_order import register_complete_order_handlers
from app.handlers.executor_completed import register_executor_completed_handlers
from app.handlers.bot_payment import register_bot_payment_handlers
from app.handlers.review_settings import register_review_handlers
from app.handlers.order_settings import register_order_handlers

from app.admin.admin_panel import register_admin_handlers
from app.admin.admin_commands import register_handlers_admin_commands
from app.admin.admin_consol import register_admin_consol_handlers
from app.admin.admin_moderation import register_admin_moderation_handlers
from app.admin.admin_querys import register_admin_inline_mode_handlers
from app.admin.bank_control import register_bank_controls

from app.filters.filter import register_filter_handlers


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Начать")
    ]
    await bot.set_my_commands(commands)


async def main(dp):
	logging.basicConfig(level=logging.INFO)

	register_handlers_common(dp)
	register_start_reg_handlers(dp)	
	register_reg_customer_profil_handlers(dp)	
	register_reg_executor_profil_handlers(dp)
	register_reg_order_handlers(dp)
	register_callback_handlers(dp)
	register_inline_mode_handlers(dp)
	register_complete_handlers(dp)
	register_complete_order_handlers(dp)
	register_executor_completed_handlers(dp)
	register_bot_payment_handlers(dp)
	register_review_handlers(dp)
	register_order_handlers(dp)
	
	register_admin_handlers(dp)
	register_handlers_admin_commands(dp)
	register_admin_consol_handlers(dp)
	register_admin_moderation_handlers(dp)
	register_admin_inline_mode_handlers(dp)
	register_bank_controls(dp)
	
	register_filter_handlers(dp)

	schedule_jobs()

	await set_commands(bot)

	await dp.start_polling()


if __name__ == '__main__':
	bot = Bot(token=TOKEN, parse_mode = 'html')
	storage = MemoryStorage()
	dp = Dispatcher(bot, storage = storage)
	scheduler.start()
	executor.start_polling(dp, on_startup = main)

