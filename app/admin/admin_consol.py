import datetime

from app.admin import admin_buttons, admin_connection
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from .. import config, connection, file_ids, buttons


bot = Bot(token=config.TOKEN, parse_mode = 'html')



class Breaking(StatesGroup):
	step1 = State()


class EditCustomer(StatesGroup):
	step1 = State()
	step2 = State()
	step3 = State()
	step4 = State()


class EditExecutor(StatesGroup):
	step1 = State()
	step2 = State()
	step3 = State()
	step4 = State()
	step5 = State()


class ProcessSetStatus(StatesGroup):
	step1 = State()
	step2 = State()


async def callback_break(c: types.CallbackQuery, state: FSMContext):
	await Breaking.step1.set()
	await bot.send_message(c.from_user.id, "Отправьте мне <b>ID</b> пользователя",
		reply_markup = admin_buttons.admin_canc())


async def callback_choose_category(message: types.Message, state: FSMContext):
	if message.text.isdigit():
		async with state.proxy() as data:
			data['user_id'] = message.text
			await bot.send_message(message.chat.id, "Какой хотите открыть профиль", 
						reply_markup = admin_buttons.chooseCategory())


async def callback_customer(c: types.CallbackQuery, state: FSMContext):
	try:
		async with state.proxy() as data:
			cus_id = data['user_id']
			profil_customer = connection.selectAll(cus_id)
			await bot.delete_message(c.from_user.id, c.message.message_id)
			await bot.send_photo(c.from_user.id, photo = profil_customer[1],
												 caption = f"<b>{profil_customer[0]}</b>\n"
														   f"  <b>Номер:</b> <code>+{profil_customer[2]}</code>", 
																reply_markup = admin_buttons.btnCustomer(cus_id))
	except Exception as e:
		await bot.send_message(c.from_user.id, f"Пользователь с ID: <b>{cus_id}</b> в каталоге заказчика не найден!")


async def callback_executor(c: types.CallbackQuery, state: FSMContext):
	try:
		async with state.proxy() as data:
			ex_id = data['user_id']
			profil_executor = connection.getExecutorProfil(ex_id)

			await bot.delete_message(c.from_user.id, c.message.message_id)
			await bot.send_photo(c.from_user.id, photo = profil_executor[3],
												 caption = f"<b>{profil_executor[1]}</b>\n\n"
														   f"  <b>Дата рождение:</b> <code>{profil_executor[2]}</code>\n"
														   f"  <b>Номер:</b> <code>+{profil_executor[4]}</code>\n\n"
														   f"<b>Навыки:</b>\n<code>{profil_executor[5]}</code>\n\n"
														   f"  <b>Рейтинг:</b> <code>{profil_executor[6]}</code>", 
																reply_markup = admin_buttons.btnExecutor(ex_id))

	except:
		await bot.send_message(c.from_user.id, f"Пользователь с ID: <b>{ex_id}</b> в каталоге исполнителя не найден!")


async def callback_edit_ex(c: types.CallbackQuery, state: FSMContext):
	try:
		async with state.proxy() as data:
			ex_id = data['user_id']
			await EditExecutor.step1.set()
			await bot.delete_message(c.message.chat.id, c.message.message_id)
			await bot.send_message(c.message.chat.id, "Отправьте мне <b>Имя Отчество</b> исполнителя.",
				reply_markup = admin_buttons.admin_canc())
			
	except:
		await Breaking.step1.set()
		await bot.delete_message(c.from_user.id, c.message.message_id)
		await bot.send_message(c.from_user.id, "Отправьте мне <b>ID</b> пользователя",
			reply_markup = admin_buttons.admin_canc())


