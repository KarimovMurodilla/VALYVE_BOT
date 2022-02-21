import asyncio
import random
import datetime
import pyqiwi
from pyqiwip2p import QiwiP2P

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from app.qiwi import Payment
from app.admin.admin_connection import selectStatuses
from .. import buttons, config, connection, file_ids


class TopUp(StatesGroup):
	step1 = State()


class WithDraw(StatesGroup):
	step1 = State()
	step2 = State()
	step3 = State()


class BuyCoupon(StatesGroup):
	step1 = State()


bot = Bot(token=config.TOKEN, parse_mode = 'html')
p2p = QiwiP2P(auth_key = config.QIWI_P2P_TOKEN)
wallet = pyqiwi.Wallet(token = config.QIWI_TOKEN, number = config.QIWI_NUMBER)


def checkPaymentStatus(name):
	def decorator(func):
		async def wrapper(c: types.CallbackQuery, state: FSMContext):
			if selectStatuses(name) == '🔴':
				await c.answer("⚠️ Ошибка:\n\n"
							   "Функция временно отключена, идут технические работы. Приносим извинения за неудобства! 😢", show_alert = True)
			else:
				return await func(c, state)
		return wrapper
	return decorator


async def callback_bank(c: types.CallbackQuery, state: FSMContext):
	user_id = c.from_user.id
	await c.answer()

	# try:
	# response = connection.selectMyJob(user_id)
	# date = response[4].split(',')
	# total_days = int(response[-1])
	# orderData = connection.selectOrderWhereCusId(response[0], response[1])
	# payment_for_waiting = int(orderData[-1])
	# date1 = datetime.datetime.now()
	# date2 = datetime.datetime(day=int(date[2]), month=int(date[1]), year=int(date[0]))
	# timedelta = date1-date2
	# result_date = (timedelta.seconds)
	# result_minutes = ((result_date % 3600) // 60) - total_days - 3
	# print(result_minutes)

	# 	if result_minutes >= 1:
	# 		connection.updateBalance(user_id, result_minutes*payment_for_waiting, '+')
	# 		connection.updateTotalDays(result_minutes, user_id)
	# 		connection.addBotPayment(user_id, 'payment_for_waiting', result_minutes*payment_for_waiting, date1)
				
	# except Exception as e:
	# 	print(e)

	balance = connection.checkReferral(user_id)
	coupons = connection.getUserCpns(user_id)[0]
	await bot.send_photo(
		chat_id = c.from_user.id, 
		photo = file_ids.PHOTO['bank'],
		caption = f"<b>Баланс:</b> <code>{float(balance[6])} ₽</code>\n\n"
				  f"<b>Купон VALYVE:</b> <code>{coupons} шт</code>\n\n"
				  f"<b>Реферальная система</b>\n"
				  f"├ <b>Активных:</b> <code>{balance[5]} уч</code>\n"
				  f"└ <b>Ожидание:</b> <code>{balance[4]} уч</code>\n\n"
				  f"🗣 <b>Пригласительная ссылка</b>\n"
				  f"└ <a href='https://t.me/ValyveExchange_bot?start={user_id}'>Зажми чтоб скопировать</a>",
					reply_markup = buttons.referral_settings)


# -----Withdraw----
@checkPaymentStatus('WITHDRAW')
async def callback_withdraw(c: types.CallbackQuery, state: FSMContext):
	user_id = c.from_user.id

	if connection.get_id(user_id)[6]:
		await c.answer()
		await WithDraw.step1.set()
		await bot.send_message(c.from_user.id, "На  какую сумму Вы хотите сделать вывод?", 
			reply_markup = buttons.back_canc)

	else:
		await c.answer(show_alert = True, text = "⚠️ Ошибка:\n\n"
						"У вас недостаточно средств")


