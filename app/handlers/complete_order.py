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
	step5 = State()
	step6 = State()


async def callback_ask_rate(c: types.CallbackQuery, state: FSMContext):
	ids = c.data[10:].split(',')
	cus_id = ids[0]
	order_id = ids[1]
	my_performers = connection.selectMyPerInOrderId(cus_id, order_id)
	async with state.proxy() as data:	
		data['order_id'] = order_id
		data['ex_id'] = my_performers

	await CompleteOrder.step1.set()
	await c.answer()
	await c.message.delete()
	await bot.send_message(c.from_user.id, f"Оцените качество работы <code>{connection.getExecutorProfil(my_performers[0])[1]}</code>:", 
		reply_markup = buttons.rating())


async def callback_call_no(c: types.CallbackQuery, state: FSMContext):
	ids = c.data[8:].split(',')
	cus_id = ids[0]
	order_id = ids[1]
	ex_id = connection.selectMyPerInOrderId(cus_id, order_id)[0]

	ex_rate = connection.getExecutorProfil(ex_id)[6]
	connection.UpdateRate(eval(f"{ex_rate}+0.1"), ex_id)
	connection.UpdateExStatus(ex_id, 'free')
	connection.removeMyPer(int(ex_id), int(cus_id), int(order_id))	

	await c.answer()
	await c.message.delete()
	await c.message.answer("Ваш заказ завершен!")


async def callback_complete_order(c: types.CallbackQuery, state: FSMContext):
	cus_id = c.from_user.id
	order_id = c.data[15:]

	if connection.selectOrderWhereCusId(cus_id, order_id)[-8] == 'Завершён':
		await bot.answer_callback_query(c.id, show_alert = True, text = "Этот заказ уже завершен!")
		await state.finish()
	
	try:
		async with state.proxy() as data:	
			data['order_id'] = order_id
			my_performers = connection.selectMyPerInOrderId(cus_id, order_id)
			data['ex_id'] = my_performers[0]

		if my_performers[0] is not None:
			await CompleteOrder.step1.set()
			await c.answer()
			await bot.send_message(c.from_user.id, f"Оцените качество работы <code>{connection.getExecutorProfil(my_performers[0])[1]}</code>:", 
				reply_markup = buttons.rating())

		else:
			await CompleteOrder.step6.set()
			await bot.send_message(c.from_user.id, "Вы хотите завершить свой заказ?", reply_markup = buttons.yesNope(order_id))
	
	except Exception as e:
		print(e, type(e))
		await c.answer()
		await CompleteOrder.step5.set()
		await bot.send_message(c.from_user.id, "Вы действительно хотите завершить этот заказ?", reply_markup = buttons.yesNope(order_id))


async def callback_finish_in_moderation(c: types.CallbackQuery, state: FSMContext):
	ids = c.data[3:]
	order_id = ids[0]
	cus_id = c.from_user.id

	if connection.selectOrderWhereCusId(cus_id, order_id)[-8] == 'Опубликован':
		payment = int(connection.selectMyFreezingMoneys(cus_id, order_id))
		order_id = connection.selectOrderWhereCusId(cus_id, order_id)[-7]
		await c.message.answer("🔔 <b>Уведомление:</b>\n\n"
								f"Объявление под номером #1 было завершено. На Ваш счёт было начислено {payment} ₽ не использованных средств")
		connection.updateBalance(cus_id, payment, '+', payment_status = True, cus_id = cus_id, order_id = order_id)
		connection.UpdateOrderStatus(cus_id, order_id, 'Завершён')

	else:
		payment = int(connection.selectOrderWhereCusId(cus_id, order_id)[-6])
		connection.updateBalance(cus_id, payment, '+')
		await c.message.answer(
			"🔔 <b>Уведомление:</b>\n\n"

			"Ваш заказ был завершён! Средства вернутся Вам на счёт в течении 24х часов."
			)
		connection.UpdateOrderStatus(cus_id, order_id, 'Завершён')