async def process_create1(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['name'] = message.text

	await EditExecutor.next()
	await bot.send_message(message.chat.id, "Отправьте мне Вашу дату рождение <b>(день.месяц.год)</b>, для определение возраста.")


async def process_create2(message: types.Message, state: FSMContext):
	try:
		date = message.text
		day = date[:2]
		month = date[3:5]
		year = date[6:]
		now = datetime.datetime.now().strftime('%Y')
		age = int(now) - int(year)

		if age > 0 and int(day) <= 31 and int(month) <= 12 and int(year) > 1920 and int(year) < int(now)-7:
			async with state.proxy() as data:
				data['date_of_birth'] = message.text

			await EditExecutor.next()
			await bot.send_photo(message.chat.id, photo = 'AgACAgIAAxkBAAP1YW51oVYVSPmlzCGUUVxGek1i0jAAAimzMRt7rXhLGuB8Y2FU_DQBAAMCAAN5AAMhBA',
				caption = "Отправьте мне Ваше фото или видео резюме, для заполнение профиля.")

		else:
			await message.answer("Введите свою дату рождения!\n(день.месяц.год)")
	except Exception as e:
		print(e)
		await message.answer("Введите свою дату рождения!\n(день.месяц.год)")


async def process_create3(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		if message.photo:
			data['media'] = message.photo[-1].file_id
		elif message.video:
			data['media'] = message.video.file_id
		else:
			await message.answer("Отправьте мне Ваше фото или видео резюме, для заполнение профиля.")
		
	await EditExecutor.next()
	await bot.send_message(message.chat.id, "Отправьте мне номер телефона исполнителя.")
		

async def process_contact_invalid(message: types.Message, state: FSMContext):
	await bot.send_message(message.chat.id, "Отправьте мне номер телефона исполнителя.")


async def process_create4(message: types.Message, state: FSMContext):
	await EditExecutor.step5.set()
	async with state.proxy() as data:
		data['contact'] = message.contact.phone_number
		
		await bot.send_message(message.chat.id, "Отправьте мне свои навыки в таком формате через запятую:\n<i>Коммуникабельность, работа с кассой, отзывчивость, распределения обязанностей.</i>\n\nИли просто пишите 'Не указано'")


async def process_create5(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['skill'] = message.text

		ex_id = data['user_id']
		ex_name = data['name']
		date_of_birth = data['date_of_birth']
		ex_pic = data['media']
		ex_contact = data['contact']
		ex_skill = data['skill']
		ex_rate = 0
		date_registration = datetime.datetime.today().strftime('%d.%m.%Y - %H:%M')
		ex_status = 'free'

		connection.UpdateExecutorProfil(ex_id, ex_name, date_of_birth, ex_pic, ex_contact, ex_skill)
		await bot.send_message(message.chat.id, "Профиль исполнителя успешно отредактирована!")

	await state.finish()
	

async def callback_ban_ex(c: types.CallbackQuery, state: FSMContext):
	try:
		async with state.proxy() as data:
			ex_id = data['user_id']	
			connection.UpdateExStatus(ex_id, 'Banned')
			await bot.send_message(c.from_user.id, f"🔒 Исполнитель с ID:<b>{ex_id}</b> забанен!")

	except:
		await bot.delete_message(c.from_user.id, c.message.message_id)
		await Breaking.step1.set()
		await bot.send_message(c.from_user.id, "Отправьте мне <b>ID</b> пользователя.",
			reply_markup = admin_buttons.admin_canc())


async def callback_unban_ex(c: types.CallbackQuery, state: FSMContext):
	try:	
		async with state.proxy() as data:
			ex_id = data['user_id']	
			connection.UpdateExStatus(ex_id, None)
			await bot.send_message(c.from_user.id, f"🔓 Исполнитель с ID:<b>{ex_id}</b> разбанен!")
	
	except:
		await bot.delete_message(c.from_user.id, c.message.message_id)
		await Breaking.step1.set()
		await bot.send_message(c.from_user.id, "Отправьте мне <b>ID</b> пользователя",
			reply_markup = admin_buttons.admin_canc())


# Edit customer profil
async def callback_edit_cus(c: types.CallbackQuery, state: FSMContext):
	try:
		async with state.proxy() as data:
			cus_id = data['user_id']

			await EditCustomer.step1.set()
			await bot.delete_message(c.from_user.id, c.message.message_id)
			await bot.send_message(c.message.chat.id, "Отправьте мне Имя Отчество заказчика.",
				reply_markup = admin_buttons.admin_canc())
	except:
		await Breaking.step1.set()		
		await bot.delete_message(c.from_user.id, c.message.message_id)
		await bot.send_message(c.from_user.id, "<b>Отправьте мне ID пользователя</b>", 
			reply_markup = admin_buttons.admin_canc())


async def process_reg1(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['name'] = message.text

	await EditCustomer.next()
	await bot.send_message(message.chat.id, "Отправьте мне фото заказчика.")


async def process_img(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['photo'] = message.photo[-1].file_id

	await EditCustomer.next()
	await bot.send_message(message.chat.id, "Отправьте мне номер телефона.")


async def process_contact_and_all_data(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['contact'] = message.contact.phone_number

		cus_id = data['user_id']
		cus_name = data['name']
		cus_pic = data['photo']
		cus_contact = data['contact']
		date_registration = datetime.datetime.today().strftime('%d.%m.%Y - %H:%M')

		connection.UpdateData(cus_id, cus_name, cus_pic, cus_contact, date_registration)
		await bot.send_message(message.chat.id, "Профиль заказчика успешно отредактирован!", reply_markup = buttons.menu_customer)

	await state.finish()


async def cancel_handler(message: types.Message, state: FSMContext):
	await state.finish()
	
	await bot.send_message(message.chat.id, "<b>Админ панель</b>", 
	reply_markup = admin_buttons.adminPanel())


async def process_contact_if_not_img(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['contact'] = message.contact.phone_number

		cus_id = data['user_id']
		cus_name = data['name']
		cus_pic = 'AgACAgIAAxkBAAOvYW5woS9KTofLU3EqNCIoo3jTWx0AAhezMRt7rXhL5FS-aNbKWN8BAAMCAAN5AAMhBA'
		cus_contact = data['contact']
		date_registration = datetime.datetime.today().strftime('%d.%m.%Y - %H:%M')
		
		connection.UpdateData(cus_id, cus_name, cus_pic, cus_contact, date_registration)
		await bot.send_message(message.chat.id, "Профиль заказчика успешно отредактирован!")

	await state.finish()


async def callback_ban_cus(c: types.CallbackQuery, state: FSMContext):
	try:
		async with state.proxy() as data:
			cus_id = data['user_id']
			connection.UpdateCusStatus(cus_id, "Banned")
			await bot.send_message(c.from_user.id, f"Заказчик с ID:<b>{cus_id}</b> забанен!")
	
	except:
		await Breaking.step1.set()		
		await bot.delete_message(c.from_user.id, c.message.message_id)
		await bot.send_message(c.from_user.id, "Отправьте мне <b>ID</b> пользователя.",
			reply_markup = admin_buttons.admin_canc())


async def callback_unban_cus(c: types.CallbackQuery, state: FSMContext):
	try:
		async with state.proxy() as data:
			cus_id = data['user_id']
			connection.UpdateCusStatus(cus_id, None)
			await bot.send_message(c.from_user.id, f"Заказчик с ID:<b>{cus_id}</b> Разбанен!")
	
	except:
		await Breaking.step1.set()		
		await bot.delete_message(c.from_user.id, c.message.message_id)
		await bot.send_message(c.from_user.id, "Отправьте мне <b>ID</b> пользователя.",
			reply_markup = admin_buttons.admin_canc())


async def callback_ban(c: types.CallbackQuery, state: FSMContext):
	await ProcessSetStatus.step1.set()
	await bot.send_message(c.from_user.id, "Отправьте мне <b>ID</b> пользователя")


async def process_ban(message: types.Message, state: FSMContext):
	user_id = message.text

	if user_id.isdigit():
		if not connection.checkReferral(user_id):
			await bot.send_message(message.chat.id, f"Такого пользователя c ID: <b>{user_id}</b> в боте не существует!")

		else:
			connection.UpdateUserStatus("Banned", user_id)
			await bot.send_message(message.chat.id, f"Пользователь с ID: <b>{user_id}</b> забанен!")
			await state.finish()


async def callback_unban(c: types.CallbackQuery, state: FSMContext):
	await ProcessSetStatus.step2.set()
	await bot.send_message(c.from_user.id, "Отправьте мне <b>ID</b> пользователя")


async def process_unban(message: types.Message, state: FSMContext):
	user_id = message.text

	if user_id.isdigit():
		if not connection.checkReferral(user_id):
			await bot.send_message(message.chat.id, f"Такого пользователя c ID: <b>{user_id}</b> в боте не существует!")

		else:
			connection.UpdateUserStatus(None, user_id)
			await bot.send_message(message.chat.id, f"Пользователь с ID: <b>{user_id}</b> разбанен!")
			await state.finish()


async def callback_payment(c: types.CallbackQuery, state: FSMContext):
	if admin_connection.selectFromAdminTable()[1][1] == '✅':
		admin_connection.changeAdminTable('✖️', 'BOT_PAYMENT')
		await bot.edit_message_reply_markup(
			chat_id = c.from_user.id, 
			message_id = c.message.message_id,
			reply_markup = admin_buttons.adminConsol(sensor = admin_connection.selectFromAdminTable()[1][1],  sensor2 = admin_connection.selectFromAdminTable()[0][1],  sensor3= admin_connection.selectFromAdminTable()[2][1],  sensor4 = admin_connection.selectFromAdminTable()[3][1])[0])
		await bot.answer_callback_query(c.id, show_alert = False, text = "Оплата отключено ✖️")


	elif admin_connection.selectFromAdminTable()[1][1] == '✖️':
		admin_connection.changeAdminTable('✅', 'BOT_PAYMENT')
		await bot.edit_message_reply_markup(
			chat_id = c.from_user.id, 
			message_id = c.message.message_id,
			reply_markup = admin_buttons.adminConsol(sensor = admin_connection.selectFromAdminTable()[1][1],  sensor2 = admin_connection.selectFromAdminTable()[0][1],  sensor3= admin_connection.selectFromAdminTable()[2][1],  sensor4 = admin_connection.selectFromAdminTable()[3][1])[0])
		await bot.answer_callback_query(c.id, show_alert = False, text = "Оплата включено ✅")		


async def callback_order_feed(c: types.CallbackQuery, state: FSMContext):
	if admin_connection.selectFromAdminTable()[0][1] == '✅':
		admin_connection.changeAdminTable('✖️', 'ORDER_REGISTRATION')
		await bot.edit_message_reply_markup(
			chat_id = c.from_user.id, 
			message_id = c.message.message_id,
			reply_markup = admin_buttons.adminConsol(sensor = admin_connection.selectFromAdminTable()[1][1],  sensor2 = admin_connection.selectFromAdminTable()[0][1],  sensor3= admin_connection.selectFromAdminTable()[2][1],  sensor4 = admin_connection.selectFromAdminTable()[3][1])[0])
		await bot.answer_callback_query(c.id, show_alert = False, text = "Лента заказов отключено ✖️")


	elif admin_connection.selectFromAdminTable()[0][1] == '✖️':
		admin_connection.changeAdminTable('✅', 'ORDER_REGISTRATION')
		await bot.edit_message_reply_markup(
			chat_id = c.from_user.id, 
			message_id = c.message.message_id,
			reply_markup = admin_buttons.adminConsol(sensor = admin_connection.selectFromAdminTable()[1][1],  sensor2 = admin_connection.selectFromAdminTable()[0][1],  sensor3= admin_connection.selectFromAdminTable()[2][1],  sensor4 = admin_connection.selectFromAdminTable()[3][1])[0])
		await bot.answer_callback_query(c.id, show_alert = False, text = "Лента заказов включено ✅")


async def callback_replenishment(c: types.CallbackQuery, state: FSMContext):
	if admin_connection.selectFromAdminTable()[3][1] == '✅':
		admin_connection.changeAdminTable('✖️', 'REPLENISHMENT')
		await bot.edit_message_reply_markup(
			chat_id = c.from_user.id, 
			message_id = c.message.message_id,
			reply_markup = admin_buttons.adminConsol(sensor = admin_connection.selectFromAdminTable()[1][1],  sensor2 = admin_connection.selectFromAdminTable()[0][1],  sensor3= admin_connection.selectFromAdminTable()[2][1],  sensor4 = admin_connection.selectFromAdminTable()[3][1])[0])
		await bot.answer_callback_query(c.id, show_alert = False, text = "Пополнение отключено ✖️")


	elif admin_connection.selectFromAdminTable()[3][1] == '✖️':
		admin_connection.changeAdminTable('✅', 'REPLENISHMENT')
		await bot.edit_message_reply_markup(
			chat_id = c.from_user.id, 
			message_id = c.message.message_id,
			reply_markup = admin_buttons.adminConsol(sensor = admin_connection.selectFromAdminTable()[1][1],  sensor2 = admin_connection.selectFromAdminTable()[0][1],  sensor3= admin_connection.selectFromAdminTable()[2][1],  sensor4 = admin_connection.selectFromAdminTable()[3][1])[0])
		await bot.answer_callback_query(c.id, show_alert = False, text = "Пополнение включено ✅")		

async def callback_ads(c: types.CallbackQuery, state: FSMContext):
	if admin_connection.selectFromAdminTable()[2][1] == '✅':
		admin_connection.changeAdminTable('✖️', 'ADS')
		await bot.edit_message_reply_markup(
			chat_id = c.from_user.id, 
			message_id = c.message.message_id,
			reply_markup = admin_buttons.adminConsol(sensor = admin_connection.selectFromAdminTable()[1][1],  sensor2 = admin_connection.selectFromAdminTable()[0][1],  sensor3= admin_connection.selectFromAdminTable()[2][1],  sensor4 = admin_connection.selectFromAdminTable()[3][1])[0])
		await bot.answer_callback_query(c.id, show_alert = False, text = "Объявление отключено ✖️")


	elif admin_connection.selectFromAdminTable()[2][1] == '✖️':
		admin_connection.changeAdminTable('✅', 'ADS')
		await bot.edit_message_reply_markup(
			chat_id = c.from_user.id, 
			message_id = c.message.message_id,
			reply_markup = admin_buttons.adminConsol(sensor = admin_connection.selectFromAdminTable()[1][1],  sensor2 = admin_connection.selectFromAdminTable()[0][1],  sensor3= admin_connection.selectFromAdminTable()[2][1],  sensor4 = admin_connection.selectFromAdminTable()[3][1])[0])
		await bot.answer_callback_query(c.id, show_alert = False, text = "Объявление включено ✅")		


def register_admin_consol_handlers(dp: Dispatcher):
	dp.register_message_handler(cancel_handler, text = 'Отменa', state = '*')

	dp.register_callback_query_handler(callback_break, lambda c: c.data == 'breaking',  state = '*')
	dp.register_message_handler(callback_choose_category, state = Breaking.step1)

	dp.register_callback_query_handler(callback_customer, lambda c: c.data == 'customer',  state = '*')
	dp.register_callback_query_handler(callback_edit_cus, lambda c: c.data == 'edit_profil_cus',  state = '*')
	dp.register_callback_query_handler(callback_ban_cus, lambda c: c.data == 'ban_cus',  state = '*')
	dp.register_callback_query_handler(callback_unban_cus, lambda c: c.data == 'unban_cus',  state = '*')
	dp.register_message_handler(process_reg1, state = EditCustomer.step1)
	dp.register_message_handler(process_img, content_types = 'photo', state = EditCustomer.step2)
	dp.register_message_handler(process_contact_and_all_data, content_types = 'contact', state = EditCustomer.step3)
	dp.register_message_handler(process_contact_if_not_img, content_types = 'contact', state = EditCustomer.step4)

	dp.register_callback_query_handler(callback_executor, lambda c: c.data == 'executor',  state = '*')
	dp.register_callback_query_handler(callback_edit_ex, lambda c: c.data == 'edit_profil_ex', state = '*')
	dp.register_callback_query_handler(callback_ban_ex, lambda c: c.data == 'ban_ex', state = '*')
	dp.register_callback_query_handler(callback_unban_ex, lambda c: c.data == 'unban_ex', state = '*')
	dp.register_message_handler(process_create1, state = EditExecutor.step1)
	dp.register_message_handler(process_create2, state = EditExecutor.step2)
	dp.register_message_handler(process_create3, content_types = ['photo', 'video'], state = EditExecutor.step3)
	dp.register_message_handler(process_contact_invalid, lambda message: not message.contact, state = EditExecutor.step4)
	dp.register_message_handler(process_create4, content_types = ['contact'], state = EditExecutor.step4)
	dp.register_message_handler(process_create5, state = EditExecutor.step5)

	dp.register_callback_query_handler(callback_ban, lambda c: c.data == 'ban',  state = '*')
	dp.register_message_handler(process_ban, state = ProcessSetStatus.step1)

	dp.register_callback_query_handler(callback_unban, lambda c: c.data == 'unban',  state = '*')
	dp.register_message_handler(process_unban, state = ProcessSetStatus.step2)

	dp.register_callback_query_handler(callback_payment, lambda c: c.data == 'payment',  state = '*')
	dp.register_callback_query_handler(callback_order_feed, lambda c: c.data == 'ribbons',  state = '*')

	dp.register_callback_query_handler(callback_replenishment, lambda c: c.data == 'replenishment',  state = '*')
	dp.register_callback_query_handler(callback_ads, lambda c: c.data == 'ads',  state = '*')
