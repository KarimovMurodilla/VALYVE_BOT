import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from .. import buttons, config, connection, file_ids


bot = Bot(token=config.TOKEN, parse_mode = 'html')


class ExecutorWasComplete(StatesGroup):
	step1 = State()
	step2 = State()
	step3 = State()
	step4 = State()
	step5 = State()
	step6 = State()


class UnderConsideration(StatesGroup):
	step1 = State()
	step2 = State()


async def callback_the_end(c: types.CallbackQuery, state: FSMContext):
	ids = c.data[8:].split(',')

	if c.from_user.id not in connection.selectMyPerInOrderId(ids[0], ids[1]):
		await bot.answer_callback_query(c.id, show_alert = True, text = "Вы уже завершили этот заказ!")

	else:
		await ExecutorWasComplete.step1.set()
		
		async with state.proxy() as data:
			data['cus_id'] = ids[0]
			data['order_id'] = ids[1]
			data['ex_id'] = c.from_user.id

		await c.answer()
		await bot.send_message(c.from_user.id, "Вы действительно хотите завершить заказ?",
			reply_markup = buttons.yesNo())


async def process_the_end(c: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		cus_id = data['cus_id']
		order_id = data['order_id']
		ex_id = data['ex_id']	

	
	await bot.delete_message(c.from_user.id, c.message.message_id)
	await bot.send_message(c.from_user.id, "🔔 <b>Уведомление:</b>\n\n"
											"Заказ завершён! Теперь вы можете просматривать и откликаться на новые заказы",
		reply_markup = buttons.menu_executor)
	

	connection.UpdateExStatus(c.from_user.id, 'free')
	connection.deleteMyPer(int(ex_id), int(cus_id), int(order_id))	


	await ExecutorWasComplete.step2.set()
	await bot.send_message(cus_id,  "🔔 <b>Уведомление:</b>\n\n"
									f"Исполнитель <code>{connection.getExecutorProfil(c.from_user.id)[1]}</code> завершил с Вами работу. Как Вы оценете качество его работы?",
		reply_markup = buttons.rating2(cus_id, order_id, ex_id))


async def process_change_rate(c: types.CallbackQuery, state: FSMContext):
	ids = c.data[9:].split(',')
	
	cus_id = ids[0]
	order_id = ids[1]
	ex_id = ids[2]

	await bot.send_message(c.from_user.id, f"Оцените работу сотрудника по шкале:", 
		reply_markup = buttons.rating2(cus_id, order_id, ex_id))


async def process_to_rate(c: types.CallbackQuery, state: FSMContext):
	ids = c.data[9:].split(',')
	await ExecutorWasComplete.step3.set()
	async with state.proxy() as data:
		data['rate'] = ids[0]
		data['cus_id'] = ids[1]
		data['order_id'] = ids[2]
		data['ex_id'] = ids[3]

		await bot.delete_message(c.from_user.id, c.message.message_id)
		await bot.send_message(c.from_user.id, "Хотите ли Вы оставить отзыв исполнителю?", 
			reply_markup = buttons.comment())
	
	
async def process_leave_comment(c: types.CallbackQuery, state: FSMContext):
	await ExecutorWasComplete.step4.set()
	await bot.delete_message(c.from_user.id, c.message.message_id)
	await bot.send_message(c.from_user.id,"Опишите работу исполнителя, как он справляется со стрессовыми ситуациями, порекомендовали бы Вы его на постоянную работу?",
		reply_markup = buttons.back_canc)
	


async def process_no_com(c: types.CallbackQuery, state: FSMContext):
	await ExecutorWasComplete.step5.set()
	async with state.proxy() as data:
		cus_id = c.from_user.id
		data['review'] = 'Без отзыва'
		review = data['review']
		order_id = data['order_id']
		ex_id = data['ex_id']
		rate = data['rate']
		review = data['review']

		order = f"<a href='https://t.me/ValyveExchange_bot?start={cus_id}_{order_id}'>Просмотреть заказ</a>"
		orderData = connection.selectOrderWhereCusId(cus_id, order_id)
		cus_name = connection.selectAll(cus_id)[0]

		await bot.delete_message(c.from_user.id, c.message.message_id)
		await bot.send_message(cus_id,  f"<b>Отзыв от #{cus_id}</b>\n\n"
										f"<b>Заказчик:</b> <code>{orderData[1]}</code>\n"
										f"<b>Адрес:</b> <code>{orderData[2]}</code>\n\n"
										f"{order}\n\n"
										f"<b>Отзыв:</b> {review}", disable_web_page_preview = True)	
		await bot.send_message(cus_id, "Верно или хотите изменить отзыв?", 
			reply_markup = buttons.realOrNot2(cus_id, ex_id, rate, order_id)
			)



async def process_text_comment(message: types.Message, state: FSMContext):
	await ExecutorWasComplete.step5.set()
	async with state.proxy() as data:
		data['review'] = message.text

		cus_id = message.from_user.id
		review = data['review']
		order_id = data['order_id']
		ex_id = data['ex_id']
		rate = data['rate']
		order = f"<a href='https://t.me/ValyveExchange_bot?start={cus_id}_{order_id}'>Просмотреть заказ</a>"
		orderData = connection.selectOrderWhereCusId(cus_id, order_id)
		cus_name = connection.selectAll(cus_id)[0]

		await bot.send_message(cus_id, f"<b>Отзыв от #{cus_id}</b>\n\n"
												f"<b>Заказчик:</b> <code>{orderData[1]}</code>\n"
												f"<b>Адрес:</b> <code>{orderData[2]}</code>\n\n"
												f"{order}\n\n"
												f"<b>Отзыв:</b> {review}", disable_web_page_preview = True)	
		await bot.send_message(cus_id, "Верно или хотите изменить отзыв?", 
			reply_markup = buttons.realOrNot2(cus_id, ex_id, rate, order_id))



async def process_publish(c: types.CallbackQuery, state: FSMContext):
	ids = c.data[10:].split(',')
	await c.answer( "🔔 Уведомление:\n\n"
					"Вы успешно завершили сотрудничество с исполнителем!", show_alert = True)
	await bot.delete_message(c.from_user.id, c.message.message_id)
	await bot.delete_message(c.from_user.id, c.message.message_id-1)
	
	async with state.proxy() as data:
		review = data['review']
		cus_id = c.from_user.id
		ex_id = ids[1]
		rate = ids[2]
		order_id = ids[3]
		cus_name = connection.selectAll(cus_id)[0]
		orderData = connection.selectOrderWhereCusId(cus_id, order_id)
		date_of_completion = datetime.datetime.today().strftime('%d.%m.%Y')

		connection.UpdateRating(ex_id, review, cus_id, order_id, date_of_completion)
		ex_rate = connection.getExecutorProfil(ex_id)[6]
		connection.UpdateRate(eval(f"{ex_rate}{rate}"), ex_id)

		if orderData[-2] == 'stock':
			payment_for_waiting = int(orderData[-1])
			response_data = connection.selectAllFromCusOr(cus_id, order_id)
			date = response_data[4].split(',')

			date1 = datetime.datetime.now()
			date2 = datetime.datetime(day=int(date[2]), month=int(date[1]), year=int(date[0]))
			timedelta = date1-date2
			connection.updateBalance(ex_id, timedelta.days * payment_for_waiting, '+')

		await state.finish()


# ----UNDER CONSIDERATION---
async def callback_con_finish(c: types.CallbackQuery, state: FSMContext):
	ids = c.data[11:].split(',')

	if c.from_user.id not in connection.selectMyPerInOrderId(ids[0], ids[1]):
		await bot.answer_callback_query(c.id, show_alert = True, text = "Вы уже завершили этот заказ!")

	else:
		await UnderConsideration.step1.set()
		
		async with state.proxy() as data:
			data['cus_id'] = ids[0]
			data['order_id'] = ids[1]
			data['ex_id'] = c.from_user.id

		await c.answer()
		await bot.send_message(c.from_user.id, "Вы действительно хотите завершить заказ?",
			reply_markup = buttons.yesNo())


async def process_finish_under_consideration(c: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		cus_id = data['cus_id']
		order_id = data['order_id']
		ex_id = data['ex_id']	

	
	await bot.delete_message(c.from_user.id, c.message.message_id)
	await bot.send_message(c.from_user.id, "🔔 <b>Уведомление:</b>\n\n"
											"Заказ завершён! Теперь вы можете просматривать и откликаться на новые заказы",
		reply_markup = buttons.menu_executor)

	connection.UpdateExStatus(c.from_user.id, 'free')
	connection.deleteMyPer(int(ex_id), int(cus_id), int(order_id))	

	await bot.send_message(cus_id,  "🔔 <b>Уведомление:</b>\n\n"
									f"Исполнитель <code>{connection.getExecutorProfil(c.from_user.id)[1]}</code> завершил с Вами сотрудничество")


async def callback_write_to_cus(c: types.CallbackQuery, state: FSMContext):
	cus_id = c.data[13:]

	async with state.proxy() as data:
		data['cus_id'] = cus_id

	await UnderConsideration.step2.set()
	await c.answer()
	await bot.send_message(c.from_user.id, "Напишите что хотите отправить на заказчика:", 
		reply_markup = buttons.leaveChat())


async def start_of_conversation(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		cus_id = data['cus_id']

		await bot.send_message(cus_id, message.text, reply_markup = buttons.replyTo(message.from_user.id))


def register_executor_completed_handlers(dp: Dispatcher):
	dp.register_callback_query_handler(callback_the_end, lambda c: c.data.startswith('the_end'),  state = '*')
	dp.register_callback_query_handler(process_the_end, lambda c: c.data == 'yep',  state = ExecutorWasComplete.step1)
	dp.register_callback_query_handler(process_to_rate, lambda c: c.data.startswith('!to_rate'),  state = '*')	
	dp.register_callback_query_handler(process_leave_comment, lambda c: c.data == 'leave_comment',  state = ExecutorWasComplete.step3)
	dp.register_callback_query_handler(process_no_com, lambda c: c.data == 'no_com',  state = ExecutorWasComplete.step3)
	
	dp.register_message_handler(process_text_comment, state = ExecutorWasComplete.step4)

	dp.register_callback_query_handler(process_change_rate, lambda c: c.data.startswith('toChange'),  state = '*')
	dp.register_callback_query_handler(process_publish, lambda c: c.data.startswith('toPublish'),  state = '*')

	dp.register_callback_query_handler(callback_con_finish, lambda c: c.data.startswith('con_finish'),  state = '*')
	dp.register_callback_query_handler(process_finish_under_consideration, lambda c: c.data == 'yep',  state = UnderConsideration.step1)

	dp.register_callback_query_handler(callback_write_to_cus, lambda c: c.data.startswith('write_to_cus'),  state = '*')
	dp.register_message_handler(start_of_conversation, state = UnderConsideration.step2)
