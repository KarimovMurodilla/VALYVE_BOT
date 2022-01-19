import asyncio
import random
import datetime
import pyqiwi
from pyqiwip2p import QiwiP2P


from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from app.admin.admin_connection import selectStatuses
from .. import buttons, config, connection, file_ids


class TopUp(StatesGroup):
	step1 = State()


class WithDraw(StatesGroup):
	step1 = State()
	step2 = State()


class BuyCoupon(StatesGroup):
	step1 = State()


bot = Bot(token=config.TOKEN, parse_mode = 'html')
p2p = QiwiP2P(auth_key = config.QIWI_P2P_TOKEN)
wallet = pyqiwi.Wallet(token = config.QIWI_TOKEN, number = config.QIWI_NUMBER)


def checkPaymentStatus(name):
	def decorator(func):
		async def wrapper(c: types.CallbackQuery, state: FSMContext):
			if selectStatuses(name) == '🔴':
				await c.answer("Извините! Данная функция временно закрыта!", show_alert = True)
			else:
				return await func(c, state)
		return wrapper
	return decorator




async def callback_bank(c: types.CallbackQuery, state: FSMContext):
	user_id = c.from_user.id
	await c.answer()

	try:
		ref_actives = connection.getRefActives(user_id)
		for i in ref_actives[0]:
			if connection.selectWherePublished(i):
				connection.addActiveReferral(user_id)
				connection.setActiveUser(i)
				
	except Exception as e:
		print(e)

	referral = connection.checkReferral(user_id)
	coupons = connection.getUserCpns(user_id)[0]
	await bot.send_photo(
		chat_id = c.from_user.id, 
		photo = file_ids.PHOTO['bank'],
		caption = f"<b>Баланс:</b> <code>{float(referral[6])} ₽</code>\n\n"
				  f"<b>Купон VALYVE:</b> <code>{coupons} шт</code>\n\n"
				  f"<b>Реферальная система</b>\n"
				  f"├ <b>Активных:</b> <code>{referral[5]} уч</code>\n"
				  f"└ <b>Ожидание:</b> <code>{referral[4]} уч</code>\n\n"
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
		await bot.send_message(c.from_user.id, "На  какую сумму Вы хотите сделать вывод", 
			reply_markup = buttons.back_canc)

	else:
		await c.answer(show_alert = True, text = "⚠️ Ошибка:\n\n"
						"У вас недостаточно средств")


@checkPaymentStatus('WITHDRAW')
async def process_withdraw(message: types.Message, state: FSMContext):
	user_id = message.from_user.id

	if message.text.isdigit():
		if int(message.text) <= connection.get_id(user_id)[6]:
			async with state.proxy() as data:
				data['user_money'] = message.text

			commission = wallet.commission(pid=99, recipient=config.QIWI_NUMBER, amount=int(message.text))
			await bot.send_message(message.chat.id, "На что Вы хотите вывести средства?\n\n"

													"Комиссия Qiwi\n" 
													f"Карта: 2% + {float(commission.qw_commission.amount)} ₽\n" 
													"└Qiwi Кошелёк: 2%",
														reply_markup = buttons.withdrawBtns())
		else:
			await message.answer("⚠️ Ошибка:\n\n"
								 "У вас недостаточно средств")
	else:
		await message.answer("⚠️ Ошибка:\n\n"
							 "Вводите только цифрами!")


@checkPaymentStatus('WITHDRAW')
async def callback_pay_with_card(c: types.CallbackQuery, state: FSMContext):
	await c.answer()	

	await WithDraw.step2.set()
	await c.message.answer("Отправьте мне номер карты для вывода средства на ней.")


@checkPaymentStatus('WITHDRAW')
async def callback_pay_with_purse(c: types.CallbackQuery, state: FSMContext):
	await c.answer()
	await WithDraw.step2.set()
	await c.message.answer("Отправьте мне номер телефона, который привязан к кошельку.")


@checkPaymentStatus('WITHDRAW')
async def process_withdraw_check(message: types.Message, state: FSMContext):
	user_id = message.from_user.id	

	async with state.proxy() as data:
		data['recipient'] = message.text
		user_money = data['user_money']

		await message.answer("Информация об выводе\n" 
							   f"К выводу: {float(user_money)} ₽\n"
							   f"На карту: {message.text}",
							   		reply_markup = buttons.withdrawCheckBtns())


@checkPaymentStatus('WITHDRAW')
async def callback_confirm(c: types.CallbackQuery, state: FSMContext):
	try:
		async with state.proxy() as data:
			user_id = c.from_user.id
			recipient = data['recipient']
			user_money = data['user_money']
			comment = (f"{user_id}_{random.randint(1000, 9999)}")

			today = datetime.datetime.today()

			payment = wallet.send(pid=99, recipient=recipient, amount=user_money, comment=comment)
			connection.addBotPayment(user_id, 'withdraw', user_money, today)
			await c.message.answer("🔔 Уведомление:\n\nВаша заявка принята в обработку!\nОжидайте перевода в течении 24х часов.")

	except Exception as e:
		print(e, type(e))
		await c.message.answer("⚠️ Ошибка:\n\n"
			"Пожалуйста проверьте карта/номер получателя !")


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

		await message.answer(f"Информация об оплате\nК зачислению: {float(message.text)} ₽", 
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
			connection.addPayment(user_id, 'refill', price, today)

			await c.message.delete()
			await c.answer(show_alert = True, text = "🔔 Уведомление:\n\nПоздравляю, оплата прошла успешно!")

			await c.message.answer("Главное меню", reply_markup = buttons.autoMenu(connection.checkUserStatus(user_id)[0]))
			await state.finish()
		
		else:
			await bot.answer_callback_query(c.id, show_alert = True, text = "❗️Вы не оплатили счет!")

	except Exception as e:
		print(e)
		await c.answer()
		await bot.send_message(c.from_user.id, "Произошла неизвестная ошибка или утекли срок данных. Пожалуйста повторите попытку!")

	
# -----BUY COUPONS-----
async def callback_buy_cupons(c: types.CallbackQuery, state: FSMContext):
	await c.answer()
	await bot.send_photo(
		chat_id = c.from_user.id, 
		photo = file_ids.PHOTO['agreement'],
		caption = "Торгуется лот №1\n"
				  "В наличии: 25.000 шт\n"
				  "  Цена купона: 1шт = 1.00 ₽\n"
				  "  Доход от прибыли: 0.00008%",
		reply_markup = buttons.getCouponsBtn()
		)


async def callback_buy_cpn(c: types.CallbackQuery, state: FSMContext):
	await c.answer()
	await BuyCoupon.step1.set()
	await c.message.answer("Сколько купонов Вы хотите приобрести?",
			reply_markup = buttons.back_canc)


async def process_buy_coupons(message: types.Message, state: FSMContext):
	if message.text.isdigit():
		async with state.proxy() as data:
			data['price'] = message.text
			
			await message.answer(
				"Информация об оплате\n"
				f"Покупка купонов: <code>{message.text} шт</code>\n" 
				f"  К оплате: <code>{float(message.text)}₽</code>",
					reply_markup = buttons.getPayCpnsBtn())

	else:
		await message.answer("Введите только цифрами!")		



async def callback_refresh_cpns(c: types.CallbackQuery, state: FSMContext):
	await c.answer()


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
			await bot.answer_callback_query(c.id, show_alert = True, text = "🔔 Уведомление:\n\nПоздравляю, оплата прошла успешно!")
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


	await bot.send_message(c.from_user.id, "<b>Информация по статистике</b>\n\n"

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
	dp.register_message_handler(process_withdraw_check, state = WithDraw.step2)
	dp.register_callback_query_handler(callback_confirm, lambda c: c.data == 'confirm',  state = '*')	

	dp.register_callback_query_handler(callback_top_up, lambda c: c.data == 'top_up',  state = '*')
	dp.register_message_handler(process_top_up, state = TopUp.step1)
	dp.register_callback_query_handler(check_payment, lambda c: c.data.startswith('check'),  state = '*')

	dp.register_callback_query_handler(callback_buy_cupons, lambda c: c.data == 'buy_cupons',  state = '*')
	dp.register_callback_query_handler(callback_buy_cpn, lambda c: c.data == 'buy_cpn',  state = '*')
	dp.register_message_handler(process_buy_coupons, state = BuyCoupon.step1)
	dp.register_callback_query_handler(callback_pay_cpns, lambda c: c.data == 'pay_cpn',  state = '*')

	dp.register_callback_query_handler(callback_refresh_cpns, lambda c: c.data == 'refresh_cpn',  state = '*')

	dp.register_callback_query_handler(callback_stat, lambda c: c.data == 'stat',  state = '*')