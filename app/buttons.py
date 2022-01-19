from aiogram import types


btn = types.InlineKeyboardMarkup(row_width = 1)
link = types.InlineKeyboardButton(text = "Пользовательский договор", url = 'https://ru.wikipedia.org/wiki/%D0%9F%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8C%D1%81%D0%BA%D0%BE%D0%B5_%D1%81%D0%BE%D0%B3%D0%BB%D0%B0%D1%88%D0%B5%D0%BD%D0%B8%D0%B5')
agreement = types.InlineKeyboardButton(text = "Я принимаю условия", callback_data = 'agree')
btn.add(agreement)


btn2 = types.InlineKeyboardMarkup(row_width = 2)
zak = types.InlineKeyboardButton(text = "Заказчик", callback_data = 'zak')
isp = types.InlineKeyboardButton(text = "Исполнитель", callback_data = 'isp')
btn2.add(zak, isp)


# --------Customer buttons--------
menu_customer = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
mzak = types.KeyboardButton("Мои заказы")
info = types.KeyboardButton("Доп.Функции")
per = types.KeyboardButton("Личный кабинет")
menu_customer.add(mzak, info, per)


create_account = types.InlineKeyboardMarkup(row_width = 1)
create_acc = types.InlineKeyboardButton(text = "Создать профиль", callback_data = 'create_acc')
create_account.add(create_acc)


back_canc = types.ReplyKeyboardMarkup(resize_keyboard = True)
canc = types.KeyboardButton("Отменить")
back_canc.add(canc)


send_geo = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 1)
geo = types.KeyboardButton("Отправить геолокацию", request_location = True)
cancel = types.KeyboardButton("Отменить")
send_geo.add(geo, cancel)


nope = types.InlineKeyboardMarkup(row_width = 1)
no = types.InlineKeyboardButton(text = "Пропустить", callback_data = 'no')
nope.add(no)


contact = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 1)
send_contact = types.KeyboardButton("Поделиться контактом", request_contact = True)
contact.add(send_contact, cancel)


another = types.InlineKeyboardMarkup(row_width = 1)
other = types.InlineKeyboardButton(text = "Другое", callback_data = 'other')
another.add(other)


edit_profil = types.InlineKeyboardMarkup(row_width = 1)
edit = types.InlineKeyboardButton(text = 'Ред.профиль', callback_data = 'edit')
edit_profil.add(edit)


info = types.InlineKeyboardMarkup(row_width = 1)
auth = types.InlineKeyboardButton(text = "Переподключение", callback_data = 'auth')
faq = types.InlineKeyboardButton(text = "FAQ Справочная", callback_data = 'faq')
ref = types.InlineKeyboardButton(text = "Банк проекта", callback_data = 'bank')
support = types.InlineKeyboardButton(text = "Поддержка", callback_data = 'support')
info.add(auth, faq, ref, support)


change_order = types.InlineKeyboardMarkup(row_width = 2)
change = types.InlineKeyboardButton(text = 'Изменить', callback_data = 'change')
publish = types.InlineKeyboardButton(text = 'Опубликовать', callback_data = 'publish')
change_order.add(change, publish)


# --------Executor buttons--------
menu_executor = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
search_order = types.KeyboardButton("Поиск заказов")
info_ex = types.KeyboardButton("Доп.Функции")
cabinet_ex = types.KeyboardButton("Личный кaбинет") # a
menu_executor.add(search_order, info_ex, cabinet_ex)


create_executor_profil = types.InlineKeyboardMarkup(row_width = 1)
create_profil = types.InlineKeyboardButton(text = "Создать профиль", callback_data = 'create_profil')
create_executor_profil.add(create_profil)


yes_no = types.InlineKeyboardMarkup(row_width = 2)
yes = types.InlineKeyboardButton(text = "Да", callback_data = 'yes')
nep = types.InlineKeyboardButton(text = "Нет", callback_data = 'nep')
yes_no.add(yes, nep)

back_to_menu = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 1)
bck = types.KeyboardButton("Отменить")
bck_geo = types.KeyboardButton("Изменить геолокацию", request_location = True)
back_to_menu.add(bck, bck_geo)


