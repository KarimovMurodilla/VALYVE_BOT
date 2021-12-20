from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from .. import connection, config, getLocationInfo


bot = Bot(token=config.TOKEN, parse_mode = 'html')


async def filter_user(message: types.Message):
	connection.checkDeletionDate()
	user_id = message.from_user.id
	
	if connection.checkReferral(user_id)[3] == 'Banned':
		await bot.send_message(message.chat.id, "Ваш профиль забанен!")


async def getFileId(message: types.Message):
	print(message.photo[-1].file_id)
	await bot.send_photo(message.chat.id, photo = message.photo[-1].file_id, caption = 'smth')


def register_filter_handlers(dp: Dispatcher):
    dp.register_message_handler(filter_user, content_types = types.ContentTypes.ANY)
    dp.register_message_handler(getFileId, content_types = ['document', 'photo'], state = '*')