import time
import datetime
import random

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from .. import connection, file_ids, buttons, config, getLocationInfo
from app.admin import admin_connection

bot = Bot(token=config.TOKEN, parse_mode = 'html')



class CreateOrder(StatesGroup):
	step1 = State()
	new_step = State()
	step2 = State()
	step3 = State()
	step4 = State()
	step5 = State()
	step6 = State()
	step7 = State()
	step8 = State()



def checkStatus(func):
	async def wrapper(c: types.CallbackQuery, state: FSMContext):
		if admin_connection.selectFromAdminTable()[0][1] == '🔴':
			await bot.send_message(c.from_user.id, "⚠️ Ошибка:\n\n"
												   "Функция временно отключена, идут технические работы. Приносим извинения за неудобства! 😢",
				reply_markup = buttons.menu_customer)
		else:
			return await func(c, state)
	return wrapper


@checkStatus
async def process_get_create_order(c: types.CallbackQuery, state: FSMContext):
	await c.answer()
	await c.message.delete()
	await bot.send_photo(
		chat_id = c.from_user.id,
		photo = file_ids.PHOTO_ADMIN['publication_rules'],
		caption = "- Объявление остаётся в ленте на выбранное Вами время, мы оставляем за собой право отказать в публикации объявления в случае мошенничества или маскировки под вакансию рекламы и работы, запрещенной законом (Закладки, Операторы наркочатов).\n\n"
				  "- В публикации объявления может быть отказано если в нём присутствует ненормативная лексика.\n\n"
				  "- Также можем отказать в публикации сомнительного объявления (По мнению модерации).",
			reply_markup = buttons.get_understand()
		)


@checkStatus
async def process_ask_type_publication(c: types.CallbackQuery, state: FSMContext):
	await c.message.delete()
	await c.message.answer("Вам нужен исполнитель для разовой задачи или же вы хотите найти в запас?",
		reply_markup = buttons.order_type_btns())


@checkStatus
async def process_get_location(c: types.CallbackQuery, state: FSMContext):
	await c.message.delete()
	await CreateOrder.step1.set()

	async with state.proxy() as data:
		if c.data == 'stock':
			data['order_type'] = 'stock'

		elif c.data == 'on_time':
			data['order_type'] = 'on_time'

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
	async with state.proxy() as data:
		if data['order_type'] == 'stock':
			await CreateOrder.next()

		else:
			await CreateOrder.step2.set()

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
async def process_output_payment_for_waiting(message: types.Message, state: FSMContext):
	await CreateOrder.next()

	try:
		async with state.proxy() as data:
			comment = data['comment']
			data['position'] = message.text
			
			await bot.send_message(message.chat.id, "Отправьте мне сколько вы будете платить за 1 день ожидание.",
				reply_markup = buttons.skipBtn())


	except:
		async with state.proxy() as data:
			data['position'] = message.text

			await bot.send_message(message.chat.id, "Отправьте мне сколько вы будете платить за 1 день ожидание.")

