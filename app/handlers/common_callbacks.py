import time

from app.handlers.reg_executor_profil import RegExecutor
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from .. import buttons, config, connection, file_ids, getLocationInfo


bot = Bot(token=config.TOKEN, parse_mode = 'html')


def fast_answer(func):
	async def wrapper(c: types.CallbackQuery, state: FSMContext):
		await c.answer()
		
		return 	await func(c, state)
	return wrapper


@fast_answer
async def callback_zak(c: types.CallbackQuery, state: FSMContext):
	user_id = c.from_user.id
	user_name = c.from_user.first_name
	user_username = c.from_user.username

	await bot.delete_message(c.from_user.id, c.message.message_id)
	await bot.send_message(c.from_user.id, "Главное меню", reply_markup = buttons.menu_customer)

	if not connection.checkUserStatus(user_id):
		connection.RegUser(user_id, user_name, user_username, 'customer')
	else:
		connection.UpdateUserStatus('customer', user_id)


@fast_answer
async def callback_isp(c: types.CallbackQuery, state: FSMContext):
	user_id = c.from_user.id
	user_name = c.from_user.first_name
	user_username = c.from_user.username

	await bot.delete_message(c.message.chat.id, c.message.message_id)
	await bot.send_message(c.from_user.id, "Главное меню", reply_markup = buttons.menu_executor)

	if not connection.checkUserStatus(user_id):
		connection.RegUser(user_id, user_name, user_username, 'executor')
	else:
		connection.UpdateUserStatus('executor', user_id)


@fast_answer
async def callback_auth(c: types.CallbackQuery, state: FSMContext):
	await bot.send_message(c.from_user.id, "Как Вы хотите авторизоваться?", reply_markup = buttons.btn2)


# @fast_answer
# async def callback_refresh(c: types.CallbackQuery, state: FSMContext):
# 	user_id = c.from_user.id
# 	await bot.answer_callback_query(c.id, show_alert = False, text = "Обновлено")

# 	try:
# 		ref_actives = connection.getRefActives(user_id)
# 		for i in ref_actives[0]:
# 			if connection.checkRegStatus(i) or connection.checkExecutor(i):
# 				connection.addActiveReferral(user_id)
# 				connection.setActiveUser(i)

# 		referral = connection.checkReferral(user_id)		
# 		await bot.edit_message_media(media = types.InputMedia(
# 					type = 'photo', 
# 					media = file_ids.PHOTO['bank'], 
# 					caption  = 	f"Баланс: {referral[6]} ₽\n\n"
# 								f"👥 Реферальная система\n"
# 								f"├ Активных: {referral[5]} уч\n"
# 								f"└ Ожидание: {referral[4]} уч\n\n"
# 								f"🗣 Пригласительная ссылка\n"
# 								f"└ <a href='https://t.me/ValyveExchange_bot?start={user_id}'>Зажми чтоб скопировать</a>"),
# 									chat_id = c.message.chat.id,
# 									message_id = c.message.message_id,
# 									reply_markup = buttons.referral_settings
# 										)
# 	except Exception as e:
# 		print(e)


@fast_answer
async def callback_support(c: types.CallbackQuery, state: FSMContext):
	await bot.send_photo(c.from_user.id, photo = file_ids.PHOTO['support'], caption = "👱🏼‍♂️ <b>Основатель</b>\n"
																						 " └ @geovet04\n\n"

																						 "👨🏼‍⚖️ <b>Модератор</b>\n"
																						 " └ @vitomoderno\n\n"

																						 "👨🏻‍💻 <b>Разработчик</b>\n"
																						 " └ @MurodillaKarimov")


