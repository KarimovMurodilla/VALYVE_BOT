import datetime
import random

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from app.admin import admin_connection, admin_buttons
from app.qiwi import Payment, wallet
from .. import file_ids, config, buttons, connection

bot = Bot(token=config.TOKEN, parse_mode = 'html')


class IcStock(StatesGroup):
	step1 = State()
	step2 = State()
	step3 = State()
	step4 = State()


class IcOneTime(StatesGroup):
	step1 = State()
	step2 = State()
	step3 = State()
	step4 = State()


class AdminWithDraw(StatesGroup):
	step1 = State()
	step2 = State()
	step3 = State()


bank = sum([int(i[0]) for i in admin_connection.getStatPayment('bank', None, None)])

# ----ADMIN WITHDRAW----
async def callback_admin_withdraw(c: types.CallbackQuery, state: FSMContext):
	user_id = c.from_user.id

	if bank:
		await c.answer()
		await AdminWithDraw.step1.set()
		await bot.send_message(c.from_user.id, "На  какую сумму Вы хотите сделать вывод?", 
			reply_markup = admin_buttons.admin_canc())

	else:
		await c.answer(show_alert = True, text = "⚠️ <b>Ошибка:</b>\n\n"
						"У вас недостаточно средств")


async def admin_process_withdraw(message: types.Message, state: FSMContext):
	user_id = message.from_user.id
	today = datetime.datetime.today()

	history = int(connection.getWithDraw(user_id, today))
	print(history)

	if message.text.isdigit():
		if int(message.text) <= bank:
			async with state.proxy() as data:
				data['user_money'] = message.text

			commission = wallet.commission(pid=99, recipient=config.QIWI_NUMBER, amount=int(message.text))
			await message.answer("<b>Комиссия Qiwi</b>\n" 
								f"<b>Карта:</b> <code>2% + 50.00 ₽</code>\n" 
								"<b>└Qiwi Кошелёк:</b> <code>2%</code>")
			await message.answer("На что Вы хотите вывести средства?",
									reply_markup = admin_buttons.adminWithdrawBtns())

		else:
			await message.answer("⚠️ <b>Ошибка:</b>\n\n"
								 "У вас недостаточно средств")
	else:
		await message.answer("⚠️ <b>Ошибка:</b>\n\n"
							 "Вводите только цифрами!")


async def admin_callback_pay_with_card(c: types.CallbackQuery, state: FSMContext):
	await c.answer()	

	async with state.proxy() as data:
		data['type'] = 'card'

	await AdminWithDraw.step2.set()
	await c.message.answer("Отправьте номер карты, для вывода средств на неё.")


async def admin_callback_pay_with_purse(c: types.CallbackQuery, state: FSMContext):
	await c.answer()

	async with state.proxy() as data:
		data['type'] = 'purse'

	await AdminWithDraw.step3.set()
	await c.message.answer("Отправьте мне номер телефона, который привязан к кошельку.")


async def admin_process_withdraw_check_card(message: types.Message, state: FSMContext):
	user_id = message.from_user.id	

	if message.text.isdigit():
		async with state.proxy() as data:
			data['recipient'] = message.text
			user_money = data['user_money']

			await message.answer(  "<b>Информация об выводе</b>\n" 
								   f"<b>Списание:</b> <code>{float(int(user_money)+int(user_money)/100*2+50)} ₽</code>\n"
								   f"<b>Зачисление:</b> <code>{float(user_money)}</code>\n"
								   f"<b>Карта:</b> <code>{message.text}</code>",
										reply_markup = admin_buttons.adminWithdrawCheckBtns())

	else:
		await message.answer("⚠️ <b>Ошибка:</b>\n\n"
					 "Вводите только цифрами!")


