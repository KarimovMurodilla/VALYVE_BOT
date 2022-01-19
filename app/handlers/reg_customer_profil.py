import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from .. import connection, file_ids, buttons, config
from app.admin import admin_connection


bot = Bot(token=config.TOKEN, parse_mode = 'html')


class RegCustomer(StatesGroup):
	step1 = State()
	step2 = State()
	step3 = State()
	step4 = State()



def checkStatusUser(func):
	async def wrapper(message: types.Message, state: FSMContext):
		user_id = message.from_user.id
		try:
			if not connection.checkUserStatus(user_id)[0]:
				await bot.send_photo(message.chat.id, photo = file_ids.PHOTO['agreement'], caption = "Для использования бота, необходимо ознакомиться с <a href = 'https://ru.wikipedia.org/wiki/%D0%9F%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8C%D1%81%D0%BA%D0%BE%D0%B5_%D1%81%D0%BE%D0%B3%D0%BB%D0%B0%D1%88%D0%B5%D0%BD%D0%B8%D0%B5'>пользовательским договором</a> и согласиться с ним чтоб продолжить использование бота.", reply_markup = buttons.btn)

			else:
				return await func(message, state)

		except TypeError:
			await bot.send_photo(message.chat.id, photo = file_ids.PHOTO['agreement'], caption = "Для использования бота, необходимо ознакомиться с <a href = 'https://ru.wikipedia.org/wiki/%D0%9F%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8C%D1%81%D0%BA%D0%BE%D0%B5_%D1%81%D0%BE%D0%B3%D0%BB%D0%B0%D1%88%D0%B5%D0%BD%D0%B8%D0%B5'>пользовательским договором</a> и согласиться с ним чтоб продолжить использование бота.", reply_markup = buttons.btn)

	return wrapper



async def process_set_reg_state(c: types.CallbackQuery, state: FSMContext):
	await RegCustomer.step1.set()
	await bot.delete_message(c.message.chat.id, c.message.message_id)
	await bot.send_message(c.message.chat.id, "Отправьте мне Ваше Имя Отчество,  для идентификация Вас.",
		reply_markup = buttons.back_canc)


