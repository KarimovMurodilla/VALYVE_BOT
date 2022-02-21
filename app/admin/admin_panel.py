import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from app.admin import admin_connection, admin_buttons
from app.qiwi import Payment
from .. import file_ids, config

bot = Bot(token=config.TOKEN, parse_mode = 'html')


async def get_stat(message: types.Message, state: FSMContext):
	all_users = admin_connection.allUsers()
	during_the_week = admin_connection.usersByWeek()

	all_orders = admin_connection.allOrders()
	orders_during_the_week = admin_connection.ordersByWeek()

	await bot.send_photo(message.chat.id, photo = file_ids.PHOTO_ADMIN['stat'],
										  caption = f"<b>Пользователей:</b> <code>{all_users} ч.</code>\n"
										  			f"<b>└ За неделю:</b> <code>{during_the_week} ч.</code>\n\n"

										  			f"<b>[P] Купонов:</b> <code>0 шт.\n</code>"
												    f"<b>└ За месяц:</b> <code>0 шт.\n\n</code>"

										  			f"<b>[S] Объявлений:</b> <code>{all_orders} шт.</code>\n"
										  			f"<b>└ За неделю:</b> <code>{orders_during_the_week} шт.</code>", 
										  				reply_markup = admin_buttons.update(title = 'stat'))

async def update_stat(c: types.CallbackQuery, state: FSMContext):
	all_users = admin_connection.allUsers()
	during_the_week = admin_connection.usersByWeek()

	all_orders = admin_connection.allOrders()
	orders_during_the_week = admin_connection.ordersByWeek()

	await c.answer("✅ Обновлено")
	await c.message.edit_media(types.InputMedia(
						media = file_ids.PHOTO_ADMIN['stat'],
						caption =   f"<b>Пользователей:</b> <code>{all_users} ч.</code>\n"
						  			f"<b>└ За неделю:</b> <code>{during_the_week} ч.</code>\n\n"

						  			f"<b>[P] Купонов:</b> <code>0 шт.\n</code>"
								    f"<b>└ За месяц:</b> <code>0 шт.\n\n</code>"

						  			f"<b>[S] Объявлений:</b> <code>{all_orders} шт.</code>\n"
						  			f"<b>└ За неделю:</b> <code>{orders_during_the_week} шт.</code>"), 
						  				reply_markup = admin_buttons.update(title = 'stat'))


async def show_bank(message: types.Message, state: FSMContext):
	today = datetime.datetime.today()
	per_month = datetime.timedelta

	income_month = sum([int(i[0]) for i in admin_connection.getStatPayment('to_order', today-per_month(days=30), today)])
	income_week = sum([int(i[0]) for i in admin_connection.getStatPayment('to_order', today-per_month(days=7), today)])

	costs_month = sum([int(i[0]) for i in admin_connection.getStatPayment('bot_payment', today-per_month(days=30), today)])
	costs_week = sum([int(i[0]) for i in admin_connection.getStatPayment('bot_payment', today-per_month(days=7), today)])

	profit_month = sum([int(i[0]) for i in admin_connection.getStatPayment('profit', today-per_month(days=30), today)])
	profit_week = sum([int(i[0]) for i in admin_connection.getStatPayment('profit', today-per_month(days=7), today)])

	bank = sum([int(i[0]) for i in admin_connection.getStatPayment('bank', None, None)])

	top_up_month = sum([int(i[0]) for i in admin_connection.getStatPayment('top_up', today-per_month(days=30), today)])
	top_up_week = sum([int(i[0]) for i in admin_connection.getStatPayment('top_up', today-per_month(days=7), today)])

	withdraw_month = sum([int(i[0]) for i in admin_connection.getStatPayment('withdraw', today-per_month(days=30), today)])
	withdraw_week = sum([int(i[0]) for i in admin_connection.getStatPayment('withdraw', today-per_month(days=7), today)])

	await bot.send_photo(message.chat.id, photo = file_ids.PHOTO['bank'],
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
														f"<b>К выводу:</b> <code>{float(bank)} ₽</code>",
															reply_markup = admin_buttons.bankProject())


async def get_consol(message: types.Message, state: FSMContext):
	await bot.send_photo(message.chat.id, 
			photo = file_ids.PHOTO_ADMIN['console'],
				reply_markup = admin_buttons.adminConsol(
					sensor = admin_connection.selectFromAdminTable()[1][1],  
						sensor2 = admin_connection.selectFromAdminTable()[0][1],  
							sensor3= admin_connection.selectFromAdminTable()[2][1],  
								sensor4 = admin_connection.selectFromAdminTable()[3][1])[0])


async def theModer(message: types.Message, state: FSMContext):
	ads = [a[0] for a in admin_connection.getViews('ads') if a[0] != 0]
	profils = [p[0] for p in admin_connection.getViews('profils') if p[0] != 0]
	complaints = [c[0] for c in admin_connection.getViews('complaints') if c[0] != 0]

	await bot.send_photo(message.chat.id,  
		photo = file_ids.PHOTO_ADMIN['moderation'],
		caption =   "За сегодня просмотрено\n" 
					f"    Объявлений: <code>{len(ads)} шт</code>\n\n"
					"За сегодня просмотрено\n"
					f"    Профилей: <code>{len(profils)} шт</code>\n\n"
					"За сегодня просмотрено\n"
					f"    Жалоб: <code>{len(complaints)} шт</code>",
		reply_markup = admin_buttons.adminModeration())	


def register_admin_handlers(dp: Dispatcher):
	dp.register_message_handler(get_stat, chat_id = config.ADMINS, text = "Статистика", state = '*')
	dp.register_callback_query_handler(update_stat, chat_id = config.ADMINS, text = 'update_stat', state = '*')
	dp.register_message_handler(show_bank, chat_id = config.ADMINS, text = "Банк", state = '*')
	dp.register_message_handler(get_consol, chat_id = config.ADMINS, text = "Консоль", state = '*')
	dp.register_message_handler(theModer, chat_id = config.ADMINS, text = "Модерация", state = '*')