async def callback_back(c: types.CallbackQuery, state: FSMContext):
	try:
		async with state.proxy() as data:
			user_id = c.from_user.id	
			connection.backPagination(user_id)
			pag = connection.selectPag(user_id)
			lat = data['lat']
			lon = data['long']			
			orders = connection.selectAllOrders(lat, lon)[pag]


		if pag < 0:
			connection.nextPagination(user_id)
			await bot.answer_callback_query(c.id, show_alert = False, text = "Вы в начале списка!")


		else:
			await c.answer()
			await bot.edit_message_text(chat_id = c.from_user.id, 	
									message_id = c.message.message_id,
									text =	f"<b>Заказчик:</b> <code>{orders[1]}</code>\n"
											f"<b>Расстояние:</b> <code>{getLocationInfo.calculate_distance(lat, lon, orders[8], orders[9])}</code> от Вас\n\n"

											f"<b>Должность:</b> <code>{orders[6]}</code>\n"
											f"<b>Время работы:</b> <code>{orders[4]}</code>\n"
											f"<b>График:</b> <code>{orders[3]}</code>\n"
											f"<b>Смена:</b> <code>{orders[5]}</code>\n\n"
											
											f"<b>Требование:</b>\n<code>{orders[14]}</code>\n\n"
											f"<b>Обязанности:</b>\n<code>{orders[15]}</code>\n\n"

											f"{orders[7]}",
												reply_markup = buttons.globalOrders(orders[0], orders[12]))
	except Exception as e:
		print(e)
		if type(e) == IndexError:
			await bot.answer_callback_query(c.id, show_alert = False, text = "❗️Вы находитесь на первом каталоге списка")	

		else:
			await c.answer()			
			await bot.delete_message(c.from_user.id, c.message.message_id)
			await bot.send_message(c.from_user.id, "Отправьте мне свою геолокацию, чтоб я мог показать объявления в Вашем регионе.", reply_markup = buttons.send_geo)
			await RegExecutor.step6.set()



async def callback_nex(c: types.CallbackQuery, state: FSMContext):
	try:
		async with state.proxy() as data:
			user_id = c.from_user.id
			connection.nextPagination(user_id)
			pag = connection.selectPag(user_id)
			lat = data['lat']
			lon = data['long']			
			orders = connection.selectAllOrders(lat, lon)[pag]

		await c.answer()
		await bot.edit_message_text(chat_id = c.from_user.id, 	
							message_id = c.message.message_id,
							text = 	f"<b>Заказчик:</b> <code>{orders[1]}</code>\n"
									f"<b>Расстояние:</b> <code>{getLocationInfo.calculate_distance(lat, lon, orders[8], orders[9])}</code> от Вас\n\n"

									f"<b>Должность:</b> <code>{orders[6]}</code>\n"
									f"<b>Время работы:</b> <code>{orders[4]}</code>\n"
									f"<b>График:</b> <code>{orders[3]}</code>\n"
									f"<b>Смена:</b> <code>{orders[5]}</code>\n\n"

									f"<b>Требование:</b>\n<code>{orders[14]}</code>\n\n"
									f"<b>Обязанности:</b>\n<code>{orders[15]}</code>\n\n"

									f"{orders[7]}",
										reply_markup = buttons.globalOrders(orders[0], orders[12]))
	except Exception as e:
		print(e)
		if type(e) == IndexError:
			connection.backPagination(user_id)
			await bot.answer_callback_query(c.id, show_alert = True, text = "🔔 Уведомление:\n\n" 
																			 "Вы просмотрели все объявление. Зайдите позже, мы обязательно что-то подберём для вас!")

		else:
			await c.answer()
			await bot.delete_message(c.from_user.id, c.message.message_id)
			await bot.send_message(c.from_user.id, "Отправьте мне свою геолокацию, чтоб я мог показать объявления в Вашем регионе.", reply_markup = buttons.send_geo)
			await RegExecutor.step6.set()



