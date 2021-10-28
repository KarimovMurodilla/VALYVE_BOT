import asyncio
import datetime
import random
from pyqiwip2p import QiwiP2P

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from .. import connection, file_ids, buttons, config, getLocationInfo
from app.admin import admin_connection

bot = Bot(token=config.TOKEN, parse_mode = 'html')
p2p = QiwiP2P(auth_key = config.QIWI_TOKEN)



class CreateOrder(StatesGroup):
	step1 = State()
	step2 = State()
	step3 = State()
	step4 = State()
	step5 = State()
	step6 = State()
	step7 = State()
	step8 = State()



def checkStatus(func):
	async def wrapper(c: types.CallbackQuery, state: FSMContext):
		if admin_connection.selectFromAdminTable()[0][1] == '✖️':
			await bot.send_message(c.from_user.id, "Приносим извинения! Данная функция временно закрыта!",
				reply_markup = buttons.menu_customer)
		else:
			return await func(c, state)
	return wrapper


@checkStatus
async def process_get_location(c: types.CallbackQuery, state: FSMContext):
	await CreateOrder.step1.set()
	
	try:
		async with state.proxy() as data:
			comment = data['comment']
			
			await bot.send_message(c.message.chat.id, ".", reply_markup = buttons.send_geo)
			await bot.send_message(c.message.chat.id, "Отправьте мне геолокацию места работы, для корректного поиска исполнителей.",
				reply_markup = buttons.skipBtn())



	except Exception as e:
		print(e)
		await bot.send_message(c.message.chat.id, "Отправьте мне геолокацию работы, для корректного поиска исполнителей.",
			reply_markup = buttons.send_geo)


@checkStatus
async def process_output_location(message: types.Message, state: FSMContext):
	await CreateOrder.next()
	try:
		
		async with state.proxy() as data:
			comment = data['comment']
			data['location_lat'] = message.location.latitude
			data['location_long'] = message.location.longitude
			data['adress_info'] = getLocationInfo.location_info(f"{data['location_long']} {data['location_lat']}")	
			
			await bot.send_message(message.chat.id, ".", reply_markup = buttons.back_canc)
			await bot.send_message(message.chat.id, "Отправьте мне название должности.",
				reply_markup = buttons.skipBtn())



	except:
		async with state.proxy() as data:
			data['location_lat'] = message.location.latitude
			data['location_long'] = message.location.longitude
			data['adress_info'] = getLocationInfo.location_info(f"{data['location_long']} {data['location_lat']}")	

			await bot.send_message(message.chat.id, "Отправьте мне название должности.",
				reply_markup = buttons.back_canc)


@checkStatus
async def process_output_position(message: types.Message, state: FSMContext):
	await CreateOrder.next()

	try:
		async with state.proxy() as data:
			comment = data['comment']
			data['position'] = message.text
			
			await bot.send_message(message.chat.id, "На какое кол-в дней вам нужен сотрудник?",
				reply_markup = buttons.skipBtn())



	except:
		async with state.proxy() as data:
			data['position'] = message.text

			await bot.send_message(message.chat.id, "На какое кол-в дней вам нужен сотрудник?")


@checkStatus
async def process_output_days(message: types.Message, state: FSMContext):
	await CreateOrder.next()

	try:
		
		async with state.proxy() as data:
			comment = data['comment']
			data['days'] = message.text
			
			await bot.send_message(message.chat.id, "Отправьте мне график работы.",
				reply_markup = buttons.skipBtn())



	except:
		async with state.proxy() as data:
			data['days'] = message.text

			await bot.send_message(message.chat.id, "Отправьте мне график работы.")


@checkStatus
async def process_output_graphic(message: types.Message, state: FSMContext):
	await CreateOrder.next()

	try:
		
		async with state.proxy() as data:
			comment = data['comment']
			data['graphic'] = message.text
			
			await bot.send_message(message.chat.id, "Отправьте сколько исполнитель получит за смену.",
				reply_markup = buttons.skipBtn())


	except Exception as e:
		print(e)
		async with state.proxy() as data:
			data['graphic'] = message.text

			await bot.send_message(message.chat.id, "Отправьте сколько исполнитель получит за смену.")


@checkStatus
async def process_output_bid(message: types.Message, state: FSMContext):
	await CreateOrder.next()

	try:
		async with state.proxy() as data:
			comment = data['comment']
			data['bid'] = message.text
			
			await bot.send_message(message.chat.id, "Укажите требование к исполнителю, в таком формате:\n"
													" - Коммуникабельность;\n"
													" - Опыт работы с кассой;\n"
													" - Опыт от 1 года;",
														reply_markup = buttons.skipBtn())


	except:
		async with state.proxy() as data:
			data['bid'] = message.text

			await bot.send_message(message.chat.id, "Укажите требование к исполнителю, в таком формате:\n"
													" - Коммуникабельность;\n"
													" - Опыт работы с кассой;\n"
													" - Опыт от 1 года;")