contact_ex = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 1)
contact_ex.add(send_contact, canc)


skip_btn = types.InlineKeyboardMarkup(row_width = 1)
skip = types.InlineKeyboardButton(text = "Пропустить", callback_data = 'skip')
skip_btn.add(skip)



# --------Referral buttons--------
referral_settings = types.InlineKeyboardMarkup(row_width = 2)
withdraw = types.InlineKeyboardButton(text = 'Вывести', callback_data = 'withdraw')
top_up = types.InlineKeyboardButton(text = 'Пополнить', callback_data = 'top_up')
buy_cupons = types.InlineKeyboardButton(text = 'Купить купоны', callback_data = 'buy_cupons')
stat = types.InlineKeyboardButton(text = 'Статистика', callback_data = 'stat')
referral_settings.add(withdraw, top_up)
referral_settings.add(buy_cupons)
referral_settings.add(stat)


def autoMenu(title: str):
	if title == 'customer':
		return menu_customer

	else:
		return menu_executor


def get_orders(chat_id, just_inline = False):
	orders = types.InlineKeyboardMarkup(row_width = 2)
	view = types.InlineKeyboardButton(text = "Посмотреть", switch_inline_query_current_chat = f"!get_order {chat_id}")
	get_create = types.InlineKeyboardButton(text = "Создать", callback_data = 'get_create')

	if just_inline:
		orders.add(view)
	else:
		orders.add(view, get_create)

	return orders

def get_create_order():
	createBtn = types.InlineKeyboardMarkup()
	create = types.InlineKeyboardButton(text = "Я ознакомлен(а) с правилами", callback_data = 'create')
	createBtn.add(create)

	return createBtn


def globalOrders(cus_id: int, order_id: int):
	btns_order = types.InlineKeyboardMarkup(row_width = 2)
	back = types.InlineKeyboardButton(text = "Назад", callback_data = f'back {cus_id}, {order_id}')
	nex = types.InlineKeyboardButton(text = "Далее", callback_data = f'nex {cus_id}, {order_id}')
	appl = types.InlineKeyboardButton(text = "Откликнуться", callback_data = f'apply {cus_id}, {order_id}')
	btns_order.add(back, nex, appl)

	return btns_order


# --------Rate buttons--------
def yesNo():
	yes_no = types.InlineKeyboardMarkup(row_width = 2)
	yes = types.InlineKeyboardButton(text = "Да", callback_data = f'yep')
	net = types.InlineKeyboardButton(text = "Нет", callback_data = 'net')
	yes_no.add(yes, net)

	return yes_no


def yesNope(cus_id, order_id):
	yes_no = types.InlineKeyboardMarkup(row_width = 2)
	yes = types.InlineKeyboardButton(text = "Да", callback_data = f'da {order_id}')
	net = types.InlineKeyboardButton(text = "Нет", callback_data = 'net')
	yes_no.add(yes, net)

	return yes_no



def rating():
	rate = types.InlineKeyboardMarkup(row_width = 1)
	a = types.InlineKeyboardButton(text = "Отличное", callback_data = '!rate +0.3')
	b = types.InlineKeyboardButton(text = "Хорошое", callback_data = '!rate +0.2')
	c = types.InlineKeyboardButton(text = "Нормальное", callback_data = '!rate +0.1')
	d = types.InlineKeyboardButton(text = "Плохое", callback_data = '!rate -0.3')
	f = types.InlineKeyboardButton(text = "Ужасное", callback_data = '!rate -0.5')
	rate.add(a, b, c, d, f)

	return rate

