import os
import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from app.handlers.start_reg import Start
from .. import connection, file_ids, buttons, config, common_captcha


today = datetime.datetime.today()


bot = Bot(token=config.TOKEN, parse_mode = 'html')


def extract_unique_code(text):
    # Extracts the unique_code from the sent /start command.
    return text.split()[1] if len(text.split()) > 1 else None


async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.chat.id

    unique_code = extract_unique_code(message.text)
    if unique_code:
        if not connection.get_id(user_id):
            await state.finish()
            connection.addReferral(unique_code)
            connection.RegUser(user_id, message.from_user.first_name, message.from_user.username, None, 0, 0, 0, unique_code, date_start = today)

        elif '_' in unique_code:
            ids = unique_code.split('_')
            cus_id = ids[0]
            order_id = ids[1]
            all_data = connection.selectOrderWhereCusId(cus_id, order_id)

            await bot.send_message(message.chat.id, f"<b>Статус заказа:</b> <code>{all_data[11]}</code>\n"
                                                    f"<b>Заказчик:</b> <code>{all_data[1]}</code>\n"
                                                    f"<b>Номер:</b> <code>+{connection.selectAll(cus_id)[2]}</code>\n"
                                                    f"<b>Адреc:</b> <code>{all_data[2]}</code>\n\n"
                                                    
                                                    f"<b>Должность:</b> <code>{all_data[6]}</code>\n"
                                                    f"{connection.checkOrderType(all_data[-2], all_data)}\n"
                                                    f"<b>График:</b> <code>{all_data[3]}</code>\n"
                                                    f"<b>Смена:</b> <code>{all_data[5]}</code>\n\n"

                                                    f"<b>Требование:</b>\n<code>{all_data[14]}</code>\n\n"
                                                    f"<b>Обязанности:</b>\n<code>{all_data[15]}</code>\n\n"
                                              
                                                    f"{all_data[7]}")
    else:
        await state.finish()

        if not connection.get_id(user_id):
            connection.RegUser(user_id, message.from_user.first_name, message.from_user.username, None, 0, 0, 0, date_start = today)




    if not connection.checkUserStatus(user_id):
        await state.finish()

        cap = common_captcha.process_captcha()
        async with state.proxy() as data:
            data['captcha_key'] = cap
        
            with open(f'{config.CAPTCHA_PHOTO_PATH}{cap}.png', 'rb') as img:
                await bot.send_photo(
                    chat_id = message.from_user.id,
                    photo = img, 
                    caption = "⚠️ <b>Чтоб продолжить использование бота, необходимо решить капчу.</b>\n\nОтправьте мне текст, что изображен на картинке.")
                    
                
                os.system(f"del -y {config.CAPTCHA_PHOTO_PATH}{cap}.png")
                await Start.step1.set()

    else:
        await state.finish()

        user_status = connection.checkUserStatus(user_id)
        if not connection.checkUserStatus(user_id):
            cap = common_captcha.process_captcha()
            async with state.proxy() as data:
                data['captcha_key'] = cap
            
                with open(f'{config.CAPTCHA_PHOTO_PATH}{cap}.png', 'rb') as img:
                    await bot.send_photo(
                        chat_id = message.from_user.id,
                        photo = img, 
                        caption = "⚠️ <b>Чтоб продолжить использование бота, необходимо решить капчу.</b>\n\nОтправьте мне текст, что изображен на картинке.")
                    
                
                    
                    os.system(f"unlink {config.CAPTCHA_PHOTO_PATH}{cap}.png")
                    await Start.step1.set()

        else:
            await state.finish()

            if user_status[0] == 'customer':
                cus_id = message.from_user.id
                try:
                    if connection.selectAll(cus_id)[3] == 'Banned':
                        await bot.send_message(message.chat.id, "Ваш профиль заказчика забанен!")
                        
                    else:
                        await bot.send_message(message.chat.id, "Главное меню", reply_markup = buttons.menu_customer)
                        await state.finish()
                except:
                    await bot.send_message(message.chat.id, "Главное меню", reply_markup = buttons.menu_customer)
                    await state.finish()                  

            elif user_status[0] == 'executor':
                await state.finish()

                ex_id = message.from_user.id
                try:
                    if connection.getExecutorProfil(ex_id)[8] == 'Banned':
                        await bot.send_message(message.chat.id, "Ваш профиль исполнителя забанен!")

                    else:
                        await bot.send_message(message.chat.id, "Главное меню", reply_markup = buttons.menu_executor)
                        await state.finish()
                except:
                    await bot.send_message(message.chat.id, "Главное меню", reply_markup = buttons.menu_executor)
                    await state.finish()                   

            elif connection.checkReferral(user_id)[3] == 'Banned':
                await state.finish()

                await bot.send_message(message.chat.id, "Ваш профиль забанен!")

            else:
                await state.finish()
                
                cap = common_captcha.process_captcha()
                async with state.proxy() as data:
                    data['captcha_key'] = cap
                
                    with open(f'{config.CAPTCHA_PHOTO_PATH}{cap}.png', 'rb') as img:
                        await bot.send_photo(
                            chat_id = message.from_user.id,
                            photo = img, 
                            caption = "⚠️ <b>Чтоб продолжить использование бота, необходимо решить капчу.</b>\n\nОтправьте мне текст, что изображен на картинке.")
                    
                
                        
                        os.system(f"unlink {config.CAPTCHA_PHOTO_PATH}{cap}.png")
                        await Start.step1.set()


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands = 'start', state="*")
