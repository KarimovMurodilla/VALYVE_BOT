from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from app.admin import admin_connection, admin_buttons
from .. import file_ids, config, buttons

bot = Bot(token=config.TOKEN, parse_mode = 'html')


class IcOneTime(StatesGroup):
	step1 = State()
	step2 = State()


async def callback_admin_output(c: types.CallbackQuery, state: FSMContext):
	pass


async def callback_refresh(c: types.CallbackQuery, state: FSMContext):
	pass


async def callback_ic_stock(c: types.CallbackQuery, state: FSMContext):
	pass


async def callback_ic_one_time(c: types.CallbackQuery, state: FSMContext):
	await IcOneTime.step1.set()

	total_1 = admin_connection.selectIcOneTime()[0][0]
	total_2 = admin_connection.selectIcOneTime()[1][0]
	total_3 = admin_connection.selectIcOneTime()[2][0]

	await bot.send_photo(
		chat_id = c.message.chat.id, 
		photo = file_ids.PHOTO['price'],
		caption = f"<b>1.</b> <code>30</code> дня в ленте - <code>{total_1}</code> <code>₽</code>\n"
				  f"<b>2.</b> <code>90</code> дней в ленте - <code>{total_2}</code> <code>₽</code>\n"
				  f"<b>3.</b> <code>180</code> дней в ленте - <code>{total_3}</code> <code>₽</code>\n",
					reply_markup = admin_buttons.adminPrice(1, 2, 3))


async def set_ic_one_time(c: types.CallbackQuery, state: FSMContext):
	await IcOneTime.next()
	rowid = c.data[7:]
	async with state.proxy() as data:
		data['rowid'] = rowid

	await c.message.answer("Какую сумму вы хотите выставить?")


async def input_price(message: types.Message, state: FSMContext):
	if message.text.isdigit():
		async with state.proxy() as data:
			data['new_price'] = message.text
			rowid = data['rowid']

			total_1 = admin_connection.selectIcOneTime()[0][0]
			total_2 = admin_connection.selectIcOneTime()[1][0]
			total_3 = admin_connection.selectIcOneTime()[2][0]

			if rowid == '1':
				total_1 = message.text
			
			elif rowid == '2':
				total_2 = message.text			

			elif rowid == '3':
				total_3 = message.text



			await bot.send_photo(
				chat_id = message.chat.id, 
				photo = file_ids.PHOTO['price'],
				caption = f"<b>1.</b> <code>30</code> дня в ленте - <code>{total_1}</code> <code>₽</code>\n"
						  f"<b>2.</b> <code>90</code> дней в ленте - <code>{total_2}</code> <code>₽</code>\n"
						  f"<b>3.</b> <code>180</code> дней в ленте - <code>{total_3}</code> <code>₽</code>\n",
							reply_markup = admin_buttons.icOneSets())

	else:
		await message.answer("Введите только цифрами")


async def callback_aPubslish(c: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		new_price = data['new_price']
		rowid = data['rowid']

		admin_connection.updateIcOneTime(new_price, rowid)
		await c.message.delete()
		await c.message.answer("✅ Опубликовано")


async def callback_aCancel(c: types.CallbackQuery, state: FSMContext):
	await c.message.delete()
	await c.message.answer("Отменено")


async def callback_list_of_expenses(c: types.CallbackQuery, state: FSMContext):
	pass


async def callback_list_of_reports(c: types.CallbackQuery, state: FSMContext):
	pass


def register_bank_controls(dp: Dispatcher):
	dp.register_callback_query_handler(callback_admin_output, lambda c: c.data == "admin_output", chat_id = config.ADMINS, state = '*')
	dp.register_callback_query_handler(callback_refresh, lambda c: c.data == "refresh", chat_id = config.ADMINS, state = '*')
	dp.register_callback_query_handler(callback_ic_stock, lambda c: c.data == "ic_stock", chat_id = config.ADMINS, state = '*')

	dp.register_callback_query_handler(callback_ic_one_time, lambda c: c.data == "ic_one_time", chat_id = config.ADMINS, state = '*')
	dp.register_callback_query_handler(set_ic_one_time, lambda c: c.data.startswith("aPrice"), chat_id = config.ADMINS, state = IcOneTime.step1)
	dp.register_message_handler(input_price, chat_id = config.ADMINS, state = IcOneTime.step2)
	dp.register_callback_query_handler(callback_aPubslish, lambda c: c.data == "aPublish", chat_id = config.ADMINS, state = '*')
	dp.register_callback_query_handler(callback_aCancel, lambda c: c.data == "aCancel", chat_id = config.ADMINS, state = '*')


	dp.register_callback_query_handler(callback_list_of_expenses, lambda c: c.data == "list_of_expenses", chat_id = config.ADMINS, state = '*')
	dp.register_callback_query_handler(callback_list_of_reports, lambda c: c.data == "list_of_reports", chat_id = config.ADMINS, state = '*')
	
