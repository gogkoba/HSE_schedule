#Бот который запрашивает Имя фамилию, а затем выдает расписание
#Импортирую библиотеки
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
from telegram import Bot
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import datetime
import logging
import requests
from bs4 import BeautifulSoup as bs
import urllib


def scheduler(n, t): #Функция, которая по имени n, и номеру нужного эффекта t выдает расписание. Раньше находилась в отдельном файле и импортировалась как библиотека
    sched = "" # строка, куда позже добавляю ответ
    name= urllib.parse.quote(n) #перевожу кириллицу в url
    y = requests.get('https://ruz.hse.ru/api/search?term=' + str(name) + '&type=student' ).text #получаю расписание определенного студента
    y = eval(y)
    id_u = y[0]["id"]
    if t == 0: #номер  эффекта t=0 значит - получение расписание на сегодня
        sched+= 'Сегодня\n\n' #Добавляю в ответ "Сегодня" и пропускаю одну строку
        today = datetime.datetime.now() #узнаю дату и время сейчас
        d = today.day #обозначаю сегоднешний день как d
        m = today.month #обозначаю сегоднешний месяц как m

        if len(str(d)) == 1:#привожу день к формату dd
            d = '0' + str(d)
        if len(str(m)) == 1:#привожу месяц к формату mm
            l = '0' + str(m)
        today = str(today.year) + '.' + str(m) + '.' + str(d)#собираю дату заново

        r = requests.get('https://ruz.hse.ru/api/schedule/student/' + str(id_u) +'?start='+today+'&finish='+today+'&lng=1').json()#получаю расписание определенного студента в определеннный день 

        for i in r:#формирую расписание в нужном формате
            sched += (i["discipline"] + "  " + i['beginLesson'] + " - " + i["endLesson"] + "  " + "Аудитория:" + str(i['auditorium']) + "  " + str(i["url1"]) * (i["url1"] != None)) + "\n"
            sched += " " + "\n"

        if sched != "":#если в расписании ничего нет, вывожу "Сегодня нет пар"
            return sched
        else:
            return "Сегодня нет пар"

    if t == 1:#номер  эффекта t=1 значит - получение расписание на завтра
        sched += 'Завтра\n\n'#Добавляю в ответ "Сегодня" и пропускаю одну строку
        today = datetime.datetime.now() + datetime.timedelta(days=t)#узнаю дату и время завтра
        d = today.day
        m = today.month

        if len(str(d)) == 1:#привожу день к формату dd
            d = '0' + str(d)
        if len(str(m)) == 1:#привожу месяц к формату mm
            l = '0' + str(m)
        today = str(today.year) + '.' + str(m) + '.' + str(d)

        r = requests.get('https://ruz.hse.ru/api/schedule/student/' + str(id_u) +'?start='+today+'&finish='+today+'&lng=1').json()#получаю расписание определенного студента в определеннный день 


        for i in r:#формирую расписание в нужном формате
            sched += (i["discipline"] + "  " + i['beginLesson'] + " - " + i["endLesson"] + "  " + "Аудитория:" + str(i['auditorium']) + "  " + str(i["url1"]) * (i["url1"] != None)) + "\n"
            sched += " " + "\n"

        if sched != "":#если в расписании ничего нет, вывожу "Сегодня нет пар"
            return sched
        else:
            return "Завтра нет пар"

    if t == 6:#номер  эффекта t=6 значит - получение расписание на всю неделю, исключая прошедшие дни 
        date = datetime.datetime.now()#получаю сегодняшнюю дату и время
        t = 6 - datetime.datetime.weekday(date)#определяю сколько осталось дней до конца недели
        for i in range (t+1):#добавляю в рассписание каждый день по отдельности
            today = datetime.datetime.now() + datetime.timedelta(days=i)#выбираю день
            d = today.day
            m = today.month
            if len(str(d)) == 1: #привожу день и месец к формату dd и mm
                d = '0' + str(d)
            if len(str(m)) == 1:
                l = '0' + str(m)
            today = str(today.year) + '.' + str(m) + '.' + str(d)

            r = requests.get('https://ruz.hse.ru/api/schedule/student/' + str(id_u) + '?start=' + today + '&finish=' + today + '&lng=1').json()#получаю расписание определенного студента в определеннный день 

            sched += today + ":" + "\n"
            for i in r:
                sched += (i["discipline"] + "  " + i['beginLesson'] + " - " + i["endLesson"] + "  " + "Аудитория:" + str(i['auditorium']) + "  " + str(i["url1"]) * (i["url1"] != None)) + "\n"+ "\n"
        if sched != "":
            return sched
        else:
            return "На этой неделе нет пар"

bot = Bot(token='') #объявляю самого бота и выдаю ему токен
updater = Updater(token='')#выдаю токен для обновлений
dp = updater.dispatcher

def start(update, context):#функция start требующая информайию, кто, где и когда вызвал. Дает пояснение, как работает бот
    bot.sendMessage(update.effective_user.id, "Привет, напиши /crossroads Ф И для получения рассписания. Пожалуйста не забудь написать свое имя и фамилию после /crossroads")

def crossroads(update, context: CallbackContext):#основная функция, вызывает кнопки и записывет, что выбрал пользователь. Функция crossroads требующая информайию, кто, где и когда вызвал, а еще, что было написано после самой команды.
    name = " ".join(context.args)#определяю имя. имя - то, что было после самой команды
    namer = urllib.parse.quote(name)#перевожу имя url
    y = requests.get('https://ruz.hse.ru/api/search?term=' + str(namer) + '&type=student').text#получаю рассписание студента
    y = eval(y)
    if y == []:#Если рассписание пустое, то прошу повторно отправить имя и фамилию
        bot.sendMessage(update.effective_user.id, "А я вас не знаю, попробуйте снова")
        return "остановка"
    if name != "":#Если имя не отсутствует. Вывожу кнопки и добаляю, выбор пользователя в callback_data
        bot.sendMessage(update.effective_user.id,name)
        keyboard = [

                [InlineKeyboardButton("сегодня", callback_data= "0"+name),
                InlineKeyboardButton("завтра", callback_data= "1"+name)],
                [InlineKeyboardButton("неделю", callback_data= "6"+name),
                InlineKeyboardButton("след. неделю", callback_data="7"+name)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Получить расписание на:', reply_markup=reply_markup)
    else:#Если имени нет, прошу заново запустить команду
        bot.sendMessage(update.effective_user.id,"Вы кажется забыли представиться. Напишите команду заново с фамилией и именем")

def button(update, context: CallbackContext):#функция, рассматривающая CallbackContext и вызывающая функцию scheduler в нужном формате
    query = update.callback_query
    query.answer()
    query.edit_message_text(scheduler(query.data[1:len(query.data)], int(query.data[0])))

dp.add_handler(CommandHandler("start", start))#добавляю боту команду start
dp.add_handler(CommandHandler("crossroads", crossroads))#добавляю боту команду crossroads
updater.dispatcher.add_handler(CallbackQueryHandler(button))
updater.start_polling()
updater.idle()
