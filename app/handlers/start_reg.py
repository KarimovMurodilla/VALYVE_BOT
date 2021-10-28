from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from .. import common_captcha, file_ids, buttons, config


bot = Bot(token=config.TOKEN, parse_mode = 'html')


# cap = common_captcha.process_captcha()


class Start(StatesGroup):
    step1 = State()


async def process_callback_ok(c: types.CallbackQuery, state: FSMContext):
	cap = common_captcha.process_captcha()
	async with state.proxy() as data:
		data['captcha_key'] = cap[1]
	
	await bot.edit_message_media(media = types.InputMedia(
								type = 'photo', 
								media = cap[0], 
								caption = "⚠️ <b>Чтоб продолжить использование бота, необходимо решить капчу.</b>\n\nОтправьте мне текст, что изображен на картинке."),
								chat_id = c.message.chat.id,
								message_id = c.message.message_id
								)
	await Start.step1.set()



async def captchaReg(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		captcha_key = data['captcha_key']

		if message.text.lower() == captcha_key.lower():
			await bot.send_message(message.chat.id, "Здравствуйте, как Вы хотите авторизоваться?", reply_markup = buttons.btn2)
			await state.finish()

		else:
			await bot.send_message(message.chat.id, "Некорректно! Пожалуйста повторите попытку.")


def register_start_reg_handlers(dp: Dispatcher):
    dp.register_message_handler(captchaReg, state = Start.step1)
    dp.register_callback_query_handler(process_callback_ok, lambda c: c.data == 'agree',  state = '*')