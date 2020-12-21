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


def scheduler(n, t):
    """
    Функция выдающаяя рассписание по имени и номеру эффекта
    :param n: имя пользователя. Строка.
    :param t: номер эффекта. Число
    :return: расписание. Строка
    """
    sched = ""# строка, куда позже добавляю ответ
    name= urllib.parse.quote(n) #перевожу кириллицу в url
    y = requests.get('https://ruz.hse.ru/api/search?term=' + str(name) + '&type=student' ).json()#получаю данные определенного студента
    id_u = y[0]["id"]#нахожу в данных id студента

    if t < 6 :#если эффект < 6, значит выводим один день
        if t == 0:#если 0 - значит сегодня
            sched += 'Сегодня\n\n'
        if t == 1:#если 1 - значит завтра
            sched += 'Завтра\n\n'
        today = datetime.datetime.now() + datetime.timedelta(days=t)#получаю нужную дату
        d = today.day
        m = today.month

        if len(str(d)) == 1:
            d = '0' + str(d)
        if len(str(m)) == 1:
            l = '0' + str(m)
        today = str(today.year) + '.' + str(m) + '.' + str(d)#привожу today к нужному формату

        r = requests.get('https://ruz.hse.ru/api/schedule/student/' + str(id_u) +'?start='+today+'&finish='+today+'&lng=1').json()#получаю расписание определенного студента в определеннный день

        for i in r:#формирую расписание в нужном формате
            sched += (i["discipline"] + "  " + i['beginLesson'] + " - " + i["endLesson"] + "  " + "Аудитория:" + str(i['auditorium']) + "  " + str(i["url1"]) * (i["url1"] != None)) + "\n"
            sched += " " + "\n"

        if sched != "":#если в расписании ничего нет, вывожу "Сегодня нет пар"
            return sched
        else:
            return "Сегодня нет пар"

    if t == 6 or t == 7:#если эффект = 6 или 7, значит выводим неделю день 6 - эта неделя. 7 - следующая
        date = datetime.datetime.now()

        if t == 6:
            t = 6 - datetime.datetime.weekday(date)
        if t == 7:
            t = 6

        for i in range (t+1):#добавляю в рассписание каждый день по отдельности

            today = datetime.datetime.now() + datetime.timedelta(days=i)
            if t == 7:
                today = datetime.datetime.now() + datetime.timedelta(days=i+7)
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
                sched += (i["discipline"] + "  " + i['beginLesson'] + " - " + i["endLesson"] + "  " + "Аудитория:" + str(i['auditorium']) + "  " + str(i["url1"]) * (i["url1"] != None)) + "\n" + "\n"
        if sched != "":
            return sched
        else:
            return "На этой неделе нет пар"


bot = Bot(token='') #объявляю самого бота и выдаю ему токен
updater = Updater(token='')#выдаю токен для обновлений
dp = updater.dispatcher

def start(update, context):#функция start требующая информайию, кто, где и когда вызвал. Дает пояснение, как работает бот
    """
    Функция, которая при запуске, выводит в чат сообщение
    :param update: параметры чата
    :param context: параметры сообщения в чате
    :return: строку
    """
    bot.sendMessage(update.effective_user.id, "Привет, напиши /crossroads Ф И для получения рассписания. Пожалуйста не забудь написать свое имя и фамилию после /crossroads")

def crossroads(update, context: CallbackContext):#основная функция, вызывает кнопки и записывет, что выбрал пользователь. Функция crossroads требующая информайию, кто, где и когда вызвал, а еще, что было написано после самой команды.
    """
    Функция вызывающая в чат кнопки, считывающаяя их и проверяющаяя существует ли пользователь 
    :param update:  параметры чата
    :param context: параметры сообщения в чате. Конкретно, что было написано после самой команды
    :return: сообщение в чате и callback_data
    """
    name = " ".join(context.args)#определяю имя. имя - то, что было после самой команды
    namer = urllib.parse.quote(name)#перевожу имя url
    y = requests.get('https://ruz.hse.ru/api/search?term=' + str(namer) + '&type=student').json()#получаю рассписание студента

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

def button(update, context: CallbackContext):
    """
    Функция обрабатывающая CallbackContext и вызывающаяя scheduler в нужном формате
    :param update:  параметры чата
    :param context: параметры сообщения в чате
    :return: сообщение в чате
    """
    query = update.callback_query
    query.answer()
    query.edit_message_text(scheduler(query.data[1:len(query.data)], int(query.data[0])))

dp.add_handler(CommandHandler("start", start))#добавляю боту команду start
dp.add_handler(CommandHandler("crossroads", crossroads))#добавляю боту команду crossroads
updater.dispatcher.add_handler(CallbackQueryHandler(button))
updater.start_polling()
updater.idle()