@checkPaymentStatus('WITHDRAW')
async def process_withdraw(message: types.Message, state: FSMContext):
	user_id = message.from_user.id
	today = datetime.datetime.today()

	history = int(connection.getWithDraw(user_id, today))
	print(history)

	if message.text.isdigit():
		if int(message.text) <= connection.get_id(user_id)[6]:
			if history <= 2000 and int(message.text) <= 2000 and int(message.text) >= 100:
				async with state.proxy() as data:
					data['user_money'] = message.text

				commission = wallet.commission(pid=99, recipient=config.QIWI_NUMBER, amount=int(message.text))
				await message.answer("<b>Комиссия Qiwi</b>\n" 
									f"<b>Карта:</b> <code>2% + 50.00 ₽</code>\n" 
									"<b>└Qiwi Кошелёк:</b> <code>2%</code>")
				await message.answer("<b>На что Вы хотите вывести средства?</b>",
										reply_markup = buttons.withdrawBtns())

			else:
				await message.answer(
					"⚠️ <b>Ошибка:</b>\n\n"

					"Вывод недоступен! Вывод возможен 1 раз в день, от 100 до 2000 рублей."
					)

		else:
			await message.answer("⚠️ Ошибка:\n\n"
								 "У вас недостаточно средств")
	else:
		await message.answer("⚠️ Ошибка:\n\n"
							 "Вводите только цифрами!")


@checkPaymentStatus('WITHDRAW')
async def callback_pay_with_card(c: types.CallbackQuery, state: FSMContext):
	await c.answer()	

	async with state.proxy() as data:
		data['type'] = 'card'

	await WithDraw.step2.set()
	await c.message.answer("Отправьте номер карты, для вывода средств на неё.")


@checkPaymentStatus('WITHDRAW')
async def callback_pay_with_purse(c: types.CallbackQuery, state: FSMContext):
	await c.answer()

	async with state.proxy() as data:
		data['type'] = 'purse'

	await WithDraw.step3.set()
	await c.message.answer("Отправьте мне номер телефона, который привязан к кошельку.")


@checkPaymentStatus('WITHDRAW')
async def process_withdraw_check_card(message: types.Message, state: FSMContext):
	user_id = message.from_user.id	

	if message.text.isdigit():
		async with state.proxy() as data:
			data['recipient'] = message.text
			user_money = data['user_money']

			await message.answer(  "<b>Информация об выводе</b>\n" 
								   f"<b>Списание:</b> <code>{float(int(user_money)+int(user_money)/100*2+50)} ₽</code>\n"
								   f"<b>Зачисление:</b> <code>{float(user_money)}</code>\n"
								   f"<b>Карта:</b> <code>{message.text}</code>",
										reply_markup = buttons.withdrawCheckBtns())

	else:
		await message.answer("⚠️ <b>Ошибка:\n\n"
					 "Вводите только цифрами!")


@checkPaymentStatus('WITHDRAW')
async def process_withdraw_check_purse(message: types.Message, state: FSMContext):
	user_id = message.from_user.id	

	if message.text.isdigit():
		async with state.proxy() as data:
			data['recipient'] = message.text
			user_money = int(data['user_money'])

			await message.answer(  "<b>Информация об выводе</b>\n" 
								   f"<b>К выводу:</b> <code>{user_money + user_money/100*2} ₽</code>\n"
								   f"<b>На кошелёк:</b> <code>{message.text}</code>",
										reply_markup = buttons.withdrawCheckBtns())

	else:
		await message.answer("⚠️ <b>Ошибка:</b>\n\n"
					 "Вводите только цифрами!")		


@checkPaymentStatus('WITHDRAW')
async def callback_confirm(c: types.CallbackQuery, state: FSMContext):
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
				fee_with_commission = int(user_money)+int(user_money)/100*2+50
				connection.addBotPayment(user_id, 'withdraw', fee_with_commission, today)
				connection.updateBalance(user_id, fee_with_commission, '-')
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
				fee_with_commission = int(user_money)+int(user_money)/100*2+50
				connection.addBotPayment(user_id, 'withdraw', fee_with_commission, today)
				connection.updateBalance(user_id, fee_with_commission, '-')
				await c.message.answer("🔔 <b>Уведомление:</b>\n\nВаша заявка принята в обработку!\nОжидайте перевода в течении 24х часов.")

		except Exception as e:
			print(e, type(e))
			await c.message.answer("⚠️ <b>Ошибка:</b>\n\n"
				"Пожалуйста проверьте карта/номер получателя !")

			await state.finish()


