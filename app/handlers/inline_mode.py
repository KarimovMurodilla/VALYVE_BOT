import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from .. import connection, file_ids, buttons, config


bot = Bot(token=config.TOKEN, parse_mode = 'html')


# ----FOR ORDERS----
async def my_orders(query: types.InlineQuery):
	item = connection.selectOrders(query.from_user.id)
	
	try:
		r = [types.InlineQueryResultArticle( 
				id = f'{n}', 
				title = f'Заказ #{n+1} | {item[n][10]}', 
				input_message_content = types.InputTextMessageContent(
				message_text =  f"<b>Статус заказа:</b> <code>{item[n][11]}</code>\n\n"
								f"<b>Заказчик:</b> <code>{item[n][1]}</code>\n"
								f"<b>Адреc:</b> <code>{item[n][2]}</code>\n\n"

                                f"<b>Должность:</b> <code>{item[n][6]}</code>\n"
                                f"<b>Время работы:</b> <code>{item[n][4]}</code>\n"
                                f"<b>График:</b> <code>{item[n][3]}</code>\n"
                                f"<b>Смена:</b> <code>{item[n][5]}</code>\n\n"

                                f"<b>Требование:</b>\n<code>{item[n][14]}</code>\n\n"
                                f"<b>Обязанности:</b>\n<code>{item[n][15]}</code>\n\n"
                          
                                f"{item[n][7]}"), 
									reply_markup = buttons.orderButtons(n))
										for n in range(len(item))]
			
		await query.answer(r, cache_time = 60)
		
	except Exception as e:
		print(e)



async def my_requests(query: types.InlineQuery):
	cus_id = query.from_user.id
	q = query.query[13:]
	item = connection.selectRequestsWhereOrderId(cus_id, q)

	try:
		requests = [types.InlineQueryResultArticle( 
						id = f'{n}', 
						title = f'{connection.checkExecutor(item[n][0])[1]} | Рейтинг: {connection.checkExecutor(item[n][0])[6]}', 
						input_message_content = types.InputTextMessageContent(
						message_text =  f"Вы хотите просмотреть профиль <code>{connection.checkExecutor(item[n][0])[1]}</code>?"),
							reply_markup = buttons.getProfil(item[n][0], q, 'my_request'))
								for n in range(len(item)) if item[n][0] is not None]
				

		await query.answer(requests, cache_time=60, is_personal=True)
	except Exception as e:
		print(e)


async def my_performers(query: types.InlineQuery):
	cus_id = query.from_user.id
	q = query.query[15:]
	item = connection.selectMyPerWhereOrderId(cus_id, q)
	now = datetime.datetime.now().strftime('%Y')

	try:
		pending = connection.selectPendingsWhereOrderId(cus_id, q)[3]
	except:
		pending = None
	
	try:
		my_performers = [types.InlineQueryResultArticle( 
							id = f'{n}', 
							title = f'{connection.checkExecutor(item[n])[1]} | {int(now)-int(connection.checkExecutor(item[n])[2][6:])} лет', 
							input_message_content = types.InputTextMessageContent(
							message_text =  f"Вы хотите просмотреть профиль <code>{connection.checkExecutor(item[n])[1]}</code>?"),
												reply_markup = buttons.getProfil(item[n], q, 'my_performer'))
													for n in range(len(item)) if item[n] is not None and item[n] != pending]

		await query.answer(my_performers, cache_time=60, is_personal=True)
	except Exception as e:
		print(e)


async def my_pendings(query: types.InlineQuery):
	cus_id = query.from_user.id
	q = query.query[13:]
	
	try:
		item = connection.selectPendingsWhereOrderId(cus_id, q)[3]
		requests = [types.InlineQueryResultArticle( 
						id = f'{n}', 
						title = f'{connection.checkExecutor(item)[1]} | Рейтинг: {connection.checkExecutor(item)[6]}', 
						input_message_content = types.InputTextMessageContent(
						message_text =  f"Вы хотите просмотреть профиль <code>{connection.checkExecutor(item)[1]}</code>?"),
							reply_markup = buttons.getProfil(item, q, 'my_pending'))
								for n in range(1) if item is not None]
				

		await query.answer(requests, cache_time=60, is_personal=True)
	except Exception as e:
		print(e)


# ----FOR USERS----
async def query_reviews(query: types.InlineQuery):
	user_id = query.from_user.id
	ex_id = query.query[8:]
	item = connection.selectReviews(ex_id)

	try:
		my_performers = [types.InlineQueryResultArticle( 
			id = f'{n}', 
			title = f'Отзыв от {connection.selectAll(item[n][2])[0]}', 
			input_message_content = types.InputTextMessageContent(
			message_text =  f"<b>Заказчик:</b> <code>{connection.selectAll(item[n][2])[0]}</code>\n"
							f"<b>Адрес:</b> <code>{connection.selectOrderWhereCusId(item[n][2], item[n][3])[2]}</code>\n\n"

							f"<a href='https://t.me/ValyveExchange_bot?start={item[n][2]}_{item[n][3]}'>Просмотреть заказ</a>\n\n"

							f"<b>Отзыв:</b>\n<code>{item[n][1]}</code>\n\n"

							f"{item[n][5]}", disable_web_page_preview = True),
								reply_markup = buttons.answerToReview(ex_id, item[n][2], item[n][3], int(user_id) == int(ex_id), item[n][5]))
									for n in range(len(item)) if item[n][1] is not None and not item[n][1] == '']

		await query.answer(my_performers, cache_time=60, is_personal=True)
	except Exception as e:
		print(e)



