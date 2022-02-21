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
	# selectOrder = connection.selectAllOrders()
	cus_lat = message.location.latitude
	cus_long = message.location.longitude

	print(connection.selectAllOrders(cus_lat, cus_long))

	# for n in range(len(selectOrder)):
	# 	print(f"{selectOrder[n][1]}-{getLocationInfo.calculate_km(cus_lat, cus_long, selectOrder[n][8], selectOrder[n][9])}")


def register_filter_handlers(dp: Dispatcher):
    dp.register_message_handler(filter_user, content_types = types.ContentTypes.ANY)
    dp.register_message_handler(getFileId, content_types = ['location', 'venue'], state = '*')