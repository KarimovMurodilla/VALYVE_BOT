import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from .. import buttons, config, connection, file_ids, getLocationInfo


bot = Bot(token=config.TOKEN, parse_mode = 'html')


class CallPerformer(StatesGroup):
	step1 = State()
	step2 = State()
	step3 = State()
	step4 = State()


class Refuse(StatesGroup):
	step1 = State()
	step2 = State()


class FindNewEx(StatesGroup):
	step1 = State()
	step2 = State()
	step3 = State()
	step4 = State()


def fast_answer(func):
	async def wrapper(c: types.CallbackQuery, state: FSMContext):
		await c.answer()
		
		return 	await func(c, state)
	return wrapper


async def callback_call_performer(c: types.CallbackQuery, state: FSMContext):
	order_id = c.data[12:]

	if connection.selectMyPerWhereOrderId(c.from_user.id, order_id)[0]:
		await c.answer()
		async with state.proxy() as data:
			data['order_id'] = order_id

		await CallPerformer.step1.set()
		await bot.send_message(c.from_user.id, "Укажите дату начало работы. В таком формате (день.месяц.год)",
			reply_markup = buttons.back_canc)

	else:
		await c.answer("⚠️ Ошибка:\n\nУ вас еще не имеется исполнитель!!", show_alert = True)


async def process_call_performer(message: types.Message, state: FSMContext):
	y = datetime.datetime.now().year
	date = message.text.split('.')
	
	try:
		if int(date[0]) <= 31 and int(date[1]) <= 12 and int(date[2]) >= y:
			await CallPerformer.step2.set()
			async with state.proxy() as data:
				data['start_day'] = message.text

			await message.answer("Укажите дату конца работы. В таком формате (день.месяц.год)")

		else:
			await message.answer("Укажите дату начало работы. В таком формате (день.месяц.год)")

	except Exception as e:
		print(e)
		await message.answer("Укажите дату начало работы. В таком формате (день.месяц.год)")



async def process_output_comment(message: types.Message, state: FSMContext):
	y = datetime.datetime.now().year
	date = message.text.split('.')

	try:
		if int(date[0]) <= 31 and int(date[1]) <= 12 and int(date[2]) >= y:
			async with state.proxy() as data:
				data['end_day'] = message.text

				await message.answer("Хотите указать комментарий ?",
					reply_markup = buttons.skipBtn())
				await CallPerformer.step3.set()

		else:
			await message.answer("Укажите дату конца работы. В таком формате (день.месяц.год)")
			
	except Exception as e:
		print(e)
		await message.answer("Укажите дату конца работы. В таком формате (день.месяц.год)")


async def callback_cskip(c: types.CallbackQuery, state: FSMContext):
	await CallPerformer.next()
	async with state.proxy() as data:
		data['comment'] = ''
		start_day = data['start_day']
		end_day = data['end_day']

		await c.message.delete()
		await c.message.answer("<b>Информация об вызове</b>\n"
							f"<b>Начало:</b> <code>{start_day}</code>\n"
							f"<b>Конец:</b> <code>{end_day}</code>\n\n"

							f"{data['comment']}",
								reply_markup = buttons.answerSets(answer = False))

async def process_end(message: types.Message, state: FSMContext):
	await CallPerformer.next()
	async with state.proxy() as data:
		data['comment'] = f"<b>Комментарий:</b>\n<code>{message.text}</code>"
		start_day = data['start_day']
		end_day = data['end_day']

		await message.answer("<b>Информация об вызове</b>\n"
							f"<b>Начало:</b> <code>{start_day}</code>\n"
							f"<b>Конец:</b> <code>{end_day}</code>\n\n"

							f"{data['comment']}",
								reply_markup = buttons.answerSets(answer = False))


@fast_answer
async def callback_change_call(c: types.CallbackQuery, state: FSMContext):
	await CallPerformer.step1.set()
	await bot.send_message(c.from_user.id, "Укажите дату начало работы. В таком формате (день.месяц.год)",
		reply_markup = buttons.back_canc)