async def recent_works(query: types.InlineQuery):
	ex_id = query.from_user.id
	item = connection.selectReviews(ex_id)

	try:
		recent = [types.InlineQueryResultArticle( 
			id = f'{n}', 
			title = f'Заказ#{n+1} | {connection.selectOrderWhereCusId(item[n][2], item[n][3])[10]}', 
			input_message_content = types.InputTextMessageContent(
			message_text =  f"<b>Заказчик:</b> <code>{connection.selectOrderWhereCusId(item[n][2], item[n][3])[1]}</code>\n"
							f"<b>Номер:</b> <code>+{connection.selectAll(item[n][2])[2]}</code>\n"
							f"<b>Адреc:</b> <code>{connection.selectOrderWhereCusId(item[n][2], item[n][3])[2]}</code>\n\n"

                            f"<b>Должность:</b> <code>{connection.selectOrderWhereCusId(item[n][2], item[n][3])[6]}</code>\n"
                            f"<b>Время работы:</b> <code>{connection.selectOrderWhereCusId(item[n][2], item[n][3])[4]}</code>\n"
                            f"<b>График:</b> <code>{connection.selectOrderWhereCusId(item[n][2], item[n][3])[3]}</code>\n"
                            f"<b>Смена:</b> <code>{connection.selectOrderWhereCusId(item[n][2], item[n][3])[5]}</code>\n\n"

                            f"<b>Требование:</b>\n<code>{connection.selectOrderWhereCusId(item[n][2], item[n][3])[14]}</code>\n\n"
                            f"<b>Обязанности:</b>\n<code>{connection.selectOrderWhereCusId(item[n][2], item[n][3])[15]}</code>\n\n"
                      
                            f"{connection.selectOrderWhereCusId(item[n][2], item[n][3])[7]}"),
								reply_markup = buttons.endOrder(item[n][2], item[n][3]))
									for n in range(len(item))]

		await query.answer(recent, cache_time=60, is_personal=True)
	except Exception as e:
		print(e)


async def my_considerations(query: types.InlineQuery):
	item = connection.getMyConsiderations(query.from_user.id)

	try:
		recent = [types.InlineQueryResultArticle( 
			id = f'{n}', 
			title = f'Заказ#{n+1} | {connection.selectOrderWhereCusId(item[n][0], item[n][1])[10]}', 
			input_message_content = types.InputTextMessageContent(
			message_text =  f"<b>Заказчик:</b> <code>{connection.selectOrderWhereCusId(item[n][0], item[n][1])[1]}</code>\n"
							f"<b>Номер:</b> <code>+{connection.selectAll(item[n][0])[2]}</code>\n"
							f"<b>Адреc:</b> <code>{connection.selectOrderWhereCusId(item[n][0], item[n][1])[2]}</code>\n\n"

                            f"<b>Должность:</b> <code>{connection.selectOrderWhereCusId(item[n][0], item[n][1])[6]}</code>\n"
                            f"<b>Время работы:</b> <code>{connection.selectOrderWhereCusId(item[n][0], item[n][1])[4]}</code>\n"
                            f"<b>График:</b> <code>{connection.selectOrderWhereCusId(item[n][0], item[n][1])[3]}</code>\n"
                            f"<b>Смена:</b> <code>{connection.selectOrderWhereCusId(item[n][0], item[n][1])[5]}</code>\n\n"

                            f"<b>Требование:</b>\n<code>{connection.selectOrderWhereCusId(item[n][0], item[n][1])[14]}</code>\n\n"
                            f"<b>Обязанности:</b>\n<code>{connection.selectOrderWhereCusId(item[n][0], item[n][1])[15]}</code>\n\n"
                      
                            f"{connection.selectOrderWhereCusId(item[n][0], item[n][1])[7]}"),
								reply_markup = buttons.getUnderConsiderationBtns(item[n][0], item[n][1]))
									for n in range(len(item))]

		await query.answer(recent, cache_time=60, is_personal=True)
	except Exception as e:
		print(e)



async def get_msg_id(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['msgId'] = message.message_id





def register_inline_mode_handlers(dp: Dispatcher):
	dp.register_inline_handler(my_orders, lambda query: query.query ==  f"!get_order {query.from_user.id}", state = '*')
	dp.register_inline_handler(my_requests, lambda query: query.query.startswith('!my_requests'), state = '*')
	dp.register_inline_handler(my_performers, lambda query: query.query.startswith("!my_performers"), state = '*')
	dp.register_inline_handler(my_pendings, lambda query: query.query.startswith("!my_pendings"), state = '*')
	dp.register_inline_handler(query_reviews, lambda query: query.query.startswith("!reviews"), state = '*')

	dp.register_inline_handler(recent_works, lambda query: query.query.startswith("!recent_works"), state = '*')
	dp.register_inline_handler(my_considerations, lambda query: query.query.startswith("!under_consideration"), state = '*')


	dp.register_message_handler(get_msg_id, lambda message: message.text.startswith("Вы хотите просмотреть профиль"), state = '*')