import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from .. import buttons, config, connection, file_ids


bot = Bot(token=config.TOKEN, parse_mode = 'html')


class CompleteOrder(StatesGroup):
	step1 = State()
	step2 = State()	
	step3 = State()
	step4 = State()



async def callback_complete_order(c: types.CallbackQuery, state: FSMContext):
	try:
		async with state.proxy() as data:	
			cus_id = c.from_user.id
			order_id = c.data[15:]
			data['order_id'] = order_id
			my_performers = connection.selectMyPerInOrderId(cus_id, order_id)
			data['ex_id'] = my_performers[0]

	
		if connection.selectOrderWhereCusId(cus_id, order_id)[11] == 'Завершён':
			await bot.answer_callback_query(c.id, show_alert = True, text = "Этот заказ уже завершен!")
			await state.finish()


		elif my_performers[0] is not None:
			await CompleteOrder.step1.set()
			await bot.send_message(c.from_user.id, f"Оцените качество работы <code>{connection.getExecutorProfil(my_performers[0])[1]}</code>:", 
				reply_markup = buttons.rating())

		else:
			print("Da")
	
	except Exception as e:
		print(e, type(e))
		await bot.send_message(c.from_user.id, "Вы действительно хотите завершить этот заказ?", reply_markup = buttons.yesNope(cus_id, order_id))


async def callback_change(c: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		cus_id = c.from_user.id	
		order_id = data['order_id']
		my_performers = connection.selectMyPerInOrderId(cus_id, order_id)
		
		await CompleteOrder.step1.set()
		await bot.send_message(c.from_user.id, f"Оцените качество работы <code>{connection.getExecutorProfil(my_performers[0])[1]}</code>:", 
			reply_markup = buttons.rating())


async def callback_da(c: types.CallbackQuery, state: FSMContext):
	ids = c.data[3:]
	order_id = ids[0]
	cus_id = c.from_user.id

	connection.UpdateOrderStatus(cus_id, order_id, "Завершён")
	await bot.delete_message(c.from_user.id, c.message.message_id)
	await bot.send_message(cus_id, "Ваш заказ завершена!")



async def ask_comment(c: types.CallbackQuery, state: FSMContext):
	await CompleteOrder.next()
	async with state.proxy() as data:
		data['rate'] = c.data[6:]
		await bot.delete_message(c.from_user.id, c.message.message_id)
		await bot.send_message(c.from_user.id, "Хотите ли Вы оставить отзыв исполнителю?", 
			reply_markup = buttons.comment())


async def callback_leave_comment(c: types.CallbackQuery, state: FSMContext):
	await CompleteOrder.step3.set()
	await bot.delete_message(c.from_user.id, c.message.message_id)
	await bot.send_message(c.from_user.id,"Опишите работу исполнителя, как он справляется с стрессовыми ситуациями, порекомендовали бы Вы его на постоянную работу?",
		reply_markup = buttons.back_canc)


async def callback_no_com(c: types.CallbackQuery, state: FSMContext):
	await CompleteOrder.step4.set()
	async with state.proxy() as data:
		cus_id = c.from_user.id
		data['review'] = 'Без отзыва'
		ex_id = data['ex_id']
		rate = data['rate']
		review = data['review']
		order_id = data['order_id']

		order = f"<a href='https://t.me/ValyveExchange_bot?start={cus_id}_{order_id}'>Просмотреть заказ</a>"
		orderData = connection.selectOrderWhereCusId(cus_id, order_id)
		cus_name = connection.selectAll(cus_id)[0]

		await bot.delete_message(c.from_user.id, c.message.message_id)
		await bot.send_message(cus_id, f"Отзыв от #{cus_id}\n\n"
												f"Заказчик: {orderData[1]}\n"
												f"Адрес: {orderData[2]}\n\n"
												f"{order}\n\n"
												f"Отзыв: {review}")	
		await bot.send_message(cus_id, "Верно или хотите изменить отзыв?", reply_markup = buttons.realOrNot())


async def text_comment(message: types.Message, state: FSMContext):
	await CompleteOrder.step4.set()
	async with state.proxy() as data:
		data['review'] = message.text

		cus_id = message.from_user.id
		ex_id = data['ex_id']
		rate = data['rate']
		review = data['review']
		order_id = data['order_id']
		order = f"<a href='https://t.me/ValyveExchange_bot?start={cus_id}_{order_id}'>Просмотреть заказ</a>"
		orderData = connection.selectOrderWhereCusId(cus_id, order_id)
		cus_name = connection.selectAll(cus_id)[0]

		await bot.send_message(message.chat.id, f"<b>Отзыв от #{cus_id}</b>\n\n"
												f"<b>Заказчик:</b> <code>{orderData[1]}</code>\n"
												f"<b>Адрес:</b> <code>{orderData[2]}</code>\n\n"
												f"{order}\n\n"
												f"<b>Отзыв:</b> {review}")	
		await bot.send_message(message.chat.id, "Верно или хотите изменить отзыв?", reply_markup = buttons.realOrNot())


async def callback_publish(c: types.CallbackQuery, state: FSMContext):
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
		connection.regExToRatings(ex_id, cus_id, order_id)
		connection.UpdateExStatus(ex_id, 'free')
		connection.removeMyPer(int(ex_id), int(cus_id), int(order_id))	

		await bot.answer_callback_query(c.id, show_alert = True, text = "Сотрудничество завершено!")
		await bot.delete_message(c.from_user.id, c.message.message_id)
		await bot.delete_message(c.from_user.id, c.message.message_id-1)	

		await bot.send_message(ex_id, f"<b>🔔 Уведомление:</b>\n\n"
									  f"Заказчик <code>{orderData[1]}</code>, завершил с Вами заказ! Теперь вы можете откликаться на новые заказы.")

		try:
			if connection.selectMyPerInOrderId(cus_id, order_id)[0] is not None:
				await CompleteOrder.step1.set()
				data['order_id'] = order_id
				my_performers = connection.selectMyPerInOrderId(cus_id, order_id)
				data['ex_id'] = my_performers[0]
				await bot.send_message(c.from_user.id, f"Оцените качество работы <code>{connection.getExecutorProfil(my_performers[0])[1]}</code>:", 
					reply_markup = buttons.rating())
		except IndexError:
			connection.UpdateOrderStatus(cus_id, order_id, "Завершён")
			connection.removeAll(cus_id, order_id)
			await bot.send_message(c.from_user.id, "Ваш заказ завершён")

			await state.finish()


def register_complete_order_handlers(dp: Dispatcher):
	dp.register_callback_query_handler(callback_complete_order, lambda c: c.data.startswith('complete_order'),  state = '*')
	dp.register_callback_query_handler(callback_da, lambda c: c.data.startswith('da'),  state = '*')
	dp.register_callback_query_handler(ask_comment, lambda c: c.data.startswith('!rate'),  state = CompleteOrder.step1)
	dp.register_callback_query_handler(callback_leave_comment, lambda c: c.data == 'leave_comment',  state = CompleteOrder.step2)
	dp.register_callback_query_handler(callback_no_com, lambda c: c.data == 'no_com',  state = CompleteOrder.step2)

	dp.register_message_handler(text_comment, state = CompleteOrder.step3)

	dp.register_callback_query_handler(callback_change, lambda c: c.data == 'to_change',  state = CompleteOrder.step4)
	dp.register_callback_query_handler(callback_publish, lambda c: c.data == 'to_publish',  state = CompleteOrder.step4)