async def callback_apply(c: types.CallbackQuery, state: FSMContext):
	user_id = c.from_user.id	
	cusAndOrder = c.data[6:]
	ids = cusAndOrder.split(',')
	cus_id = int(ids[0])
	order_id = int(ids[1])
	pag = connection.selectPag(user_id)+1
	readd = connection.selectAllFromCusOr(cus_id, order_id)

	if user_id not in connection.selectRequests(order_id, cus_id) and connection.selectRequests(order_id, cus_id)[0] is None or connection.selectRequests(order_id, cus_id)[0] == '':
		if connection.selectMyPerInOrderId(cus_id, order_id)[0] is None or connection.selectMyPerInOrderId(cus_id, order_id)[0] == '':
			if cus_id == user_id:
				await bot.answer_callback_query(c.id, show_alert = True, text = "⚠️ Ошибка:\n\n"
																				"Вы не можете откликаться на свои заказы! Попробуйте откликнуться на другой заказ.")
			
			elif user_id in connection.selectRequests(order_id, cus_id) or user_id in connection.selectMyPerInOrderId(cus_id, order_id):
				await bot.answer_callback_query(c.id, show_alert = True, text = "⚠️ Ошибка:\n\n"
																				"Вы уже откликнулись на это объявление! Дождитесь ответа от заказчика.")
			else:		
				connection.UpdateRequests(user_id, cus_id, order_id)
				await bot.answer_callback_query(c.id, show_alert = True, text = "🔔 Уведомление:\n\n"
																				"Ваша заявка отправлена! Ожидайте ответа от заказчика.")

		else:
			if cus_id == user_id:
				await bot.answer_callback_query(c.id, show_alert = True, text = "⚠️ Ошибка:\n\n"
																				"Вы не можете откликаться на свои заказы! Попробуйте откликнуться на другой заказ.")

			elif user_id in connection.selectRequests(order_id, cus_id) or user_id in connection.selectMyPerInOrderId(cus_id, order_id):
				await bot.answer_callback_query(c.id, show_alert = True, text = "⚠️ Ошибка:\n\n"
																				"Вы уже откликнулись на это объявление! Дождитесь ответа от заказчика.")	


			else:
				await bot.answer_callback_query(c.id, show_alert = True, text = "🔔 Уведомление:\n\n"
																				"Ваша заявка отправлена! Ожидайте ответа от заказчика.")
				connection.regResponses(readd[0],
										readd[1],
										user_id,
										readd[3])

	else:
		if cus_id == user_id:
			await bot.answer_callback_query(c.id, show_alert = True, text = "⚠️ Ошибка:\n\n"
																			"Вы не можете откликаться на свои заказы! Попробуйте откликнуться на другой заказ.")

		elif user_id in connection.selectRequests(order_id, cus_id) or user_id in connection.selectMyPerInOrderId(cus_id, order_id):
			await bot.answer_callback_query(c.id, show_alert = True, text = "⚠️ Ошибка:\n\n"
																			"Вы уже откликнулись на это объявление! Дождитесь ответа от заказчика.")	


		else:
			await bot.answer_callback_query(c.id, show_alert = True, text = "🔔 Уведомление:\n\n"
																			"Ваша заявка отправлена! Ожидайте ответа от заказчика.")
			connection.regResponses(readd[0],
									readd[1],
									user_id,
									readd[3])


		


@fast_answer
async def callback_approve(c: types.CallbackQuery, state: FSMContext):
	cus_id = c.from_user.id
	exAndOrderId = c.data[10:]
	ids = exAndOrderId.split(',')
	ex_id = int(ids[0])
	orderId = int(ids[1])
	contact = int(ids[2])
	item = connection.selectOrders(cus_id)
	
	if ex_id not in connection.selectMyPerInOrderId(cus_id, orderId):
		if connection.checkExecutor(ex_id)[8] == 'busy':
			await bot.answer_callback_query(c.id, show_alert = True, text = "⚠️ Исполнитель уже взялася за другой заказ, выберите другого исполнителя.")

		elif ex_id not in connection.selectRequests(orderId, cus_id):
			await bot.answer_callback_query(c.id, show_alert = True, text = "⚠️ Ошибка:\n\n"
																			"Вы уже отклонили этого исполнителя!")
		else:
			await bot.answer_callback_query(c.id, show_alert = True, text = "🔔 Уведомление:\n\n" 
																			"Исполнитель добавлен в список \"Мои исполнители\". Чтоб взаимодействовать с ним, зайдите в этот раздел.")
			connection.replaceReqToPer(cus_id, ex_id, orderId)	

			await bot.send_message(ex_id, "<b>🔔 Уведомление:</b>\n\n"
										  f"Заказчик <code>{connection.selectAll(cus_id)[0]}</code>, "
										  "одобрил вашу заявку на вакансию",
										  	reply_markup = buttons.viewVacancy(cus_id, orderId))	

			connection.UpdateExStatus(ex_id, 'busy')
			connection.regExToRatings(ex_id, cus_id, orderId)

	
	else:
		await bot.answer_callback_query(c.id, show_alert = True, text = "⚠️ Ошибка:\n\n"
																		"Вы уже одобрили этого исполнителя!")




