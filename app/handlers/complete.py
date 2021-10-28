import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from .. import buttons, config, connection, file_ids


bot = Bot(token=config.TOKEN, parse_mode = 'html')


class Complete(StatesGroup):
	step1 = State()
	step2 = State()
	step3 = State()
	step4 = State()
	step5 = State()



class ExecutorWasComplete(StatesGroup):
	step1 = State()
	step2 = State()
	step3 = State()
	step4 = State()
	step5 = State()
	step6 = State()




async def callback_end_executor(c: types.CallbackQuery, state: FSMContext):
	ids = c.data[5:]
	sep = ids.split(',')
	ex_id = sep[0]
	order_id = sep[1]

	if connection.selectOrderWhereCusId(c.from_user.id, order_id)[11] == 'Опубликован':
		if int(ex_id) not in connection.selectMyPerInOrderId(c.from_user.id, int(order_id)):
			await bot.answer_callback_query(c.id, show_alert = True, text = "Вы уже закончили с этим исполнителем сотрудничество!")
		else:
			await Complete.step1.set()
			async with state.proxy() as data:
				data['ex_id'] = ex_id
				data['order_id'] = order_id

				await bot.send_message(c.from_user.id, "Вы действительно хотите закончить сотрудничество?",
														reply_markup = buttons.yesNo())

	elif connection.selectOrderWhereCusId(c.from_user.id, order_id)[11] == 'Завершён':
		await bot.answer_callback_query(c.id, show_alert = True, text = "Этот заказ уже завершен!")

	else:
		await bot.answer_callback_query(c.id, show_alert = True, text = "Подождите! Этот заказ еще на модерации.")




async def callback_yes(c: types.CallbackQuery, state: FSMContext):
	await Complete.step2.set()
	await bot.delete_message(c.from_user.id, c.message.message_id)
	await bot.send_message(c.from_user.id, "Оцените работу сотрудника по шкале:", 
		reply_markup = buttons.rating())


async def callback_no(c: types.CallbackQuery, state: FSMContext):
	await state.finish()
	user_id = c.from_user.id
	user_status = connection.checkUserStatus(user_id)

	if user_status[0] == 'customer':
		await bot.delete_message(c.from_user.id, c.message.message_id)
		await bot.send_message(c.from_user.id, "Отменено !", reply_markup = buttons.menu_customer)
		await state.finish()

	elif user_status[0] == 'executor':
		await bot.delete_message(c.from_user.id, c.message.message_id)
		await bot.send_message(c.from_user.id, "Отменено !", reply_markup = buttons.menu_executor)
		await state.finish() 



async def callback_rate(c: types.CallbackQuery, state: FSMContext):
	await Complete.step3.set()
	async with state.proxy() as data:
		data['rate'] = c.data[6:]

		await bot.delete_message(c.from_user.id, c.message.message_id)
		await bot.send_message(c.from_user.id, "Хотите ли Вы оставить отзыв исполнителю?", 
			reply_markup = buttons.comment())
	
	
async def callback_leave_comment(c: types.CallbackQuery, state: FSMContext):
	await Complete.step4.set()
	await bot.delete_message(c.from_user.id, c.message.message_id)
	await bot.send_message(c.from_user.id,"Опишите работу исполнителя, как он справляется с стрессовыми ситуациями, порекомендовали бы Вы его на постоянную работу?",
		reply_markup = buttons.back_canc)
	




async def callback_no_com(c: types.CallbackQuery, state: FSMContext):
	await Complete.step5.set()
	async with state.proxy() as data:
		cus_id = c.from_user.id
		data['review'] = 'Без отзыва'
		review = data['review']
		order_id = data['order_id']

		order = f"<a href='https://t.me/ValyveExchange_bot?start={cus_id}_{order_id}'>Просмотреть заказ</a>"
		orderData = connection.selectOrderWhereCusId(cus_id, order_id)
		cus_name = connection.selectAll(cus_id)[0]

		await bot.delete_message(c.from_user.id, c.message.message_id)
		await bot.send_message(cus_id,  f"<b>Отзыв от #</b> <code>{cus_id}</code>\n\n"
										f"<b>Заказчик:</b> <code>{orderData[1]}</code>\n"
										f"<b>Адрес:</b> <code>{orderData[2]}</code>\n\n"
										f"{order}\n\n"
										f"<b>Отзыв:</b> {review}")	
		await bot.send_message(cus_id, "Верно или хотите изменить отзыв ?", reply_markup = buttons.realOrNot())



