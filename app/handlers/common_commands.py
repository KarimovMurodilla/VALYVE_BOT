import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from .. import connection, file_ids, buttons, config


today = datetime.datetime.today().strftime('%d.%m.%Y')


bot = Bot(token=config.TOKEN, parse_mode = 'html')


def extract_unique_code(text):
    # Extracts the unique_code from the sent /start command.
    return text.split()[1] if len(text.split()) > 1 else None


async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    user_id = message.chat.id

    unique_code = extract_unique_code(message.text)
    if unique_code:
        if not connection.get_id(user_id):
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
                                                    f"<b>Время работы:</b> <code>{all_data[4]}</code>\n"
                                                    f"<b>График:</b> <code>{all_data[3]}</code>\n"
                                                    f"<b>Смена:</b> <code>{all_data[5]}</code>\n\n"

                                                    f"<b>Требование:</b>\n<code>{all_data[14]}</code>\n\n"
                                                    f"<b>Обязанности:</b>\n<code>{all_data[15]}</code>\n\n"
                                              
                                                    f"{all_data[7]}")
    else:
        if not connection.get_id(user_id):
            connection.RegUser(user_id, message.from_user.first_name, message.from_user.username, None, 0, 0, 0, date_start = today)




    if not connection.checkUserStatus(user_id):
        await bot.send_photo(message.chat.id, photo = file_ids.PHOTO['agreement'], caption = "Для использования бота, необходимо ознакомиться с <a href = 'https://ru.wikipedia.org/wiki/%D0%9F%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8C%D1%81%D0%BA%D0%BE%D0%B5_%D1%81%D0%BE%D0%B3%D0%BB%D0%B0%D1%88%D0%B5%D0%BD%D0%B8%D0%B5'>пользовательским договором</a> и согласиться с ним чтоб продолжить использование бота.", reply_markup = buttons.btn)

    else:
        user_status = connection.checkUserStatus(user_id)
        if not connection.checkUserStatus(user_id):
            await bot.send_photo(message.chat.id, photo = file_ids.PHOTO['agreement'], caption = "Для использования бота, необходимо ознакомиться с <a href = 'https://ru.wikipedia.org/wiki/%D0%9F%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8C%D1%81%D0%BA%D0%BE%D0%B5_%D1%81%D0%BE%D0%B3%D0%BB%D0%B0%D1%88%D0%B5%D0%BD%D0%B8%D0%B5'>пользовательским договором</a> и согласиться с ним чтоб продолжить использование бота.", reply_markup = buttons.btn)

        else:
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
                await bot.send_message(message.chat.id, "Ваш профиль забанен!")

            else:
                await bot.send_photo(message.chat.id, photo = file_ids.PHOTO['agreement'], caption = "Для использования бота, необходимо ознакомиться с <a href = 'https://ru.wikipedia.org/wiki/%D0%9F%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8C%D1%81%D0%BA%D0%BE%D0%B5_%D1%81%D0%BE%D0%B3%D0%BB%D0%B0%D1%88%D0%B5%D0%BD%D0%B8%D0%B5'>пользовательским договором</a> и согласиться с ним чтоб продолжить использование бота.", reply_markup = buttons.btn)



def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands = 'start', state="*")