async def callback_change(c: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		cus_id = c.from_user.id	
		order_id = data['order_id']
		my_performers = connection.selectMyPerInOrderId(cus_id, order_id)
		
		await CompleteOrder.step1.set()
		await c.answer()
		await bot.send_message(c.from_user.id, f"Оцените качество работы <code>{connection.getExecutorProfil(my_performers[0])[1]}</code>:", 
			reply_markup = buttons.rating())


async def callback_da(c: types.CallbackQuery, state: FSMContext):
	ids = c.data[3:]
	order_id = ids[0]
	cus_id = c.from_user.id

	if connection.selectOrderWhereCusId(cus_id, order_id)[-8] == 'На модерации':
		price = connection.selectOrderWhereCusId(cus_id, order_id)[13]
		connection.UpdateOrderStatus(cus_id, order_id, "Завершён", None)
		connection.updateBalance(cus_id, price, '+')
		connection.deletePayment(cus_id, price)
		await c.message.answer(
			"🔔 <b>Уведомление:</b>\n\n"

			"Ваш заказ был завершён! Средства вернутся Вам на счёт в течении 24х часов."
			)
	else:
		try:
			freezing_money = int(connection.selectMyFreezingMoneys(cus_id, order_id))
			connection.updateBalance(cus_id, freezing_money, '+')
		except Exception as e:
			print(e)

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
		print(cus_id, order_id)

		await bot.delete_message(c.from_user.id, c.message.message_id)
		await bot.send_message(cus_id, f"Отзыв от #{cus_id}\n\n"
												f"Заказчик: {orderData[1]}\n"
												f"Адрес: {orderData[2]}\n\n"
												f"{order}\n\n"
												f"Отзыв: {review}",
													disable_web_page_preview = True)	
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

		await bot.send_message(cus_id, f"<b>Отзыв от #{cus_id}</b>\n\n"
												f"<b>Заказчик:</b> <code>{orderData[1]}</code>\n"
												f"<b>Адрес:</b> <code>{orderData[2]}</code>\n\n"
												f"{order}\n\n"
												f"<b>Отзыв:</b> {review}",
													disable_web_page_preview = True)	
		await bot.send_message(cus_id, "Верно или хотите изменить отзыв?", reply_markup = buttons.realOrNot())


async def callback_publish(c: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		cus_id = c.from_user.id
		
		try:
			ex_id = data['ex_id'][0]
		except:
			ex_id = data['ex_id']

		rate = data['rate']
		review = data['review']
		order_id = data['order_id']
		orderData = connection.selectOrderWhereCusId(cus_id, order_id)
		date_of_completion = datetime.datetime.today().strftime('%d.%m.%Y')
		
		freezing_money = int(connection.selectMyFreezingMoneys(cus_id, order_id))
		connection.updateBalance(cus_id, freezing_money, '+')
		ex_rate = connection.getExecutorProfil(ex_id)[6]
		connection.UpdateRate(eval(f"{ex_rate}{rate}"), ex_id)
		connection.UpdateRating(ex_id, review, cus_id, order_id, date_of_completion)
		connection.UpdateExStatus(ex_id, 'free')
		connection.removeMyPer(int(ex_id), int(cus_id), int(order_id))	

		await c.answer( "🔔 Уведомление:\n\n"
						"Вы успешно завершили сотрудничество с исполнителем!",
							show_alert = True)
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
		except Exception as e:
			print(e)
			connection.UpdateOrderStatus(cus_id, order_id, "Завершён")
			connection.removeAll(cus_id, order_id)
			await bot.send_message(c.from_user.id, "Ваш заказ завершён")

			await state.finish()


def register_complete_order_handlers(dp: Dispatcher):
	dp.register_callback_query_handler(callback_complete_order, lambda c: c.data.startswith('complete_order'),  state = '*')
	dp.register_callback_query_handler(callback_ask_rate, lambda c: c.data.startswith('ask_rate'),  state = '*')
	dp.register_callback_query_handler(callback_call_no, lambda c: c.data.startswith('call_no'),  state = '*')
	dp.register_callback_query_handler(callback_da, lambda c: c.data.startswith('da'),  state = CompleteOrder.step5)
	dp.register_callback_query_handler(callback_finish_in_moderation, lambda c: c.data.startswith('da'),  state = CompleteOrder.step6)
	dp.register_callback_query_handler(ask_comment, lambda c: c.data.startswith('!rate'),  state = CompleteOrder.step1)
	dp.register_callback_query_handler(callback_leave_comment, lambda c: c.data == 'leave_comment',  state = CompleteOrder.step2)
	dp.register_callback_query_handler(callback_no_com, lambda c: c.data == 'no_com',  state = CompleteOrder.step2)

	dp.register_message_handler(text_comment, state = CompleteOrder.step3)

	dp.register_callback_query_handler(callback_change, lambda c: c.data == 'to_change',  state = CompleteOrder.step4)
	dp.register_callback_query_handler(callback_publish, lambda c: c.data == 'to_publish',  state = CompleteOrder.step4)