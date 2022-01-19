import datetime
import sqlite3 as sql
from app import getLocationInfo, config



with sql.connect(config.DB_PATH, check_same_thread=False) as con:
	cur = con.cursor()



def checkReferral(user_id: str):
	user_ref = cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
	return user_ref


def get_id(user_id: str):
	idUser = cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
	return idUser


def addReferral(user_id: str):
	cur.execute("UPDATE users SET user_referral = user_referral+1 WHERE user_id = ?", (user_id,))
	con.commit()


def addActiveReferral(user_id: str):
	cur.execute("UPDATE users SET user_referral = user_referral-1, active_referrals = active_referrals+1, user_balance = user_balance+0.5 WHERE user_id = ?", (user_id,))
	con.commit()


def setActiveUser(user_id: str):
	cur.execute("UPDATE users SET refferal_status = 'actived' WHERE user_id = ?", (user_id,))
	con.commit()


def getRefActives(refferal_status: str):
	ref_actives = cur.execute("SELECT user_id FROM users WHERE refferal_status = ?", (refferal_status,)).fetchall()
	return ref_actives


def selectStatRefferal(from_id, status, interval, interval2):
	response = cur.execute("SELECT count(user_id) FROM users WHERE from_id = ? AND refferal_status = ? AND date_start BETWEEN ? AND ?", (from_id, status, interval, interval2,)).fetchall()
	return response[0]


# -------All bot users------
def checkUserStatus(user_id: str):
	user_status = cur.execute("SELECT user_status FROM users WHERE user_id = ?", (user_id,)).fetchone()
	return user_status


def RegUser(user_id: str, user_name: str, user_username, user_status: str, user_referral = None, active_referrals = None, user_balance = None, refferal_status = None, date_start = None):
	cur.execute("INSERT INTO users (user_id, user_name, user_username, user_status, user_referral, active_referrals, user_balance, refferal_status, date_start, from_id)VALUES(?,?,?,?,?,?,?,?,?,?)", 
		(user_id, user_name, user_username, user_status, user_referral, active_referrals, user_balance, refferal_status, date_start, refferal_status,))
	con.commit()


def UpdateUserStatus(user_status: str, user_id: str):
	cur.execute("UPDATE users SET user_status = ? WHERE user_id = ?", (user_status, user_id,))
	con.commit()


def selectPag(user_id: str):
	pag = cur.execute("SELECT pagination FROM users WHERE user_id = ?", (user_id,)).fetchone()
	return pag[0]


def nullPagination(user_id: str):
	cur.execute("UPDATE users SET pagination = 0 WHERE user_id = ?", (user_id,))
	con.commit()


def nextPagination(user_id: str):
	cur.execute("UPDATE users SET pagination = pagination+1 WHERE user_id = ?", (user_id,))
	con.commit()


def backPagination(user_id: str):
	cur.execute("UPDATE users SET pagination = pagination-1 WHERE user_id = ?", (user_id,))
	con.commit()


def updateBalance(user_id: str, new_balance: int, status: str):
	if status == '+':
		cur.execute(f"UPDATE users SET user_balance = user_balance+\'{new_balance}\' WHERE user_id = ?", (user_id,))
		con.commit()

	else:
		cur.execute(f"UPDATE users SET user_balance = user_balance-\'{new_balance}\' WHERE user_id = ?", (user_id,))
		con.commit()



# -----------------FOR CUSTOMERS-----------------
def checkRegStatus(cus_id: str):
	checkReg = cur.execute("SELECT * FROM customers WHERE cus_id = ?", (cus_id,)).fetchone()
	return checkReg


# create customer profil
def RegData(cus_id: str, cus_name: str, cus_pic: str, cus_contact: str, date_registration: str):
	cur.execute("INSERT INTO customers (cus_id, cus_name, cus_pic, cus_contact, date_registration)VALUES(?,?,?,?,?)", (cus_id, cus_name, cus_pic, cus_contact, date_registration,))
	con.commit()


# get customer profil
def selectAll(cus_id: str):
	select = cur.execute("SELECT cus_name, cus_pic, cus_contact, cus_status FROM customers WHERE cus_id = ?", (cus_id,)).fetchone()
	return select


# update customer profil
def UpdateData(cus_id: str, cus_name: str, cus_pic: str, cus_contact: str, date_registration = None):
	cur.execute("UPDATE customers SET cus_name = ?, cus_pic = ?, cus_contact = ?, date_registration = ? WHERE cus_id = ?", (cus_name, cus_pic, cus_contact, date_registration, cus_id,))
	con.commit()


# get customer name
def getCustomerName(cus_id: str): 
	customer_name = cur.execute("SELECT cus_name FROM customers WHERE cus_id = ?", (cus_id,)).fetchone()
	return customer_name


