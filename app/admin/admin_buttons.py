from aiogram import types


def adminPanel():
	panel = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
	stat = types.KeyboardButton("Статистика")
	bank = types.KeyboardButton("Банк")
	console = types.KeyboardButton("Консоль")
	moder = types.KeyboardButton("Модерация")
	panel.add(stat)
	panel.add(bank, console)
	panel.add(moder)

	return panel

 
def adminConsol(sensor, sensor2, sensor3, sensor4):
	consol = types.InlineKeyboardMarkup(row_width = 2)
	breaking = types.InlineKeyboardButton("Пробить", callback_data = "breaking")
	ban = types.InlineKeyboardButton("Забанить", callback_data = "ban")
	unban = types.InlineKeyboardButton("Разбанить", callback_data = "unban")
	payment = types.InlineKeyboardButton(f"Вывод {sensor}", callback_data = "payment")
	report = types.InlineKeyboardButton(f"Сообщить", callback_data = "report")
	list_of_announcements = types.InlineKeyboardButton(f"Список объявлений", callback_data = "list_of_announcements")
	ads = types.InlineKeyboardButton(f"[S] Объявления {sensor3}", callback_data = "ads")
	ribbons = types.InlineKeyboardButton(f"[P] Ленты {sensor2}", callback_data = "ribbons")
	replenishment = types.InlineKeyboardButton(f"Пополнение {sensor4}", callback_data = "replenishment")
	withdrawal_history = types.InlineKeyboardButton(f"История вывода", callback_data = "withdrawal_history")

	consol.add(unban, ban)
	consol.add(report, breaking)
	consol.add(list_of_announcements)
	consol.add(ads, ribbons)
	consol.add(payment, replenishment)
	consol.add(withdrawal_history)


	return consol, sensor, sensor2


def chooseCategory():
	categ = types.InlineKeyboardMarkup(row_width = 2)
	customer = types.InlineKeyboardButton("Заказчик", callback_data = "customer")
	executor = types.InlineKeyboardButton("Исполнитель", callback_data = "executor")
	categ.add(customer, executor)

	return categ


def btnCustomer(cus_id):
	btns_cus = types.InlineKeyboardMarkup(row_width = 2)
	edit_profil_cus = types.InlineKeyboardButton("Ред.профиль", callback_data = "edit_profil_cus")
	ban_cus = types.InlineKeyboardButton("Бан", callback_data = "ban_cus")
	unban_cus = types.InlineKeyboardButton("Разбан", callback_data = "unban_cus")
	ads_history = types.InlineKeyboardButton("История объявлений", switch_inline_query_current_chat = f"!ads_history {cus_id}")
	btns_cus.add(edit_profil_cus)
	btns_cus.add(ban_cus, unban_cus)
	btns_cus.add(ads_history)

	return btns_cus
	

def btnExecutor(ex_id):
	btns_ex = types.InlineKeyboardMarkup(row_width = 2)
	edit_profil_ex = types.InlineKeyboardButton("Ред.профиль", callback_data = f"edit_profil_ex")
	ban_ex = types.InlineKeyboardButton("Бан", callback_data = "ban_ex")
	unban_ex = types.InlineKeyboardButton("Разбан", callback_data = "unban_ex")
	work_history = types.InlineKeyboardButton("История работы", switch_inline_query_current_chat = f"!work_history {ex_id}")
	view_review = types.InlineKeyboardButton("Просмотреть отзывы", switch_inline_query_current_chat = f"!view_review {ex_id}")
	btns_ex.add(edit_profil_ex)
	btns_ex.add(ban_ex, unban_ex)
	btns_ex.add(work_history)
	btns_ex.add(view_review)

	return btns_ex


def admin_canc():
	btn_canc = types.ReplyKeyboardMarkup(resize_keyboard = True)
	canc = types.KeyboardButton("Отменa")# a
	btn_canc.add(canc)

	return btn_canc


