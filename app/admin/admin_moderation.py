import datetime

from app.admin import admin_buttons, admin_connection
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from .. import config, connection, file_ids, buttons, getLocationInfo


bot = Bot(token=config.TOKEN, parse_mode = 'html')


class EditOrder(StatesGroup):
	step1 = State()
	step2 = State()
	step3 = State()
	step4 = State()
	step5 = State()
	step6 = State()
	step7 = State()
	step8 = State()
	step9 = State()


class EditCustomerProfil(StatesGroup):
	step1 = State()
	step2 = State()
	step3 = State()
	step4 = State()


class EditExecutorProfil(StatesGroup):
	step1 = State()
	step2 = State()
	step3 = State()
	step4 = State()
	step5 = State()


class ProcessCDelete(StatesGroup):
	step1 = State()
	step2 = State()
	step3 = State()
	step4 = State()


async def order_requests(c: types.CallbackQuery, state: FSMContext):
	admin_id = c.from_user.id

	try:
		connection.nullPagination(admin_id)
		pag = connection.selectPag(admin_id)
		orders = admin_connection.selectOrdersWhereInModeration()[pag]

		await bot.send_message(c.from_user.id, 'Все объявления которое находятся на модерации:', reply_markup = admin_buttons.admin_canc())
		await bot.send_message(c.from_user.id, 
			f"<b>Заказчик:</b> <code>{orders[1]}</code>\n"
			f"<b>Адрес:</b> <code>{orders[2]}</code>\n\n"
			f"<b>Должность:</b> <code>{orders[6]}</code>\n"
            f"{connection.checkOrderType(orders[-2], orders)}"

			# f"<b>Время работы:</b> <code>{orders[4]}</code>\n"
			f"<b>График:</b> <code>{orders[3]}</code>\n"
			f"<b>Смена:</b> <code>{orders[5]}</code>\n\n"
			
			f"<b>Требование:</b>\n<code>{orders[14]}</code>\n\n"
			f"<b>Обязанности:</b>\n<code>{orders[15]}</code>\n\n"

			f"{orders[7]}",
				reply_markup = admin_buttons.requestOrderBtns(orders[0], orders[12]))
		await c.answer()
		
	except Exception as e:
		print(e)
		await bot.answer_callback_query(c.id, show_alert = True, text = "Ничего не найдено")	


async def callbackToBack(c: types.CallbackQuery, state: FSMContext):
	try:
		async with state.proxy() as data:
			user_id = c.from_user.id	
			connection.backPagination(user_id)
			pag = connection.selectPag(user_id)
			orders = admin_connection.selectOrdersWhereInModeration()[pag]

		if pag < 0:
			connection.nextPagination(user_id)
			await bot.answer_callback_query(c.id, show_alert = False, text = "❗️Вы находитесь на первом каталоге списка")	

		else:
			await bot.edit_message_text(chat_id = c.message.chat.id, 	
									message_id = c.message.message_id,
									text =	f"<b>Заказчик:</b> <code>{orders[1]}</code>\n"
											f"<b>Адрес:</b> <code>{orders[2]}</code>\n\n"
											f"<b>Должность:</b> <code>{orders[6]}</code>\n"
								            f"{connection.checkOrderType(orders[-2], orders)}"
											# f"<b>Время работы:</b> <code>{orders[4]}</code>\n"
											f"<b>График:</b> <code>{orders[3]}</code>\n"
											f"<b>Смена:</b> <code>{orders[5]}</code>\n\n"
													
											f"<b>Требование:</b>\n<code>{orders[14]}</code>\n\n"
											f"<b>Обязанности:</b>\n<code>{orders[15]}</code>\n\n"

											f"{orders[7]}",
												reply_markup = admin_buttons.requestOrderBtns(orders[0], orders[12]))
	except:
		await bot.answer_callback_query(c.id, show_alert = False, text = "❗️Вы находитесь на первом каталоге списка")	


async def callbackToNext(c: types.CallbackQuery, state: FSMContext):
	try:
		async with state.proxy() as data:
			user_id = c.from_user.id
			connection.nextPagination(user_id)
			pag = connection.selectPag(user_id)
			orders = admin_connection.selectOrdersWhereInModeration()[pag]

		await bot.edit_message_text(chat_id = c.message.chat.id, 	
							message_id = c.message.message_id,
							text = 	f"<b>Заказчик:</b> <code>{orders[1]}</code>\n"
									f"<b>Адрес:</b> <code>{orders[2]}</code>\n\n"
									
									f"<b>Должность:</b> <code>{orders[6]}</code>\n"
						            f"{connection.checkOrderType(orders[-2], orders)}"
									# f"<b>Время работы:</b> <code>{orders[4]}</code>\n"
									f"<b>График:</b> <code>{orders[3]}</code>\n"
									f"<b>Смена:</b> <code>{orders[5]}</code>\n\n"
			
									f"<b>Требование:</b>\n<code>{orders[14]}</code>\n\n"
									f"<b>Обязанности:</b>\n<code>{orders[15]}</code>\n\n"

									f"{orders[7]}",
										reply_markup = admin_buttons.requestOrderBtns(orders[0], orders[12]))
	except IndexError:
		connection.backPagination(user_id)
		await bot.answer_callback_query(c.id, show_alert = False, text = "❗️Вы находитесь на последнем каталоге списка")


def pay_to_refferal(cus_id, comission):
	from_id = connection.getMyFromId(cus_id)
	today = datetime.datetime.today()
	
	try:
		if from_id.isdigit():
			connection.addActiveReferral(from_id)
			connection.addBotPayment(from_id, 'refferal', comission/100*7, today)
			connection.updateBalance(from_id, comission/100*7, '+')
			connection.setActiveUser(cus_id)
			print(comission)
	except Exception as e:
		print(e)
		return None