@checkStatus
async def process_output_position(message: types.Message, state: FSMContext):
	try:
		async with state.proxy() as data:
			if data['order_type'] == 'stock':
				if message.text.isdigit():
					comment = data['comment']
					data['payment_for_waiting'] = message.text
					
					await bot.send_message(message.chat.id, "Отправьте мне график работы.", reply_markup = buttons.skipBtn())
					await CreateOrder.step4.set()		
				else:
					await message.answer("Введите только цифрами!")

			else:
				async with state.proxy() as data:
					comment = data['comment']
					data['position'] = message.text
					
					await bot.send_message(message.chat.id, "На какое кол-в дней вам нужен сотрудник?", reply_markup = buttons.skipBtn())
					await CreateOrder.next()				


	except:
		if data['order_type'] == 'stock':	
			if message.text.isdigit():
				async with state.proxy() as data:
					data['payment_for_waiting'] = message.text

					await bot.send_message(message.chat.id, "Отправьте мне график работы.")
					await CreateOrder.step4.set()				

			else:
				await message.answer("Введите только цифрами!")
		
		else:
			async with state.proxy() as data:
				data['position'] = message.text

				await bot.send_message(message.chat.id, "На какое кол-в дней вам нужен сотрудник?")
				await CreateOrder.next()				


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
		cus_bid = data['bid']
		requirement = data['requirement']
		respons = data['respons']
		cus_position = data['position']
		cus_comment = data['comment']
		cus_lat = data['location_lat']
		cus_long = data['location_long']

		if data['order_type'] == 'stock':
			await bot.send_message(message.chat.id, f"<b>Заказчик:</b> <code>{cus_name[0]}</code>\n"
													f"<b>Адреc: </b><code>{cus_adress}</code>\n\n"

													f"<b>Должность:</b> <code>{cus_position}</code>\n"
													f"<b>Ожидание:</b> <code>{data['payment_for_waiting']}₽/1 день</code>\n"
													f"<b>График:</b> <code>{cus_work_graphic}</code>\n"
													f"<b>Смена:</b> <code>{cus_bid}</code>\n\n"

													f"<b>Требование:</b>\n<code>{requirement}</code>\n\n"
													f"<b>Обязанности:</b>\n<code>{respons}</code>\n\n"

													f"{data['comment']}")
			await bot.send_message(message.chat.id, "Ваше объявление готово, хотите ли Вы его опубликовать?",
													reply_markup = buttons.change_order)

		
		elif data['order_type'] == 'on_time':
			cus_work_day = data['days']
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
		
		cus_bid = data['bid']
		requirement = data['requirement']
		respons = data['respons']
		cus_position = data['position']
		cus_comment = data['comment']
		cus_lat = data['location_lat']
		cus_long = data['location_long']

		if data['order_type'] == 'stock':
			await bot.send_message(c.from_user.id, f"<b>Заказчик:</b> <code>{cus_name[0]}</code>\n"
													f"<b>Адреc: </b><code>{cus_adress}</code>\n\n"

													f"<b>Должность:</b> <code>{cus_position}</code>\n"
													f"<b>Ожидание:</b> <code>{data['payment_for_waiting']}₽/1 день</code>\n"
													f"<b>График:</b> <code>{cus_work_graphic}</code>\n"
													f"<b>Смена:</b> <code>{cus_bid}</code>\n\n"

													f"<b>Требование:</b>\n<code>{requirement}</code>\n\n"
													f"<b>Обязанности:</b>\n<code>{respons}</code>")
			await bot.send_message(c.from_user.id, "Ваше объявление готово, хотите ли Вы его опубликовать?",
													reply_markup = buttons.change_order)


		elif data['order_type'] == 'on_time':
			cus_work_day = data['days']
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

	await c.message.delete()
	await bot.delete_message(c.from_user.id, c.message.message_id-1)

	await bot.send_message(c.from_user.id, "Отправьте мне название должности.",
		reply_markup = buttons.skipBtn())


async def cSkip_output_payment_for_waiting(c: types.CallbackQuery, state: FSMContext):
	await CreateOrder.next()

	await c.message.delete()
	await bot.send_message(c.from_user.id, "Отправьте мне сколько вы будете платить за 1 день ожидание.",
		reply_markup = buttons.skipBtn())



