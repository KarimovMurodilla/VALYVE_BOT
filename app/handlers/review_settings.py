import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from app.admin import admin_connection
from .. import buttons, config, connection, file_ids, getLocationInfo


bot = Bot(token=config.TOKEN, parse_mode = 'html')


class AnswerToReview(StatesGroup):
	step1 = State()


class ComplaintToReview(StatesGroup):
	step1 = State()
	step2 = State()


class ComplaintToRequest(StatesGroup):
	step1 = State()
	step2 = State()



def fast_answer(func):
	async def wrapper(c: types.CallbackQuery, state: FSMContext):
		await c.answer()
		
		return 	await func(c, state)
	return wrapper


async def callback_answer_to_review(c: types.CallbackQuery, state: FSMContext):
	ids = c.data[7:].split(',')

	if not connection.selectReview(c.from_user.id, ids[1], ids[2])[5]:
		async with state.proxy() as data:
			data['ex_id'] = ids[0]
			data['cus_id'] = ids[1]
			data['order_id'] = ids[2]

		await AnswerToReview.step1.set()
		await c.answer()
		await bot.send_message(c.from_user.id, "Что вы хотите ответить на этот отзыв?", 
			reply_markup = buttons.back_canc)

	else:
		await c.answer("Вы уже ответили на отзыв!", show_alert = True)


