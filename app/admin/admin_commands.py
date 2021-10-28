from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from app.admin import admin_buttons
from .. import config

bot = Bot(token=config.TOKEN, parse_mode = 'html')


async def cmd_admin(message: types.Message, state: FSMContext):
    await bot.send_message(message.chat.id, "Добро пожаловать на админ панель !", reply_markup = admin_buttons.adminPanel())



def register_handlers_admin_commands(dp: Dispatcher):
    dp.register_message_handler(cmd_admin, chat_id = config.ADMINS, commands = 'admin', state="*")
