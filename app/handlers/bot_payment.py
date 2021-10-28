import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from app.admin.admin_connection import selectFromAdminTable
from .. import buttons, config, connection, file_ids, getLocationInfo


bot = Bot(token=config.TOKEN, parse_mode = 'html')

def checkPaymentStatus(func):
	async def wrapper(c: types.CallbackQuery, state: FSMContext):
		if selectFromAdminTable()[1][1] == '✖️':
			await bot.send_message(c.from_user.id, "Извините! Данная функция временно закрыта!")
		else:
			return await func(c, state)
	return wrapper


@checkPaymentStatus
async def callback_withdraw(c: types.CallbackQuery, state: FSMContext):
	pass











def register_bot_payment_handlers(dp: Dispatcher):
	dp.register_callback_query_handler(callback_withdraw, lambda c: c.data == 'withdraw',  state = '*')   