@fast_answer
async def callback_send_call(c: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		order_id = data['order_id']
		start_day = data['start_day']
		end_day = data['end_day']
		comment = data['comment']

		ex_data = connection.selectMyPerWhereOrderId(c.from_user.id, order_id)[0]
		cus_data = connection.selectAll(c.from_user.id)

		s = start_day.split('.')
		e = end_day.split('.')

		d = datetime.date(int(s[2]), int(s[1]), int(s[0]))
		d1 = datetime.date(int(e[2]), int(e[1]), int(e[0]))
		delta = d1-d

		
		await c.message.delete()
		await c.message.answer("✅ Вызов отправлено")
		await bot.send_message(ex_data, "🔔 Уведомление:\n\n"
										f"Заказчик <code>{cus_data[0]}</code>, Вызывает вас на {delta.days} дней.\n\n"
										f"Начало: {start_day}\n"
										f"Конец: {end_day}\n\n"
										f"{comment}",
											reply_markup = buttons.executor_choice(c.from_user.id, order_id, start_day, end_day))

		await state.finish()


async def callback_refuse(c: types.CallbackQuery, state: FSMContext):
	ids = c.data[7:].split(',')
	async with state.proxy() as data:
		data['cus_id'] = ids[0]
		data['order_id'] = ids[1]
		data['start_day'] = ids[2]
		data['end_day'] = ids[3]

		await Refuse.step1.set()
		await c.message.delete()
		await c.message.answer("По какой причине вы отказываетесь?",
			reply_markup = buttons.back_canc)



async def process_refuse(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['comment'] = message.text
		cus_id = data['cus_id']

		await Refuse.next()
		await message.answer(f"<b>Вы отказываетесь по причине:</b>\n\n<code>{message.text}</code>",
			reply_markup = buttons.answerSets(answer = False, r = 2))



async def callback_send_refuse(c: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		user_id = c.from_user.id
		cus_id = data['cus_id']
		order_id = data['order_id']
		start_day = data['start_day']
		end_day = data['end_day']
		comment = data['comment']

		await c.message.delete()
		await c.message.answer("Мы уведомили заказчика что Вы отказались выйти на это время.", reply_markup = buttons.autoMenu(connection.checkUserStatus(c.from_user.id)[0]))
		await bot.send_message(cus_id, "🔔 Уведомление:\n\n"
									   f"Исполнитель {connection.checkExecutor(user_id)[1]} отказался выходить.\n\n"
									   f"Причина:\n<code>{comment}</code>",
									   		reply_markup = buttons.findNewEx(order_id, start_day, end_day))


async def callback_change_refuse(c: types.CallbackQuery, state: FSMContext):
	await Refuse.step1.set()
	await c.message.answer("По какой причине вы отказываетесь?",
		reply_markup = buttons.back_canc)

	
# Accept
async def callback_accept(c: types.CallbackQuery, state: FSMContext):
	user_id = c.from_user.id
	cus_id = c.data[7:]

	await c.message.delete()
	await c.message.answer("Мы уведомили заказчика что Вы согласны выйти на это время.", reply_markup = buttons.autoMenu(connection.checkUserStatus(c.from_user.id)[0]))
	await bot.send_message(cus_id, "🔔 Уведомление:\n\n"
									f"Исполнитель {connection.checkExecutor(user_id)[1]} согласился выйти.")



# -----------------------------------------------
async def callback_find_new_ex(c: types.CallbackQuery, state: FSMContext):
	user_id = c.from_user.id
	ids = c.data[8:].split(',')
	order_id = ids[0]
	start_day = ids[1]
	end_day = ids[2]
	item = connection.selectOrders(user_id)[int(order_id)]

	async with state.proxy() as data:
		data['order_id'] = order_id


	await FindNewEx.step1.set()
	await c.message.answer( f"<b>Заказчик:</b> <code>{item[1]}</code>\n"
						    f"<b>Адреc:</b> <code>{item[2]}</code>\n\n"

						    f"Начало: {start_day}\n\n"
						  
						    f"<b>Должность:</b> <code>{item[6]}</code>\n"
						    f"<b>Время работы:</b> <code>{item[4]}</code>\n"
						    f"<b>График:</b> <code>{item[3]}</code>\n"
						    f"<b>Смена:</b> <code>{item[5]}</code>\n\n"

						    f"<b>Требование:</b>\n<code>{item[14]}</code>\n\n"
						    f"<b>Обязанности:</b>\n<code>{item[15]}</code>\n\n"

						    f"{item[7]}",
								reply_markup = buttons.realOrNot())


async def change_new_order(c: types.CallbackQuery, state: FSMContext):
	await FindNewEx.next()
	await c.message.answer("Укажите дату начало работы. В таком формате (день.месяц.год)", 
		reply_markup = buttons.back_canc)


async def process_input_start_day(message: types.Message, state: FSMContext):
	y = datetime.datetime.now().year
	date = message.text.split('.')
	try:
		if int(date[0]) <= 31 and int(date[1]) <= 12 and int(date[2]) >= y:
			async with state.proxy() as data:
				data['start_day'] = message.text
			await message.answer("Укажите дату конца работы. В таком формате (день.месяц.год)")
			await FindNewEx.next()

		else:
			await message.answer("Укажите дату начало работы. В таком формате (день.месяц.год)")

	
	except Exception as e:
		print(e)
		await message.answer("Укажите дату начало работы. В таком формате (день.месяц.год)")


async def process_input_end_day(message: types.Message, state: FSMContext):
	y = datetime.datetime.now().year
	date = message.text.split('.')

	try:
		if int(date[0]) <= 31 and int(date[1]) <= 12 and int(date[2]) >= y:
			async with state.proxy() as data:
				data['end_day'] = message.text

				await message.answer("Хотите указать комментарий ?", reply_markup = buttons.skipBtn())
				await FindNewEx.next()

		else:
			await message.answer("Укажите дату конца работы. В таком формате (день.месяц.год)")
			
	except Exception as e:
		print(e)
		await message.answer("Укажите дату конца работы. В таком формате (день.месяц.год)")


async def show_without_comment(c: types.CallbackQuery, state: FSMContext):
	await FindNewEx.step1.set()

	user_id = c.from_user.id
	async with state.proxy() as data:
		data['comment'] = ''
		start_day = data['start_day']
		end_day = data['end_day']
		order_id = data['order_id']

	item = connection.selectOrders(cus_id)[int(order_id)]
	await c.message.answer( f"<b>Заказчик:</b> <code>{item[1]}</code>\n"
						    f"<b>Адреc:</b> <code>{item[2]}</code>\n\n"

						    f"Начало: {start_day}\n\n"
						  
						    f"<b>Должность:</b> <code>{item[6]}</code>\n"
						    f"<b>Время работы:</b> <code>{item[4]}</code>\n"
						    f"<b>График:</b> <code>{item[3]}</code>\n"
						    f"<b>Смена:</b> <code>{item[5]}</code>\n\n"

						    f"<b>Требование:</b>\n<code>{item[14]}</code>\n\n"
						    f"<b>Обязанности:</b>\n<code>{item[15]}</code>\n\n"

						    f"{data['comment']}",
								reply_markup = buttons.realOrNot())


async def show_with_comment(message: types.Message, state: FSMContext):
	await FindNewEx.step1.set()

	user_id = message.from_user.id
	async with state.proxy() as data:
		data['comment'] = f"<b>Комментарий:</b>\n<code>{message.text}</code>"
		start_day = data['start_day']
		end_day = data['end_day']
		order_id = data['order_id']

	item = connection.selectOrders(user_id)[int(order_id)]
	await message.answer( f"<b>Заказчик:</b> <code>{item[1]}</code>\n"
						    f"<b>Адреc:</b> <code>{item[2]}</code>\n\n"

						    f"Начало: {start_day}\n\n"
						  
						    f"<b>Должность:</b> <code>{item[6]}</code>\n"
						    f"<b>Время работы:</b> <code>{item[4]}</code>\n"
						    f"<b>График:</b> <code>{item[3]}</code>\n"
						    f"<b>Смена:</b> <code>{item[5]}</code>\n\n"

						    f"<b>Требование:</b>\n<code>{item[14]}</code>\n\n"
						    f"<b>Обязанности:</b>\n<code>{item[15]}</code>\n\n"

						    f"{data['comment']}",
								reply_markup = buttons.realOrNot())

# ---Publish---
async def callback_publish_new_order(c: types.CallbackQuery, state: FSMContext):
	user_id = c.from_user.id
	async with state.proxy() as data:
		start_day = data['start_day']
		end_day = data['end_day']
		order_id = data['order_id']
		comment = data['comment']
		
		s = start_day.split('.')
		e = end_day.split('.')

		d = datetime.date(int(s[2]), int(s[1]), int(s[0]))
		d1 = datetime.date(int(e[2]), int(e[1]), int(e[0]))
		delta = d1-d

		payment_for_waiting = delta.days

		await c.message.delete()
		await c.message.answer("Ваш заказ отправлен на модерацию")
		connection.orderMiniUpdate(user_id, order_id, comment, start_day, end_day, payment_for_waiting)



def register_order_handlers(dp: Dispatcher):
	dp.register_callback_query_handler(callback_call_performer, lambda c: c.data.startswith('call_to_per'),  state = '*')    
	dp.register_message_handler(process_call_performer, state = CallPerformer.step1)
	dp.register_message_handler(process_output_comment, state = CallPerformer.step2)
	dp.register_message_handler(process_end, state = CallPerformer.step3)
	dp.register_callback_query_handler(callback_cskip, lambda c: c.data == 'cSkip', state = CallPerformer.step3)
	dp.register_callback_query_handler(callback_change_call, lambda c: c.data == 'change_complaint',  state = CallPerformer.step4)	
	dp.register_callback_query_handler(callback_send_call, lambda c: c.data == 'send_complaint',  state = CallPerformer.step4)	

	dp.register_callback_query_handler(callback_refuse, lambda c: c.data.startswith('refuse'),  state = '*')
	dp.register_message_handler(process_refuse, state = Refuse.step1)
	dp.register_callback_query_handler(callback_send_refuse, lambda c: c.data == 'send_complaint',  state = Refuse.step2)
	dp.register_callback_query_handler(callback_change_refuse, lambda c: c.data == 'change_complaint',  state = Refuse.step2)

	dp.register_callback_query_handler(callback_accept, lambda c: c.data.startswith('accept'),  state = '*')	

	dp.register_callback_query_handler(callback_find_new_ex, lambda c: c.data.startswith('find_ex'),  state = '*')	
	dp.register_callback_query_handler(change_new_order, lambda c: c.data == 'to_change',  state = FindNewEx.step1)	
	dp.register_message_handler(process_input_start_day, state = FindNewEx.step2)
	dp.register_message_handler(process_input_end_day, state = FindNewEx.step3)
	dp.register_callback_query_handler(show_without_comment, lambda c: c.data == 'cSkip', state = FindNewEx.step4)
	dp.register_message_handler(show_with_comment, state = FindNewEx.step4)

	dp.register_callback_query_handler(callback_publish_new_order, lambda c: c.data == 'to_publish',  state = FindNewEx.step1)	