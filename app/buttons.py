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


def get_orders(chat_id):
	orders = types.InlineKeyboardMarkup(row_width = 2)
	view = types.InlineKeyboardButton(text = "Посмотреть", switch_inline_query_current_chat = f"!get_order {chat_id}")
	create = types.InlineKeyboardButton(text = "Создать", callback_data = 'create')
	orders.add(view, create)

	return orders


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
	my_performs = types.InlineKeyboardButton(text = 'Мои исполнители', switch_inline_query_current_chat = f'!my_performers {order_id}')
	order_buttons.add(complete_order, request_order, my_performs)
	# order_buttons.add()

	return order_buttons


def get_works(chat_id):
	profil_settings = types.InlineKeyboardMarkup(row_width = 1)
	recent_works = types.InlineKeyboardButton(text = 'История работы', switch_inline_query_current_chat = f"!recent_works {chat_id}")
	edit_ex = types.InlineKeyboardButton(text = 'Ред.профиль', callback_data = 'edit_ex')
	my_reviews = types.InlineKeyboardButton(text = 'Мои отзывы', switch_inline_query_current_chat = f"!reviews {chat_id}")
	profil_settings.add(recent_works, edit_ex, my_reviews)

	return profil_settings


def requestButton(ex_id: int, order_id: int, ex_contact: int):
	request = types.InlineKeyboardMarkup(row_width = 2)
	approve = types.InlineKeyboardButton(text = 'Одобрить', callback_data = f"sendAccept {ex_id},{order_id},{ex_contact}")
	reject = types.InlineKeyboardButton(text = 'Отклонить', callback_data = f"sendRefusal {ex_id},{order_id},{ex_contact}")
	reviews = types.InlineKeyboardButton(text = 'История отзывов', switch_inline_query_current_chat = f"!reviews {ex_id}")
	request.add(approve, reject, reviews)

	return request


def performerButtons(ex_id: int, order_id: int):
	pb = types.InlineKeyboardMarkup(row_width = 1)
	reviews = types.InlineKeyboardButton(text = 'История отзывов', switch_inline_query_current_chat = f"!reviews {ex_id}")
	end = types.InlineKeyboardButton(text = 'Завершить', callback_data = f"!end {ex_id},{order_id}")
	pb.add(reviews, end)

	return pb


def getProfil(ex_id, order_id):
	buttons = types.InlineKeyboardMarkup()
	yes = types.InlineKeyboardButton(text = 'Да', callback_data = f"yes_i_view {ex_id},{order_id}")
	no = types.InlineKeyboardButton(text = 'Нет', callback_data = f"no_view")
	buttons.add(yes, no)

	return buttons


def endOrder(cus_id, order_id):
	end_order = types.InlineKeyboardMarkup()
	the_end = types.InlineKeyboardButton(text = "Завершить", callback_data = f"the_end {cus_id},{order_id}")
	get_geo = types.InlineKeyboardButton(text = "Получить ГЕО", callback_data = f"getGeo {cus_id},{order_id}")
	end_order.add(the_end, get_geo)

	return end_order

def menuPrice():
	prices = types.InlineKeyboardMarkup()
	price_1 = types.InlineKeyboardButton(text = '1️⃣', callback_data = 'price_50')
	price_2 = types.InlineKeyboardButton(text = '2️⃣', callback_data = 'price_80')
	price_3 = types.InlineKeyboardButton(text = '3️⃣', callback_data = 'price_270')
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