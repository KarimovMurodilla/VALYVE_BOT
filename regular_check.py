import os
import time
from datetime import datetime
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app import connection, config, buttons

scheduler = AsyncIOScheduler()
bot = Bot(token=config.TOKEN, parse_mode = 'html')


async def pay_for_waiter():
    connection.getResponses()
    mailing = [await bot.send_message(i[2], f"🔔 Уведомление:\n\nВам начислено <code>{i[0]} ₽</code> на баланс, за ожидание работы от заказчика <code>{connection.selectAll(i[1])[0]}</code>") 
        for i in connection.getResponses(to_mail = True)]


async def check_order_deletion_date():
    send = [x for x in connection.checkDeletionDate(send_finish = True)]
    try:
        for i in send:
            connection.updateBalance(i[0], int(connection.selectMyFreezingMoneys(i[0], i[1])), '+')
            await bot.send_message(i[0], "🔔 <b>Уведомление:</b>\n\n"
                                         f"Объявление под номером #1 было завершено. На Ваш счёт было начислено <code>{connection.selectMyFreezingMoneys(i[0], i[1])} ₽</code> не использованных средств")
            connection.updateFreezingMoney(connection.selectMyFreezingMoneys(i[0], i[1]), i[0], i[1])

            if connection.selectMyPerInOrderId(i[0], i[1])[0]:
                await bot.send_message(i[0], "Вы хотите оценить качество работы исполнителя?", reply_markup = buttons.askPutRate(i[0], i[1]))
    except Exception as e:
        print(e)
    
    connection.checkDeletionDate()

def schedule_jobs():
    scheduler.add_job(pay_for_waiter, 'interval', minutes=1)
    scheduler.add_job(check_order_deletion_date, 'interval', seconds=30)