# ----APPROVE----
async def callbackApprove(c: types.CallbackQuery, state: FSMContext):
	ids = c.data[10:].split(',')
	cus_id = ids[0]
	order_id = ids[1]
	comission = 0
	today = datetime.datetime.today()
	order_data = connection.selectOrderWhereCusId(cus_id, order_id)

	if connection.selectOrderWhereCusId(cus_id, order_id)[11] == 'Отклонён':
		await c.answer("⚠️ Ошибка:\n\nЭтот заказ уже oтклонён")


	else:
		if connection.selectOrderWhereCusId(cus_id, order_id)[11] == 'На модерации':
			actual_days = int(connection.selectOrderWhereCusId(cus_id, order_id)[16])
			deletion_date = today + datetime.timedelta(days=actual_days)
			connection.UpdateOrderStatus(cus_id, order_id, "Опубликован", str(deletion_date.strftime("%#Y, %#m, %#d, %#H, %#M")))
			admin_connection.addView('ads', today)

			if order_data[-2] == 'stock':
				frst = int(admin_connection.selectIcs('ic_stock', 1)[0])
				connection.addPayment(cus_id, 'profit', frst*actual_days, today)
				connection.addPayment(cus_id, 'to_order', order_data[-6], today)
				connection.regResponses(cus_id, order_id, None, None, order_data[-2], actual_days*int(order_data[-1]))
				# pay_to_refferal(cus_id, frst*actual_days)
				pay_to_refferal(cus_id, 10)


			elif order_data[-2] == 'on_time':
				frst = int(admin_connection.selectIcs('ic_one_time', 1)[0])
				scnd = int(admin_connection.selectIcs('ic_one_time', 2)[0])
				thrd = int(admin_connection.selectIcs('ic_one_time', 3)[0])

				if actual_days == 3:
					# comission = frst * 3
					connection.addPayment(cus_id, 'profit', 3, today)
					connection.regResponses(cus_id, order_id, None, None, order_data[-2], None)
					# pay_to_refferal(cus_id, 3)
					pay_to_refferal(cus_id, 10)


				elif actual_days == 7:
					# comission = scnd * 7
					connection.addPayment(cus_id, 'profit', comission, today)
					connection.regResponses(cus_id, order_id, None, None, order_data[-2], None)
					# pay_to_refferal(cus_id, comission)
					pay_to_refferal(cus_id, 10)

					
				elif actual_days == 30:
					# comission = thrd * 30
					connection.addPayment(cus_id, 'profit', comission, today)
					connection.regResponses(cus_id, order_id, None, None, order_data[-2], None)
					# pay_to_refferal(cus_id, comission)
					pay_to_refferal(cus_id, 10)

			
			await c.message.delete()
			await bot.delete_message(c.from_user.id, c.message.message_id-1)
			await bot.answer_callback_query(c.id, show_alert = True, text = "✅ Этот заказ опубликован")
			await bot.send_message(c.from_user.id, "Админ панель", reply_markup = admin_buttons.adminPanel())

		else:
			actual_days = int(connection.selectOrderWhereCusId(cus_id, order_id)[16])
			deletion_date = today + datetime.timedelta(days=actual_days)
			connection.UpdateOrderStatus(cus_id, order_id, "Опубликован", str(deletion_date.strftime("%#Y, %#m, %#d, %#H, %#M")))
			
			await c.message.delete()
			await bot.answer_callback_query(c.id, show_alert = True, text = "✅ Этот заказ опубликован")
			await bot.send_message(c.from_user.id, "Админ панель", reply_markup = admin_buttons.adminPanel())


async def callbackReject(c: types.CallbackQuery, state: FSMContext):
	ids = c.data[9:].split(',')
	cus_id = ids[0]
	order_id = ids[1]
	price = connection.selectOrderWhereCusId(cus_id, order_id)[13]

	if connection.selectOrderWhereCusId(cus_id, order_id)[11] == 'Опубликован':
		await c.answer("⚠️ Ошибка:\n\nЭтот заказ уже опубликован")

	else:
		connection.UpdateOrderStatus(cus_id, order_id, "Отклонён", None)
		connection.updateBalance(cus_id, price, '+')
		connection.deletePayment(cus_id, price)
		admin_connection.addView('ads', datetime.datetime.today().strftime('%d.%m.%Y'))

		await bot.answer_callback_query(c.id, show_alert = True, text = "🗑 Этот заказ отклонён")


# ------To Edit------
async def callbackEdit(c: types.CallbackQuery, state: FSMContext):
	ids = c.data[7:].split(',')
	cus_id = ids[0]
	order_id = ids[1]
	order_type = connection.selectOrderWhereCusId(cus_id, order_id)[-2]

	if connection.selectOrderWhereCusId(cus_id, order_id)[11] == 'Опубликован':
		await c.answer("⚠️ Ошибка:\n\nЭтот заказ уже опубликован")

	elif connection.selectOrderWhereCusId(cus_id, order_id)[11] == 'Отклонён':
		await c.answer("⚠️ Ошибка:\n\nЭтот заказ уже oтклонён")

	else:
		async with state.proxy() as data:
			data['cus_id'] = cus_id
			data['order_id'] = order_id
			data['order_type'] = order_type

		await EditOrder.step1.set()
		await bot.send_message(c.message.chat.id, ".", 
			reply_markup = buttons.send_geo)
		await bot.send_message(c.message.chat.id, "Отправьте мне <b>адрес места работы</b>, для корректного поиска исполнителей.", 
			reply_markup = admin_buttons.skipBtn())