# ---------TOP UP-----------
@checkPaymentStatus('REPLENISHMENT')
async def callback_top_up(c: types.CallbackQuery, state: FSMContext):
	await c.answer()
	user_id = c.from_user.id

	await TopUp.step1.set()
	await bot.send_message(c.from_user.id, "На какую сумму Вы хотите пополнить свой баланс?", 
			reply_markup = buttons.back_canc)
	

@checkPaymentStatus('REPLENISHMENT')
async def process_top_up(message: types.Message, state: FSMContext):
	if message.text.isdigit():
		user_id = message.from_user.id
		user_money = int(message.text)
		comment = (f"{user_id}_{random.randint(1000, 9999)}")
		bill = p2p.bill(amount=user_money, lifetime=15, comment=comment)

		await message.answer(f"<b>Информация об оплате</b>\n<b>К зачислени:</b> <code>{float(message.text)} ₽</code>", 
			reply_markup = buttons.showPayment(bill_id = bill.bill_id, url = bill.pay_url, price = user_money))	


@checkPaymentStatus('REPLENISHMENT')
async def check_payment(c: types.CallbackQuery, state: FSMContext):
	try:
		user_id = c.from_user.id
		ids = c.data[6:].split(',')
		bill = ids[0]
		price = ids[1]
		today = datetime.datetime.today()

		if str(p2p.check(bill_id = bill).status) == "PAID":

			connection.updateBalance(user_id, price, '+')
			connection.addPayment(user_id, 'top_up', price, today)

			await c.message.delete()
			await c.answer("🔔 <b>Уведомление:</b>\n\nПоздравляю, оплата прошла успешно!",
								show_alert = True)

			await c.message.answer("Главное меню", reply_markup = buttons.autoMenu(connection.checkUserStatus(user_id)[0]))
			await state.finish()
		
		else:
			await c.answer( "⚠️ <b>Ошибка:</b>"
							"Оплата не найдена! Повторите попытку или обратитесь в поддержку бота",
								show_alert = True)

	except Exception as e:
		print(e)
		await c.answer()
		await bot.send_message(c.from_user.id, "Произошла неизвестная ошибка или утекли срок данных. <b>Пожалуйста повторите попытку!</b>")

	
# -----BUY COUPONS-----
async def callback_buy_cupons(c: types.CallbackQuery, state: FSMContext):
	# user_cpn_list = [25000, 50000, 75000, 100000, 125000, 150000, 175000, 200000, 225000, 250000]

	# user_id = c.from_user.id
	# user_cpns = connection.getUserCpns(user_id)[0]
	# lot = int(user_cpns) // 25000
	# available = user_cpn_list[lot] - int(user_cpns)

	# if lot > 10:
	# 	await c.answer("Вы уже купили все купоны!", show_alert = True)

	await c.answer()
	# await bot.send_photo(
	# 	chat_id = c.from_user.id, 
	# 	photo = file_ids.PHOTO['raccoon'],
	# 	caption = f"<b>Торгуется лот №{lot+1}</b>\n"
	# 			  f"<b>В наличии:</b> <code>{available} шт</code>\n"
	# 			  f"  <b>Цена купона:</b> <code>1шт</code> = <code>{float(lot+1)} ₽</code>\n"
	# 			   "  <b>Доход от прибыли:</b> 0.00008%",
	# 	reply_markup = buttons.getCouponsBtn()
	# 	)


async def callback_buy_cpn(c: types.CallbackQuery, state: FSMContext):
	await c.answer()
	await BuyCoupon.step1.set()
	await c.message.answer("Сколько купонов Вы хотите приобрести?",
			reply_markup = buttons.back_canc)


