import random
from captcha.image import ImageCaptcha
from app import config


image = ImageCaptcha(width=280, height=90)
symbols = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

def process_captcha():
	random.shuffle(symbols)
	captcha_text = ''.join(symbols)[:6]

	data = image.generate(captcha_text)
	img = image.write(captcha_text, f'{config.CAPTCHA_PHOTO_PATH}{captcha_text}.png')

	return captcha_text