def rating2(cus_id, order_id, ex_id):
	rate = types.InlineKeyboardMarkup(row_width = 1)
	a = types.InlineKeyboardButton(text = "Отличное", callback_data = f'!to_rate +0.3,{cus_id},{order_id},{ex_id}')
	b = types.InlineKeyboardButton(text = "Хорошое", callback_data = f'!to_rate +0.2,{cus_id},{order_id},{ex_id}')
	c = types.InlineKeyboardButton(text = "Нормальное", callback_data = f'!to_rate +0.1,{cus_id},{order_id},{ex_id}')
	d = types.InlineKeyboardButton(text = "Плохое", callback_data = f'!to_rate -0.3,{cus_id},{order_id},{ex_id}')
	f = types.InlineKeyboardButton(text = "Ужасное", callback_data = f'!to_rate -0.5,{cus_id},{order_id},{ex_id}')
	rate.add(a, b, c, d, f)

	return rate


def comment():
	com = types.InlineKeyboardMarkup(row_width = 2)
	nep = types.InlineKeyboardButton(text = "Нет", callback_data = 'no_com')
	leave_comment = types.InlineKeyboardButton(text = "Оставить", callback_data = 'leave_comment')
	com.add(nep, leave_comment)

	return com


def realOrNot():
	ron = types.InlineKeyboardMarkup(resize_keyboard = True, row_width = 2)
	to_change = types.InlineKeyboardButton("Изменить", callback_data = 'to_change')
	to_publish = types.InlineKeyboardButton("Опубликовать", callback_data = 'to_publish')
	# cancl = types.InlineKeyboardButton("Отменить", callback_data = 'net')
	ron.add(to_change, to_publish)

	return ron


def realOrNot2(cus_id, ex_id, rate, order_id):
	ron = types.InlineKeyboardMarkup(resize_keyboard = True, row_width = 2)
	to_change = types.InlineKeyboardButton("Изменить", callback_data = f'toChange {cus_id},{order_id},{ex_id}')
	to_publish = types.InlineKeyboardButton("Опубликовать", callback_data = f'toPublish {cus_id},{ex_id},{rate},{order_id}')
	# cancl = types.InlineKeyboardButton("Отменить", callback_data = 'net')
	ron.add(to_change, to_publish)

	return ron

# ------BUTTONS WITH FUNCTIONS------
def orderButtons(order_id):
	order_buttons = types.InlineKeyboardMarkup(row_width = 2)
	complete_order = types.InlineKeyboardButton(text = 'Завершить', callback_data = f'complete_order {order_id}')
	request_order = types.InlineKeyboardButton(text = 'Заявки', switch_inline_query_current_chat = f'!my_requests {order_id}')
	call_to_per = types.InlineKeyboardButton(text = 'Вызвать исполнителя', callback_data = f'call_to_per {order_id}')
	my_performs = types.InlineKeyboardButton(text = 'Мои исполнители', switch_inline_query_current_chat = f'!my_performers {order_id}')
	my_pendings = types.InlineKeyboardButton(text = "На рассмотрении", switch_inline_query_current_chat = f'!my_pendings {order_id}')
	order_buttons.add(complete_order, request_order)
	order_buttons.add(call_to_per)
	order_buttons.add(my_performs)
	order_buttons.add(my_pendings)

	return order_buttons


def get_works(chat_id):
	profil_settings = types.InlineKeyboardMarkup(row_width = 1)
	recent_works = types.InlineKeyboardButton(text = 'История работы', switch_inline_query_current_chat = f"!recent_works {chat_id}")
	edit_ex = types.InlineKeyboardButton(text = 'Ред.профиль', callback_data = 'edit_ex')
	my_reviews = types.InlineKeyboardButton(text = 'Мои отзывы', switch_inline_query_current_chat = f"!reviews {chat_id}")
	under_consideration = types.InlineKeyboardButton(text = "На рассмотрении", switch_inline_query_current_chat = f'!under_consideration {chat_id}')

	profil_settings.add(recent_works, edit_ex, my_reviews, under_consideration)

	return profil_settings


def requestButton(ex_id: int, order_id: int, ex_contact: int):
	request = types.InlineKeyboardMarkup(row_width = 2)
	approve = types.InlineKeyboardButton(text = 'Одобрить', callback_data = f"sendAccept {ex_id},{order_id},{ex_contact}")
	reject = types.InlineKeyboardButton(text = 'Отклонить', callback_data = f"sendRefusal {ex_id},{order_id},{ex_contact}")
	reviews = types.InlineKeyboardButton(text = 'История отзывов', switch_inline_query_current_chat = f"!reviews {ex_id}")
	complaint_for_requests = types.InlineKeyboardButton(text = 'Отправить жалобу', callback_data = f'send_complaint_to_req {ex_id}')
	request.add(approve, reject, reviews)
	request.add(complaint_for_requests)

	return request


