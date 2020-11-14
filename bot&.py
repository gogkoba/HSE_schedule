from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
from telegram import Bot
#from re2 import scheduler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import datetime
import logging
import requests
from bs4 import BeautifulSoup as bs
import urllib

def scheduler(n, t):
    sched = ""
    name= urllib.parse.quote(n)
    y = requests.get('https://ruz.hse.ru/api/search?term=' + str(name) + '&type=student' ).text
    y = eval(y)
    id_u = y[0]["id"]
    if t == 0:
        sched+= 'Сегодня\n\n'
        today = datetime.datetime.now()
        d = today.day
        m = today.month

        if len(str(d)) == 1:
            d = '0' + str(d)
        if len(str(m)) == 1:
            l = '0' + str(m)
        today = str(today.year) + '.' + str(m) + '.' + str(d)

        r = requests.get('https://ruz.hse.ru/api/schedule/student/' + str(id_u) +'?start='+today+'&finish='+today+'&lng=1').json()

        for i in r:
            sched += (i["discipline"] + "  " + i['beginLesson'] + " - " + i["endLesson"] + "  " + "Аудитория:" + str(i['auditorium']) + "  " + str(i["url1"]) * (i["url1"] != None)) + "\n"
            sched += " " + "\n"

        if sched != "":
            return sched
        else:
            return "Сегодня нет пар"

    if t == 1:
        sched += 'Завтра\n\n'
        today = datetime.datetime.now() + datetime.timedelta(days=t)
        d = today.day
        m = today.month

        if len(str(d)) == 1:
            d = '0' + str(d)
        if len(str(m)) == 1:
            l = '0' + str(m)
        today = str(today.year) + '.' + str(m) + '.' + str(d)

        r = requests.get('https://ruz.hse.ru/api/schedule/student/' + str(id_u) +'?start='+today+'&finish='+today+'&lng=1').json()

        for i in r:
            sched += (i["discipline"] + "  " + i['beginLesson'] + " - " + i["endLesson"] + "  " + "Аудитория:" + str(i['auditorium']) + "  " + str(i["url1"]) * (i["url1"] != None)) + "\n"
            sched += " " + "\n"

        if sched != "":
            return sched
        else:
            return "Сегодня нет пар"

    if t == 6:
        date = datetime.datetime.now()
        t = 6 - datetime.datetime.weekday(date)
        for i in range (t+1):
            today = datetime.datetime.now() + datetime.timedelta(days=i)
            d = today.day
            m = today.month
            if len(str(d)) == 1:
                d = '0' + str(d)
            if len(str(m)) == 1:
                l = '0' + str(m)
            today = str(today.year) + '.' + str(m) + '.' + str(d)

            r = requests.get('https://ruz.hse.ru/api/schedule/student/' + str(id_u) + '?start=' + today + '&finish=' + today + '&lng=1').json()

            sched += today + ":" + "\n"
            for i in r:
                sched += (i["discipline"] + "  " + i['beginLesson'] + " - " + i["endLesson"] + "  " + "Аудитория:" + str(i['auditorium']) + "  " + str(i["url1"]) * (i["url1"] != None)) + "\n"+ "\n"
        if sched != "":
            return sched
        else:
            return "На этой неделе нет пар"

bot = Bot(token='')
updater = Updater(token='')
dp = updater.dispatcher

def start(update, context):
    bot.sendMessage(update.effective_user.id, "Привет, напиши /crossroads Ф И для получения рассписания. Пожалуйста не забудь написать свое имя и фамилию после /crossroads")

def crossroads(update, context: CallbackContext):
    name = " ".join(context.args)
    namer = urllib.parse.quote(name)
    y = requests.get('https://ruz.hse.ru/api/search?term=' + str(namer) + '&type=student').text
    y = eval(y)
    if y == []:
        bot.sendMessage(update.effective_user.id, "А я вас не знаю, попробуйте снова")
        return "остановка"
    if name != "":
        bot.sendMessage(update.effective_user.id,name)
        keyboard = [

                [InlineKeyboardButton("сегодня", callback_data= "0"+name),
                InlineKeyboardButton("завтра", callback_data= "1"+name)],
                [InlineKeyboardButton("неделю", callback_data= "6"+name),
                InlineKeyboardButton("след. неделю", callback_data="7"+name)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Получить расписание на:', reply_markup=reply_markup)
    else:
        bot.sendMessage(update.effective_user.id,"Вы кажется забыли представиться. Напишите команду заново с фамилией и именем")

def button(update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(scheduler(query.data[1:len(query.data)], int(query.data[0])))

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("crossroads", crossroads))
updater.dispatcher.add_handler(CallbackQueryHandler(button))
updater.start_polling()
updater.idle()
