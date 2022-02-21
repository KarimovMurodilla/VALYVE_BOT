from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from .. import common_captcha, file_ids, buttons, config


bot = Bot(token=config.TOKEN, parse_mode = 'html')


class Start(StatesGroup):
    step1 = State()


async def captchaReg(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		captcha_key = data['captcha_key']

		if message.text.lower() == captcha_key.lower():
			await bot.send_message(message.chat.id, "Здравствуйте, как Вы хотите авторизоваться?", reply_markup = buttons.btn2)
			await state.finish()

		else:
			await bot.send_message(
				chat_id = message.chat.id, 
				text = "⚠️ <b>Ошибка:</b>\n\n"

						"Капча введена не верно! Повторите попытку или обновите капчу командой /start")


def register_start_reg_handlers(dp: Dispatcher):
    # dp.register_callback_query_handler(process_callback_ok, lambda c: c.data == 'agree',  state = '*')	
    dp.register_message_handler(captchaReg, state = Start.step1)