async def process_output_location(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['location_lat'] = message.location.latitude
		data['location_long'] = message.location.longitude
		data['adress_info'] = getLocationInfo.location_info(f"{data['location_long']} {data['location_lat']}")	
		await EditOrder.next()
		
		await bot.send_message(message.chat.id, ".", 
			reply_markup = admin_buttons.admin_canc())
		await bot.send_message(message.chat.id, "- Отправьте мне <b>название должности.</b>", 
			reply_markup = admin_buttons.skipBtn())


async def process_output_position(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['position'] = message.text
		await EditOrder.next()

		if data['order_type'] == 'stock':
			await message.answer("Отправьте мне сколько вы будете платить за 1 день ожидание.",
				reply_markup = admin_buttons.skipBtn())	

		else:
			await bot.send_message(message.chat.id, "- На какое <b>кол-в дней</b> вам нужен сотрудник?",
				reply_markup = admin_buttons.skipBtn())


async def process_output_days(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		if data['order_type'] == 'stock':
			if message.text.isdigit():
				await EditOrder.next()
				data['payment_for_waiting'] = message.text
				data['days'] = None
				await message.answer("- Отправьте мне <b>график работы.</b>", reply_markup = admin_buttons.skipBtn())
			else:
				await message.answer("Введите только цифрами!")

		else:
			await EditOrder.next()
			data['days'] = message.text
			data['payment_for_waiting'] = None
			await message.answer("- Отправьте мне <b>график работы.</b>", reply_markup = admin_buttons.skipBtn())


async def process_output_graphic(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['graphic'] = message.text
		await EditOrder.next()

		await bot.send_message(message.chat.id, "- Отправьте сколько исполнитель получит за <b>смену.</b>",
			reply_markup = admin_buttons.skipBtn())	


async def process_output_bid(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['bid'] = message.text
		await EditOrder.next()

		await bot.send_message(message.chat.id, "- Укажите <b>требование</b> к исполнителю, в таком формате:\n"
												" - Коммуникабельность;\n"
												" - Опыт работы с кассой;\n"
												" - Опыт от 1 года;",
			reply_markup = admin_buttons.skipBtn())


async def process_output_requirement(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['requirement'] = message.text
		await EditOrder.next()

		await bot.send_message(message.chat.id, "- Укажите <b>обязанности</b> к исполнителю, в таком формате:\n"
												" - Обслуживание клиентов;\n"
												" - Работа с кассой;\n"
												" - Приём товар;",
			reply_markup = admin_buttons.skipBtn())


async def process_output_respons(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['respons'] = message.text
		await EditOrder.next()

		await bot.send_message(message.chat.id, "- Укажите <b>комментарий к вакансии</b>, например особенности вашей работы и т.д\n", 
			reply_markup = buttons.skip_btn)


async def process_output_comment_and_all_data(message: types.Message, state: FSMContext):
	today = datetime.datetime.today().strftime('%d.%m.%Y')

	async with state.proxy() as data:
		data['comment'] = f"<b>Комментарий:</b>\n<code>{message.text}</code>"

		order_id = data['order_id']
		cus_id = data['cus_id']
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
		payment_for_waiting = data['payment_for_waiting']

		if data['order_type'] == 'stock':
			text = f"<b>Ожидание:</b> <code>{payment_for_waiting}₽/1 день</code>\n"
		else:
			text = f"<b>Время работы:</b> <code>{cus_work_day}</code>\n"


		await bot.send_message(message.chat.id, f"<b>Заказчик:</b> <code>{cus_name[0]}</code>\n"
												f"<b>Адреc: </b><code>{cus_adress}</code>\n\n"

												f"<b>Должность:</b> <code>{cus_position}</code>\n"
												f"{text}"
												f"<b>График:</b> <code>{cus_work_graphic}</code>\n"
												f"<b>Смена:</b> <code>{cus_bid}</code>\n\n"

												f"<b>Требование:</b>\n<code>{requirement}</code>\n\n"
												f"<b>Обязанности:</b>\n<code>{respons}</code>\n\n"

												f"{data['comment']}")
		await bot.send_message(message.chat.id, "Ваше <b>объявление готово</b>, хотите ли вы его опубликовать?", 
												reply_markup = admin_buttons.settingsOrderBtns(cus_id, order_id))


async def process_output_without_comment(c: types.CallbackQuery, state: FSMContext):
	await bot.delete_message(c.from_user.id, c.message.message_id)
	today = datetime.datetime.today().strftime('%d.%m.%Y')

	async with state.proxy() as data:
		data['comment'] = ''
		cus_id = data['cus_id']		
		order_id = data['order_id']
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
		payment_for_waiting = data['payment_for_waiting']	
		
		if data['order_type'] == 'stock':
			text = f"<b>Ожидание:</b> <code>{payment_for_waiting}₽/1 день</code>\n"
		else:
			text = f"<b>Время работы:</b> <code>{cus_work_day}</code>\n"

		await bot.send_message(c.from_user.id, f"<b>Заказчик:</b> <code>{cus_name[0]}</code>\n"
												f"<b>Адреc: </b><code>{cus_adress}</code>\n\n"

												f"<b>Должность:</b> <code>{cus_position}</code>\n"
												f"{text}"
												f"<b>График:</b> <code>{cus_work_graphic}</code>\n"
												f"<b>Смена:</b> <code>{cus_bid}</code>\n\n"

												f"<b>Требование:</b>\n<code>{requirement}</code>\n\n"
												f"<b>Обязанности:</b>\n<code>{respons}</code>")
		await bot.send_message(c.from_user.id, "Ваше объявление готово, хотите ли вы его опубликовать?", 
												reply_markup = admin_buttons.settingsOrderBtns(cus_id, order_id))



async def callbackPublish(c: types.CallbackQuery, state: FSMContext):
	await c.answer()

	async with state.proxy() as data:
		order_id = data['order_id']
		cus_id = data['cus_id']
		cus_name = connection.getCustomerName(cus_id)[0]
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
		payment_for_waiting = data['payment_for_waiting']	


		await bot.delete_message(c.message.chat.id, c.message.message_id)
	
	admin_connection.addView('ads', datetime.datetime.today().strftime('%d.%m.%Y'))
	connection.UpdateOrder(cus_id, order_id, cus_name, cus_adress, cus_work_graphic, cus_work_day, cus_bid, 
		cus_position, cus_comment, cus_lat, cus_long, requirement, respons, payment_for_waiting)

	await bot.send_message(c.from_user.id, "🔔 <b>Уведомление:</b>\n\nПоздравляю, <b>заказ</b> успешно отредактирован! 🥳", reply_markup = admin_buttons.adminPanel())
	await state.finish()


async def callback_output_location(c: types.CallbackQuery, state: FSMContext):
	await bot.delete_message(c.from_user.id, c.message.message_id)
	await EditOrder.next()
	
	async with state.proxy() as data:
		cus_id = data['cus_id']
		order_id = data['order_id']
		order = connection.selectOrderWhereCusId(cus_id, order_id)

		data['location_lat'] = order[8]
		data['location_long'] = order[9]
		data['adress_info'] = order[2]	

		await bot.send_message(c.from_user.id, ".", 
			reply_markup = admin_buttons.admin_canc())
		await bot.send_message(c.from_user.id, "- Отправьте мне <b>название должности.</b>", 
			reply_markup = admin_buttons.skipBtn())


async def callback_output_position(c: types.CallbackQuery, state: FSMContext):
	await bot.delete_message(c.from_user.id, c.message.message_id)
	await EditOrder.next()
	
	async with state.proxy() as data:
		cus_id = data['cus_id']
		order_id = data['order_id']
		order = connection.selectOrderWhereCusId(cus_id, order_id)

		data['position'] = order[6]

		if data['order_type'] == 'stock':
			await c.message.answer("Отправьте мне сколько вы будете платить за 1 день ожидание.",
				reply_markup = admin_buttons.skipBtn())	

		else:
			await c.message.answer("- На какое <b>кол-в дней</b> вам нужен сотрудник?",
				reply_markup = admin_buttons.skipBtn())


async def callback_output_days(c: types.CallbackQuery, state: FSMContext):
	await bot.delete_message(c.from_user.id, c.message.message_id)
	await EditOrder.next()

	async with state.proxy() as data:
		cus_id = data['cus_id']
		order_id = data['order_id']
		order = connection.selectOrderWhereCusId(cus_id, order_id)
		
		if data['order_type'] == 'stock':
			data['payment_for_waiting'] = order[-1]
			data['days'] = None

		else:
			data['days'] = order[4]
			data['payment_for_waiting'] = None

		await bot.send_message(c.from_user.id, "- Отправьте мне <b>график работы.</b>",
			reply_markup = admin_buttons.skipBtn())


async def callback_output_graphic(c: types.CallbackQuery, state: FSMContext):
	await bot.delete_message(c.from_user.id, c.message.message_id)
	await EditOrder.next()

	async with state.proxy() as data:
		cus_id = data['cus_id']
		order_id = data['order_id']
		order = connection.selectOrderWhereCusId(cus_id, order_id)

		data['graphic'] = order[3]

		await bot.send_message(c.from_user.id, "- Отправьте сколько исполнитель получит за <b>смену.</b>",
			reply_markup = admin_buttons.skipBtn())	


async def callback_output_bid(c: types.CallbackQuery, state: FSMContext):
	await bot.delete_message(c.from_user.id, c.message.message_id)
	await EditOrder.next()

	async with state.proxy() as data:
		cus_id = data['cus_id']
		order_id = data['order_id']
		order = connection.selectOrderWhereCusId(cus_id, order_id)

		data['bid'] = order[5]

		await bot.send_message(c.from_user.id, "- Укажите <b>требование</b> к исполнителю, в таком формате:\n"
												" - Коммуникабельность;\n"
												" - Опыт работы с кассой;\n"
												" - Опыт от 1 года;",
			reply_markup = admin_buttons.skipBtn())


async def callback_output_requirement(c: types.CallbackQuery, state: FSMContext):
	await bot.delete_message(c.from_user.id, c.message.message_id)
	await EditOrder.next()

	async with state.proxy() as data:
		cus_id = data['cus_id']
		order_id = data['order_id']
		order = connection.selectOrderWhereCusId(cus_id, order_id)

		data['requirement'] = order[14]

		await bot.send_message(c.from_user.id, "- Укажите <b>обязанности</b> к исполнителю, в таком формате:\n"
												" - Обслуживание клиентов;\n"
												" - Работа с кассой;\n"
												" - Приём товар;",
			reply_markup = admin_buttons.skipBtn())


async def callback_output_respons(c: types.CallbackQuery, state: FSMContext):
	await bot.delete_message(c.from_user.id, c.message.message_id)
	await EditOrder.next()

	async with state.proxy() as data:
		cus_id = data['cus_id']
		order_id = data['order_id']
		order = connection.selectOrderWhereCusId(cus_id, order_id)

		data['respons'] = order[15]

		await bot.send_message(c.from_user.id, "- Укажите <b>комментарий к вакансии</b>, например особенности вашей работы и т.д\n", 
			reply_markup = buttons.skip_btn)


# -------------PROFILE CLAIMS-------------
async def callback_profile_claims(c: types.CallbackQuery, state: FSMContext):
	admin_id = c.from_user.id
	try:
		connection.nullPagination(admin_id)
		pag = connection.selectPag(admin_id)
		profils = admin_connection.selectRequestsProfil()[pag]

		await bot.send_message(c.from_user.id, 'Все заявки профиля которое находятся на модерации:', reply_markup = admin_buttons.admin_canc())
		
		if profils[1] == 'customer':
			await bot.send_photo(c.from_user.id, photo = profils[3],
												 caption = f"<b>{profils[2]}</b>\n"
														   f"  <b>Номер:</b> <code>+{profils[4]}</code>",
														   		reply_markup = admin_buttons.requestProfilBtns(profils[0], profils[1]))

		elif profils[1] == 'executor':
			try:
				await bot.send_photo(c.from_user.id, photo = profils[3],
													caption = f"<b>{profils[2]}</b>\n"
															  f"  <b>Дата рождения:</b> <code>{profils[5]}</code>\n"
															  f"  <b>Номер:</b> <code>+{profils[4]}</code>\n\n"

															  f"<b>Навыки:</b>\n{profils[6]}\n\n"

															  f"  <b>Рейтинг:</b> <code>{connection.getExecutorProfil(profils[0])[6]}</code>",
															   		reply_markup = admin_buttons.requestProfilBtns(profils[0], profils[1]))
			except Exception as e:
				print(e)
				await bot.send_video(c.from_user.id, profils[3],
													caption = f"<b>{profils[2]}</b>\n"
															  f"  <b>Дата рождения:</b> <code>{profils[5]}</code>\n"
															  f"  <b>Номер:</b> <code>+{profils[4]}</code>\n\n"

															  f"<b>Навыки:</b>\n{profils[6]}\n\n"

															  f"  <b>Рейтинг:</b> <code>{connection.getExecutorProfil(profils[0])[6]}</code>",
															   		reply_markup = admin_buttons.requestProfilBtns(profils[0], profils[1]))			
		

	except Exception as e:
		print(e)
		await bot.answer_callback_query(c.id, show_alert = True, text = "Ничего не найдено")

async def callbackPBack(c: types.CallbackQuery, state: FSMContext):
	try:
		async with state.proxy() as data:
			user_id = c.from_user.id	
			connection.backPagination(user_id)
			pag = connection.selectPag(user_id)
			profils = admin_connection.selectRequestsProfil()[pag]


		if pag < 0:
			connection.nextPagination(user_id)
			await bot.answer_callback_query(c.id, show_alert = False, text = "❗️Вы находитесь на первом каталоге списка")	


		else:
			if profils[1] == 'customer':
				await bot.edit_message_media(media = types.InputMedia(
								type = 'photo', 
								media = profils[3], 
								caption = f"<b>{profils[2]}</b>\n"
										  f"  <b>Номер:</b> <code>+{profils[4]}</code>"),		
								chat_id = c.message.chat.id,
								message_id = c.message.message_id,
									reply_markup = admin_buttons.requestProfilBtns(profils[0], profils[1]))
				
			elif profils[1] == 'executor':
				try:
					await bot.edit_message_media(media = types.InputMedia(
									type = 'photo', 
									media = profils[3], 
									caption = f"<b>{profils[2]}</b>\n"
											  f"  <b>Дата рождения:</b> <code>{profils[5]}</code>\n"
											  f"  <b>Номер:</b> <code>+{profils[4]}</code>\n\n"

											  f"<b>Навыки:</b>\n{profils[6]}\n\n"

											  f"  <b>Рейтинг:</b> <code>{connection.getExecutorProfil(profils[0])[6]}</code>"),		
									chat_id = c.message.chat.id,
									message_id = c.message.message_id,
										reply_markup = admin_buttons.requestProfilBtns(profils[0], profils[1]))
				except Exception as e:
					print(e)
					await bot.edit_message_media(media = types.InputMedia(
								type = 'video', 
								media = profils[3], 
								caption = f"<b>{profils[2]}</b>\n"
										  f"  <b>Дата рождения:</b> <code>{profils[5]}</code>\n"
										  f"  <b>Номер:</b> <code>+{profils[4]}</code>\n\n"

										  f"<b>Навыки:</b>\n{profils[6]}\n\n"

										  f"  <b>Рейтинг:</b> <code>{connection.getExecutorProfil(profils[0])[6]}</code>"),		
								chat_id = c.message.chat.id,
								message_id = c.message.message_id,
									reply_markup = admin_buttons.requestProfilBtns(profils[0], profils[1]))

	except:
		await bot.answer_callback_query(c.id, show_alert = False, text = "❗️Вы находитесь на первом каталоге списка")	


async def callbackPNext(c: types.CallbackQuery, state: FSMContext):
	try:
		user_id = c.from_user.id
		connection.nextPagination(user_id)
		pag = connection.selectPag(user_id)
		profils = admin_connection.selectRequestsProfil()[pag]
		
		if profils[1] == 'customer':
			await bot.edit_message_media(media = types.InputMedia(
							type = 'photo', 
							media = profils[3], 
							caption = f"<b>{profils[2]}</b>\n"
									  f"  <b>Номер:</b> <code>+{profils[4]}</code>"),		
							chat_id = c.message.chat.id,
							message_id = c.message.message_id,
								reply_markup = admin_buttons.requestProfilBtns(profils[0], profils[1]))
		
		elif profils[1] == 'executor':
			try:
				await bot.edit_message_media(media = types.InputMedia(
								type = 'photo', 
								media = profils[3], 
								caption = f"<b>{profils[2]}</b>\n"
										  f"  <b>Дата рождения:</b> <code>{profils[5]}</code>\n"
										  f"  <b>Номер:</b> <code>+{profils[4]}</code>\n\n"

										  f"<b>Навыки:</b>\n{profils[6]}\n\n"

										  f"  <b>Рейтинг:</b> <code>{connection.getExecutorProfil(profils[0])[6]}</code>"),		
								chat_id = c.message.chat.id,
								message_id = c.message.message_id,
									reply_markup = admin_buttons.requestProfilBtns(profils[0], profils[1]))
			except Exception as e:
				await bot.edit_message_media(media = types.InputMedia(
								type = 'video', 
								media = profils[3], 
								caption = f"<b>{profils[2]}</b>\n"
										  f"  <b>Дата рождения:</b> <code>{profils[5]}</code>\n"
										  f"  <b>Номер:</b> <code>+{profils[4]}</code>\n\n"

										  f"<b>Навыки:</b>\n{profils[6]}\n\n"

										  f"  <b>Рейтинг:</b> <code>{connection.getExecutorProfil(profils[0])[6]}</code>"),		
								chat_id = c.message.chat.id,
								message_id = c.message.message_id,
									reply_markup = admin_buttons.requestProfilBtns(profils[0], profils[1]))		
	except Exception as e:
		if type(e) == IndexError:
			connection.backPagination(user_id)
			await bot.answer_callback_query(c.id, show_alert = False, text = "❗️Вы находитесь на последнем каталоге списка")
		else:
			print(type(e))
			print(e)




async def callbackPApprove(c: types.CallbackQuery, state: FSMContext):
	admin_connection.addView('profils', datetime.datetime.today().strftime('%d.%m.%Y'))

	await bot.delete_message(c.from_user.id, c.message.message_id)
	ids = c.data[9:].split(',')
	user_id = ids[0]
	status = ids[1]

	if status == 'customer':
		try:
			async with state.proxy() as data:
				cus_name = data['name']
				cus_pic = 'AgACAgIAAxkBAAOvYW5woS9KTofLU3EqNCIoo3jTWx0AAhezMRt7rXhL5FS-aNbKWN8BAAMCAAN5AAMhBA'
				cus_contact = data['contact']
				
				connection.UpdateData(user_id, cus_name, cus_pic, cus_contact)
				admin_connection.deleteRequestsProfil(user_id, status)				
				await bot.answer_callback_query(c.id, show_alert = True, text = "Заявка принята!")
			
				await bot.send_message(user_id, "<b>🔔 Уведомление:</b>\n\n" 
												"Модерация подтвердила изменение профиля! Ваш профиль был изменён.")
				await state.finish()

		except Exception as e:
			print(e)	
			profil = admin_connection.selectUserFromRequestProfils(user_id, status)
			connection.UpdateData(user_id, profil[0][2], profil[0][3], profil[0][4])
			await bot.send_message(user_id, "<b>🔔 Уведомление:</b>\n\n" 
											"Модерация подтвердила изменение профиля! Ваш профиль был изменён.")
			await bot.answer_callback_query(c.id, show_alert = True, text = "Заявка принята!")
			admin_connection.deleteRequestsProfil(user_id, status)


	elif status == 'executor':
		try:
			async with state.proxy() as data:
				ex_name = data['name']
				date_of_birth = data['date_of_birth']
				ex_pic = data['media']
				ex_contact = data['contact']
				ex_skill = data['skill']
				ex_rate = 0

				connection.UpdateExecutorProfil(user_id, ex_name, date_of_birth, ex_pic, ex_contact, ex_skill)
				
				await bot.send_message(user_id, "<b>🔔 Уведомление:</b>\n\n" 
												"Модерация подтвердила изменение профиля! Ваш профиль был изменён.")
				await bot.answer_callback_query(c.id, show_alert = True, text = "Заявка принята!")
				admin_connection.deleteRequestsProfil(user_id, status)

				await state.finish()

		except Exception as e:
			print(e)
			profil = admin_connection.selectUserFromRequestProfils(user_id, status)
			connection.UpdateExecutorProfil(user_id, profil[0][2], profil[0][5], profil[0][3], profil[0][4], profil[0][6])
			await bot.send_message(user_id, "<b>🔔 Уведомление:</b>\n\n" 
											"Модерация подтвердила изменение профиля! Ваш профиль был изменён.")
			await bot.answer_callback_query(c.id, show_alert = True, text = "Заявка принята!")
			admin_connection.deleteRequestsProfil(user_id, status)




async def callbackPReject(c: types.CallbackQuery, state: FSMContext):
	await EditOrder.step9.set()
	ids = c.data[8:].split(',')
	user_id = ids[0]
	status = ids[1]
	async with state.proxy() as data:
		data['user_id'] = user_id
		data['status'] = status
		await bot.send_message(c.from_user.id, "Отправьте причину почему вы хочете отклонить заявку?", 
			reply_markup = admin_buttons.admin_canc())	



async def processPReject(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		user_id = data['user_id']
		status = data['status']

		await bot.send_message(user_id, "<b>🔔 Уведомление:</b>\n\n"
										"Ваша заявка был отклонена на изменение профиля.\n\n" 
										f"<b>Причина:</b>\n{message.text}", reply_markup = admin_buttons.admin_canc())
		await bot.send_message(message.chat.id, "Заявка отклонена!")

		admin_connection.addView('profils', datetime.datetime.today().strftime('%d.%m.%Y'))
		admin_connection.deleteRequestsProfil(user_id, status)


async def callbackPEdit(c: types.CallbackQuery, state: FSMContext):
	ids = c.data[6:].split(',')
	user_id = ids[0]
	status = ids[1]

	if status == 'customer':
		async with state.proxy() as data:
			data['user_id'] = user_id

			await EditCustomerProfil.step1.set()
			await bot.delete_message(c.from_user.id, c.message.message_id)
			await bot.send_message(c.message.chat.id, "Отправьте мне <b>Имя Отчество заказчика</b>.", 
				reply_markup = admin_buttons.admin_canc())

	elif status == 'executor':
		async with state.proxy() as data:
			data['user_id'] = user_id
			await EditExecutorProfil.step1.set()
			await bot.delete_message(c.message.chat.id, c.message.message_id)
			await bot.send_message(c.message.chat.id, "Отправьте мне <b>Имя Отчество исполнителя</b>.", 
				reply_markup = admin_buttons.admin_canc())


async def process_reg1(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['name'] = message.text

	await EditCustomerProfil.next()
	await bot.send_message(message.chat.id, "Отправьте мне <b>фото заказчика</b>.")


async def process_img(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['photo'] = message.photo[-1].file_id

	await EditCustomerProfil.next()
	await bot.send_message(message.chat.id, "Отправьте мне <b>номер телефона</b>")


async def process_contact_and_all_data(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['contact'] = message.contact.phone_number

		cus_id = data['user_id']
		cus_name = data['name']
		cus_pic = data['photo']
		cus_contact = data['contact']
		date_registration = datetime.datetime.today().strftime('%d.%m.%Y - %H:%M')

		# connection.UpdateData(cus_id, cus_name, cus_pic, cus_contact, date_registration)
		await bot.send_photo(chat_id = message.chat.id, 
							 photo = cus_pic,
							 caption = f"<b>{cus_name}</b>"
							 		   f"  <b>Номер:</b> <code>+{cus_contact}</code>", 
							 reply_markup = admin_buttons.requestProfilBtns(cus_id, 'customer', show_pagination = False))


async def process_contact_if_not_img(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['contact'] = message.contact.phone_number

		cus_id = data['user_id']
		cus_name = data['name']
		cus_pic = 'AgACAgIAAxkBAAOvYW5woS9KTofLU3EqNCIoo3jTWx0AAhezMRt7rXhL5FS-aNbKWN8BAAMCAAN5AAMhBA'
		cus_contact = data['contact']
		date_registration = datetime.datetime.today().strftime('%d.%m.%Y - %H:%M')
		
		# connection.UpdateData(cus_id, cus_name, cus_pic, cus_contact, date_registration)
		await bot.send_photo(chat_id = message.chat.id, 
							   photo = cus_pic,
							   caption = f"<b>{cus_name}</b>"
							 		     f"  <b>Номер:</b> <code>+{cus_contact}</code>", 
							 		reply_markup = admin_buttons.requestProfilBtns(cus_id, 'customer', show_pagination = False))


async def process_create1(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['name'] = message.text

	await EditExecutorProfil.next()
	await bot.send_message(message.chat.id, "Отправьте мне Вашу <b>дату рождение (день.месяц.год)</b>, для определение возраста.")


async def process_create2(message: types.Message, state: FSMContext):
	try:
		date = message.text
		day = date[:2]
		month = date[3:5]
		year = date[6:]
		now = datetime.datetime.now().strftime('%Y')
		age = int(now) - int(year)

		if age > 0 and int(day) <= 31 and int(month) <= 12 and int(year) > 1920 and int(year) < int(now)-7:
			async with state.proxy() as data:
				data['date_of_birth'] = message.text

			await EditExecutorProfil.next()
			await bot.send_photo(message.chat.id, photo = 'AgACAgIAAxkBAAP1YW51oVYVSPmlzCGUUVxGek1i0jAAAimzMRt7rXhLGuB8Y2FU_DQBAAMCAAN5AAMhBA',
				caption = "Отправьте мне Ваше <b>фото</b> или <b>видео резюме</b>, для заполнение профиля.")

		else:
			await message.answer("Введите правильный дата рождение!\n<b>(день.месяц.год)</b>")
	except Exception as e:
		print(e)
		await message.answer("Введите правильный дата рождение!\n<b>(день.месяц.год)</b>")


async def process_create3(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		if message.photo:
			data['media'] = message.photo[-1].file_id
		elif message.video:
			data['media'] = message.video.file_id
		else:
			await message.answer("Отправьте мне Ваше <b>фото</b> или <b>видео резюме</b>, для заполнение профиля.")
		
	await EditExecutorProfil.next()
	await bot.send_message(message.chat.id, "Отправьте мне <b>номер телефона исполнителя</b>.")
		

async def process_contact_invalid(message: types.Message, state: FSMContext):
	await bot.send_message(message.chat.id, "Отправьте мне <b>номер телефона исполнителя</b>.")


async def process_create4(message: types.Message, state: FSMContext):
	await EditExecutorProfil.step5.set()
	async with state.proxy() as data:
		data['contact'] = message.contact.phone_number
		
		await bot.send_message(message.chat.id, "Отправьте мне свои навыки в таком формате через запятую:\n<i>Коммуникабельность, работа с кассой, отзывчивость, распределения обязанностей.</i>\n\nИли просто пишите 'Не указано'")


async def process_create5(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['skill'] = message.text

		ex_id = data['user_id']
		ex_name = data['name']
		date_of_birth = data['date_of_birth']
		ex_pic = data['media']
		ex_contact = data['contact']
		ex_skill = data['skill']
		ex_rate = 0
		date_registration = datetime.datetime.today().strftime('%d.%m.%Y - %H:%M')
		ex_status = 'free'

		admin_connection.addView('profils', datetime.datetime.today().strftime('%d.%m.%Y'))

		try:
			await bot.send_photo(
				chat_id = message.chat.id, 
				photo = ex_pic,
				caption = f"<b>{ex_name}</b>\n"
						  f"  <b>Дата рождения:</b> <code>{date_of_birth}</code>\n"
						  f"  <b>Номер:</b> <code>+{ex_contact}</code>\n\n"

						  f"<b>Навыки:</b>\n{ex_skill}\n\n"

						  f"  <b>Рейтинг:</b> <code>{connection.getExecutorProfil(ex_id)[6]}</code>",
						  	reply_markup = admin_buttons.requestProfilBtns(ex_id, 'executor', show_pagination = False))
		except Exception as e:
			print(e)
			await bot.send_video(message.chat.id, ex_pic,
				caption = f"<b>{ex_name}</b>\n"
						  f"  <b>Дата рождения:</b> <code>{date_of_birth}</code>\n"
						  f"  <b>Номер:</b> <code>+{ex_contact}</code>\n\n"

						  f"<b>Навыки:</b>\n{ex_skill}\n\n"

						  f"  <b>Рейтинг:</b> <code>{connection.getExecutorProfil(ex_id)[6]}</code>",
						  	reply_markup = admin_buttons.requestProfilBtns(ex_id, 'executor', show_pagination = False))


# ---COMPLAINTS----
async def view_complaint(c: types.CallbackQuery, state: FSMContext):
	data = admin_connection.getComplaintsFromReview()
	data_1 = admin_connection.getComplaintsFromUser()

	try:
		if data[0]:
			for n in range(len(data)):
				await c.message.answer( 
					f"<b>Заказчик:</b> <code>{connection.selectAll(data[n][1])[0]}</code>\n"
					f"<b>Адрес:</b> <code>{connection.selectOrderWhereCusId(data[n][1], data[n][2])[2]}</code>\n\n"

					f"<a href='https://t.me/ValyveExchange_bot?start={data[n][1]}_{data[n][2]}'>Просмотреть заказ</a>\n\n"

					f"<b>Отзыв:</b>\n<code>{connection.selectReview(str(data[n][0]), str(data[n][1]), str(data[n][2]))[1]}</code>\n\n",
						disable_web_page_preview = True)
				await c.message.answer(
					"<b>Причина:</b>\n"
					f"<code>{data[n][3]}</code>",
						reply_markup = admin_buttons.showReviewComplaintsBtns(data[n][0], data[n][1], data[n][2]))

		elif data_1[0]:
			for i in range(len(data_1)):
				alldata = connection.getExecutorProfil(data_1[i][0])
				try:
					await bot.send_photo(
						chat_id = c.from_user.id, 
						photo = alldata[3], 
						caption = f"<b>{alldata[1]}</b>\n\n"
								  f"  <b>Дата рождения:</b> <code>{alldata[2]}</code>\n"
								  f"  <b>Номер:</b> <code>+{alldata[4]}</code>\n\n"

								  f"<b>Навыки:</b>\n{alldata[5]}\n\n" 
								  f"  <b>Рейтинг:</b> <code>{alldata[6]}</code>")
					await c.message.answer(f"Причина:\n<code>{data_1[i][1]}</code>",
						reply_markup = admin_buttons.showUserComplaintsBtns(data_1[i][0], data_1[i][2]))
					
				
				except:
					await bot.send_video(
						chat_id = c.from_user.id, 
						video = alldata[3], 
						caption = f"<b>{alldata[1]}</b>\n\n"
							      f"  <b>Рейтинг:</b> <code>{alldata[6]}</code>\n\n"
							      f"<b>Навыки:</b>\n{alldata[5]}"
						)
					await c.message.answer(f"Причина:\n<code>{data_1[i][1]}</code>",
						reply_markup = admin_buttons.showUserComplaintsBtns(data_1[i][0], data_1[i][2]))
	except Exception as e:
		await c.answer("Ничего не найдено!", show_alert = True)


async def callback_cdelete(c: types.CallbackQuery, state: FSMContext):
	ids = c.data[8:].split(',')
	await ProcessCDelete.step1.set()

	async with state.proxy() as data:
		data['ex_id'] = ids[0]
		data['cus_id'] = ids[1]
		data['order_id'] = ids[2]

	await c.message.answer("Отправьте мне комментарии об удалении отзывa.")


async def input_couse_cdelete(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['cause'] = message.text

		await ProcessCDelete.next()
		await message.answer(f"Вы хотите удалить отзыв по причине '{message.text}'?",
			reply_markup = admin_buttons.causeDelete())


async def callbackcConfirm(c: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		ex_id = data['ex_id']
		cus_id = data['cus_id']
		order_id = data['order_id']
		cause = data['cause']

	admin_connection.deleteComplaintForReview(ex_id, cus_id, order_id)
	connection.deleteRating(ex_id, cus_id, order_id)
	admin_connection.addView('complaints', datetime.datetime.today().strftime('%d.%m.%Y'))


	await c.message.delete()
	await bot.send_message(ex_id, 
		"🔔 <b>Уведомление:</b>\n\n"
		f"Отзыв от <code>{connection.selectAll(cus_id)[0]}</code> "
		f"адресу: <code>{connection.selectOrderWhereCusId(cus_id, order_id)[2]}</code> "
		f"с текстом '<code>{connection.selectReview(str(ex_id), str(cus_id), str(order_id))[1]}</code>'. "
		f"Был удален модерацией по причине '<code>{cause}</code>'."
		)
	await c.message.answer("Комментрия удалено!")
	await state.finish()


async def callbackcChangeCause(c: types.CallbackQuery, state: FSMContext):
	await ProcessCDelete.step1.set()
	await c.message.answer("Отправьте мне комментарии об удалении отзывa.")


# ----change----
async def callback_change_review(c: types.CallbackQuery, state: FSMContext):
	ids = c.data[6:].split(',')
	await ProcessCDelete.step3.set()

	async with state.proxy() as data:
		data['ex_id'] = ids[0]
		data['cus_id'] = ids[1]
		data['order_id'] = ids[2]

	await c.message.answer("Отправьте мне текст для отзыва.")


async def process_change_review(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		ex_id = data['ex_id']
		cus_id = data['cus_id']
		order_id = data['order_id']
		data['new_review'] = message.text
		
		await ProcessCDelete.next()
		await message.answer( 
			f"<b>Заказчик:</b> <code>{connection.selectAll(cus_id)[0]}</code>\n"
			f"<b>Адрес:</b> <code>{connection.selectOrderWhereCusId(cus_id, order_id)[2]}</code>\n\n"
			
			f"<b>Отзыв:</b>\n<code>{message.text}</code>\n\n",
				reply_markup = admin_buttons.causeDelete())


async def callback_cConfirm(c: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		ex_id = data['ex_id']
		cus_id = data['cus_id']
		order_id = data['order_id']
		new_review = data['new_review']

	admin_connection.deleteComplaintForReview(ex_id, cus_id, order_id)
	connection.UpdateReview(ex_id, cus_id, order_id, new_review)
	admin_connection.addView('complaints', datetime.datetime.today().strftime('%d.%m.%Y'))


	await c.message.delete()

	try:
		await bot.send_message(cus_id, 
			"🔔 <b>Уведомление:</b>\n\n"
			f"Отзыв от <code>{connection.selectAll(cus_id)[0]}</code> "
			f"адресу: <code>{connection.selectOrderWhereCusId(cus_id, order_id)[2]}</code> "
			f"с текстом '<code>{connection.selectReview(str(ex_id), str(cus_id), str(order_id))[1]}</code>'. "
			f"Был отредактирован модерацией."
			)
		
		await bot.send_message(cus_id,
			f"<b>Заказчик:</b> <code>{connection.selectAll(cus_id)[0]}</code>\n"
			f"<b>Адрес:</b> <code>{connection.selectOrderWhereCusId(cus_id, order_id)[2]}</code>\n\n"
			
			f"<b>Отзыв:</b>\n<code>{new_review}</code>\n\n"
			)
	except Exception as e:
		print(e)
	
	await c.message.answer(
		"🔔 <b>Уведомление:</b>\n\n"
		f"Отзыв от <code>{connection.selectAll(cus_id)[0]}</code> "
		f"адресу: <code>{connection.selectOrderWhereCusId(cus_id, order_id)[2]}</code> "
		f"с текстом '<code>{connection.selectReview(str(ex_id), str(cus_id), str(order_id))[1]}</code>'. "
		f"Был успешно отредактирован!")

	await state.finish()


async def callback_cChangeCause(c: types.CallbackQuery, state: FSMContext):
	await ProcessCDelete.step3.set()
	await c.message.answer("Отправьте мне текст для отзыва.")


async def callback_cReject(c: types.CallbackQuery, state: FSMContext):
	ids = c.data[8:].split(',')
	admin_connection.addView('complaints', datetime.datetime.today().strftime('%d.%m.%Y'))


	try:
		ex_id = ids[0]
		cus_id = ids[1]
		order_id = ids[2]
		admin_connection.deleteComplaintForReview(ex_id, cus_id, order_id)
		await c.message.delete()
		await bot.delete_message(c.from_user.id, c.message.message_id-1)
		await c.message.answer("Отклонено!")

	except:
		ex_id = ids[0]
		rowid = ids[1]
		admin_connection.deleteComplaintForUser(ex_id, rowid)
		await c.message.delete()
		await bot.delete_message(c.from_user.id, c.message.message_id-1)
		await c.message.answer("Отклонено!")

	await state.finish()


# ----COMPLAINTS FOR USER----
async def callback_ban_to_user(c: types.CallbackQuery, state: FSMContext):
	ex_id = c.data[5:]
	connection.UpdateExStatus(ex_id, 'Banned')
	connection.deleteComplaintForUser(ex_id)
	admin_connection.addView('complaints', datetime.datetime.today().strftime('%d.%m.%Y'))

	await c.message.answer("Пользователь забанен!")



def register_admin_moderation_handlers(dp: Dispatcher):
	dp.register_callback_query_handler(order_requests, lambda c: c.data == 'announcement_requests',  state = '*')
	dp.register_callback_query_handler(callbackToBack, lambda c: c.data.startswith('toBack'),  state = '*')
	dp.register_callback_query_handler(callbackToNext, lambda c: c.data.startswith('toNext'),  state = '*')
	dp.register_callback_query_handler(callbackApprove, lambda c: c.data.startswith('toApprove'),  state = '*')
	dp.register_callback_query_handler(callbackReject, lambda c: c.data.startswith('toReject'),  state = '*')
	dp.register_callback_query_handler(callbackEdit, lambda c: c.data.startswith('toEdit'),  state = '*')

	dp.register_callback_query_handler(callbackPublish, lambda c: c.data.startswith('finishEdit'),  state = '*')
	dp.register_message_handler(process_output_location, content_types = ['location','venue'], state = EditOrder.step1)
	dp.register_message_handler(process_output_position, state = EditOrder.step2)
	dp.register_message_handler(process_output_days, state = EditOrder.step3)
	dp.register_message_handler(process_output_graphic, state = EditOrder.step4)
	dp.register_message_handler(process_output_bid, state = EditOrder.step5)
	dp.register_message_handler(process_output_requirement, state = EditOrder.step6)
	dp.register_message_handler(process_output_respons, state = EditOrder.step7)
	dp.register_message_handler(process_output_comment_and_all_data, state = EditOrder.step8)
	dp.register_callback_query_handler(process_output_without_comment, lambda c: c.data == 'skip', state = EditOrder.step8)

	dp.register_callback_query_handler(callback_output_location, lambda c: c.data == 'cSkip', state = EditOrder.step1)
	dp.register_callback_query_handler(callback_output_position, lambda c: c.data == 'cSkip', state = EditOrder.step2)
	dp.register_callback_query_handler(callback_output_days, lambda c: c.data == 'cSkip', state = EditOrder.step3)
	dp.register_callback_query_handler(callback_output_graphic, lambda c: c.data == 'cSkip', state = EditOrder.step4)
	dp.register_callback_query_handler(callback_output_bid, lambda c: c.data == 'cSkip', state = EditOrder.step5)
	dp.register_callback_query_handler(callback_output_requirement, lambda c: c.data == 'cSkip', state = EditOrder.step6)
	dp.register_callback_query_handler(callback_output_respons, lambda c: c.data == 'cSkip', state = EditOrder.step7)

	dp.register_callback_query_handler(callback_profile_claims, lambda c: c.data == 'profile_claims', state = '*')
	dp.register_callback_query_handler(callbackPBack, lambda c: c.data == 'pBack', state = '*')
	dp.register_callback_query_handler(callbackPNext, lambda c: c.data == 'pNext', state = '*')
	dp.register_callback_query_handler(callbackPApprove, lambda c: c.data.startswith('pApprove'), state = '*')
	dp.register_callback_query_handler(callbackPReject, lambda c: c.data.startswith('pReject'), state = '*')
	dp.register_message_handler(processPReject, state = EditOrder.step9)
	dp.register_callback_query_handler(callbackPEdit, lambda c: c.data.startswith('pEdit'), state = '*')

	dp.register_message_handler(process_reg1, state = EditCustomerProfil.step1)
	dp.register_message_handler(process_img, content_types = 'photo', state = EditCustomerProfil.step2)
	dp.register_message_handler(process_contact_and_all_data, content_types = 'contact', state = EditCustomerProfil.step3)
	dp.register_message_handler(process_contact_if_not_img, content_types = 'contact', state = EditCustomerProfil.step4)

	dp.register_message_handler(process_create1, state = EditExecutorProfil.step1)
	dp.register_message_handler(process_create2, state = EditExecutorProfil.step2)
	dp.register_message_handler(process_create3, content_types = ['photo', 'video'], state = EditExecutorProfil.step3)
	dp.register_message_handler(process_contact_invalid, lambda message: not message.contact, state = EditExecutorProfil.step4)
	dp.register_message_handler(process_create4, content_types = ['contact'], state = EditExecutorProfil.step4)
	dp.register_message_handler(process_create5, state = EditExecutorProfil.step5)

	dp.register_callback_query_handler(view_complaint, lambda c: c.data.startswith('aComplaint'), state = '*')
	dp.register_callback_query_handler(callback_cdelete, lambda c: c.data.startswith('cDelete'), state = '*')
	dp.register_message_handler(input_couse_cdelete, state = ProcessCDelete.step1)
	dp.register_callback_query_handler(callbackcConfirm, lambda c: c.data.startswith('cConfirm'), state = ProcessCDelete.step2)
	dp.register_callback_query_handler(callbackcChangeCause, lambda c: c.data.startswith('cChange'), state = ProcessCDelete.step2)

	dp.register_callback_query_handler(callback_change_review, lambda c: c.data.startswith('cEdit'), state = '*')
	dp.register_message_handler(process_change_review, state = ProcessCDelete.step3)
	dp.register_callback_query_handler(callback_cConfirm, lambda c: c.data.startswith('cConfirm'), state = ProcessCDelete.step4)
	dp.register_callback_query_handler(callback_cChangeCause, lambda c: c.data.startswith('cChange'), state = ProcessCDelete.step4)
	dp.register_callback_query_handler(callback_cReject, lambda c: c.data.startswith('cReject'), state = '*')

	dp.register_callback_query_handler(callback_ban_to_user, lambda c: c.data.startswith('cBan'), state = '*')