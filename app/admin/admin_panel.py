from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from app.admin import admin_connection, admin_buttons
from .. import file_ids, config

bot = Bot(token=config.TOKEN, parse_mode = 'html')


async def get_stat(message: types.Message, state: FSMContext):
	all_users = admin_connection.allUsers()
	during_the_week = admin_connection.orderByWeek()

	all_orders = admin_connection.allOrders()
	orders_during_the_week = admin_connection.ordersByWeek()

	await bot.send_photo(message.chat.id, photo = file_ids.PHOTO['stat'],
										  caption = f"<b>Пользователей:</b> <code>{all_users} ч.</code>\n"
										  			f"<b>└ За неделю:</b> <code>{during_the_week} ч.</code>\n\n"

										  			f"<b>[P] Купонов:</b> <code>0 шт.\n</code>"
												    f"<b>└ За месяц:</b> <code>0 шт.\n\n</code>"

										  			f"<b>[S] Объявлений:</b> <code>{all_orders} шт.</code>\n"
										  			f"<b>└ За неделю:</b> <code>{orders_during_the_week} шт.</code>")


async def show_bank(message: types.Message, state: FSMContext):
	await bot.send_message(message.chat.id, f"<b>Выручка за месяц</b>\n"
											f"└ <code>0.0руб.</code>\n"
											f"  <b>За неделю</b>\n"
											"  └ <code>0.0 руб.</code>\n\n"

											f"<b>Сотрудник в запасе</b>\n"
											f"<b>Выплата за месяц</b>\n"
											f"└ <code>0.0 руб.</code>\n"
											f"  <b>За неделю</b>\n"
											f"  └ <code>0.0 руб.</code>\n\n"

											f"<b>Реферальная система</b>\n"
											f"<b>Выплата за месяц</b>\n"
											f"└ <code>0.0 руб.</code>\n"
											f"   <b>За неделю</b>\n"
											f"   └ <code>0.0 руб.</code>\n\n"

											f"<b>Купоны VALYVE</b>\n"
											f"<b>Выплата за месяц</b>\n"
											f"└  <code>0.0 руб.</code>\n"
											f"  <b>За неделю</b>\n"
											f"  └ <code>0.0 руб.</code>\n\n"

											f"<b>Выплаты сотрудникам</b>\n"
											f"<b>Выплата за месяц</b>\n"
											f"└ <code>0.0 руб.</code>\n"
											f"  <b>За неделю</b>\n"
											f"  └ <code>0.0 руб.</code>\n\n"

											f"<b>Прибыль за месяц</b>\n"
											f"└ <code>0.0 руб.</code>\n"
											f"  <b>За неделю</b>\n"
											f"  └ <code>0.0 руб.</code>\n\n"

											f"<b>Баланс проекта:</b> <code>0.0 руб.</code>\n"
											f"<b>В заморозке:</b> <code>0.0 руб.</code>",
											reply_markup = admin_buttons.bankProject())


async def get_consol(message: types.Message, state: FSMContext):
	await bot.send_message(message.chat.id, "<b>Админ консоль:</b>", 
		reply_markup = admin_buttons.adminConsol(sensor = admin_connection.selectFromAdminTable()[1][1],  sensor2= admin_connection.selectFromAdminTable()[0][1])[0])



async def theModer(message: types.Message, state: FSMContext):
	await bot.send_message(message.chat.id, "Модерация:",
		reply_markup = admin_buttons.adminModeration())




def register_admin_handlers(dp: Dispatcher):
	dp.register_message_handler(get_stat, chat_id = config.ADMINS, text = "📊 Статистика", state = '*')
	dp.register_message_handler(show_bank, chat_id = config.ADMINS, text = "🏦 Банк", state = '*')
	dp.register_message_handler(get_consol, chat_id = config.ADMINS, text = "🎛 Консоль", state = '*')
	dp.register_message_handler(theModer, chat_id = config.ADMINS, text = "👨🏻‍💻 Модерация", state = '*')