async def process_buy_coupons(message: types.Message, state: FSMContext):
	user_cpn_list = [25000, 50000, 75000, 100000, 125000, 150000, 175000, 200000, 225000, 250000]

	user_id = message.from_user.id
	user_cpns = connection.getUserCpns(user_id)[0]
	lot = int(user_cpns) // 25000
	available = user_cpn_list[lot] - int(user_cpns)

	if message.text.isdigit():

		if int(message.text) <= 25000:
			if int(message.text) <= available:
				async with state.proxy() as data:
					data['price'] = message.text
					
					await message.answer(
						"<b>Информация об оплате</b>\n"
						f"<b>Покупка купонов:</b> <code>{message.text} шт</code>\n" 
						f"  <b>К оплате:</b> <code>{float(int(message.text)*(lot+1))}₽</code>",
							reply_markup = buttons.getPayCpnsBtn())

			else:
				await message.answer(f"На вашем лоте осталось <code>{available}</code>шт. купонов")
		else:
			await message.answer("Вы можете приобрести в одном лоте максимум <code>25000</code> купонов.")

	else:
		await message.answer("Введите только цифрами!")		



# async def callback_refresh_cpns(c: types.CallbackQuery, state: FSMContext):
# 	await c.answer()


async def callback_pay_cpns(c: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		user_id = c.from_user.id
		price = int(data['price'])
		today = datetime.datetime.today()
		user_balance = int(connection.get_id(user_id)[6])
			

		if user_balance >= price:
			connection.addCoupon(user_id, price)
			connection.addPayment(user_id, 'coupon', price, today, price)
			connection.updateBalance(user_id, price, '-')
			await bot.answer_callback_query(c.id, show_alert = True, text = "🔔 <b>Уведомление:</b>\n\nПоздравляю, оплата прошла успешно!")
			await c.message.delete()
			await bot.send_message(c.from_user.id, "Главное меню", reply_markup = buttons.autoMenu(connection.checkUserStatus(c.from_user.id)[0]))
			await state.finish()
		
		else:
			await bot.answer_callback_query(c.id, show_alert = True, text = "⚠️ Ошибка:\n\n"
																			"У вас недостаточно средств")


# ----STATISTICS----
async def callback_stat(c: types.CallbackQuery, state: FSMContext):
	await c.answer()	
	user_id = c.from_user.id

	today = datetime.datetime.today()
	per_month = datetime.timedelta

	top_up_this_month = connection.selectStatPayments(user_id, 'refill', today-per_month(days=30), today)
	top_up_last_month = connection.selectStatPayments(user_id, 'refill', today-per_month(days=60), today-per_month(days=30))

	withdraw_this_month = connection.selectStatPayments(user_id, 'withdraw', today-per_month(days=30), today)
	withdraw_last_month = connection.selectStatPayments(user_id, 'withdraw', today-per_month(days=60), today-per_month(days=30))

	coupon_count_this_month = connection.selectStatPayments(user_id, 'coupon_count', today-per_month(days=30), today)
	coupon_count_last_month = connection.selectStatPayments(user_id, 'coupon_count', today-per_month(days=60), today-per_month(days=30))

	active_refferals_this_month = connection.selectStatRefferal(user_id, 'active', today-per_month(days=30), today)
	active_refferals_last_month = connection.selectStatRefferal(user_id, 'active', today-per_month(days=60), today-per_month(days=30))

	non_active_refferals_this_month = connection.selectStatRefferal(user_id, user_id, today-per_month(days=30), today)
	non_active_refferals_last_month = connection.selectStatRefferal(user_id, user_id, today-per_month(days=60), today-per_month(days=30))


	await bot.send_message(c.from_user.id, 
					"<b>Информация по статистике</b>\n\n"

					"<b>Пополнили за этот месяц:</b>\n"
					f"└  <code>{float(sum(top_up_this_month))} ₽</code>\n"
					"<b>  За прошлый месяц:</b>\n"
					f"  └  <code>{float(sum(top_up_last_month))} ₽</code>\n\n"

					"<b>Вывели за этот месяц:</b>\n"
					f"└  <code>{float(sum(withdraw_this_month))} ₽</code>\n"
					"  <b>За прошлый месяц:</b>\n"
					f"  └  <code>{float(sum(withdraw_last_month))} ₽</code>\n\n\n"


					"<b>Статистика купонов</b>\n\n"

					"<b>Куплено за этот месяц:</b>\n"
					f"└  <code>{sum(coupon_count_this_month)} шт</code>\n"
					"  <b>За прошлый месяц:</b>\n"
					f"  └  <code>{sum(coupon_count_last_month)} шт</code>\n\n"

					"<b>Выплачено за этот месяц:</b>\n"
					f"└ <code>{float(sum(coupon_count_this_month))} ₽</code>\n"
					"  <b>За прошлый месяц:</b>\n"
					f"  └  <code>{float(sum(coupon_count_last_month))} ₽</code>\n\n\n"


					"<b>Статистика рефералов</b>\n\n"

					"<b>Активных за этот месяц:</b>\n"
					f"└ <code>{active_refferals_this_month[0]} уч</code>\n"
					"  <b>За прошлый месяц:</b>\n"
					f"  └  <code>{active_refferals_last_month[0]} уч</code>\n\n"

					"<b>Ожидающих за этот месяц:</b>\n"
					f"└  <code>{non_active_refferals_this_month[0]} уч</code>\n"
					"  <b>За прошлый месяц:</b>\n"
					f"  └  <code>{non_active_refferals_last_month[0]} уч</code>\n\n"

					"<b>Выплачено за этот месяц:</b>\n"
					f"└  <code>{float(int(active_refferals_this_month[0])*0.5)} ₽</code>\n"
					"  <b>За прошлый месяц:</b>\n"
					f"  └  <code>{float(int(active_refferals_last_month[0])*0.5)} ₽</code>")


def register_bot_payment_handlers(dp: Dispatcher):
	dp.register_callback_query_handler(callback_bank, lambda c: c.data == 'bank',  state = '*')
	
	dp.register_callback_query_handler(callback_withdraw, lambda c: c.data == 'withdraw',  state = '*')
	dp.register_callback_query_handler(callback_withdraw, lambda c: c.data == 'change_withdraw',  state = '*')
	dp.register_callback_query_handler(callback_pay_with_card, lambda c: c.data == 'card',  state = '*')
	dp.register_callback_query_handler(callback_pay_with_purse, lambda c: c.data == 'purse',  state = '*')	
	dp.register_message_handler(process_withdraw, state = WithDraw.step1)
	dp.register_message_handler(process_withdraw_check_card, state = WithDraw.step2)
	dp.register_message_handler(process_withdraw_check_purse, state = WithDraw.step3)
	dp.register_callback_query_handler(callback_confirm, lambda c: c.data == 'confirm',  state = '*')	

	dp.register_callback_query_handler(callback_top_up, lambda c: c.data == 'top_up',  state = '*')
	dp.register_message_handler(process_top_up, state = TopUp.step1)
	dp.register_callback_query_handler(check_payment, lambda c: c.data.startswith('check'),  state = '*')

	dp.register_callback_query_handler(callback_buy_cupons, lambda c: c.data == 'buy_cupons',  state = '*')
	dp.register_callback_query_handler(callback_buy_cpn, lambda c: c.data == 'buy_cpn',  state = '*')
	dp.register_message_handler(process_buy_coupons, state = BuyCoupon.step1)
	dp.register_callback_query_handler(callback_pay_cpns, lambda c: c.data == 'pay_cpn',  state = '*')

	# dp.register_callback_query_handler(callback_refresh_cpns, lambda c: ,  state = '*')

	dp.register_callback_query_handler(callback_stat, lambda c: c.data == 'stat',  state = '*')