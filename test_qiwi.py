import pyqiwi
import time
import requests

wallet = pyqiwi.Wallet(token = 'e41adf3cef2e5f53abf254ab982463da', number = '89157742502')

print(wallet.balance())
commission = wallet.commission(pid=99, recipient='5469100014949433', amount=1)
print(commission.qw_commission.amount)

# payment = wallet.send(pid=99, recipient='5469100014949433', amount=1.11, comment='Привет!')
# example = 'Payment is {0}\nRecipient: {1}\nPayment Sum: {2}'.format(
#           payment.transaction['state']['code'], payment.fields['account'], payment.sum)
# print(example)

# def send_to_card(payment_data):
#     # payment_data - dictionary with all payment data
#     s = requests.Session()
#     s.headers['Accept'] = 'application/json'
#     s.headers['Content-Type'] = 'application/json'
#     s.headers['authorization'] = 'Bearer ' + wallet.token
#     postjson = {"id": "", "sum": {"amount": "", "currency": "643"},
#                 "paymentMethod": {"type": "Account", "accountId": "643"}, "fields": {"account": ""}}
#     postjson['id'] = str(int(time.time() * 1000))
#     postjson['sum']['amount'] = payment_data.get('sum')
#     postjson['fields']['account'] = payment_data.get('to_card')
#     prv_id = payment_data.get('prv_id')

#     res = s.post('https://edge.qiwi.com/sinap/api/v2/terms/' + prv_id + '/payments', json=postjson)
#     return res.json()


# def get_card_system(card_number):
#     s = requests.Session()
#     res = s.post('https://qiwi.com/card/detect.action', data={'cardNumber': card_number})
#     return res.json()['message']


# def pay_to_user():
#     prv_id = get_card_system('5469100014949433')
#     payment_data = {'sum': '1.00',
#                     'to_card': '5469100014949433',
#                     'prv_id': prv_id}
#     answer_from_qiwi = send_to_card(payment_data)
#     try:
#         status_transaction = answer_from_qiwi["transaction"]["state"]
#     except:
#         print(f"Ошибка: {answer_from_qiwi['message']}")

#         return

#     if status_transaction['code'] == "Accepted":
#     	return "Done"

# pay_to_user()