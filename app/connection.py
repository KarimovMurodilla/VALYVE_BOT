import datetime
import sqlite3 as sql
from app import getLocationInfo, config



with sql.connect(config.DB_PATH, check_same_thread=False) as con:
	cur = con.cursor()


# ---For Users---
def createUserStatus():
	cur.execute("""CREATE TABLE IF NOT EXISTS users(
				user_id INT,
				user_name TEXT,
				user_username TEXT,
				user_status TEXT,
				user_referral INT DEFAULT 0,
				active_referrals INT DEFAULT 0,
				user_balance BOOLEAN DEFAULT 0,
				user_coupon INT DEFAULT 0,
				from_id INT,
				pagination INT,
				date_start timestamp
				)""")
	con.commit()


# ---Customers---
def createCusTable():
	cur.execute("""CREATE TABLE IF NOT EXISTS customers(
				cus_id INT,
				cus_name TEXT,
				cus_pic TEXT,
				cus_contact INT,
				date_registration TIMESTAMP,
				cus_status TEXT)""")
	con.commit()


#-----For Orders-----
def createTableOrders():
	cur.execute("""CREATE TABLE IF NOT EXISTS orders(
				cus_id INT,
				cus_name TEXT,
				cus_adress TEXT,
				cus_work_graphic TEXT,
				cus_work_day TEXT,
				cus_bid TEXT,
				cus_position TEXT,
				cus_comment TEXT,
				cus_lat INT,
				cus_long INT, 
				date_order TIMESTAMP,
				order_status TEXT,
				order_id INT, 
				deletion_date TIMESTAMP,
				requirements TEXT,
				respons TEXT
				)""")
	con.commit()


# ---For Executors---
def createExecutorTable():
	cur.execute("""CREATE TABLE IF NOT EXISTS executors(
				ex_id INT,
				ex_name TEXT,
				date_of_birth TEXT,
				ex_pic TEXT,
				ex_contact INT,
				ex_skill TEXT,
				ex_rate INT,
				date_registration TIMESTAMP,
				ex_status TEXT
				)""")
	con.commit()


# ---For Responses---
def createResponsesTable():
	cur.execute("""CREATE TABLE IF NOT EXISTS responses(
				cus_id INT,
				order_id TEXT,
				requests INT,
				my_performers INT
				)""")
	con.commit()



# ---For Rating---
def createRatingTable():
	cur.execute("""CREATE TABLE IF NOT EXISTS ratings(
				ex_id INT,
				review TEXT,
				cus_id INT,
				order_id INT,
				date_of_completion TIMESTAMP
				)""")
	con.commit()


def createPaymentTable():
	cur.execute("""CREATE TABLE IF NOT EXISTS payments(
				user_id INT,
				title TEXT,
				user_payment INT DEFAULT 0,
				bot_payment INT DEFAULT 0,
				date_of_payment TIMESTAMP
				)""")
	con.commit()



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
	cur.execute("UPDATE users SET from_id = 'actived' WHERE user_id = ?", (user_id,))
	con.commit()


def getRefActives(from_id: str):
	ref_actives = cur.execute("SELECT user_id FROM users WHERE from_id = ?", (from_id,)).fetchall()
	return ref_actives

# -------All bot users------
def checkUserStatus(user_id: str):
	user_status = cur.execute("SELECT user_status FROM users WHERE user_id = ?", (user_id,)).fetchone()
	return user_status


def RegUser(user_id: str, user_name: str, user_username, user_status: str, user_referral = None, active_referrals = None, user_balance = None, from_id = None, date_start = None):
	cur.execute("INSERT INTO users (user_id, user_name, user_username, user_status, user_referral, active_referrals, user_balance, from_id, date_start)VALUES(?,?,?,?,?,?,?,?,?)", (user_id, user_name, user_username, user_status, user_referral, active_referrals, user_balance, from_id, date_start,))
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


def addBalance(user_id: str, user_balance: int):
	cur.execute(f"UPDATE users SET user_balance = user_balance+\'{user_balance}\' WHERE user_id = ?", (user_id,))
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
def checkNewOrder(cus_id: str):
	checkOrder = cur.execute("SELECT * FROM orders WHERE cus_id = ?", (cus_id,)).fetchone()
	return checkOrder