async def admin_process_withdraw_check_purse(message: types.Message, state: FSMContext):
	user_id = message.from_user.id	

	if message.text.isdigit():
		async with state.proxy() as data:
			data['recipient'] = message.text
			user_money = int(data['user_money'])

			await message.answer(  "<b>Информация об выводе</b>\n" 
								   f"<b>К выводу:</b> <code>{user_money + user_money/100*2} ₽</code>\n"
								   f"<b>На кошелёк:</b> <code>{message.text}</code>",
										reply_markup = admin_buttons.adminWithdrawCheckBtns())

	else:
		await message.answer("⚠️ <b>Ошибка:</b>\n\n"
					 "Вводите только цифрами!")		


async def admin_callback_confirm(c: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		type_card = data['type']
		user_id = c.from_user.id
		recipient = data['recipient']
		user_money = data['user_money']
		comment = (f"{user_id}_{random.randint(1000, 9999)}")
	
	if type_card == 'card':
		prv_id = Payment.get_card_system(recipient)
		payment_data = {'sum': user_money,
						'to_card': recipient,
						'prv_id': prv_id}
		answer_from_qiwi = Payment.send_to_card(payment_data)

		try:
			status_transaction = answer_from_qiwi["transaction"]["state"]
			if status_transaction['code'] == "Accepted":
				today = datetime.datetime.today()
				connection.addBotPayment(user_id, 'admin_withdraw', -int(user_money), today)
				await c.message.answer("🔔 <b>Уведомление:</b>\n\nВаша заявка принята в обработку!\nОжидайте перевода в течении 24х часов.")

		except Exception as e:
			print(answer_from_qiwi)
			print(e, type(e))
			await c.message.answer("⚠️ <b>Ошибка:</b>\n\n"
				"Пожалуйста проверьте карта/номер получателя !")

			await state.finish()


	elif type_card == 'purse':
		answer_from_qiwi = Payment.send_to_qiwi(recipient, user_money)
		try:
			status_transaction = answer_from_qiwi["transaction"]["state"]
			
			if status_transaction['code'] == "Accepted":
				today = datetime.datetime.today()
				# fee_with_commission = int(user_money)+int(user_money)/100*2+50
				connection.addPayment(user_id, 'profit', -int(user_money), today)
				# connection.updateBalance(user_id, fee_with_commission, '-')
				await c.message.answer("🔔 <b>Уведомление:</b>\n\nВаша заявка принята в обработку!\nОжидайте перевода в течении 24х часов.")

		except Exception as e:
			print(e, type(e))
			await c.message.answer("⚠️ <b>Ошибка:</b>\n\n"
				"Пожалуйста проверьте карта/номер получателя !")

			await state.finish()


# -----REFRESH BANK STATIC-----
async def callback_refresh(c: types.CallbackQuery, state: FSMContext):
	today = datetime.datetime.today()
	per_month = datetime.timedelta

	income_month = sum([int(i[0]) for i in admin_connection.getStatPayment('user_payment', today-per_month(days=30), today)])
	income_week = sum([int(i[0]) for i in admin_connection.getStatPayment('user_payment', today-per_month(days=7), today)])

	costs_month = sum([int(i[0]) for i in admin_connection.getStatPayment('bot_payment', today-per_month(days=30), today)])
	costs_week = sum([int(i[0]) for i in admin_connection.getStatPayment('bot_payment', today-per_month(days=7), today)])

	profit_month = sum([int(i[0]) for i in admin_connection.getStatPayment('profit', today-per_month(days=30), today)])
	profit_week = sum([int(i[0]) for i in admin_connection.getStatPayment('profit', today-per_month(days=7), today)])

	bank = sum([int(i[0]) for i in admin_connection.getStatPayment('bank', None, None)])

	top_up_month = sum([int(i[0]) for i in admin_connection.getStatPayment('top_up', today-per_month(days=30), today)])
	top_up_week = sum([int(i[0]) for i in admin_connection.getStatPayment('top_up', today-per_month(days=7), today)])

	withdraw_month = sum([int(i[0]) for i in admin_connection.getStatPayment('withdraw', today-per_month(days=30), today)])
	withdraw_week = sum([int(i[0]) for i in admin_connection.getStatPayment('withdraw', today-per_month(days=7), today)])

	await c.answer("✅ Обновлено")
	await c.message.edit_media(types.InputMedia(
								media = file_ids.PHOTO['bank'],
							  	caption =  "<b>Пополнено за месяц</b>\n"
											f"└  <code>{float(top_up_month)} ₽</code>\n"
											" За неделю\n"
											f" └ <code>{float(top_up_week)} ₽</code>\n\n"
										    
										    "<b>Доход за месяц</b>\n"
											f"└ <code>{float(income_month)} ₽</code>\n"
											 " <b>За неделю</b>\n"
											f" └ <code>{float(income_week)} ₽</code>\n\n"

											"<b>Расходы за месяц</b>\n"
											f"└ <code>{float(costs_month)} ₽</code>\n"
											"<b>За неделю</b>\n"
											f"└ <code>{float(costs_week)} ₽</code>\n\n"
											
											"<b>Выведено за месяц</b>\n"
											f"└  <code>{float(withdraw_month)} ₽</code>\n"
											 "За неделю\n"
											f" └ <code>{float(withdraw_week)} ₽</code>\n\n"

											"<b>Прибыль за месяц</b>\n"
											f"└ <code>{float(profit_month)} ₽</code>\n"
											" <b>За неделю</b>\n"			
											f" └ <code>{float(profit_week)} ₽</code>\n\n"

											f"<b>Банк проекта:</b> <code>{Payment.get_my_balance()} ₽</code>\n"
											f"<b>К выводу:</b> <code>{float(bank)} ₽</code>"),
												reply_markup = admin_buttons.bankProject())


# ----IC STOCK----
async def callback_ic_stock(c: types.CallbackQuery, state: FSMContext):
	await c.answer()
	await IcStock.step1.set()

	ic_stock = admin_connection.selectIcs('ic_stock', 1)[0]

	await c.message.answer(
		"Информация доли\n" 
		f"Процент: <code>{ic_stock}/1 сутки</code>", 
			reply_markup = admin_buttons.changeIcStock())


async def set_ic_stock(c: types.CallbackQuery, state: FSMContext):
	await c.answer()
	await IcStock.next()

	await c.message.answer(
		"Какую сумму вы хотите выставить?",
			reply_markup = admin_buttons.admin_canc())


async def input_price(message: types.Message, state: FSMContext):
	await IcStock.next()
	if message.text.isdigit():
		async with state.proxy() as data:
			data['new_price'] = message.text

		await message.answer(
			"Информация доли\n" 
			f"Процент: <code>{message.text}/1 сутки</code>", 
				reply_markup = admin_buttons.icOneSets())

	else:
		await message.answer("Введите только цифрами")


async def callback_aPubslish(c: types.CallbackQuery, state: FSMContext):
	await c.answer()
	async with state.proxy() as data:
		new_price = data['new_price']

		admin_connection.updateIcStock(new_price, 1)
		await c.message.delete()
		await c.message.answer("✅ Опубликовано", reply_markup = admin_buttons.adminPanel())

	await state.finish()


async def callback_aCancel(c: types.CallbackQuery, state: FSMContext):
	await c.message.delete()
	await c.message.answer("Отменено", reply_markup = admin_buttons.adminPanel())
	await state.finish()


# ----IC ONE TIME----
async def callback_ic_one_time(c: types.CallbackQuery, state: FSMContext):
	await c.answer()
	await IcOneTime.step1.set()

	total_1 = admin_connection.selectIcs('ic_one_time', 1)[0]
	total_2 = admin_connection.selectIcs('ic_one_time', 2)[0]
	total_3 = admin_connection.selectIcs('ic_one_time', 3)[0]

	await bot.send_photo(
		chat_id = c.message.chat.id, 
		photo = file_ids.PHOTO['price'],
		caption = f"<b>1.</b> <code>3</code> дня в ленте - <code>{total_1}</code> <code>₽</code>\n"
				  f"<b>2.</b> <code>7</code> дней в ленте - <code>{total_2}</code> <code>₽</code>\n"
				  f"<b>3.</b> <code>30</code> дней в ленте - <code>{total_3}</code> <code>₽</code>\n",
					reply_markup = admin_buttons.adminPrice(1, 2, 3))


async def set_ic_one_time(c: types.CallbackQuery, state: FSMContext):
	await c.answer()
	await IcOneTime.next()
	rowid = c.data[7:]
	async with state.proxy() as data:
		data['rowid'] = rowid

	await c.message.answer(
		"Какую сумму вы хотите выставить?", 
			reply_markup = admin_buttons.admin_canc())


async def input_price_one_time(message: types.Message, state: FSMContext):
	await IcOneTime.next()
	if message.text.isdigit():
		async with state.proxy() as data:
			data['new_price'] = message.text
			rowid = data['rowid']

			total_1 = admin_connection.selectIcs('ic_one_time', 1)[0]
			total_2 = admin_connection.selectIcs('ic_one_time', 2)[0]
			total_3 = admin_connection.selectIcs('ic_one_time', 3)[0]

			if rowid == '1':
				total_1 = message.text
			
			elif rowid == '2':
				total_2 = message.text			

			elif rowid == '3':
				total_3 = message.text

			await bot.send_photo(
				chat_id = message.chat.id, 
				photo = file_ids.PHOTO['price'],
				caption = f"<b>1.</b> <code>3</code> дня в ленте - <code>{total_1}</code> <code>₽</code>\n"
						  f"<b>2.</b> <code>7</code> дней в ленте - <code>{total_2}</code> <code>₽</code>\n"
						  f"<b>3.</b> <code>30</code> дней в ленте - <code>{total_3}</code> <code>₽</code>\n",
							reply_markup = admin_buttons.icOneSets())

	else:
		await message.answer("Введите только цифрами")


async def callback_aPubslish_one_time(c: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		new_price = data['new_price']
		rowid = data['rowid']

		admin_connection.updateIcOneTime(new_price, rowid)
		await c.message.delete()
		await c.message.answer("✅ Опубликовано", reply_markup = admin_buttons.adminPanel())

	await state.finish()


# ----LIST OF EXPENSES----
async def callback_list_of_expenses(c: types.CallbackQuery, state: FSMContext):
	today = datetime.datetime.today()
	per_month = datetime.timedelta

	refferal_month = sum([int(i[0]) for i in admin_connection.getStatPayment('refferal', today-per_month(days=30), today)])
	refferal_week = sum([int(i[0]) for i in admin_connection.getStatPayment('refferal', today-per_month(days=7), today)])

	waiting_month = sum([int(i[0]) for i in admin_connection.getStatPayment('payment_for_waiting', today-per_month(days=30), today)])
	waiting_week = sum([int(i[0]) for i in admin_connection.getStatPayment('payment_for_waiting', today-per_month(days=7), today)])

	moderation = sum([i[0] for i in admin_connection.selectOrderPrice()])
	stock = sum([i[0]*i[1] for i in admin_connection.selectWaitingPayments()])

	payment_for_waiting = sum([int(i[0]) for i in connection.getPaymentsforWaiting()])

	if c.data == 'list_of_expenses':
		await c.answer()
		await c.message.answer(
			"Исполнителю в запас\n"
			"Выплаты за месяц\n" 
			f"└<code>{float(waiting_month)} ₽</code>\n"
			"За неделю\n"
			f"└<code>{float(waiting_week)} ₽</code>\n\n"

			"Реферальная система\n" 
			"Выплаты за месяц\n"
			f"└<code>{float(refferal_month)} ₽</code>\n"
			"За неделю\n"
			f"└<code>{float(refferal_week)} ₽</code>\n\n" 

			"Купоны VALYVE\n"
			"Выплаты за месяц\n"
			f"└<code>0.0 ₽</code>\n\n"

			"Заморожено средств\n"
			f"Модерация: <code>{float(moderation)} ₽</code>\n"
			f"Купоны: <code>0.0 ₽</code>\n"
			f"└ Запас: <code>{float(moderation - payment_for_waiting)} ₽</code>",
				reply_markup = admin_buttons.update(title = 'expenses')
			)

	else:
		await c.answer("✅ Обновлено")
		await c.message.edit_text(
			"Исполнителю в запас\n"
			"Выплаты за месяц\n" 
			f"└<code>{float(waiting_month)} ₽</code>\n"
			"За неделю\n"
			f"└<code>{float(waiting_week)} ₽</code>\n\n"

			"Реферальная система\n" 
			"Выплаты за месяц\n"
			f"└<code>{float(refferal_month)} ₽</code>\n"
			"За неделю\n"
			f"└<code>{float(refferal_week)} ₽</code>\n\n" 

			"Купоны VALYVE\n"
			"Выплаты за месяц\n"
			f"└<code>0.0 ₽</code>\n\n"

			"Заморожено средств\n"
			f"Модерация: <code>{float(moderation)} ₽</code>\n"
			f"Купоны: <code>0.0 ₽</code>\n"
			f"└ Запас: <code>{float(moderation - payment_for_waiting)} ₽</code>",
				reply_markup = admin_buttons.update(title = 'expenses')
			)


async def callback_list_of_reports(c: types.CallbackQuery, state: FSMContext):
	pass




def register_bank_controls(dp: Dispatcher):
	dp.register_callback_query_handler(callback_admin_withdraw, lambda c: c.data == "admin_withdraw", chat_id = config.ADMINS, state = '*')
	dp.register_callback_query_handler(callback_admin_withdraw, lambda c: c.data == 'admin_change_withdraw',  state = '*')
	dp.register_callback_query_handler(admin_callback_pay_with_card, lambda c: c.data == 'admin_card',  state = '*')
	dp.register_callback_query_handler(admin_callback_pay_with_purse, lambda c: c.data == 'admin_purse',  state = '*')	
	dp.register_message_handler(admin_process_withdraw, state = AdminWithDraw.step1)
	dp.register_message_handler(admin_process_withdraw_check_card, state = AdminWithDraw.step2)
	dp.register_message_handler(admin_process_withdraw_check_purse, state = AdminWithDraw.step3)
	dp.register_callback_query_handler(admin_callback_confirm, lambda c: c.data == 'admin_confirm',  state = '*')

	dp.register_callback_query_handler(callback_refresh, lambda c: c.data == "refresh", chat_id = config.ADMINS, state = '*')

	dp.register_callback_query_handler(callback_ic_stock, lambda c: c.data == "ic_stock", chat_id = config.ADMINS, state = '*')
	dp.register_callback_query_handler(set_ic_stock, lambda c: c.data == 'change_stock', chat_id = config.ADMINS, state = IcStock.step1)
	dp.register_message_handler(input_price, chat_id = config.ADMINS, state = IcStock.step2)
	dp.register_callback_query_handler(callback_aPubslish, lambda c: c.data == "aPublish", chat_id = config.ADMINS, state = IcStock.step3)
	dp.register_callback_query_handler(callback_aCancel, lambda c: c.data == "aCancel", chat_id = config.ADMINS, state = '*')

	dp.register_callback_query_handler(callback_ic_one_time, lambda c: c.data == "ic_one_time", chat_id = config.ADMINS, state = '*')
	dp.register_callback_query_handler(set_ic_one_time, lambda c: c.data.startswith("aPrice"), chat_id = config.ADMINS, state = IcOneTime.step1)
	dp.register_message_handler(input_price_one_time, chat_id = config.ADMINS, state = IcOneTime.step2)
	dp.register_callback_query_handler(callback_aPubslish_one_time, lambda c: c.data == "aPublish", chat_id = config.ADMINS, state = IcOneTime.step3)
	
	dp.register_callback_query_handler(callback_list_of_expenses, lambda c: c.data == "list_of_expenses" or c.data == 'update_expenses', chat_id = config.ADMINS, state = '*')
	dp.register_callback_query_handler(callback_list_of_reports, lambda c: c.data == "list_of_reports", chat_id = config.ADMINS, state = '*')