async def callback_refusal(c: types.CallbackQuery, state: FSMContext):
	cus_id = c.from_user.id
	exAndOrderId = c.data[11:]
	ids = exAndOrderId.split(',')
	ex_id = int(ids[0])
	orderId = int(ids[1])
	contact = int(ids[2])
	item = connection.selectOrders(cus_id)

	if ex_id == connection.selectRequestsWhereOrderId(cus_id, orderId)[0][0]:
		await bot.answer_callback_query(c.id, show_alert = True, text = "🔔 Уведомление:\n\n"
																		"Заявка была успешно отклонена!")
		connection.deleteRequests(ex_id, orderId)
		await bot.send_message(ex_id, f"<b>Заказчик:</b> <code>{item[orderId][1]}</code>\n"
									  f"<b>Адреc:</b> <code>{item[orderId][2]}</code>\n\n"
									  
									  f"<b>Должность:</b> <code>{item[orderId][6]}</code>\n"
									  f"<b>Время работы:</b> <code>{item[orderId][4]}</code>\n"
									  f"<b>График:</b> <code>{item[orderId][3]}</code>\n"
									  f"<b>Смена:</b> <code>{item[orderId][5]}</code>\n\n"

									  f"<b>Требование:</b>\n<code>{item[orderId][14]}</code>\n\n"
									  f"<b>Обязанности:</b>\n<code>{item[orderId][15]}</code>\n\n"

									  f"{item[orderId][7]}")
		await bot.send_message(ex_id, "🔔 <b>Уведомление:</b>\n\n"
									  f"Заказчик <code>{connection.selectAll(cus_id)[0]}</code>, " 
									  "отклонил вашу заявку на вакансию!",
										  	reply_markup = buttons.viewVacancy(cus_id, orderId))

	elif ex_id in connection.selectMyPerInOrderId(cus_id, orderId):
		await bot.answer_callback_query(c.id, show_alert = True, text = "⚠️ Ошибка:\n\n"
																		"Вы уже одобрили этого исполнителя!")
	else:
		await bot.answer_callback_query(c.id, show_alert = True, text = "⚠️ Ошибка:\n\n"
																		"Вы уже отклонили этого исполнителя!")


