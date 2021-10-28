from aiogram import types


def adminPanel():
	panel = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
	stat = types.KeyboardButton("📊 Статистика")
	bank = types.KeyboardButton("🏦 Банк")
	console = types.KeyboardButton("🎛 Консоль")
	moder = types.KeyboardButton("👨🏻‍💻 Модерация")
	panel.add(stat)
	panel.add(bank, console)
	panel.add(moder)

	return panel


def adminConsol(sensor, sensor2):
	consol = types.InlineKeyboardMarkup(row_width = 2)
	breaking = types.InlineKeyboardButton("Пробив", callback_data = "breaking")
	ban = types.InlineKeyboardButton("Бан", callback_data = "ban")
	unban = types.InlineKeyboardButton("Разбан", callback_data = "unban")
	payment = types.InlineKeyboardButton(f"Оплата {sensor}", callback_data = "payment")
	order_feed = types.InlineKeyboardButton(f"Лента заказов {sensor2}", callback_data = "order_feed")
	consol.add(breaking, ban, unban, payment, order_feed)

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
	edit_profil_ex = types.InlineKeyboardButton("Ред.профиль", callback_data = "edit_profil_ex")
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
	announcement_requests = types.InlineKeyboardButton("Заявки объявлений", callback_data = "announcement_requests")
	profile_claims = types.InlineKeyboardButton("Заявки профиля", callback_data = "profile_claims")
	complaints_applications = types.InlineKeyboardButton("Заявки жалоб", callback_data = "complaints_applications")
	moder.add(announcement_requests, profile_claims, complaints_applications)

	return moder


def bankProject():	
	bank = types.InlineKeyboardMarkup(row_width = 2)
	admin_output = types.InlineKeyboardButton("💸 Вывод", callback_data = "admin_output")
	ref_limit = types.InlineKeyboardButton("🧮 Реф.Лимит", callback_data = "ref_limit")
	list_of_reports = types.InlineKeyboardButton("📜 Список Отчетов", switch_inline_query_current_chat = "list_of_reports")
	bank.add(admin_output, ref_limit, list_of_reports)

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
	toEdit = types.InlineKeyboardButton(text = "Ред.профиль", callback_data = f'toEdit {cus_id},{order_id}')
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