async def cSkip_output_position(c: types.CallbackQuery, state: FSMContext):
	await CreateOrder.next()

	await bot.delete_message(c.from_user.id, c.message.message_id)
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
	await c.answer()
	try:
		async with state.proxy() as data:
			if data['order_type'] == 'stock':
				allowance = int(data['payment_for_waiting'])

				frst = int(admin_connection.selectIcs('ic_stock', 1)[0])

				total_1 = allowance*30+frst*30
				total_2 = allowance*90+frst*90
				total_3 = allowance*180+frst*180

				await bot.send_photo(
					chat_id = c.message.chat.id, 
					photo = file_ids.PHOTO['price'],
					caption = f"<b>1.</b> <code>30</code> дня в ленте - <code>{total_1}</code> <code>₽</code>\n"
							  f"<b>2.</b> <code>90</code> дней в ленте - <code>{total_2}</code> <code>₽</code>\n"
							  f"<b>3.</b> <code>180</code> дней в ленте - <code>{total_3}</code> <code>₽</code>\n",
								reply_markup = buttons.menuPrice(total_1, total_2, total_3))
			
			elif data['order_type'] == 'on_time':
				frst = int(admin_connection.selectIcs('ic_one_time', 1)[0])
				scnd = int(admin_connection.selectIcs('ic_one_time', 2)[0])
				thrd = int(admin_connection.selectIcs('ic_one_time', 3)[0])

				total_1 = frst*3
				total_2 = scnd*7
				total_3 = thrd*30

				await bot.send_photo(
					chat_id = c.message.chat.id, 
					photo = file_ids.PHOTO['price'],
					caption = f"<b>1.</b> <code>3</code> дня в ленте - <code>{total_1}</code> <code>₽</code>\n"
							  f"<b>2.</b> <code>7</code> дней в ленте - <code>{total_2}</code> <code>₽</code>\n"
							  f"<b>3.</b> <code>30</code> дней в ленте - <code>{total_3}</code> <code>₽</code>\n",
								reply_markup = buttons.menuPrice(total_1, total_2, total_3, is_stock = False))

	except KeyError:
		await c.message.delete()
		await bot.delete_message(c.from_user.id, c.message.message_id-1)


@checkStatus
async def process_pay(c: types.CallbackQuery, state: FSMContext):
	await c.answer()
	try:
		async with state.proxy() as data:
			if data['order_type'] == 'stock':
				ids = c.data[6:].split(',')
				days = ids[0]
				total = ids[1]
				async with state.proxy() as data:
					data['actual_days'] = days
				
					await bot.send_message(c.from_user.id, f"<b>Информация по оплате</b>\n\n<b>Вы покупаете:</b> <code>{days} дней в ленте</code>\n <b>К оплате:</b> <code>{total} ₽</code>", 
						reply_markup = buttons.to_pay(total))
			
			elif data['order_type'] == 'on_time':
				ids = c.data[6:].split(',')
				days = ids[0]
				total = ids[1]
				async with state.proxy() as data:
					data['actual_days'] = days
				
					await bot.send_message(c.from_user.id, f"<b>Информация по оплате</b>\n\n<b>Вы покупаете:</b> <code>{days} дней в ленте</code>\n <b>К оплате:</b> <code>{total} ₽</code>", 
						reply_markup = buttons.to_pay(total))			

	except Exception as e:
		print(e)
		await c.message.delete()


async def check_payment(c: types.CallbackQuery, state: FSMContext):
	try:
		user_id = c.from_user.id
		price = int(c.data[10:])
		today = datetime.datetime.today()
		# dmy = datetime.datetime.today().strftime('%d.%m.%Y')
		user_balance = int(connection.get_id(user_id)[6])
			

		if user_balance >= price:
			async with state.proxy() as data:
				order_id = len(connection.selectOrders(user_id))
				cus_name = connection.getCustomerName(user_id)
				cus_adress = data['adress_info']
				cus_work_graphic = data['graphic']
				cus_bid = data['bid']
				requirement = data['requirement']
				respons = data['respons']
				cus_position = data['position']
				cus_comment = data['comment']
				cus_lat = data['location_lat']
				cus_long = data['location_long']
				order_status = 'На модерации'
				actual_days = data['actual_days']
				order_type = data['order_type']
				from_id = connection.getMyFromId(user_id)

				await bot.delete_message(c.message.chat.id, c.message.message_id)

				# if data['order_type'] == 'stock':
				# 	frst = int(admin_connection.selectIcs('ic_stock', 1)[0])
					
				# 	if actual_days == '30':
				# 		comission = frst * 30

				# 	elif actual_days == '90':
				# 		comission = frst * 90
					
				# 	elif actual_days == '180':
				# 		comission = frst * 180

				# elif data['order_type'] == 'on_time':
				# 	cus_work_day = data['days']

				# 	frst = int(admin_connection.selectIcs('ic_one_time', 1)[0])
				# 	scnd = int(admin_connection.selectIcs('ic_one_time', 2)[0])
				# 	thrd = int(admin_connection.selectIcs('ic_one_time', 3)[0])

				# 	if actual_days == '3':
				# 		comission = frst * 3

				# 	elif actual_days == '7':
				# 		comission = scnd * 7
						
				# 	elif actual_days == '30':
				# 		comission = thrd * 30
						

			connection.updateBalance(user_id, price, '-')
			if data['order_type'] == 'stock':
				connection.createNewOrder(user_id, cus_name[0], cus_adress, cus_work_graphic, None, cus_bid, cus_position, cus_comment, 
					cus_lat, cus_long, today, order_status, order_id, price, requirement, respons, actual_days, order_type, data['payment_for_waiting'])

			else:
				connection.createNewOrder(user_id, cus_name[0], cus_adress, cus_work_graphic, cus_work_day, cus_bid, cus_position, cus_comment, 
					cus_lat, cus_long, today, order_status, order_id, price, requirement, respons, actual_days, order_type, None)				

			await bot.send_message(c.from_user.id,  "🔔 <b>Уведомление:</b>\n\n"
													"Оплата прошла успешно! Объявление отправлено на модерацию, отследить его можно в \"Мои заказы\"", 
														reply_markup = buttons.autoMenu(connection.checkUserStatus(c.from_user.id)[0]))
			await state.finish()
		else:
			await bot.answer_callback_query(c.id, show_alert = True, text = "⚠️ Ошибка:\n\n"
																		    "У вас недостаточно средств")

	except Exception as e:
		print(e)
		await bot.send_message(c.from_user.id, "Произошла неизвестная ошибка или утекли срок данных. Пожалуйста повторите попытку!")