@checkStatus
async def process_output_requirement(message: types.Message, state: FSMContext):
	await CreateOrder.next()

	try:
		async with state.proxy() as data:
			comment = data['comment']
			data['requirement'] = message.text

			await bot.send_message(message.chat.id, "Укажите обязанности к исполнителю, в таком формате:\n"
													" - Обслуживание клиентов;\n"
													" - Работа с кассой;\n"
													" - Приём товар;",
														reply_markup = buttons.skipBtn())


	except:
		async with state.proxy() as data:
			data['requirement'] = message.text

			await bot.send_message(message.chat.id, "Укажите обязанности к исполнителю, в таком формате:\n"
													" - Обслуживание клиентов;\n"
													" - Работа с кассой;\n"
													" - Приём товар;")


@checkStatus
async def process_output_respons(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['respons'] = message.text
		await CreateOrder.next()

		await bot.send_message(message.chat.id, "Укажите комментарий к вакансии, например особенности Вашей работы и т.д\n",
			reply_markup = buttons.skip_btn)


@checkStatus
async def process_output_comment_and_all_data(message: types.Message, state: FSMContext):
	today = datetime.datetime.today().strftime('%d.%m.%Y')

	async with state.proxy() as data:
		data['comment'] = f"<b>Комментарий:</b>\n<code>{message.text}</code>"

		cus_id = message.from_user.id
		order_id = len(connection.selectOrders(cus_id))
		cus_name = connection.getCustomerName(cus_id)
		cus_adress = data['adress_info']
		cus_work_graphic = data['graphic']
		cus_work_day = data['days']
		cus_bid = data['bid']
		requirement = data['requirement']
		respons = data['respons']
		cus_position = data['position']
		cus_comment = data['comment']
		cus_lat = data['location_lat']
		cus_long = data['location_long']


		await bot.send_message(message.chat.id, f"<b>Заказчик:</b> <code>{cus_name[0]}</code>\n"
												f"<b>Адреc: </b><code>{cus_adress}</code>\n\n"

												f"<b>Должность:</b> <code>{cus_position}</code>\n"
												f"<b>Время работы:</b> <code>{cus_work_day}</code>\n"
												f"<b>График:</b> <code>{cus_work_graphic}</code>\n"
												f"<b>Смена:</b> <code>{cus_bid}</code>\n\n"

												f"<b>Требование:</b>\n<code>{requirement}</code>\n\n"
												f"<b>Обязанности:</b>\n<code>{respons}</code>\n\n"

												f"{data['comment']}")
		await bot.send_message(message.chat.id, "Ваше объявление готово, хотите ли Вы его опубликовать?",
												reply_markup = buttons.change_order)


@checkStatus
async def process_output_without_comment(c: types.CallbackQuery, state: FSMContext):
	await bot.delete_message(c.from_user.id, c.message.message_id)
	today = datetime.datetime.today().strftime('%d.%m.%Y')

	async with state.proxy() as data:
		cus_id = c.from_user.id
		data['comment'] = ''
		order_id = len(connection.selectOrders(cus_id))
		cus_name = connection.getCustomerName(cus_id)
		cus_adress = data['adress_info']
		cus_work_graphic = data['graphic']
		cus_work_day = data['days']
		cus_bid = data['bid']
		requirement = data['requirement']
		respons = data['respons']
		cus_position = data['position']
		cus_comment = data['comment']
		cus_lat = data['location_lat']
		cus_long = data['location_long']


		await bot.send_message(c.from_user.id, f"<b>Заказчик:</b> <code>{cus_name[0]}</code>\n"
												f"<b>Адреc: </b><code>{cus_adress}</code>\n\n"

												f"<b>Должность:</b> <code>{cus_position}</code>\n"
												f"<b>Время работы:</b> <code>{cus_work_day}</code>\n"
												f"<b>График:</b> <code>{cus_work_graphic}</code>\n"
												f"<b>Смена:</b> <code>{cus_bid}</code>\n\n"

												f"<b>Требование:</b>\n<code>{requirement}</code>\n\n"
												f"<b>Обязанности:</b>\n<code>{respons}</code>")
		await bot.send_message(c.from_user.id, "Ваше объявление готово, хотите ли Вы его опубликовать?",
												reply_markup = buttons.change_order)


async def cSkip_output_location(c: types.CallbackQuery, state: FSMContext):
	await CreateOrder.next()

	await bot.delete_message(c.from_user.id, c.message.message_id)
	
	# async with state.proxy() as data:
	# 	data['location_lat'] = data
	# 	data['location_long'] = message.location.longitude
	# 	data['adress_info'] = getLocationInfo.location_info(f"{data['location_long']} {data['location_lat']}")	
	# 	await CreateOrder.next()

	await bot.send_message(c.from_user.id, "Отправьте мне название должности.",
		reply_markup = buttons.skipBtn())



async def cSkip_output_position(c: types.CallbackQuery, state: FSMContext):
	await CreateOrder.next()

	await bot.delete_message(c.from_user.id, c.message.message_id)

	# async with state.proxy() as data:
	# 	data['position'] = message.text
	# 	await CreateOrder.next()

	await bot.send_message(c.from_user.id, "На какое кол-в дней Вам нужен сотрудник?",
		reply_markup = buttons.skipBtn())




async def cSkip_output_days(c: types.CallbackQuery, state: FSMContext):
	await CreateOrder.next()

	await bot.delete_message(c.from_user.id, c.message.message_id)
	await bot.send_message(c.from_user.id, "Отправьте мне график работы.",
		reply_markup = buttons.skipBtn())

	



async def cSkip_output_graphic(c: types.CallbackQuery, state: FSMContext):
	await CreateOrder.next()
	
	await bot.delete_message(c.from_user.id, c.message.message_id)
	await bot.send_message(c.from_user.id, "Отправьте сколько исполнитель получит за смену.",
		reply_markup = buttons.skipBtn())



async def cSkip_output_bid(c: types.CallbackQuery, state: FSMContext):
	await CreateOrder.next()

	await bot.delete_message(c.from_user.id, c.message.message_id)
	await bot.send_message(c.from_user.id, "Укажите требование к исполнителю, в таком формате:\n"
											" - Коммуникабельность;\n"
											" - Опыт работы с кассой;\n"
											" - Опыт от 1 года;",
												reply_markup = buttons.skipBtn())	



async def cSkip_output_requirement(c: types.CallbackQuery, state: FSMContext):
	await CreateOrder.next()	

	await bot.delete_message(c.from_user.id, c.message.message_id)
	await bot.send_message(c.from_user.id, "Укажите обязанности к исполнителю, в таком формате:\n"
											" - Обслуживание клиентов;\n"
											" - Работа с кассой;\n"
											" - Приём товар;",
												reply_markup = buttons.skipBtn())



async def cSkip_output_respons(c: types.CallbackQuery, state: FSMContext):
	await CreateOrder.next()	
	
	await bot.delete_message(c.from_user.id, c.message.message_id)
	await bot.send_message(c.from_user.id, "Укажите комментарий к вакансии, например особенности Вашей работы и т.д\n",
		reply_markup = buttons.skip_btn)



@checkStatus
async def process_get_publish(c: types.CallbackQuery, state: FSMContext):
	await bot.send_photo(
		chat_id = c.message.chat.id, 
		photo = file_ids.PHOTO['price'],
		caption = "<b>1.</b> <code>3</code> дня в ленте - <code>50.0</code> <code>₽</code>\n"
				  "<b>2.</b> <code>7</code> дней в ленте - <code>80.0</code> <code>₽</code>\n"
				  "<b>3.</b> <code>30</code> дней в ленте - <code>270.0</code> <code>₽</code>\n",
					reply_markup = buttons.menuPrice())


@checkStatus
async def process_pay_50(c: types.CallbackQuery, state: FSMContext):
	price = c.data[6:]
	user_id = c.from_user.id
	
	comment = (f"{user_id}_{random.randint(1000, 9999)}")
	bill = p2p.bill(amount=50, lifetime=15, comment=comment)

	await bot.send_message(c.from_user.id, f"<b>Информация по оплате</b>\n\n<b>Вы покупаете:</b> <code>3 дней в ленте</code>\n <b>К оплате:</b> <code>50.0 ₽</code>", reply_markup = buttons.showPayment(bill_id = bill.bill_id, url = bill.pay_url, price = price))


@checkStatus
async def process_pay_80(c: types.CallbackQuery, state: FSMContext):
	price = c.data[6:]
	user_id = c.from_user.id
	
	comment = (f"{user_id}_{random.randint(1000, 9999)}")
	bill = p2p.bill(amount=80, lifetime=15, comment=comment)

	await bot.send_message(c.from_user.id, f"<b>Информация по оплате</b>\n\n<b>Вы покупаете:</b> <code>7 дней в ленте</code>\n <b>К оплате:</b> <code>80.0 ₽</code>", reply_markup = buttons.showPayment(bill_id = bill.bill_id, url = bill.pay_url, price = price))


@checkStatus
async def process_pay_270(c: types.CallbackQuery, state: FSMContext):
	price = c.data[6:]
	user_id = c.from_user.id
	
	comment = (f"{user_id}_{random.randint(1000, 9999)}")
	bill = p2p.bill(amount=270, lifetime=15, comment=comment)

	await bot.send_message(c.from_user.id, f"<b>Информация по оплате</b>\n\n<b>Вы покупаете:</b> <code>30 дней в ленте</code>\n <b>К оплате:</b> <code>270.0 ₽</code>", reply_markup = buttons.showPayment(bill_id = bill.bill_id, url = bill.pay_url, price = price))


@checkStatus
async def check_payment(c: types.CallbackQuery, state: FSMContext):
	try:
		user_id = c.from_user.id
		ids = c.data[6:].split(',')
		bill = ids[0]
		price = ids[1]
		today = datetime.datetime.today()
		dmy = datetime.datetime.today().strftime('%d.%m.%Y')
			

		if str(p2p.check(bill_id = bill).status) == "PAID":
			async with state.proxy() as data:
				order_id = len(connection.selectOrders(user_id))
				cus_name = connection.getCustomerName(user_id)
				cus_adress = data['adress_info']
				cus_work_graphic = data['graphic']
				cus_work_day = data['days']
				cus_bid = data['bid']
				requirement = data['requirement']
				respons = data['respons']
				cus_position = data['position']
				cus_comment = data['comment']
				cus_lat = data['location_lat']
				cus_long = data['location_long']
				order_status = 'На модерации'

				connection.regResponses(user_id, order_id, None, None)

				await bot.delete_message(c.message.chat.id, c.message.message_id)

			connection.addPayment(c.from_user.id, price, dmy)
			connection.createNewOrder(user_id, cus_name[0], cus_adress, cus_work_graphic, cus_work_day, cus_bid, cus_position, cus_comment, cus_lat, cus_long, dmy, order_status, order_id, price, requirement, respons)

			await bot.answer_callback_query(c.id, show_alert = True, text = "🔔 <b>Уведомление:</b>\n\nПоздравляю, оплата прошла успешно!")
			await bot.send_message(c.from_user.id, "Главное меню", reply_markup = buttons.menu_customer)
			await state.finish()
		else:
			await bot.answer_callback_query(c.id, show_alert = True, text = "❗️Вы не оплатили счет!")

	except Exception as e:
		print(e)
		await bot.send_message(c.from_user.id, "Произошла неизвестная ошибка или утекли срок данных. Пожалуйста повторите попытку!")



def register_reg_order_handlers(dp: Dispatcher):
	dp.register_callback_query_handler(process_get_location, lambda c: c.data == 'create' or c.data == 'change',  state = '*')    
	dp.register_callback_query_handler(process_get_publish, lambda c: c.data == 'publish',  state = '*')

	dp.register_message_handler(process_output_location, content_types = ['location','venue'], state = CreateOrder.step1)
	dp.register_message_handler(process_output_position, state = CreateOrder.step2)
	dp.register_message_handler(process_output_days, state = CreateOrder.step3)
	dp.register_message_handler(process_output_graphic, state = CreateOrder.step4)
	dp.register_message_handler(process_output_bid, state = CreateOrder.step5)
	dp.register_message_handler(process_output_requirement, state = CreateOrder.step6)
	dp.register_message_handler(process_output_respons, state = CreateOrder.step7)
	dp.register_message_handler(process_output_comment_and_all_data, state = CreateOrder.step8)
	dp.register_callback_query_handler(process_output_without_comment, lambda c: c.data == 'skip', state = CreateOrder.step8)


	dp.register_callback_query_handler(process_pay_50, lambda c: c.data == 'price_50',  state = '*')
	dp.register_callback_query_handler(process_pay_80, lambda c: c.data == 'price_80',  state = '*')
	dp.register_callback_query_handler(process_pay_270, lambda c: c.data == 'price_270',  state = '*')
	dp.register_callback_query_handler(check_payment, lambda c: c.data.startswith('check'),  state = '*')


	dp.register_callback_query_handler(cSkip_output_location, lambda c: c.data == 'cSkip', state = CreateOrder.step1)
	dp.register_callback_query_handler(cSkip_output_position, lambda c: c.data == 'cSkip', state = CreateOrder.step2)
	dp.register_callback_query_handler(cSkip_output_days, lambda c: c.data == 'cSkip', state = CreateOrder.step3)
	dp.register_callback_query_handler(cSkip_output_graphic, lambda c: c.data == 'cSkip', state = CreateOrder.step4)
	dp.register_callback_query_handler(cSkip_output_bid, lambda c: c.data == 'cSkip', state = CreateOrder.step5)
	dp.register_callback_query_handler(cSkip_output_requirement, lambda c: c.data == 'cSkip', state = CreateOrder.step6)
	dp.register_callback_query_handler(cSkip_output_respons, lambda c: c.data == 'cSkip', state = CreateOrder.step7)
