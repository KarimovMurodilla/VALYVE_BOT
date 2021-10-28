import random




def process_captcha():
	data = {}
	cap1 = ['AgACAgIAAxkBAANCYW3QlRuTAc7HbVZvwSBuoAy53skAAiWzMRv-OaFIAsBKg2PydDkBAAMCAANtAAMhBA', 'Z8hC2']
	cap2 = ['AgACAgIAAxkBAANDYW3Qr6eSnRNNyxapa9DankSwOgEAAiazMRv-OaFIZSQ03gIZhiwBAAMCAANtAAMhBA', 'uguh']
	cap4 = ['AgACAgIAAxkBAANEYW3QyMg_rfiCJT_ED9uW73nQXrIAAiizMRv-OaFIehz0RUuyJwUBAAMCAANtAAMhBA', 'vdma']
	cap5 = ['AgACAgIAAxkBAANFYW3Q2mS5hJwMiavfvGJsJciGdx0AAiGzMRv-OaFICfi96ti3z6QBAAMCAANtAAMhBA', 'cDaBaW']
	
	c = cap1, cap2, cap4, cap5
	cap = random.choice(c)

	return cap

# t = process_captcha(1234)
# print(t[0])