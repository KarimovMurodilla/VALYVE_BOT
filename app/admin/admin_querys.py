import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from .. import connection, file_ids, buttons, config


bot = Bot(token=config.TOKEN, parse_mode = 'html')



async def query_ads_history(query: types.InlineQuery):
	cus_id = query.query[12:]
	item = connection.selectOrders(cus_id)
	
	try:
		r = [types.InlineQueryResultArticle( 
				id = f'{n}', 
				title = f'Заказ #{n+1} | {item[n][10][:-7]}', 
				input_message_content = types.InputTextMessageContent(
				message_text =  f"<b>Статус заказа:</b> <code>{item[n][11]}</code>\n\n"
								f"<b>Заказчик:</b> <code>{item[n][1]}</code>\n"
								f"<b>Адреc:</b> <code>{item[n][2]}</code>\n\n"

								f"<b>График:</b> <code>{item[n][3]}</code>\n"
								f"{connection.checkOrderType(item[n][-2], item[n])}"
								# f"<b>Время работы:</b> <code>{item[n][4]}</code>\n"
								f"<b>Ставка:</b> <code>{item[n][5]}</code>\n"
								f"<b>Должность:</b> <code>{item[n][6]}</code>\n\n"

								f"{item[n][7]}"))
										for n in range(len(item))]
			

		await query.answer(r, cache_time = 60)
		
	except Exception as e:
		print(e)



async def query_work_history(query: types.InlineQuery):
	ex_id = query.query[14:]
	item = connection.selectReviews(ex_id)

	try:
		recent = [types.InlineQueryResultArticle( 
			id = f'{n}', 
			title = f'Заказ#{n} | {connection.selectOrderWhereCusId(item[n][2], item[n][3])[10]}', 
			input_message_content = types.InputTextMessageContent(
			message_text =  f"<b>Статус заказа:</b> <code>{connection.selectOrderWhereCusId(item[n][2], item[n][3])[11]}</code>\n"
							f"<b>Заказчик:</b> <code>{connection.selectOrderWhereCusId(item[n][2], item[n][3])[1]}</code>\n"
							f"<b>Номер:</b> <code>+{connection.selectAll(item[n][2])[2]}</code>\n"
							f"<b>Адреc:</b> <code>{connection.selectOrderWhereCusId(item[n][2], item[n][3])[2]}</code>\n\n"

							f"<b>Кол-в исполнителей:</b> <code>{len(connection.selectMyPerWhereOrderId(item[n][2], item[n][3]))}</code>\n"
							f"<b>График:</b> <code>{connection.selectOrderWhereCusId(item[n][2], item[n][3])[3]}</code>\n"
                            f"{connection.checkOrderType(connection.selectOrderWhereCusId(item[n][0], item[n][1])[-2], connection.selectOrderWhereCusId(item[n][0], item[n][1]))}"
							# f"<b>Время работы:</b> <code>{connection.selectOrderWhereCusId(item[n][2], item[n][3])[4]}</code>\n"
							f"<b>Ставка:</b> <code>{connection.selectOrderWhereCusId(item[n][2], item[n][3])[5]}</code>\n"
							f"<b>Должность:</b> <code>{connection.selectOrderWhereCusId(item[n][2], item[n][3])[6]}</code>\n\n"

							f"<b>Комментарий:</b>\n{connection.selectOrderWhereCusId(item[n][2], item[n][3])[7]}"),
								reply_markup = None)
									for n in range(len(item))]

		await query.answer(recent, cache_time=60, is_personal=True)
	except Exception as e:
		print(e)



async def query_view_review(query: types.InlineQuery):
	ex_id = query.query[12:]
	item = connection.selectReviews(ex_id)

	try:
		my_performers = [types.InlineQueryResultArticle( 
			id = f'{n}', 
			title = f'Отзыв от {connection.selectAll(item[n][2])[0]}', 
			input_message_content = types.InputTextMessageContent(
			message_text =  f"Заказчик: {connection.selectAll(item[n][2])[0]}\n\n"
							f"Отзыв: {item[n][1]}"),
								reply_markup = None)
									for n in range(len(item))]

		await query.answer(my_performers, cache_time=60, is_personal=True)
	except Exception as e:
		print(e)





def register_admin_inline_mode_handlers(dp: Dispatcher):
	# For customers
	dp.register_inline_handler(query_ads_history, lambda query: query.query.startswith("!ads_history"), state = '*')
	
	# For executors
	dp.register_inline_handler(query_work_history, lambda query: query.query.startswith("!work_history"), state = '*')
	dp.register_inline_handler(query_view_review, lambda query: query.query.startswith("!view_review"), state = '*')