def createNewOrder(cus_id: str, cus_name: str, cus_adress: str, cus_work_graphic: str, cus_work_day: str, cus_bid: str, cus_position: str, cus_comment: str, cus_lat: str, cus_long: str, date_order: str, order_status: str, order_id: int, deletion_date: str, requirements: str, respons: str):
	cur.execute("INSERT INTO orders (cus_id, cus_name, cus_adress, cus_work_graphic, cus_work_day, cus_bid, cus_position, cus_comment, cus_lat, cus_long, date_order, order_status, order_id, deletion_date, requirements, respons)VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (cus_id, cus_name, cus_adress, cus_work_graphic, cus_work_day, cus_bid, cus_position, cus_comment, cus_lat, cus_long, date_order, order_status, order_id, deletion_date, requirements, respons,))
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
	Reqs = [x[0] for x in selectReqs]
	return Reqs


def selectRequestsWhereOrderId(cus_id: int, order_id: int):
	srwoi = cur.execute("SELECT requests FROM responses WHERE cus_id = ? AND order_id = ?", (cus_id, order_id,)).fetchall()
	return srwoi


def selectMyPerWhereOrderId(cus_id: int, order_id: int):
	my_perfs = cur.execute("SELECT my_performers FROM responses WHERE cus_id = ? AND order_id = ?", (cus_id, order_id,)).fetchall()
	return my_perfs


def UpdateRequests(ex_id: str, cus_id: int, order_id: int):
	cur.execute("UPDATE responses SET requests = ? WHERE cus_id = ? AND order_id = ?", (ex_id, cus_id, order_id,))
	con.commit()


def replaceReqToPer(cus_id: int, requests: int, order_id: int):
	cur.execute("UPDATE responses SET requests = Null, my_performers = ? WHERE cus_id = ? AND requests = ? AND order_id = ?", (requests, cus_id, requests, order_id,))
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

#-----RATING-----
def regExToRatings(ex_id: str, cus_id: int, order_id: int):
	cur.execute("INSERT INTO ratings (ex_id, cus_id, order_id)VALUES(?,?,?)", (ex_id, cus_id, order_id,))
	con.commit()

def UpdateRating(ex_id: str, review: str, cus_id: str, order_id: str, date_of_completion: str):
	cur.execute("UPDATE ratings SET review = ?, date_of_completion = ? WHERE ex_id = ? AND cus_id = ? AND order_id = ?", (review, date_of_completion, ex_id, cus_id, order_id,))
	con.commit()

def selectReviews(ex_id: str):
	reviews = cur.execute("SELECT * FROM ratings WHERE ex_id = ?", (ex_id,)).fetchall()
	return reviews


#-----PAYMENTS-----
def addPayment(user_id: str, title: str, user_payment: int, date_of_payment: str):
	cur.execute("INSERT INTO payments (user_id, title, user_payment, date_of_payment)VALUES(?,?,?,?)", (user_id, title, user_payment, date_of_payment,))
	con.commit()


def addBotPayment(user_id: str, title: str, bot_payment: int, date_of_payment: str):
	cur.execute("INSERT INTO payments (user_id, title, bot_payment, date_of_payment)VALUES(?,?,?,?)", (user_id, title, bot_payment, date_of_payment,))
	con.commit()



createUserStatus()
createCusTable()
createTableOrders()
createExecutorTable()
createResponsesTable()
createRatingTable()
createPaymentTable()


# cus_id = 1433345744
# order_id = 0

# if 875587704 not in selectRequests(order_id, cus_id) and selectRequests(order_id, cus_id)[0] is None or selectRequests(order_id, cus_id)[0] == '':
# 	if selectMyPerInOrderId(cus_id, order_id)[0] is None or selectMyPerInOrderId(cus_id, order_id)[0] == '':
# 		print("BOsh")
# 	else:
# 		print("BOsh emas")

# print(selectMyPerInOrderId(cus_id, order_id)[0])

# from admin import admin_connection

# user_id = 875587704
# status = 'executor'
# profil = admin_connection.selectUserFromRequestProfils(user_id, status)
# # print(profil)
# print(profil[0][2], profil[0][5], profil[0][3], profil[0][4], profil[0][6])