def UpdateCusStatus(cus_id: str, cus_status: str):
	cur.execute("UPDATE customers SET cus_status = ? WHERE cus_id = ?", (cus_status, cus_id,))
	con.commit()


# -----------------FOR ORDERS-----------------
def createNewOrder(cus_id: str, cus_name: str, cus_adress: str, cus_work_graphic: str, cus_work_day: str, 
	cus_bid: str, cus_position: str, cus_comment: str, cus_lat: str, cus_long: str, date_order: str, 
	order_status: str, order_id: int, deletion_date: str, requirements: str, respons: str, actual_days: str, payment_for_waiting: str):

	cur.execute("""INSERT INTO orders (cus_id, cus_name, cus_adress, cus_work_graphic, cus_work_day, cus_bid, cus_position, 
				cus_comment, cus_lat, cus_long, date_order, order_status, order_id, deletion_date, requirements, respons, actual_days, payment_for_waiting)
					VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (cus_id, cus_name, cus_adress, cus_work_graphic, 
						cus_work_day, cus_bid, cus_position, cus_comment, cus_lat, cus_long, date_order, order_status, 
						order_id, deletion_date, requirements, respons, actual_days, payment_for_waiting,))
	con.commit()


def selectOrders(cus_id: str):
	selectOrder = cur.execute("SELECT * FROM orders WHERE cus_id = ?", (cus_id,)).fetchall()
	return selectOrder


def selectAllOrders(cus_lat, cus_long):
	selectOrder = cur.execute(f"SELECT * FROM orders WHERE order_status = 'Опубликован' ORDER BY cus_lat>=\'{cus_lat}\' AND cus_long>=\'{cus_long}\' DESC").fetchall()
	s = [[x for x in selectOrder[n] if int(getLocationInfo.calculate_km(cus_lat, cus_long, selectOrder[n][8], selectOrder[n][9])) < 100] for n in range(len(selectOrder))]
	for i in range(len(s)-1):
		if s[i] == []:
			s.pop(i)
		else:
			continue

	return s

def selectOrderWhereCusId(cus_id: int, order_id: int):
	sowci = cur.execute("SELECT * FROM orders WHERE cus_id = ? AND order_id = ?", (cus_id, order_id,)).fetchone()
	return sowci


def checkDeletionDate():
	today = datetime.datetime.today().strftime('%Y-%m-%d')
	cur.execute("UPDATE orders SET order_status = 'Завершен' WHERE deletion_date=?", (today,)).fetchall()
	con.commit()


def UpdateOrder(cus_id: str, order_id: str, cus_name: str, cus_adress: str, cus_work_graphic: str, cus_work_day: str, cus_bid: str, cus_position: str, cus_comment: str, cus_lat: str, cus_long: str, requirements: str, respons: str):
	cur.execute("UPDATE orders SET cus_name = ?, cus_adress = ?, cus_work_graphic = ?, cus_work_day = ?, cus_bid = ?, cus_position = ?, cus_comment = ?, cus_lat = ?, cus_long = ?, requirements = ?, respons = ? WHERE cus_id = ? AND order_id = ?", (cus_name, cus_adress, cus_work_graphic, cus_work_day, cus_bid, cus_position, cus_comment, cus_lat, cus_long, requirements, respons, cus_id, order_id,))
	con.commit()


def UpdateOrderStatus(cus_id: str, order_id: int, order_status: str, deletion_date = None):
	cur.execute("UPDATE orders SET order_status = ?, deletion_date = ? WHERE cus_id = ? AND order_id = ?", (order_status, deletion_date, cus_id, order_id,))
	con.commit()


def orderMiniUpdate(cus_id, order_id, comment, date_order, deletion_date, actual_days):
	cur.execute("UPDATE orders SET cus_comment = ?, date_order = ?, deletion_date = ?, order_status = 'Пересмотр', actual_days = ? WHERE cus_id = ? AND order_id = ?", (comment, date_order, deletion_date, actual_days, cus_id, order_id,))
	con.commit()


def selectWherePublished(cus_id):
	swp = cur.execute("SELECT * FROM orders WHERE cus_id = ? AND order_status = ?", (cus_id, 'Опубликован',)).fetchall()
	return swp


# -----------------FOR EXECUTORS-----------------
def checkExecutor(ex_id: str):
	check_ex = cur.execute("SELECT * FROM executors WHERE ex_id = ?", (ex_id,)).fetchone()
	return check_ex


# create executor profil
def regExecutor(ex_id: str, ex_name: str, date_of_birth: str, ex_pic: str, ex_contact: str, ex_skill: str, ex_rate: int, date_registration: str, ex_status: str):
	cur.execute("INSERT INTO executors (ex_id, ex_name, date_of_birth, ex_pic, ex_contact, ex_skill, ex_rate, date_registration, ex_status)VALUES(?,?,?,?,?,?,?,?,?)", (ex_id, ex_name, date_of_birth, ex_pic, ex_contact, ex_skill, ex_rate, date_registration, ex_status,))
	con.commit()


# get executor profil
def getExecutorProfil(ex_id: str):
	get_profil = cur.execute("SELECT * FROM executors WHERE ex_id = ?", (ex_id,)).fetchone()
	return get_profil


# update executor profil
def UpdateExecutorProfil(ex_id: str, ex_name: str, date_of_birth: str, ex_pic: str, ex_contact: str, ex_skill: str):
	cur.execute("UPDATE executors SET ex_name = ?, date_of_birth = ?, ex_pic = ?, ex_contact = ?, ex_skill = ? WHERE ex_id = ?", (ex_name, date_of_birth, ex_pic, ex_contact, ex_skill, ex_id,))
	con.commit()


def UpdateExStatus(ex_id: str, ex_status: int):
	cur.execute("UPDATE executors SET ex_status = ? WHERE ex_id = ?", (ex_status, ex_id,))
	con.commit()


def UpdateRate(ex_rate: int, ex_id: str):
	cur.execute("UPDATE executors SET ex_rate = ? WHERE ex_id = ?", (ex_rate, ex_id,))
	con.commit()



# ---------FOR RESPONSES---------
def regResponses(cus_id: int, order_id: int, requests: int, my_performes: int):
	cur.execute("INSERT INTO responses (cus_id, order_id, requests)VALUES(?,?,?)", (cus_id, order_id, requests,))
	con.commit()


def selectAllFromCusOr(cus_id: int, order_id: int):
	selectOrder = cur.execute("SELECT * FROM responses WHERE cus_id = ? AND order_id = ?", (cus_id, order_id,)).fetchone()
	return selectOrder


def selectMyPerInOrderId(cus_id: int, order_id: int):
	smpwoi = cur.execute("SELECT my_performers FROM responses WHERE cus_id = ? AND order_id = ?", (cus_id, order_id,)).fetchall()
	my_per = [x[0] for x in smpwoi]
	return my_per


def selectRequests(order_id: int, cus_id: int):
	selectReqs = cur.execute("SELECT requests FROM responses WHERE order_id = ? AND cus_id = ?", (order_id, cus_id,)).fetchall()
	reqs = [x[0] for x in selectReqs]
	return reqs


def selectRequestsWhereOrderId(cus_id: int, order_id: int):
	srwoi = cur.execute("SELECT requests FROM responses WHERE cus_id = ? AND order_id = ?", (cus_id, order_id,)).fetchall()
	return srwoi


def selectMyPerWhereOrderId(cus_id: int, order_id: int):
	my_perfs = cur.execute("SELECT my_performers FROM responses WHERE cus_id = ? AND order_id = ?", (cus_id, order_id,)).fetchone()
	return my_perfs


def extract_3_hour(pd: list):
	now = datetime.datetime.now()
	pending_date = datetime.datetime(pd[0], pd[1], pd[2], pd[3], pd[4])
	delta = now-pending_date

	hours = delta.total_seconds() // 3600

	return hours


def selectPendingsWhereOrderId(cus_id: int, order_id: int):
	spwoi = selectAllFromCusOr(cus_id, order_id)
	
	result = [x for x in spwoi if extract_3_hour([int(i) for i in spwoi[4].split(',')]) < 3]
	return result


def getMyConsiderations(ex_id):
	my_cons = cur.execute("SELECT * FROM responses WHERE my_performers = ?", (ex_id,)).fetchall()

	result = [[x for x in my_cons[k] if extract_3_hour([int(i) for i in my_cons[k][4].split(',')]) < 3] 
		for k in range(len(my_cons))]

	return result


def UpdateRequests(ex_id: str, cus_id: int, order_id: int):
	cur.execute("UPDATE responses SET requests = ? WHERE cus_id = ? AND order_id = ?", (ex_id, cus_id, order_id,))
	con.commit()


def replaceReqToPer(cus_id: int, requests: int, order_id: int):
	cur.execute("UPDATE responses SET requests = Null, my_performers = ?, date_pending = ? WHERE cus_id = ? AND requests = ? AND order_id = ?", 
		(requests, datetime.datetime.now().strftime("%#Y, %#m, %#d, %#H, %#M"), cus_id, requests, order_id,))
	con.commit()


def deleteRequests(requests: int, order_id: int):
	cur.execute("UPDATE responses SET requests = Null WHERE requests = ? AND order_id = ?", (requests, order_id,))
	con.commit()


def deleteMyPer(ex_id: int, cus_id: int, order_id: int):
	cur.execute("UPDATE responses SET my_performers = Null WHERE my_performers = ? AND cus_id = ? AND order_id = ?", (ex_id, cus_id, order_id,))
	con.commit()


def removeMyPer(ex_id: int, cus_id: int, order_id: int):
	cur.execute("DELETE FROM responses WHERE my_performers = ? AND cus_id = ? AND order_id = ?", (ex_id, cus_id, order_id,))
	con.commit()


def removeAll(cus_id: int, order_id: int):
	cur.execute("DELETE FROM responses WHERE cus_id = ? AND order_id = ?", (cus_id, order_id,))
	con.commit()


#-----RATINGS-----
def regExToRatings(ex_id: str, cus_id: int, order_id: int):
	cur.execute("INSERT INTO ratings (ex_id, cus_id, order_id, answer)VALUES(?,?,?,?)", (ex_id, cus_id, order_id, '',))
	con.commit()


def UpdateRating(ex_id: str, review: str, cus_id: str, order_id: str, date_of_completion: str):
	cur.execute("UPDATE ratings SET review = ?, date_of_completion = ? WHERE ex_id = ? AND cus_id = ? AND order_id = ?", (review, date_of_completion, ex_id, cus_id, order_id,))
	con.commit()


def UpdateAnswer(ex_id: str, cus_id: str, order_id: str, answer: str):
	cur.execute("UPDATE ratings SET answer = ? WHERE ex_id = ? AND cus_id = ? AND order_id = ?", (answer, ex_id, cus_id, order_id,))
	con.commit()


def selectReviews(ex_id: str):
	reviews = cur.execute("SELECT * FROM ratings WHERE ex_id = ?", (ex_id,)).fetchall()
	return reviews


def selectReview(ex_id: str, cus_id: str, order_id: str):
	review = cur.execute("SELECT * FROM ratings WHERE ex_id = ? AND cus_id = ? AND order_id = ?", (ex_id, cus_id, order_id,)).fetchone()
	return review


def deleteRating(ex_id, cus_id, order_id):
	cur.execute("DELETE FROM ratings WHERE ex_id = ? AND cus_id = ? AND order_id = ?", (ex_id, cus_id, order_id,))
	con.commit()


def UpdateReview(ex_id: str, cus_id: str, order_id: str, review: str):
	cur.execute("UPDATE ratings SET review = ? WHERE ex_id = ? AND cus_id = ? AND order_id = ?", (review, ex_id, cus_id, order_id,))
	con.commit()


#-----PAYMENTS-----
def addPayment(user_id: str, title: str, user_payment: int, date_of_payment: str, count = 0):
	cur.execute("INSERT INTO payments (user_id, title, counts, user_payment, date_of_payment)VALUES(?,?,?,?,?)", (user_id, title, count, user_payment, date_of_payment,))
	con.commit()


def addBotPayment(user_id: str, title: str, bot_payment: int, date_of_payment: str):
	cur.execute("INSERT INTO payments (user_id, title, bot_payment, date_of_payment)VALUES(?,?,?,?)", (user_id, title, bot_payment, date_of_payment,))
	con.commit()


def selectUserWherePaid(user_id, title):
	if title == 'to_order':
		response = cur.execute("SELECT * FROM payments WHERE user_id = ? AND title = ?", (user_id, title,)).fetchall()
		return response


def selectStatPayments(user_id, title, interval, interval2):
	if title == 'refill':
		response = cur.execute("SELECT user_payment FROM payments WHERE user_id = ? AND title = 'refill' AND date_of_payment BETWEEN ? AND ?", (user_id, interval, interval2,))
		return [x[0] for x in response]


	elif title == 'withdraw':
		response = cur.execute("SELECT bot_payment FROM payments WHERE user_id = ? AND title = 'withdraw' AND date_of_payment BETWEEN ? AND ?", (user_id, interval, interval2,))
		return [x[0] for x in response]


	elif title == 'coupon_count':
		response = cur.execute("SELECT counts FROM payments WHERE user_id = ? AND title = 'coupon' AND date_of_payment BETWEEN ? AND ?", (user_id, interval, interval2,))
		return [x[0] for x in response]


	elif title == 'coupon_payment':
		response = cur.execute("SELECT user_payment FROM payments WHERE user_id = ? AND title = 'coupon' AND date_of_payment BETWEEN ? AND ?", (user_id, interval, interval2,))
		return [x[0] for x in response]


def deletePayment(user_id, price):
	cur.execute("DELETE FROM payments WHERE user_id = ? AND user_payment = ?", (user_id, price,))
	con.commit()


# ----COUPONS----
def addCoupon(user_id, cpn):
	cur.execute(f"UPDATE users SET user_coupon = user_coupon+\'{cpn}\' WHERE user_id = ?", (user_id,))
	con.commit()


def getUserCpns(user_id):
	cpn = cur.execute("SELECT user_coupon FROM users WHERE user_id = ?", (user_id,)).fetchone()
	return cpn