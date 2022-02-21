import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from .. import connection, file_ids, buttons, config, getLocationInfo
from app.admin import admin_connection


bot = Bot(token=config.TOKEN, parse_mode = 'html')


class RegExecutor(StatesGroup):
	step1 = State()
	step2 = State()
	step3 = State()
	step4 = State()
	step5 = State()
	step6 = State()


async def process_create_executor_profil(c: types.CallbackQuery, state: FSMContext):
		await RegExecutor.step1.set()
		await bot.delete_message(c.message.chat.id, c.message.message_id)
		await bot.send_message(c.message.chat.id, "Отправьте мне Ваше Имя Отчество, для идентификация Вас.",
			reply_markup = buttons.back_canc)


async def process_create1(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['name'] = message.text

	await RegExecutor.next()
	await bot.send_message(message.chat.id, "Отправьте мне Вашу дату рождение (день.месяц.год), для определение возраста.")


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

			await RegExecutor.next()
			await bot.send_photo(message.chat.id, photo = 'AgACAgIAAxkBAAP1YW51oVYVSPmlzCGUUVxGek1i0jAAAimzMRt7rXhLGuB8Y2FU_DQBAAMCAAN5AAMhBA',
				caption = "Отправьте мне Ваше фото или видео резюме, для заполнение профиля.")

		else:
			await message.answer("Введите свою дату рождения!\n<b>(день.месяц.год)</b>")
	except Exception as e:
		print(e)
		await message.answer("Введите свою дату рождения!\n<b>(день.месяц.год)</b>")



async def process_create3(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		if message.photo:
			data['media'] = message.photo[-1].file_id
		elif message.video:
			data['media'] = message.video.file_id
		else:
			await message.answer("Отправьте мне Ваше фото или видео резюме, для заполнение профиля.")

		

	await RegExecutor.next()
	msg = await bot.send_message(message.chat.id, "Отправьте мне Ваш номер телефона, для связи по работе.",
		reply_markup = buttons.contact_ex)
	
	async with state.proxy() as data:
		data['msg_id'] = msg.message_id


async def process_contact_invalid(message: types.Message, state: FSMContext):
	msg = await bot.send_message(message.chat.id, "Отправьте мне Ваш номер телефона, для связи по работе.",
		reply_markup = buttons.contact_ex)
	
	async with state.proxy() as data:
		data['msg_id'] = msg.message_id


async def process_create4(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['contact'] = message.contact.phone_number
		msg_id = data['msg_id']

	await RegExecutor.next()
	await bot.delete_message(message.chat.id, msg_id)
	await bot.send_message(message.chat.id, "Хотите ли Вы указать свои навыки?",
		reply_markup = buttons.yes_no)


async def process_create5(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['skill'] = message.text

		ex_id = message.from_user.id
		ex_name = data['name']
		date_of_birth = data['date_of_birth']
		ex_pic = data['media']
		ex_contact = data['contact']
		ex_skill = data['skill']
		ex_rate = 0
		date_registration = datetime.datetime.today().strftime('%d.%m.%Y - %H:%M')
		ex_status = 'free'
		
		if not connection.getExecutorProfil(ex_id):
			connection.regExecutor(ex_id, ex_name, date_of_birth, ex_pic, ex_contact, ex_skill, ex_rate, date_registration, ex_status)
			await bot.send_message(message.chat.id, "<b>🔔 Уведомление:</b>\n\n"
								                    "Профиль исполнителя успешно создан!", reply_markup = buttons.menu_executor)

		else:
			# connection.UpdateExecutorProfil(ex_id, ex_name, date_of_birth, ex_pic, ex_contact, ex_skill)
			await bot.send_message(message.chat.id, "<b>🔔 Уведомление:</b>\n\n" 
													"Ваш новый профиль отправлен на модерацию. Ожидайте ответа в течении 24х часов!", reply_markup = buttons.menu_executor)
			status = connection.checkUserStatus(message.from_user.id)[0]
			admin_connection.addRequestProfil(ex_id, status, ex_name, ex_pic, ex_contact, date_of_birth, ex_skill)

	await state.finish()



async def process_yes_skill(c: types.CallbackQuery, state: FSMContext):
	await RegExecutor.step5.set()
	await bot.delete_message(c.from_user.id, c.message.message_id)		
	await bot.send_message(c.from_user.id, "Отправьте мне свои навыки в таком формате через запятую:\nКоммуникабельность, работа с кассой, отзывчивость, распределения обязанностей.")


async def process_no_skill(c: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		data['skill'] = "Не указано"

		ex_id = c.from_user.id
		ex_name = data['name']
		date_of_birth = data['date_of_birth']
		ex_pic = data['media']
		ex_contact = data['contact']
		ex_skill = data['skill']
		ex_rate = 0
		date_registration = datetime.datetime.today().strftime('%d.%m.%Y - %H:%M')
		ex_status = 'free'


		if not connection.getExecutorProfil(ex_id):
			connection.regExecutor(ex_id, ex_name, date_of_birth, ex_pic, ex_contact, ex_skill, ex_rate, date_registration, ex_status)
			await bot.delete_message(c.message.chat.id, c.message.message_id)	
			await bot.send_message(c.message.chat.id, "<b>🔔 Уведомление:</b>\n\n"
								                      "Профиль исполнителя успешно создан!", reply_markup = buttons.menu_executor)

		else:
			# connection.UpdateExecutorProfil(ex_id, ex_name, date_of_birth, ex_pic, ex_contact, ex_skill)
			await bot.delete_message(c.message.chat.id, c.message.message_id)	
			await bot.send_message(c.from_user.id, "<b>🔔 Уведомление:</b>\n\n" 
													"Ваш новый профиль отправлен на модерацию. Ожидайте ответа в течении 24х часов!", reply_markup = buttons.menu_executor)
			status = connection.checkUserStatus(c.from_user.id)[0]
			admin_connection.addRequestProfil(ex_id, status, ex_name, ex_pic, ex_contact, date_of_birth, ex_skill)

	await state.finish()	
	

async def get_geo(message: types.Message, state: FSMContext):
	ex_id = message.from_user.id
	connection.checkDeletionDate()
	

	if connection.checkReferral(ex_id)[3] == 'Banned':
		await bot.send_message(message.chat.id, "Ваш профиль забанен!")
	
	elif not connection.checkExecutor(ex_id):
		await bot.send_message(message.chat.id, "Для использование этого функционала, необходимо создать профиль исполнителя.", reply_markup = buttons.create_executor_profil)
	
	elif connection.getExecutorProfil(ex_id)[8] == 'Banned':
		await bot.send_message(message.chat.id, "Ваш профиль исполнителя забанен!")

	elif connection.checkExecutor(ex_id)[8] == 'busy':
		await bot.send_message(message.chat.id, text = "⚠️ <b>Ошибка:</b>\n\n"
													   "Вы не можете просматривать новые заказы, пока не закончите текущий заказ")
				
	else:
		try:
			ex_id = message.from_user.id	
			async with state.proxy() as data:
				connection.nullPagination(ex_id)
				pag = connection.selectPag(ex_id)
				lat = data['lat']
				lon = data['long']
				orders = connection.selectAllOrders(lat, lon)[pag]

			await bot.send_message(message.chat.id, 
				f"<b>Заказчик:</b> <code>{orders[1]}</code>\n"
				f"<b>Расстояние:</b> <code>{getLocationInfo.calculate_distance(lat, lon, orders[8], orders[9])}</code> от Вас\n\n"
				f"<b>Должность:</b> <code>{orders[6]}</code>\n"
				f"{connection.checkOrderType(orders[-2], orders)}"
				# f"<b>Время работы:</b> <code>{orders[4]}</code>\n"
				f"<b>График:</b> <code>{orders[3]}</code>\n"
				f"<b>Смена:</b> <code>{orders[5]}</code>\n\n"

				f"<b>Требование:</b>\n<code>{orders[14]}</code>\n\n"
				f"<b>Обязанности:</b>\n<code>{orders[15]}</code>\n\n"

				f"{orders[7]}",
					reply_markup = buttons.globalOrders(orders[0], orders[12]))
			await bot.send_message(message.chat.id, 'Вот подборочка объявлений для Вас! 🥺', reply_markup = buttons.back_to_menu)


		except Exception as e:
			if type(e) == KeyError:				
				await bot.send_message(message.chat.id, "Отправьте мне свою геолокацию, чтоб я мог показать объявления в Вашем регионе.", reply_markup = buttons.send_geo)
				await RegExecutor.step6.set()
			
			else:
				print(type(e), e)
				await bot.send_message(message.chat.id, "Заказов не найдено!", reply_markup = buttons.back_to_menu)


async def search_orders(message: types.Message, state: FSMContext):
	ex_id = message.from_user.id	
	async with state.proxy() as data:
		data['lat'] = message.location.latitude
		data['long'] = message.location.longitude

	if connection.checkExecutor(ex_id)[8] == 'busy':
		await bot.send_message(message.chat.id, text =  "⚠️ <b>Ошибка:</b>\n\n"
														"Вы не можете просматривать новые заказы, пока не закончите текущий заказ",
				reply_markup = buttons.menu_executor)
				
	else:
		if not connection.selectAllOrders(data['lat'], data['long']):
			await bot.send_message(message.chat.id, "Заказов не найдено!", reply_markup = buttons.back_to_menu)


		else:
			try:
				connection.nullPagination(ex_id)
				pag = connection.selectPag(ex_id)
				lat = data['lat']
				lon = data['long']
				orders = connection.selectAllOrders(lat, lon)[pag]

				await bot.send_message(message.chat.id, 
					f"<b>Заказчик:</b> <code>{orders[1]}</code>\n"
					f"<b>Расстояние:</b> <code>{getLocationInfo.calculate_distance(lat, lon, orders[8], orders[9])}</code> от Вас\n\n"
					f"<b>Должность:</b> <code>{orders[6]}</code>\n"
					f"{connection.checkOrderType(orders[-2], orders)}"
					# f"<b>Время работы:</b> <code>{orders[4]}</code>\n"
					f"<b>График:</b> <code>{orders[3]}</code>\n"
					f"<b>Смена:</b> <code>{orders[5]}</code>\n\n"

					f"<b>Требование:</b>\n<code>{orders[14]}</code>\n\n"
					f"<b>Обязанности:</b>\n<code>{orders[15]}</code>\n\n"

					f"{orders[7]}",
						reply_markup = buttons.globalOrders(orders[0], orders[12]))
				await bot.send_message(message.chat.id, 'Вот подборочка объявлений для Вас! 🥺', reply_markup = buttons.back_to_menu)

			except Exception as e:
				print(e)
				await bot.send_message(message.chat.id, "<b>🔔 Уведомление:</b>\n\nВашем регионе не найдены заказы! Загляните к нам позже.", reply_markup = buttons.menu_executor)
													

async def personal_cabinet(message: types.Message, state: FSMContext):
	await state.finish()
	ex_id = message.from_user.id

	if connection.checkReferral(ex_id)[3] == 'Banned':
		await bot.send_message(message.chat.id, "Ваш профиль забанен!")
	
	elif not connection.checkExecutor(ex_id):
		await bot.send_message(message.chat.id, "Для использование этого функционала, необходимо создать профиль исполнителя.", reply_markup = buttons.create_executor_profil)

	else:
		if connection.getExecutorProfil(ex_id)[8] == 'Banned':
			await bot.send_message(message.chat.id, "Ваш профиль исполнителя забанен!")


		else:
			alldata = connection.getExecutorProfil(ex_id)
			try:
				await bot.send_photo(message.chat.id, photo = alldata[3], caption = f"<b>{alldata[1]}</b>\n\n"
																					f"  <b>Дата рождения:</b> <code>{alldata[2]}</code>\n"
																					f"  <b>Номер:</b> <code>+{alldata[4]}</code>\n\n"

																					f"<b>Навыки:</b>\n{alldata[5]}\n\n" 
																					f"  <b>Рейтинг:</b> <code>{alldata[6]}</code>", 
																						reply_markup = buttons.get_works(message.from_user.id))
			except Exception as e:
				print(e)
				await bot.send_video(message.chat.id, alldata[3], caption = f'<b>{alldata[1]}</b>\n\n <b>Дата рождения:</b> <code>{alldata[2]}</code>\n <b>Номер:</b> <code>+{alldata[4]}</code>\n\n<b>Навыки:</b>\n{alldata[5]}\n\n <b>Рейтинг:</b> <code>{alldata[6]}</code>', reply_markup = buttons.get_works(message.from_user.id))



def register_reg_executor_profil_handlers(dp: Dispatcher):
	dp.register_message_handler(process_create1, state = RegExecutor.step1)
	dp.register_message_handler(process_create2, state = RegExecutor.step2)
	dp.register_message_handler(process_create3, content_types = ['photo', 'video'], state = RegExecutor.step3)
	dp.register_message_handler(process_contact_invalid, state = RegExecutor.step4)
	dp.register_message_handler(process_create4, content_types = 'contact', is_sender_contact = True, state = RegExecutor.step4)
	dp.register_message_handler(process_create5, state = RegExecutor.step5)

	dp.register_message_handler(get_geo, text=['Поиск заказов', 'Изменить геолокацию'], state='*')
	dp.register_message_handler(search_orders, content_types = ['location','venue'], state=RegExecutor.step6)
	dp.register_message_handler(personal_cabinet, text='Личный кaбинет', state='*') #a

	dp.register_callback_query_handler(process_create_executor_profil, lambda c: c.data == 'create_profil' or c.data == 'edit_ex', state = '*')
	dp.register_callback_query_handler(process_yes_skill, lambda c: c.data == 'yes', state = '*')
	dp.register_callback_query_handler(process_no_skill, lambda c: c.data == 'nep', state = '*')



