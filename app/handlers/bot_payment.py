import asyncio
import random
import datetime
import pyqiwi
from pyqiwip2p import QiwiP2P


from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from app.admin.admin_connection import selectFromAdminTable
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


def checkPaymentStatus(func):
	async def wrapper(c: types.CallbackQuery, state: FSMContext):
		if selectFromAdminTable()[1][1] == '✖️':
			await c.answer("Извините! Данная функция временно закрыта!")
		else:
			return await func(c, state)
	return wrapper



async def callback_bank(c: types.CallbackQuery, state: FSMContext):
	user_id = c.from_user.id
	await c.answer()

	try:
		ref_actives = connection.getRefActives(user_id)
		for i in ref_actives[0]:
			if connection.checkRegStatus(i) or connection.checkExecutor(i):
				connection.addActiveReferral(user_id)
				connection.setActiveUser(i)
	except Exception as e:
		print(e)

	referral = connection.checkReferral(user_id)
	await bot.send_photo(
		chat_id = c.from_user.id, 
		photo = file_ids.PHOTO['bank'],
		caption = f"<b>Баланс:</b> <code>{float(referral[6])} ₽</code>\n\n"
				  f"<b>Купон VALYVE:</b> <code>0 шт</code>\n\n"
				  f"<b>Реферальная система</b>\n"
				  f"├ <b>Активных:</b> <code>{referral[5]} уч</code>\n"
				  f"└ <b>Ожидание:</b> <code>{referral[4]} уч</code>\n\n"
				  f"🗣 <b>Пригласительная ссылка</b>\n"
				  f"└ <a href='https://t.me/ValyveExchange_bot?start={user_id}'>Зажми чтоб скопировать</a>",
					reply_markup = buttons.referral_settings)


# Withdraw
@checkPaymentStatus
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



async def callback_pay_with_card(c: types.CallbackQuery, state: FSMContext):
	await c.answer()	

	await WithDraw.step2.set()
	await c.message.answer("Отправьте мне номер карты для вывода средства на ней.")


async def callback_pay_with_purse(c: types.CallbackQuery, state: FSMContext):
	await c.answer()
	await WithDraw.step2.set()
	await c.message.answer("Отправьте мне номер телефона, который привязан к кошельку.")


async def process_withdraw_check(message: types.Message, state: FSMContext):
	user_id = message.from_user.id	

	async with state.proxy() as data:
		data['recipient'] = message.text
		user_money = data['user_money']

		await message.answer("Информация об выводе\n" 
							   f"К выводу: {float(user_money)} ₽\n"
							   f"На карту: {message.text}",
							   		reply_markup = buttons.withdrawCheckBtns())


async def callback_confirm(c: types.CallbackQuery, state: FSMContext):
	try:
		async with state.proxy() as data:
			user_id = c.from_user.id
			recipient = data['recipient']
			user_money = data['user_money']
			comment = (f"{user_id}_{random.randint(1000, 9999)}")

			today = datetime.datetime.today()
			dmy = datetime.datetime.today().strftime('%d.%m.%Y')

			payment = wallet.send(pid=99, recipient=recipient, amount=user_money, comment=comment)
			connection.addBotPayment(user_id, 'withdraw', user_money, dmy)
			await c.message.answer("🔔 Уведомление:\n\nВаша заявка принята в обработку!\nОжидайте перевода в течении 24х часов.")

	except Exception as e:
		print(e, type(e))
		await c.message.answer("⚠️ Ошибка:\n\n"
			"Пожалуйста проверьте карта/номер получателя !")


# --------------------

async def callback_top_up(c: types.CallbackQuery, state: FSMContext):
	await c.answer()
	user_id = c.from_user.id

	await TopUp.step1.set()
	await bot.send_message(c.from_user.id, "На какую сумму Вы хотите пополнить свой баланс?", 
			reply_markup = buttons.back_canc)
	

async def process_top_up(message: types.Message, state: FSMContext):
	if message.text.isdigit():
		user_id = message.from_user.id
		user_money = int(message.text)
		comment = (f"{user_id}_{random.randint(1000, 9999)}")
		bill = p2p.bill(amount=user_money, lifetime=15, comment=comment)

		await message.answer(f"Информация об оплате\nК зачислению: {float(message.text)} ₽", 
			reply_markup = buttons.showPayment(bill_id = bill.bill_id, url = bill.pay_url, price = user_money))	


async def check_payment(c: types.CallbackQuery, state: FSMContext):
	try:
		user_id = c.from_user.id
		ids = c.data[6:].split(',')
		bill = ids[0]
		price = ids[1]
		today = datetime.datetime.today()
		dmy = datetime.datetime.today().strftime('%d.%m.%Y')
			

		if str(p2p.check(bill_id = bill).status) == "PAID":

			connection.addBalance(user_id, price)
			connection.addPayment(user_id, 'balance', price, dmy)

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

	
# BUY COUPONS
async def callback_buy_cupons(c: types.CallbackQuery, state: FSMContext):
	await c.answer()
	await bot.send_message(c.from_user.id, "<b>Информация о купонах</b>\n\n"
					"<b>Цена 1 купона</b> = <code>1 ₽</code>\n"
					"  <b>Прибыль купона</b> = <code>0.00008%</code>\n"
					"  <b>В наличии:</b> <code>250 000 шт</code>\n")
	

async def callback_stat(c: types.CallbackQuery, state: FSMContext):
	user_id = c.from_user.id
	await c.answer()
	await bot.send_message(c.from_user.id, "<b>Информация по статистике</b>\n\n"

					"<b>Пополнили за этот месяц:</b>\n"
					"└  <code>0.0 ₽</code>\n"
					"<b>  За прошлый месяц:</b>\n"
					"  └  <code>0.0 ₽</code>\n\n"

					"<b>Вывели за этот месяц:</b>\n"
					"└  <code>0.0 ₽</code>\n"
					"  <b>За прошлый месяц:</b>\n"
					"  └  <code>0.0 ₽</code>\n\n\n"


					"<b>Статистика купонов</b>\n\n"

					"<b>Куплено за этот месяц:</b>\n"
					"└  <code>0 шт</code>\n"
					"  <b>За прошлый месяц:</b>\n"
					"  └  <code>0 шт</code>\n\n"

					"<b>Выплачено за этот месяц:</b>\n"
					"└ <code>0.000000000 ₽</code>\n"
					"  <b>За прошлый месяц:</b>\n"
					"  └  <code>0.000000000 ₽</code>\n\n\n"


					"<b>Статистика рефералов</b>\n\n"

					"<b>Активных за этот месяц:</b>\n"
					"└ <code>0 уч</code>\n"
					"  <b>За прошлый месяц:</b>\n"
					"  └  <code>0 уч</code>\n\n"

					"<b>Ожидающих за этот месяц:</b>\n"
					"└  <code>0 уч</code>\n"
					"  <b>За прошлый месяц:</b>\n"
					"  └  <code>0 уч</code>\n\n"

					"<b>Выплачено за этот месяц:</b>\n"
					"└  <code>0.0 ₽</code>\n"
					"  <b>За прошлый месяц:</b>\n"
					"  └  <code>0.0 ₽</code>")


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
	dp.register_callback_query_handler(callback_stat, lambda c: c.data == 'stat',  state = '*')