async def text_comment(message: types.Message, state: FSMContext):
	await Complete.step5.set()
	async with state.proxy() as data:
		data['review'] = message.text

		cus_id = message.from_user.id
		review = data['review']
		order_id = data['order_id']
		order = f"<a href='https://t.me/ValyveExchange_bot?start={cus_id}_{order_id}'>Просмотреть заказ</a>"
		orderData = connection.selectOrderWhereCusId(cus_id, order_id)
		cus_name = connection.selectAll(cus_id)[0]

		await bot.send_message(cus_id, f"<b>Отзыв от #</b> <code>{cus_id}</code>\n\n"
												f"<b>Заказчик:</b> <code>{orderData[1]}</code>\n"
												f"<b>Адрес:</b> <code>{orderData[2]}</code>\n\n"
												f"{order}\n\n"
												f"<b>Отзыв:</b> {review}")	
		await bot.send_message(cus_id, "Верно или хотите изменить отзыв ?", reply_markup = buttons.realOrNot())



async def callback_publish(c: types.CallbackQuery, state: FSMContext):
	await bot.answer_callback_query(c.id, show_alert = True, text = "Сотрудничество завершено!")
	await bot.delete_message(c.from_user.id, c.message.message_id)
	await bot.delete_message(c.from_user.id, c.message.message_id-1)
	async with state.proxy() as data:
		cus_id = c.from_user.id
		ex_id = data['ex_id']
		rate = data['rate']
		review = data['review']
		order_id = data['order_id']
		orderData = connection.selectOrderWhereCusId(cus_id, order_id)
		cus_name = connection.selectAll(cus_id)[0]
		date_of_completion = datetime.datetime.today().strftime('%d.%m.%Y')

		ex_rate = connection.getExecutorProfil(ex_id)[6]
		connection.UpdateRate(eval(f"{ex_rate}{rate}"), ex_id)
		connection.UpdateRating(ex_id, review, cus_id, order_id, date_of_completion)
		connection.UpdateExStatus(ex_id, 'free')
		connection.deleteMyPer(int(ex_id), int(cus_id), int(order_id))	

	

		await bot.send_message(ex_id, "<b>🔔 Уведомление:</b>\n\n"
									 f"Заказчик <code>{orderData[1]}</code>, завершил с Вами заказ! Теперь вы можете откликаться на новые заказы.")
		await state.finish()


def register_complete_handlers(dp: Dispatcher):
	dp.register_callback_query_handler(callback_end_executor, lambda c: c.data.startswith('!end'),  state = '*')
	dp.register_callback_query_handler(callback_yes, lambda c: c.data == 'yep',  state = Complete.step1)
	dp.register_callback_query_handler(callback_no, lambda c: c.data == 'net',  state = '*')
	dp.register_callback_query_handler(callback_rate, lambda c: c.data.startswith('!rate'),  state = Complete.step2)
	dp.register_callback_query_handler(callback_leave_comment, lambda c: c.data == 'leave_comment',  state = Complete.step3)
	dp.register_callback_query_handler(callback_no_com, lambda c: c.data == 'no_com',  state = Complete.step3)

	dp.register_message_handler(text_comment, state = Complete.step4)

	dp.register_callback_query_handler(callback_yes, lambda c: c.data == 'to_change',  state = Complete.step5)
	dp.register_callback_query_handler(callback_publish, lambda c: c.data == 'to_publish',  state = Complete.step5)