async def process_reg1(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['name'] = message.text

	await RegCustomer.next()
	await bot.send_message(message.chat.id, "Отправьте мне Ваше фото, это вызовет больше доверия к Вашим объявлением.",
		reply_markup = buttons.nope)


async def process_img(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['photo'] = message.photo[-1].file_id

	await RegCustomer.next()
	await bot.send_message(message.chat.id, "Отправьте мне Ваш номер телефона, для связи по работе.",
		reply_markup = buttons.contact)


async def process_contact_and_all_data(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['contact'] = message.contact.phone_number

		cus_id = message.from_user.id
		cus_name = data['name']
		cus_pic = data['photo']
		cus_contact = data['contact']
		date_registration = datetime.datetime.today().strftime('%d.%m.%Y - %H:%M')
		
		if not connection.checkRegStatus(cus_id):
			connection.RegData(cus_id, cus_name, cus_pic, cus_contact, date_registration)
			await bot.send_message(message.chat.id, "<b>🔔 Уведомление:</b>\n\n" 
								                    "Ваш профиль успешно создан!",reply_markup = buttons.menu_customer)

		else:
			# connection.UpdateData(cus_id, cus_name, cus_pic, cus_contact, date_registration)
			await bot.send_message(message.chat.id, "<b>🔔 Уведомление:</b>\n\n" 
													"Ваш новый профиль отправлен на модерацию чтобы проверить наличие ошибок.", reply_markup = buttons.menu_customer)			
			status = connection.checkUserStatus(message.from_user.id)[0]
			admin_connection.addRequestProfil(cus_id, status, cus_name, cus_pic, cus_contact)

	await state.finish()


async def cancel_handler(message: types.Message, state: FSMContext):
	await state.finish()
	user_id = message.chat.id
	user_status = connection.checkUserStatus(user_id)

	if user_status[0] == 'customer':
		await bot.send_message(message.chat.id, "Главное меню", reply_markup = buttons.menu_customer)
		await state.finish()

	elif user_status[0] == 'executor':
		await bot.send_message(message.chat.id, "Главное меню", reply_markup = buttons.menu_executor)
		# await state.finish()   


async def process_contact_if_not_img(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['contact'] = message.contact.phone_number

		cus_id = message.from_user.id
		cus_name = data['name']
		cus_pic = 'AgACAgIAAxkBAAOvYW5woS9KTofLU3EqNCIoo3jTWx0AAhezMRt7rXhL5FS-aNbKWN8BAAMCAAN5AAMhBA'
		cus_contact = data['contact']
		date_registration = datetime.datetime.today().strftime('%d.%m.%Y - %H:%M')
		
		if not connection.checkRegStatus(cus_id):
			connection.RegData(cus_id, cus_name, cus_pic, cus_contact, date_registration)
			await bot.send_message(message.chat.id, "<b>🔔 Уведомление:</b>\n\n"
								                    "Ваш профиль заказчика успешно создан!", reply_markup = buttons.menu_customer)

		else:
			# connection.UpdateData(cus_id, cus_name, cus_pic, cus_contact, date_registration)
			await bot.send_message(message.chat.id, "<b>🔔 Уведомление:</b>\n\n" 
													"Ваш профиль отправлен на модерацию. Ожидайте ответа в течении 24х часов!", reply_markup = buttons.menu_customer)
			status = connection.checkUserStatus(message.from_user.id)[0]
			admin_connection.addRequestProfil(cus_id, status, cus_name, cus_pic, cus_contact)

	await state.finish()


async def process_edit_profil(c: types.CallbackQuery, state: FSMContext):
	cus_id = c.from_user.id

	if connection.checkReferral(cus_id)[3] == 'Banned':
		await bot.send_message(message.chat.id, "Ваш профиль забанен!")

	else:
		await RegCustomer.step1.set()
		await bot.send_message(c.message.chat.id, "Отправьте мне Ваше Имя Отчество,  для идентификация Вас.",
			reply_markup = buttons.back_canc)


async def process_no_img(c: types.CallbackQuery, state: FSMContext):
	await RegCustomer.step4.set()
	
	await bot.delete_message(c.message.chat.id, c.message.message_id)		
	await bot.send_message(c.message.chat.id, "Отправьте мне Ваш номер телефона, для связи по работе.",
		reply_markup = buttons.contact)
	

@checkStatusUser
async def my_orders(message: types.Message, state: FSMContext):
	cus_id = message.from_user.id
	
	if not connection.checkRegStatus(cus_id):
		await bot.send_message(message.chat.id, "Для использование этого функционала, необходимо создать профиль заказчика.", reply_markup = buttons.create_account)


	else:
		if connection.checkReferral(cus_id)[3] == 'Banned':
			await bot.send_message(message.chat.id, "Ваш профиль забанен!")
			
		elif connection.selectAll(cus_id)[3] == 'Banned':
			await bot.send_message(message.chat.id, "Ваш профиль заказчика забанен!")

		else:
			await bot.send_message(message.chat.id, "Вы хотите просмотреть свои заказы или создать новый заказ?", reply_markup = buttons.get_orders(cus_id))


@checkStatusUser
async def my_cab(message: types.Message, state: FSMContext):
	cus_id = message.from_user.id

	if not connection.checkRegStatus(cus_id):
		await bot.send_message(message.chat.id, "Для использование этого функционала, необходимо создать профиль заказчика.", reply_markup = buttons.create_account)

	elif connection.selectAll(cus_id)[3] == 'Banned':
		await bot.send_message(message.chat.id, "Ваш профиль заказчика забанен!")
		
	else:
		alldata = connection.selectAll(cus_id)
		await bot.send_photo(message.chat.id, photo = alldata[1], caption = f'<b>{alldata[0]}</b>\n <b>Номер:</b> <code>+{alldata[2]}</code>', reply_markup = buttons.edit_profil)


@checkStatusUser
async def info(message: types.Message, state: FSMContext):
	cus_id = message.from_user.id

	if connection.checkReferral(cus_id)[3] == 'Banned':
		await bot.send_message(message.chat.id, "Ваш профиль забанен!")

	else:
		await bot.send_photo(message.chat.id, photo = file_ids.PHOTO['info'], reply_markup = buttons.info)



def register_reg_customer_profil_handlers(dp: Dispatcher):
	dp.register_message_handler(cancel_handler, text=['Отменить', 'Назад', 'Выйти из беседы'], state='*')
	dp.register_message_handler(process_reg1, state = RegCustomer.step1)
	dp.register_message_handler(process_img, content_types = 'photo', state = RegCustomer.step2)
	dp.register_message_handler(process_contact_and_all_data, content_types = 'contact', is_sender_contact = True, state = RegCustomer.step3)
	dp.register_message_handler(process_contact_if_not_img, content_types = 'contact', is_sender_contact = True, state = RegCustomer.step4)

	dp.register_message_handler(my_orders, text='Мои заказы', state='*')
	dp.register_message_handler(my_cab, text='Личный кабинет', state='*')
	dp.register_message_handler(info, text='Доп.Функции', state='*')

	dp.register_callback_query_handler(process_set_reg_state, lambda c: c.data == 'create_acc',  state = '*')   
	dp.register_callback_query_handler(process_edit_profil, lambda c: c.data == 'edit',  state = '*')
	dp.register_callback_query_handler(process_no_img, lambda c: c.data == 'no',  state = '*')