def performerButtons(ex_id: int, order_id: int):
	pb = types.InlineKeyboardMarkup(row_width = 1)
	reviews = types.InlineKeyboardButton(text = 'История отзывов', switch_inline_query_current_chat = f"!reviews {ex_id}")
	end = types.InlineKeyboardButton(text = 'Завершить', callback_data = f"!end {ex_id},{order_id}")
	pb.add(reviews, end)

	return pb


def pendingButtons(ex_id: int, order_id: int):
	pb = types.InlineKeyboardMarkup(row_width = 1)
	reviews = types.InlineKeyboardButton(text = 'История отзывов', switch_inline_query_current_chat = f"!reviews {ex_id}")
	end = types.InlineKeyboardButton(text = 'Завершить', callback_data = f"!finish_pending {ex_id},{order_id}")
	pb.add(reviews, end)

	return pb


def getProfil(ex_id, order_id, status):
	buttons = types.InlineKeyboardMarkup()
	yes = types.InlineKeyboardButton(text = 'Да', callback_data = f"yes_i_view {ex_id},{order_id},{status}")
	no = types.InlineKeyboardButton(text = 'Нет', callback_data = f"no_view")
	buttons.add(yes, no)

	return buttons


def endOrder(cus_id, order_id):
	end_order = types.InlineKeyboardMarkup()
	the_end = types.InlineKeyboardButton(text = "Завершить", callback_data = f"the_end {cus_id},{order_id}")
	get_geo = types.InlineKeyboardButton(text = "Получить ГЕО", callback_data = f"getGeo {cus_id},{order_id}")
	end_order.add(the_end, get_geo)

	return end_order

def menuPrice(total_1, total_2, total_3):
	prices = types.InlineKeyboardMarkup()
	price_1 = types.InlineKeyboardButton(text = '1️⃣', callback_data = f'price 30,{total_1}')
	price_2 = types.InlineKeyboardButton(text = '2️⃣', callback_data = f'price 90,{total_2}')
	price_3 = types.InlineKeyboardButton(text = '3️⃣', callback_data = f'price 180,{total_3}')
	prices.add(price_1, price_2, price_3)	
	
	return prices


def showPayment(bill_id, url, price):
	menu_payment = types.InlineKeyboardMarkup(row_width=2)
	link_to_pay = types.InlineKeyboardButton(text = "Оплатить", url = url)
	check_payment = types.InlineKeyboardButton(text = "Обновить", callback_data = f"check_{bill_id},{price}")
	menu_payment.add(link_to_pay, check_payment)

	return menu_payment


def viewVacancy(cus_id, order_id):
	view_vacancy = types.InlineKeyboardMarkup()
	vacancy = types.InlineKeyboardButton(text = "Просмотреть вакансию", callback_data = f"cView {cus_id},{order_id}")
	view_vacancy.add(vacancy)

	return view_vacancy


def skipBtn():
	skip_btn = types.InlineKeyboardMarkup()
	skip = types.InlineKeyboardButton(text = "Пропустить", callback_data = f'cSkip')
	skip_btn.add(skip)

	return skip_btn


def withdrawBtns():
	withdraw_btns = types.InlineKeyboardMarkup(row_width = 2)
	card = types.InlineKeyboardButton(text = "Карта", callback_data = 'card')
	purse = types.InlineKeyboardButton(text = "Кошелёк", callback_data = 'purse')
	withdraw_btns.add(card, purse)

	return withdraw_btns


def withdrawCheckBtns():
	withdraw_check_btns = types.InlineKeyboardMarkup(row_width = 2)
	confirm = types.InlineKeyboardButton(text = "Подтвердить", callback_data = 'confirm')
	change_withdraw = types.InlineKeyboardButton(text = "Изменить", callback_data = 'change_withdraw')
	withdraw_check_btns.add(confirm, change_withdraw)

	return withdraw_check_btns