def register_reg_order_handlers(dp: Dispatcher):
	dp.register_callback_query_handler(process_get_create_order, lambda c: c.data == 'get_create',  state = '*')
	dp.register_callback_query_handler(process_ask_type_publication, lambda c: c.data == 'ok_understand', state = '*')    
	dp.register_callback_query_handler(process_get_location, lambda c: c.data == 'stock' or c.data == 'on_time' or c.data == 'change',  state = '*')    
	dp.register_callback_query_handler(process_get_publish, lambda c: c.data == 'publish',  state = '*')

	dp.register_message_handler(process_output_location, content_types = ['location','venue'], state = CreateOrder.step1)
	dp.register_message_handler(process_output_payment_for_waiting,  state = CreateOrder.new_step)
	dp.register_message_handler(process_output_position, state = CreateOrder.step2)
	dp.register_message_handler(process_output_days, state = CreateOrder.step3)
	dp.register_message_handler(process_output_graphic, state = CreateOrder.step4)
	dp.register_message_handler(process_output_bid, state = CreateOrder.step5)
	dp.register_message_handler(process_output_requirement, state = CreateOrder.step6)
	dp.register_message_handler(process_output_respons, state = CreateOrder.step7)
	dp.register_message_handler(process_output_comment_and_all_data, state = CreateOrder.step8)
	dp.register_callback_query_handler(process_output_without_comment, lambda c: c.data == 'skip', state = CreateOrder.step8)

	dp.register_callback_query_handler(process_pay, lambda c: c.data.startswith('price'),  state = '*')
	dp.register_callback_query_handler(check_payment, lambda c: c.data.startswith('pay_order'),  state = '*')

	dp.register_callback_query_handler(cSkip_output_location, lambda c: c.data == 'cSkip', state = CreateOrder.step1)
	dp.register_callback_query_handler(cSkip_output_payment_for_waiting, lambda c: c.data == 'cSkip',  state = CreateOrder.new_step)
	dp.register_callback_query_handler(cSkip_output_position, lambda c: c.data == 'cSkip', state = CreateOrder.step2)
	dp.register_callback_query_handler(cSkip_output_days, lambda c: c.data == 'cSkip', state = CreateOrder.step3)
	dp.register_callback_query_handler(cSkip_output_graphic, lambda c: c.data == 'cSkip', state = CreateOrder.step4)
	dp.register_callback_query_handler(cSkip_output_bid, lambda c: c.data == 'cSkip', state = CreateOrder.step5)
	dp.register_callback_query_handler(cSkip_output_requirement, lambda c: c.data == 'cSkip', state = CreateOrder.step6)
	dp.register_callback_query_handler(cSkip_output_respons, lambda c: c.data == 'cSkip', state = CreateOrder.step7)