def adminModeration():
	moder = types.InlineKeyboardMarkup(row_width = 1)
	announcement_requests = types.InlineKeyboardButton("Просмотреть объявления", callback_data = "announcement_requests")
	profile_claims = types.InlineKeyboardButton("Просмотреть профиля", callback_data = "profile_claims")
	complaints_applications = types.InlineKeyboardButton("Просмотреть жалобы", callback_data = "aComplaints_applications")
	moder.add(announcement_requests, profile_claims, complaints_applications)

	return moder

 
 

def bankProject():	
	bank = types.InlineKeyboardMarkup(row_width = 2)
	admin_output = types.InlineKeyboardButton("Вывести", callback_data = "admin_withdraw")
	refresh = types.InlineKeyboardButton("Обновить", callback_data = "refresh")
	ic_stock = types.InlineKeyboardButton("[iC] Запас", callback_data = "ic_stock")
	ic_one_time = types.InlineKeyboardButton("[iC] Разовой", callback_data = "ic_one_time")
	list_of_expenses = types.InlineKeyboardButton("Список расходов", callback_data = "list_of_expenses")
	list_of_reports = types.InlineKeyboardButton("Список отчетов", switch_inline_query_current_chat = "list_of_reports")
	bank.add(admin_output, refresh)
	bank.add(ic_stock, ic_one_time)
	bank.add(list_of_expenses)
	bank.add(list_of_reports)

	return bank


def requestOrderBtns(cus_id, order_id):
	btns_order = types.InlineKeyboardMarkup(row_width = 2)
	toBack = types.InlineKeyboardButton(text = "⬅️", callback_data = f'toBack {cus_id},{order_id}')
	toNext = types.InlineKeyboardButton(text = "➡️", callback_data = f'toNext {cus_id},{order_id}')

	toApprove = types.InlineKeyboardButton(text = "Одобрить", callback_data = f'toApprove {cus_id},{order_id}')
	toReject = types.InlineKeyboardButton(text = "Отклонить", callback_data = f'toReject {cus_id},{order_id}')
	toEdit = types.InlineKeyboardButton(text = "Ред.заказ", callback_data = f'toEdit {cus_id},{order_id}')
	btns_order.add(toBack, toNext, toApprove, toReject, toEdit)

	return btns_order


def settingsOrderBtns(cus_id, order_id):
	settings_order = types.InlineKeyboardMarkup(row_width = 2)
	toEdit = types.InlineKeyboardButton(text = "Ред.заказ", callback_data = f'toEdit {cus_id},{order_id}')
	finishEdit = types.InlineKeyboardButton(text = "Опубликовать", callback_data = f'finishEdit {cus_id},{order_id}')
	settings_order.add(toEdit, finishEdit)

	return settings_order


def requestProfilBtns(user_id, status, show_pagination = True):
	btns_profil = types.InlineKeyboardMarkup(row_width = 2)
	toBackProfil = types.InlineKeyboardButton(text = "⬅️", callback_data = f'pBack')
	toNextProfil = types.InlineKeyboardButton(text = "➡️", callback_data = f'pNext')

	toApproveProfil = types.InlineKeyboardButton(text = "Одобрить", callback_data = f'pApprove {user_id},{status}')
	toRejectProfil = types.InlineKeyboardButton(text = "Отклонить", callback_data = f'pReject {user_id},{status}')
	toEditProfil = types.InlineKeyboardButton(text = "Ред.профиль", callback_data = f'pEdit {user_id},{status}')
	
	if show_pagination:
		btns_profil.add(toBackProfil, toNextProfil, toApproveProfil, toRejectProfil, toEditProfil)
	else:
		btns_profil.add(toApproveProfil, toRejectProfil, toEditProfil)


	return btns_profil


def skipBtn():
	skip_btn = types.InlineKeyboardMarkup(row_width = 2)
	skip = types.InlineKeyboardButton(text = "Пропустить", callback_data = f'cSkip')
	skip_btn.add(skip)

	return skip_btn