async def process_answer(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['answer'] = message.text
		ex_id = data['ex_id']
		cus_id = data['cus_id']
		order_id = data['order_id']

		review = connection.selectReview(ex_id, cus_id, order_id)

		await message.answer(
				f"<b>Заказчик:</b> <code>{connection.selectAll(cus_id)[0]}</code>\n"
				f"<b>Адрес:</b> <code>{connection.selectOrderWhereCusId(cus_id, order_id)[2]}</code>\n\n"

				f"<b>Отзыв:</b>\n<code>{review[1]}</code>\n\n"

				f"<b>Ответ исполнителя:</b>\n<code>{message.text}</code>",
					reply_markup = buttons.answerSets())


@fast_answer
async def callback_change_answer(c: types.CallbackQuery, state: FSMContext):
	await AnswerToReview.step1.set()
	await c.message.answer("Что вы хотите ответить на этот отзыв?", 
		reply_markup = buttons.back_canc)


@fast_answer
async def callback_publish_answer(c: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		ex_id = data['ex_id']
		cus_id = data['cus_id']
		order_id = data['order_id']
		answer = data['answer']

		connection.UpdateAnswer(ex_id, cus_id, order_id, f"<b>Ответ исполнителя:</b>\n<code>{answer}</code>")

		await c.message.delete()
		await c.message.answer("🔔 <b>Уведомление:</b>\n\n"
							  f"Ваш ответ опубликован!\nТеперь его видят остальные пользователи.",
							  	reply_markup = buttons.autoMenu(connection.checkUserStatus(c.from_user.id)[0]))

		await state.finish()


@fast_answer
async def callback_complaint_for_review(c: types.CallbackQuery, state: FSMContext):
	ids = c.data[10:].split(',')
	async with state.proxy() as data:
		data['ex_id'] = ids[0]
		data['cus_id'] = ids[1]
		data['order_id'] = ids[2]

	await ComplaintToReview.step1.set()
	await bot.send_message(c.from_user.id, "По какой причине Вы хотите пожаловаться?",
		reply_markup = buttons.back_canc)


async def process_complaint(message: types.Message, state: FSMContext):
	await ComplaintToReview.next()
	async with state.proxy() as data:
		data['complaint'] = message.text
		ex_id = data['ex_id']
		cus_id = data['cus_id']
		order_id = data['order_id']

		review = connection.selectReview(ex_id, cus_id, order_id)

		await message.answer(
				f"<b>Заказчик:</b> <code>{connection.selectAll(cus_id)[0]}</code>\n"
				f"<b>Адрес:</b> <code>{connection.selectOrderWhereCusId(cus_id, order_id)[2]}</code>\n\n"

				f"<b>Отзыв:</b>\n<code>{review[1]}</code>\n\n")

		await message.answer(
				f"<b>Причина:</b>\n<code>{message.text}</code>",
					reply_markup = buttons.answerSets(answer = False))


@fast_answer
async def callback_change_complaint(c: types.CallbackQuery, state: FSMContext):
	await ComplaintToReview.step1.set()
	await c.message.answer("По какой причине Вы хотите пожаловаться?", 
		reply_markup = buttons.back_canc)


@fast_answer
async def callback_send_complaint(c: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		ex_id = data['ex_id']
		cus_id = data['cus_id']
		order_id = data['order_id']
		complaint = data['complaint']

		review = admin_connection.addComplaint(ex_id, cus_id, order_id, complaint)

		await c.message.delete()
		await c.message.answer("🔔 <b>Уведомление:</b>\n\n"
							  f"Ваша жалоба отправлена! Ожидайте ответа в течении 24x часов.",
							  	reply_markup = buttons.autoMenu(connection.checkUserStatus(c.from_user.id)[0]))

		await state.finish()



# -----------------Send Complaint To Requester-----------------------
@fast_answer
async def send_complaint_to_requester(c: types.CallbackQuery, state: FSMContext):
	ex_id = c.data[22:]
	async with state.proxy() as data:
		data['ex_id'] = ex_id

	await ComplaintToRequest.step1.set()
	await c.message.answer("По какой причине Вы хотите пожаловаться?")


async def input_complaint(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['complaint'] = message.text
		ex_id = data['ex_id']
		all_data = connection.checkExecutor(ex_id)
		now = datetime.datetime.now().strftime('%Y')

		await ComplaintToRequest.next()
		try:
			await bot.send_photo(
					   chat_id = message.chat.id,
					   photo = all_data[3], 
					   caption = f"<b>{all_data[1]}</b>, <code>{int(now)-int(all_data[2][6:])}</code> лет\n\n"
								 f"<b>  Рейтинг:</b> <code>{all_data[6]}</code>\n\n"
								 f"<b>Навыки:</b>\n{all_data[5]}")
		except:
			await bot.send_video(
					   chat_id = message.chat.id,
					   video = all_data[3], 
					   caption = f"<b>{all_data[1]}</b>, <code>{int(now)-int(all_data[2][6:])}</code> лет\n\n"
								 f"<b>  Рейтинг:</b> <code>{all_data[6]}</code>\n\n"
								 f"<b>Навыки:</b>\n{all_data[5]}")

		await message.answer(f"<b>Причина:</b>\n<code>{message.text}</code>", 
			reply_markup = buttons.answerSets(answer = False, r = 2))


async def send_complaint_to_admin(c: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		ex_id = data['ex_id']
		complaint = data['complaint']

		admin_connection.addUserComplaint(ex_id, complaint)
		await c.message.delete()
		await c.message.answer("Ваше жалоба отправлена на модерции")

		await state.finish()
		


async def change_request_complaint(c: types.CallbackQuery, state: FSMContext):
	await ComplaintToRequest.step1.set()
	await c.message.answer("По какой причине Вы хотите пожаловаться?")



def register_review_handlers(dp: Dispatcher):
	dp.register_callback_query_handler(callback_answer_to_review, lambda c: c.data.startswith('answer'),  state = '*')	
	dp.register_message_handler(process_answer, state = AnswerToReview.step1)
	dp.register_callback_query_handler(callback_change_answer, lambda c: c.data.startswith('change_answer'),  state = '*')	
	dp.register_callback_query_handler(callback_publish_answer, lambda c: c.data.startswith('publish_answer'),  state = '*')	

	dp.register_callback_query_handler(callback_complaint_for_review, lambda c: c.data.startswith('complaint'),  state = '*')	
	dp.register_message_handler(process_complaint, state = ComplaintToReview.step1)
	dp.register_callback_query_handler(callback_change_complaint, lambda c: c.data.startswith('change_complaint'),  state = ComplaintToReview.step2)	
	dp.register_callback_query_handler(callback_send_complaint, lambda c: c.data.startswith('send_complaint'),  state = ComplaintToReview.step2)	

	dp.register_callback_query_handler(send_complaint_to_requester, lambda c: c.data.startswith('send_complaint_to_req'),  state = '*')
	dp.register_message_handler(input_complaint, state = ComplaintToRequest.step1)
	dp.register_callback_query_handler(send_complaint_to_admin, lambda c: c.data == 'send_complaint',  state = ComplaintToRequest.step2)
	dp.register_callback_query_handler(change_request_complaint, lambda c: c.data == 'change_complaint',  state = ComplaintToRequest.step2)

