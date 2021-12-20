import datetime
import sqlite3 as sql
from app import config


with sql.connect(config.DB_PATH, check_same_thread=False) as con:
	cur = con.cursor()


with sql.connect(config.DB_ADMIN_PATH, check_same_thread=False) as con2:
	cur2 = con2.cursor()




today = datetime.datetime.today()
week = today - datetime.timedelta(days=7)

today = datetime.datetime.today().strftime('%d.%m.%Y')
week = week.strftime('%d.%m.%Y')


# -----------------FOR USERS-----------------
def allUsers():
	all_users = cur.execute("SELECT count(*) FROM users").fetchall()
	return all_users[0][0]


def orderByWeek():
	date1 = cur.execute(f"SELECT count(*) FROM users WHERE date_start BETWEEN \'{week}\' AND \'{today}\'").fetchall()
	return date1[0][0]


# -----------------FOR ORDERS------------------
def allOrders():
	all_users = cur.execute("SELECT count(*) FROM orders").fetchall()
	return all_users[0][0]


def ordersByWeek():
	date1 = cur.execute(F"SELECT count(*) FROM orders WHERE date_order BETWEEN \'{week}\' AND \'{today}\'").fetchall()
	return date1[0][0]


def selectOrdersWhereInModeration():
	sowim = cur.execute("SELECT * FROM orders WHERE order_status = 'На модерации' OR order_status = 'Пересмотр'").fetchall()
	return sowim

# ----------ADMIN_TABLE--------
def changeAdminTable(status, name):
	cur2.execute("UPDATE admin_table SET status = ? WHERE name = ?", (status, name,))
	con2.commit()

def selectFromAdminTable():
	sowim = cur2.execute("SELECT * FROM admin_table").fetchall()
	return sowim


def selectUserFromRequestProfils(user_id, status):
	soufat = cur2.execute("SELECT * FROM request_profils WHERE user_id = ? AND status = ?", (user_id, status,)).fetchall()
	return soufat


def addRequestProfil(user_id, status, user_name = None, user_pic = None, user_contact = None, user_date_of_birth = None, user_skill = None):
	if not selectUserFromRequestProfils(user_id, status):
		if status == 'customer':
			cur2.execute("INSERT INTO request_profils (user_id, status, user_name, user_pic, user_contact)VALUES(?,?,?,?,?)", (user_id, status, user_name, user_pic, user_contact,))
			con2.commit()
		elif status == 'executor':
			cur2.execute("INSERT INTO request_profils (user_id, status, user_name, user_pic, user_contact, user_date_of_birth, user_skill)VALUES(?,?,?,?,?,?,?)", (user_id, status, user_name, user_pic, user_contact, user_date_of_birth, user_skill,))
			con2.commit()	

	else:
		if status == 'customer':
			cur2.execute("UPDATE request_profils SET user_name = ?, user_pic = ?, user_contact = ? WHERE user_id = ? AND status = ?", (user_name, user_pic, user_contact, user_id, status,))
			con2.commit()
		elif status == 'executor':
			cur2.execute("UPDATE request_profils SET user_name = ?, user_pic = ?, user_contact = ?, user_date_of_birth = ?, user_skill = ? WHERE user_id = ? AND status = ?", (user_name, user_pic, user_contact, user_date_of_birth, user_skill, user_id, status,))
			con2.commit()


def selectRequestsProfil():
	srp = cur2.execute("SELECT * FROM request_profils").fetchall()
	return srp


def deleteRequestsProfil(user_id, status):
	cur2.execute("DELETE FROM request_profils WHERE user_id = ? AND status = ?", (user_id, status,))
	con2.commit()


def addComplaint(ex_id, cus_id, order_id, cause):
	cur2.execute("INSERT INTO complaints_for_review (ex_id, cus_id, order_id, cause)VALUES(?,?,?,?)", (ex_id, cus_id, order_id, cause,))
	con2.commit()


# -----COMPLAINTS-----
def addUserComplaint(user_id, complaint):
	cur2.execute("INSERT INTO complaints_for_user (user_id, cause)VALUES(?,?)", (user_id, complaint,))
	con2.commit()


# ----BANK CONTROL TABLE----
def selectIcOneTime():
	siot = cur2.execute("SELECT * FROM bank_control_table WHERE ic_one_time").fetchall()
	return siot


def updateIcOneTime(ic_one_time, rowid):
	cur2.execute("UPDATE bank_control_table SET ic_one_time = ? WHERE rowid = ?", (ic_one_time, rowid,))
	con2.commit()


# ----COMPLAINT FOR REVIEW----
def getComplaintsFromReview():
	result = cur2.execute("SELECT * FROM complaints_for_review").fetchall()
	return result


def deleteComplaintForReview(ex_id, cus_id, order_id):
	cur2.execute("DELETE FROM complaints_for_review WHERE ex_id = ? AND cus_id = ? AND order_id = ?", (ex_id, cus_id, order_id,))
	con2.commit()


# ----COMPLAINT FOR REVIEW----
def getComplaintsFromUser():
	result = cur2.execute("SELECT * FROM complaints_for_user").fetchall()
	return result