@fast_answer
async def callback_view(c: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		await bot.delete_message(c.from_user.id, data['msgId'])
		cus_id = c.from_user.id
		ids = c.data[11:].split(',')
		ex_id = ids[0]
		order_id = ids[1]
		all_data = connection.checkExecutor(ex_id)
		contact = connection.selectAll(cus_id)[2]

	if int(ex_id) in connection.selectMyPerInOrderId(int(cus_id), int(order_id)):
		try:
			await bot.send_photo(c.from_user.id, photo = all_data[3], caption = f"<b>{all_data[1]}</b>\n\n"
																				f"<b>  Дата рождения:</b> <code>{all_data[2]}</code>\n"
																				f"<b>  Номер:</b> <code>+{all_data[4]}</code>\n\n"
																				f"<b>Навыки:</b>\n{all_data[5]}\n\n"
																				f"<b>  Рейтинг:</b> <code>{all_data[6]}</code>",
																			reply_markup = buttons.performerButtons(ex_id, order_id))
		except Exception:
			await bot.send_video(c.from_user.id, all_data[3], caption = f"<b>{all_data[1]}</b>\n\n"
																		f"<b>  Дата рождения:</b> <code>{all_data[2]}</code>\n"
																		f"<b>  Номер:</b> <code>+{all_data[4]}</code>\n\n"
																		f"<b>Навыки:</b>\n{all_data[5]}\n\n"
																		f"<b>  Рейтинг:</b> <code>{all_data[6]}</code>",
																	reply_markup = buttons.performerButtons(ex_id, order_id))
	elif int(ex_id) in connection.selectRequests(int(order_id), int(cus_id)):
		try:
			await bot.send_photo(c.from_user.id, photo = all_data[3], caption = f"<b>{all_data[1]}</b>\n\n"
																				f"<b>  Дата рождения:</b> <code>{all_data[2]}</code>\n"
																				f"<b>  Номер:</b> <code>+{all_data[4]}</code>\n\n"
																				f"<b>Навыки:</b>\n{all_data[5]}\n\n"
																				f"<b>  Рейтинг:</b> <code>{all_data[6]}</code>",
																			reply_markup = buttons.requestButton(ex_id, order_id, contact))
		except Exception:
			await bot.send_video(c.from_user.id, all_data[3], caption = f"<b>{all_data[1]}</b>\n\n"
																		f"<b>  Дата рождения:</b> <code>{all_data[2]}</code>\n"
																		f"<b>  Номер:</b> <code>+{all_data[4]}</code>\n\n"
																		f"<b>Навыки:</b>\n{all_data[5]}\n\n"
																		f"<b>  Рейтинг:</b> <code>{all_data[6]}</code>",
																	reply_markup = buttons.requestButton(ex_id, order_id, contact))


@fast_answer
async def callback_no_view(c: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		await bot.delete_message(c.from_user.id, data['msgId'])


@fast_answer
async def callback_view_vacancy(c: types.CallbackQuery, state: FSMContext):
	ex_id = c.from_user.id
	vacancy = c.data[6:]
	ids = vacancy.split(',')
	cus_id = int(ids[0])
	order_id = int(ids[1])
	item = connection.selectOrderWhereCusId(cus_id, order_id)

	await bot.send_message(ex_id, f"<b>Заказчик:</b> <code>{item[1]}</code>\n"
							 	  f"<b>Адреc:</b> <code>{item[2]}</code>\n\n"

								  f"<b>Должность:</b> <code>{item[6]}</code>\n"
								  f"<b>Время работы:</b> <code>{item[4]}</code>\n"
								  f"<b>График:</b> <code>{item[3]}</code>\n"
								  f"<b>Смена:</b> <code>{item[5]}</code>\n\n"

								  f"<b>Требование:</b>\n<code>{item[14]}</code>\n\n"
								  f"<b>Обязанности:</b>\n<code>{item[15]}</code>\n\n"

								  f"{item[7]}")


@fast_answer
async def callback_get_geo(c: types.CallbackQuery, state: FSMContext):
	ids = c.data[7:].split(',')
	cus_id = ids[0]
	order_id = ids[1]

	geo = connection.selectOrderWhereCusId(cus_id, order_id)
	await bot.send_location(chat_id = c.from_user.id,
							latitude = geo[8],
							longitude = geo[9])





def register_callback_handlers(dp: Dispatcher):
	dp.register_callback_query_handler(callback_zak, lambda c: c.data == 'zak',  state = '*')    
	dp.register_callback_query_handler(callback_isp, lambda c: c.data == 'isp',  state = '*')    
	dp.register_callback_query_handler(callback_auth, lambda c: c.data == 'auth',  state = '*')
	# dp.register_callback_query_handler(callback_bank, lambda c: c.data == 'bank',  state = '*')
	# dp.register_callback_query_handler(callback_refresh, lambda c: c.data == 'refresh',  state = '*')
	dp.register_callback_query_handler(callback_support, lambda c: c.data == 'support',  state = '*')

	dp.register_callback_query_handler(callback_back, lambda c: c.data.startswith('back'),  state = '*') 
	dp.register_callback_query_handler(callback_nex, lambda c: c.data.startswith('nex'),  state = '*')    
	dp.register_callback_query_handler(callback_apply, lambda c: c.data.startswith('apply'),  state = '*')

	dp.register_callback_query_handler(callback_approve, lambda c: c.data.startswith("sendAccept"),  state = '*')
	dp.register_callback_query_handler(callback_refusal, lambda c: c.data.startswith("sendRefusal"),  state = '*')

	dp.register_callback_query_handler(callback_view, lambda c: c.data.startswith("yes_i_view"),  state = '*')
	dp.register_callback_query_handler(callback_no_view, lambda c: c.data == 'no_view',  state = '*')

	dp.register_callback_query_handler(callback_view_vacancy, lambda c: c.data.startswith('cView'),  state = '*')
	dp.register_callback_query_handler(callback_get_geo, lambda c: c.data.startswith('getGeo'),  state = '*')	