def to_pay(amount):
	pay_btn = types.InlineKeyboardMarkup()
	to_pay_order = types.InlineKeyboardButton(text = "Оплатить", callback_data = f'pay_order {amount}')
	pay_btn.add(to_pay_order)

	return pay_btn


def answerToReview(ex_id, cus_id, order_id, is_executor, answered):
	if is_executor and not answered:
		review_btns = types.InlineKeyboardMarkup(row_width=1)
		answer = types.InlineKeyboardButton(text = "Ответить", callback_data = f'answer {ex_id},{cus_id},{order_id}')
		complaint = types.InlineKeyboardButton(text = "Отправить жалобу", callback_data = f'complaint {ex_id},{cus_id},{order_id}')
		review_btns.add(answer, complaint)

		return review_btns


def answerSets(answer = True, r = 1):
	if answer:
		answer_btns = types.InlineKeyboardMarkup(row_width=r)
		change_answer = types.InlineKeyboardButton(text = "Изменить", callback_data = f'change_answer')
		publish_answer = types.InlineKeyboardButton(text = "Опубликовать", callback_data = f'publish_answer')
		answer_btns.add(change_answer, publish_answer)

		return answer_btns		

	else:
		complaint_btns = types.InlineKeyboardMarkup(row_width=r)
		change_complaint = types.InlineKeyboardButton(text = "Изменить", callback_data = f'change_complaint')
		send_complaint = types.InlineKeyboardButton(text = "Отправить", callback_data = f'send_complaint')
		complaint_btns.add(change_complaint, send_complaint)

		return complaint_btns	


def executor_choice(cus_id, order_id, start_day, end_day):
	answer_btns = types.InlineKeyboardMarkup(row_width=2)
	refuse = types.InlineKeyboardButton(text = "Отказать", callback_data = f'refuse {cus_id},{order_id},{start_day},{end_day}')
	accept = types.InlineKeyboardButton(text = "Принять", callback_data = f'accept {cus_id}')
	answer_btns.add(refuse, accept)

	return answer_btns


def findNewEx(order_id, start_day, end_day):
	find_btn = types.InlineKeyboardMarkup()
	find_ex = types.InlineKeyboardButton(text = "Найти другого исполнителя", callback_data = f'find_ex {order_id},{start_day},{end_day}')
	find_btn.add(find_ex)

	return find_btn



def getCouponsBtn():
	cpns_btn = types.InlineKeyboardMarkup()
	buy = types.InlineKeyboardButton(text = "Купить", callback_data = f'buy_cpn')
	refresh = types.InlineKeyboardButton(text = "Обновить", callback_data = "refresh_cpn")
	cpns_btn.add(buy, refresh)

	return cpns_btn


def getPayCpnsBtn():
	pay_btn = types.InlineKeyboardMarkup()
	pay = types.InlineKeyboardButton(text = "Оплатить", callback_data = f'pay_cpn')
	pay_btn.add(pay)

	return pay_btn


def getUnderConsiderationBtns(cus_id, order_id, again_reply = False):
	con_btns = types.InlineKeyboardMarkup()
	end = types.InlineKeyboardButton(text = "Завершить", callback_data = f'con_finish {cus_id},{order_id}')
	write_to_cus = types.InlineKeyboardButton(text = "Написать", callback_data = f'write_to_cus {cus_id}')
	
	if again_reply:
		con_btns.add(write_to_cus)

	else:
		con_btns.add(end, write_to_cus)

	return con_btns


def replyTo(user_id):
	reply = types.InlineKeyboardMarkup()
	reply_to_ex = types.InlineKeyboardButton(text = "Ответить", callback_data = f'reply_to_ex {user_id}')
	reply.add(reply_to_ex)

	return reply


def leaveChat():
	btn = types.ReplyKeyboardMarkup(resize_keyboard = True)
	leave = types.KeyboardButton("Выйти из беседы")
	btn.add(leave)

	return btn