def update(title):
	btn_update = types.InlineKeyboardMarkup(row_width = 2)
	update_expenses = types.InlineKeyboardButton(text = "Обновить", callback_data = f'update_expenses')
	update_stat = types.InlineKeyboardButton(text = "Обновить", callback_data = f'update_stat')

	if title == 'expenses':	
		btn_update.add(update_expenses)

	elif title == 'stat':
		btn_update.add(update_stat)

	return btn_update


def adminPrice(total_1, total_2, total_3):
	aPrices = types.InlineKeyboardMarkup()
	aPrice_1 = types.InlineKeyboardButton(text = '1️⃣', callback_data = f'aPrice {total_1}')
	aPrice_2 = types.InlineKeyboardButton(text = '2️⃣', callback_data = f'aPrice {total_2}')
	aPrice_3 = types.InlineKeyboardButton(text = '3️⃣', callback_data = f'aPrice {total_3}')
	aPrices.add(aPrice_1, aPrice_2, aPrice_3)

	return aPrices


def changeIcStock():
	change_btn = types.InlineKeyboardMarkup()
	change_stock = types.InlineKeyboardButton(text = 'Изменить', callback_data = f'change_stock')
	change_btn.add(change_stock)

	return change_btn


def icOneSets():
	ic_set = types.InlineKeyboardMarkup(row_width = 2)
	aPublish = types.InlineKeyboardButton(text = "Опубликовать", callback_data = f'aPublish')
	aCancel = types.InlineKeyboardButton(text = "Отменить", callback_data = f'aCancel')
	ic_set.add(aPublish, aCancel)

	return ic_set


def showReviewComplaintsBtns(ex_id, cus_id, order_id):
	srcb = types.InlineKeyboardMarkup(row_width = 2)
	cDelete = types.InlineKeyboardButton(text = "Удалить", callback_data = f'cDelete {ex_id},{cus_id},{order_id}')
	cReject = types.InlineKeyboardButton(text = "Отклонить", callback_data = f'cReject {ex_id},{cus_id},{order_id}')
	cEdit = types.InlineKeyboardButton(text = "Редактировать", callback_data = f'cEdit {ex_id},{cus_id},{order_id}')
	srcb.add(cDelete, cReject, cEdit)

	return srcb


def causeDelete():
	cd = types.InlineKeyboardMarkup(row_width = 2)
	cConfirm = types.InlineKeyboardButton(text = "Подтвердить", callback_data = f'cConfirm')
	cChange = types.InlineKeyboardButton(text = "Изменить", callback_data = f'cChange')
	cd.add(cConfirm, cChange)

	return cd


def showUserComplaintsBtns(ex_id, rowid):
	sucb = types.InlineKeyboardMarkup(row_width = 2)
	cBan = types.InlineKeyboardButton(text = "Забанить", callback_data = f'cBan {ex_id}')
	cReject = types.InlineKeyboardButton(text = "Отклонить", callback_data = f'cReject {ex_id},{rowid}')
	cEdit = types.InlineKeyboardButton(text = "Редактировать", callback_data = f'edit_profil_ex {ex_id}')
	sucb.add(cBan, cReject, cEdit)

	return sucb


def adminWithdrawBtns():
	withdraw_btns = types.InlineKeyboardMarkup(row_width = 2)
	card = types.InlineKeyboardButton(text = "Карта", callback_data = 'admin_card')
	purse = types.InlineKeyboardButton(text = "Кошелёк", callback_data = 'admin_purse')
	withdraw_btns.add(card, purse)

	return withdraw_btns


def adminWithdrawCheckBtns():
	withdraw_check_btns = types.InlineKeyboardMarkup(row_width = 2)
	confirm = types.InlineKeyboardButton(text = "Подтвердить", callback_data = 'admin_confirm')
	change_withdraw = types.InlineKeyboardButton(text = "Изменить", callback_data = 'admin_change_withdraw')
	withdraw_check_btns.add(confirm, change_withdraw)

	return withdraw_check_btns