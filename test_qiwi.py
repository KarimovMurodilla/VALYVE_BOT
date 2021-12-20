import pyqiwi
import time
import requests

# wallet = pyqiwi.Wallet(token = 'e41adf3cef2e5f53abf254ab982463da', number = '89157742502')


# payment = wallet.send(pid=99, recipient=recipient, amount=user_money, comment=comment)
# payment = wallet.send(pid=21013, recipient='5469 1000 1494 9433', amount=5, comment='Привет!')
# example = 'Payment is {0}\nRecipient: {1}\nPayment Sum: {2}'.format(
#           payment.transaction['state']['code'], payment.fields['account'], payment.sum)
# print(example)

# 16.68
# commission = wallet.commission(pid=21013, recipient='89157742502', amount=0.1)
# print(commission.qw_commission.amount)
# print(wallet.balance())

# def send_to_qiwi(to_qw, amount):
#     s = requests.Session()
#     s.headers = {'content-type': 'application/json',
#                  'authorization': 'Bearer ' + wallet.token,
#                  'User-Agent': 'Android v3.2.0 MKT',
#                  'Accept': 'application/json'}
#     postjson = {"sum": {"amount": "", "currency": ""},
#                 "paymentMethod": {"type": "Account", "accountId": "643"}, "comment": "'+comment+'",
#                 "fields": {"account": ""}, 'id': str(int(time.time() * 1000))}
#     postjson['sum']['amount'] = amount
#     postjson['sum']['currency'] = '643'
#     postjson['fields']['account'] = to_qw
#     res = s.post('https://edge.qiwi.com/sinap/api/v2/terms/99/payments', json=postjson)
#     return res.json()

# send_to_qiwi('5469 1000 1494 9433', 1)