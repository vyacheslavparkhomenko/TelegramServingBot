# version 2.4.1 (fixing global variable initialization)
# TelegramServingBot is a bot for inserting, deleting, viewing records about public serving
# Created by Viacheslav Parkhomenko
# Date of release: 22-AUG-2022
import logging
import datetime
import re

import telebot
import gsheet

from time import sleep
from telebot import types

# WARNING!!!! before deployment on prod please dont forget change token to token_prod and table name to prod name

# token for Telegram
token_test = '5702336698:AAH4VKZ9KQyNPY0BBfxAaivK_j0huuZzyiQ'
token_prod = '5324290474:AAFqcVvBOy2tHsrrrRjho9JL9SZB8cZzcwk'

bot = telebot.TeleBot(token_prod)

# global variable updating date
date_update = 25

# global variables for user
name = 'x'
date = 'x'
time = 'x'
place = 0

# flag_month show which month has been selected by user 0-current, 2-next
flag_month = 0

# flag_option deleting or inserting data: 0-insert, 1-delete, 2-view
flag_option = 0

# calculating current date, month and next month
current_month = datetime.date.today().month
current_year = datetime.date.today().year

# list of days to allow for recording: 0-Monday..6-Sunday
list_of_days = [1, 5]

# dictionary of time slots for serving
# 0-Autostation, 1-Hospital
time_slots = [{
    1: ['10:00-12:00', '12:00-14:00'],
    5: ['09:00-11:00', '11:00-13:00']
},
    {
    1: ['08:00-10:00', '10:00-12:00', '12:00-14:00'],
    5: ['08:00-10:00', '10:00-12:00', '12:00-14:00']
}]


# ---------------------------------------additional functionality---------------------------------------
def view_month(message):
    global name
    first_name = message.from_user.first_name if message.from_user.first_name is not None else ''
    last_name = message.from_user.last_name if message.from_user.last_name is not None else ''
    name = first_name + ' ' + last_name
    if message.text == 'Назад':
        markup_main_menu(message)
    elif message.text == 'Поточний місяць':
        msg = gsheet.my_records(name, flag_month=0)
        bot.send_message(message.from_user.id, msg)
        markup_main_menu(message)
    elif message.text == 'Наступний місяць':
        msg = gsheet.my_records(name, flag_month=2)
        bot.send_message(message.from_user.id, msg)
        markup_main_menu(message)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        place1 = types.KeyboardButton('Поточний місяць')
        place2 = types.KeyboardButton('Наступний місяць')
        item1 = types.KeyboardButton('Назад')
        markup.add(place1, place2, item1)
        bot.send_message(message.from_user.id, 'Ви ввели невірне значення місяця!')
        msg = bot.send_message(message.from_user.id, 'Оберіть, будь-ласка, значення з меню:', reply_markup=markup)
        bot.register_next_step_handler(msg, view_month)


# function for forming date of record
def create_date(l_date, l_current_month, l_current_year):
    if l_date < 10:
        date_l = '0' + str(l_date)
    else:
        date_l = str(l_date)

    if l_current_month < 10:
        date_l = date_l + '.0' + str(l_current_month)
    else:
        date_l = date_l + '.' + str(l_current_month)

    date_l = date_l + '.' + str(l_current_year)

    return date_l


def get_max_date(month, year):
    if month in (1, 3, 5, 7, 8, 10, 12):
        max_date = 31
    elif month in (4, 6, 9, 11):
        max_date = 30
    elif month == 2 and year % 4 != 0:
        max_date = 28
    elif month == 2 and year % 4 == 0:
        max_date = 29
    return max_date


# ---------------------------------------markup functions---------------------------------------
# function is to build markup for main menu
def markup_main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    create = types.KeyboardButton('Записатися на зміну')
    drop = types.KeyboardButton('Виписатися зі зміни')
    alter = types.KeyboardButton('Мої зміни')
    graph = types.KeyboardButton('Графік стенду')

    markup.add(create, drop, alter, graph)
    msg = bot.send_message(message.chat.id, 'Головне меню:', reply_markup=markup)
    bot.register_next_step_handler(msg, handle_text)


# function is to build place menu
def markup_place_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    place1 = types.KeyboardButton('Автостанція')
    place2 = types.KeyboardButton('Лікарня')
    item1 = types.KeyboardButton('Назад')
    markup.add(place1, place2, item1)
    msg = bot.send_message(message.from_user.id, 'Оберіть місце служіння:', reply_markup=markup)
    bot.register_next_step_handler(msg, record_place)


# function is to build month menu
def markup_month_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    place1 = types.KeyboardButton('Поточний місяць')
    place2 = types.KeyboardButton('Наступний місяць')
    item1 = types.KeyboardButton('Назад')
    markup.add(place1, place2, item1)
    msg = bot.send_message(message.from_user.id, 'Оберіть на який місяць ви хочете записатиcя:', reply_markup=markup)
    bot.register_next_step_handler(msg, record_month)


# function for markuping menu for time slot from 08:00
def markup_time_zone1():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('08:00-10:00')
    item2 = types.KeyboardButton('10:00-12:00')
    item3 = types.KeyboardButton('12:00-14:00')
    item4 = types.KeyboardButton('14:00-16:00')
    item5 = types.KeyboardButton('16:00-18:00')
    item6 = types.KeyboardButton('18:00-20:00')
    item7 = types.KeyboardButton('Назад')
    markup.add(item1, item2, item3, item4, item5, item6, item7)

    return markup


# function for markuping menu for time slot from 09:00
def markup_time_zone2():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('09:00-11:00')
    item2 = types.KeyboardButton('11:00-13:00')
    item3 = types.KeyboardButton('13:00-15:00')
    item4 = types.KeyboardButton('15:00-17:00')
    item5 = types.KeyboardButton('17:00-19:00')
    item7 = types.KeyboardButton('Назад')
    markup.add(item1, item2, item3, item4, item5, item7)

    return markup


def markup_time_zone1_rerecord(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('08:00-10:00')
    item2 = types.KeyboardButton('10:00-12:00')
    item3 = types.KeyboardButton('12:00-14:00')
    item4 = types.KeyboardButton('14:00-16:00')
    item5 = types.KeyboardButton('16:00-18:00')
    item6 = types.KeyboardButton('18:00-20:00')
    item7 = types.KeyboardButton('Назад')
    markup.add(item1, item2, item3, item4, item5, item6, item7)
    msg = bot.send_message(message.from_user.id, 'Оберіть будь-ласка іншу зміну:', reply_markup=markup)
    bot.register_next_step_handler(msg, record_time)


def markup_time_zone2_rerecord(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('09:00-11:00')
    item2 = types.KeyboardButton('11:00-13:00')
    item3 = types.KeyboardButton('13:00-15:00')
    item4 = types.KeyboardButton('15:00-17:00')
    item5 = types.KeyboardButton('17:00-19:00')
    item7 = types.KeyboardButton('Назад')
    markup.add(item1, item2, item3, item4, item5, item7)
    msg = bot.send_message(message.from_user.id, 'Оберіть будь-ласка іншу зміну:', reply_markup=markup)
    bot.register_next_step_handler(msg, record_time)


def select_markup_timezone(weekday, message):
    if place == 0 and weekday == 1:
        markup_time_zone1_rerecord(message)
    if place == 0 and weekday == 5:
        markup_time_zone2_rerecord(message)
    if place == 1 and weekday == 1:
        markup_time_zone1_rerecord(message)
    if place == 1 and weekday == 5:
        markup_time_zone1_rerecord(message)


# ---------------------------------------bot states functions---------------------------------------
# bot start working (state 0)
@bot.message_handler(commands=['start'])
def start(message):
    global current_year, current_month
    current_month = datetime.date.today().month
    current_year = datetime.date.today().year
    bot.clear_step_handler(message)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    create = types.KeyboardButton('Записатися на зміну')
    drop = types.KeyboardButton('Виписатися зі зміни')
    alter = types.KeyboardButton('Мої зміни')
    graph = types.KeyboardButton('Графік стенду')

    markup.add(create, drop, alter, graph)
    msg = bot.send_message(message.from_user.id,
                           'Раді вітати. Розпочніть роботу з ботом. Виберіть команду з меню.',
                           reply_markup=markup)
    bot.register_next_step_handler(msg, handle_text)


# start 1 of bot (calc name and select place or month for recording (available from 24th every month)
# state 1 of bot: select my serving times
@bot.message_handler(commands=['Записатися на зміну', 'Мої зміни', 'Виписатися зі зміни', 'Графік стенду'])
def handle_text(message):
    global name, flag_option, date_update
    current_date = datetime.date.today().day
    if message.text == 'Записатися на зміну':
        flag_option = 0
        # if current date is less than 24 recording for new month is closed
        if current_date < date_update:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            place1 = types.KeyboardButton('Автостанція')
            place2 = types.KeyboardButton('Лікарня')
            item1 = types.KeyboardButton('Назад')
            markup.add(place1, place2, item1)
            msg = bot.send_message(message.from_user.id, 'Оберіть місце служіння:', reply_markup=markup)
            bot.register_next_step_handler(msg, record_place)

        # if it is greater than 24, then will added adding menu
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            place1 = types.KeyboardButton('Поточний місяць')
            place2 = types.KeyboardButton('Наступний місяць')
            item1 = types.KeyboardButton('Назад')
            markup.add(place1, place2, item1)
            msg = bot.send_message(message.from_user.id, 'Оберіть на який місяць ви хочете записатиcя:', reply_markup=markup)
            bot.register_next_step_handler(msg, record_month)

        # store username
        first_name = message.from_user.first_name if message.from_user.first_name is not None else ''
        last_name = message.from_user.last_name if message.from_user.last_name is not None else ''
        name = first_name + ' ' + last_name

    # my serving functionality: for date greater than 24 allows select schedule for next and current month
    elif message.text == 'Мої зміни':
        first_name = message.from_user.first_name if message.from_user.first_name is not None else ''
        last_name = message.from_user.last_name if message.from_user.last_name is not None else ''
        name = first_name + ' ' + last_name

        if current_date < date_update:
            msg = gsheet.my_records(name, flag_month=0)
            bot.send_message(message.from_user.id, msg)
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            place1 = types.KeyboardButton('Поточний місяць')
            place2 = types.KeyboardButton('Наступний місяць')
            item1 = types.KeyboardButton('Назад')
            markup.add(place1, place2, item1)
            msg = bot.send_message(message.from_user.id, 'Оберіть за який місяць ви хочете переглянути свої зміни:',
                                   reply_markup=markup)
            bot.register_next_step_handler(msg, view_month)

    # Output schedule (from 24 available for current and next month)
    elif message.text == 'Графік стенду':
        flag_option = 2
        if current_date < date_update:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            place1 = types.KeyboardButton('Автостанція')
            place2 = types.KeyboardButton('Лікарня')
            item1 = types.KeyboardButton('Назад')
            markup.add(place1, place2, item1)
            msg = bot.send_message(message.from_user.id,
                                   'Оберіть місце служіння для якого ви хочете переглянути графік:',
                                   reply_markup=markup)
            bot.register_next_step_handler(msg, record_place)

        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            place1 = types.KeyboardButton('Поточний місяць')
            place2 = types.KeyboardButton('Наступний місяць')
            item1 = types.KeyboardButton('Назад')
            markup.add(place1, place2, item1)
            msg = bot.send_message(message.from_user.id, 'Оберіть за який місяць ви хочете переглянути графік:',
                                   reply_markup=markup)
            bot.register_next_step_handler(msg, record_month)

    elif message.text == 'Виписатися зі зміни':
        flag_option = 1
        if current_date < date_update:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            place1 = types.KeyboardButton('Автостанція')
            place2 = types.KeyboardButton('Лікарня')
            item1 = types.KeyboardButton('Назад')
            markup.add(place1, place2, item1)
            msg = bot.send_message(message.from_user.id, 'Оберіть місце служіння з якого ви хочете виписатися:', reply_markup=markup)
            bot.register_next_step_handler(msg, record_place)
        # if it is greater than 24, then will added adding menu
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            place1 = types.KeyboardButton('Поточний місяць')
            place2 = types.KeyboardButton('Наступний місяць')
            item1 = types.KeyboardButton('Назад')
            markup.add(place1, place2, item1)
            msg = bot.send_message(message.from_user.id, 'Оберіть місяць, з якого ви хочете виписатися:',
                                   reply_markup=markup)
            bot.register_next_step_handler(msg, record_month)

            # store username
        first_name = message.from_user.first_name if message.from_user.first_name is not None else ''
        last_name = message.from_user.last_name if message.from_user.last_name is not None else ''
        name = first_name + ' ' + last_name

    elif message.text == 'Назад':
        start(message)
    elif message.text == '/start':
        start(message)
    else:
        msg = bot.send_message(message.from_user.id, 'Ви ввели невірне значення. Оберіть будь-ласка значення з меню:')
        bot.register_next_step_handler(msg, handle_text)


# state 2 of bot: select month if current date >= 24
def record_month(message):
    global flag_month
    if message.text == 'Поточний місяць':
        flag_month = 0
    elif message.text == 'Наступний місяць':
        flag_month = 2
    elif message.text == 'Назад':
        markup_main_menu(message)
    elif message.text == '/start':
        start(message)
    else:
        msg = bot.send_message(message.from_user.id, 'Ви ввели невірний місяць. Будь ласка, оберіть значення з меню!')
        bot.register_next_step_handler(msg, record_month)

    if message.text in ('Поточний місяць', 'Наступний місяць'):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        place1 = types.KeyboardButton('Автостанція')
        place2 = types.KeyboardButton('Лікарня')
        item1 = types.KeyboardButton('Назад')
        markup.add(place1, place2, item1)
        if flag_option == 0:
            msg = bot.send_message(message.from_user.id, 'Оберіть місце служіння:', reply_markup=markup)
        elif flag_option == 1:
            msg = bot.send_message(message.from_user.id, 'Виберіть місце служіння, з якого ви хочете виписатися:', reply_markup=markup)
        elif flag_option == 2:
            msg = bot.send_message(message.from_user.id,
                                   'Оберіть місце служіння для якого ви хочете переглянути графік:',
                                   reply_markup=markup)
        bot.register_next_step_handler(msg, record_place)


# state 2 of bot if current_date < 24: select place of serving
# state 3 of bot if current_date >= 24: select place of serving
def record_place(message):
    global place, flag_option, date_update
    current_date = datetime.date.today().day
    if message.text == 'Автостанція':
        place = 0
    elif message.text == 'Лікарня':
        place = 1
    elif message.text == 'Назад':
        if current_date >= date_update:
            markup_month_menu(message)
        else:
            markup_main_menu(message)
    elif message.text == '/start':
        start(message)
    elif message.text not in ('Лікарня', 'Автостанція', 'Назад', '/start'):
        msg = bot.send_message(message.from_user.id, 'Ви ввели невірне місце служіння. Будь-ласка, оберіть значення в меню:')
        bot.register_next_step_handler(msg, record_place)

    # mode for changing data
    if message.text in ('Лікарня', 'Автостанція') and flag_option != 2:
        if flag_option == 0:
            msg = bot.send_message(message.from_user.id, 'Введіть дату(число) на яку ви хочете записатися:')
        elif flag_option == 1:
            msg = bot.send_message(message.from_user.id, 'Введіть дату(число) на яку ви хочете виписатися:')
        bot.register_next_step_handler(msg, record_date)

    # mode for reviewing data
    if message.text == 'Автостанція' and flag_option == 2:
        msg_arr = gsheet.report(flag_month=flag_month, place=0)
        for msg in msg_arr:
            bot.send_message(message.chat.id, msg)
        markup_main_menu(message)

    elif message.text == 'Лікарня' and flag_option == 2:
        msg_arr = gsheet.report(flag_month=flag_month, place=1)
        for msg in msg_arr:
            bot.send_message(message.chat.id, msg)
        markup_main_menu(message)


# state 3(<24): select date of serving
# state 4(>=24): select date of serving
def record_date(message):
    global date, place, current_year, current_month
    current_year = datetime.date.today().year
    current_month = datetime.date.today().month

    if flag_month == 0:
        current_year = datetime.date.today().year
        current_month = datetime.date.today().month
    elif flag_month == 2:
        current_year = datetime.date.today().year if current_month < 12 else datetime.date.today().year + 1
        current_month = datetime.date.today().month + 1 if current_month < 12 else 1

    current_date = datetime.date.today().day
    date = message.text

    if date == 'Назад':
        markup_place_menu(message)
    elif message.text == '/start':
        start(message)
    elif (flag_month == 0 and date.isdigit() and
          current_date <= int(date) <= get_max_date(current_month, current_year) and
          message.text != 'Назад') or \
         (flag_month == 2 and date.isdigit() and
          1 <= int(date) <= get_max_date(current_month, current_year) and
          message.text != 'Назад'):

        weekday = datetime.date(current_year, current_month, int(date)).weekday()

        # recording for new month is available from 24th of current moth
        if weekday == list_of_days[0] and place == 0:
            # markup from 08:00
            markup = markup_time_zone1()
        elif weekday == list_of_days[1] and place == 0:
            # markup from 09:00
            markup = markup_time_zone2()
        elif weekday == list_of_days[0] and place == 1:
            # markup from 08:00
            markup = markup_time_zone1()
        elif weekday == list_of_days[1] and place == 1:
            # markup from 08:00
            markup = markup_time_zone1()
        elif weekday not in list_of_days:
            if flag_option == 0:
                bot.send_message(message.chat.id, 'На цю дату закрито можливість записатися на стенд!')
            elif flag_option == 1:
                bot.send_message(message.chat.id, 'На цю дату було недоступно записатися на стенд!')
            msg = bot.send_message(message.from_user.id, 'Введіть нову дату (число):')
            bot.register_next_step_handler(msg, record_date)
            return

        if flag_option == 0:
            msg = bot.send_message(message.chat.id, 'Виберіть зміну на яку ви хочете записатися:', reply_markup=markup)
        elif flag_option == 1:
            msg = bot.send_message(message.chat.id, 'Виберіть зміну з якої ви хочете виписатися:', reply_markup=markup)
        bot.register_next_step_handler(msg, record_time)
    else:
        bot.send_message(message.chat.id, 'Невірна дата. Будь ласка, спробуйте ще раз!')
        msg = bot.send_message(message.from_user.id, 'Введіть нову дату (число):')
        bot.register_next_step_handler(msg, record_date)


# state 4(<24): select time of serving
# state 5(>=24): select time of serving
def record_time(message):
    global date, time, current_year, current_month
    time = message.text
    current_year = datetime.date.today().year
    current_month = datetime.date.today().month

    if flag_month == 0:
        current_year = datetime.date.today().year
        current_month = datetime.date.today().month
    elif flag_month == 2:
        current_year = datetime.date.today().year if current_month < 12 else datetime.date.today().year + 1
        current_month = datetime.date.today().month + 1 if current_month < 12 else 1

    weekday = datetime.date(current_year, current_month, int(date)).weekday()

    if time == 'Назад':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton('Назад')
        markup.add(item1)

        # re-record date
        if flag_option == 0:
            msg = bot.send_message(message.chat.id, 'Введіть іншу дату(число) на яку ви хочете записатися:', reply_markup=markup)
        elif flag_option == 1:
            msg = bot.send_message(message.chat.id, 'Введіть іншу дату(число) на яку ви хочете виписатися:', reply_markup=markup)
        bot.register_next_step_handler(msg, record_date)

    elif time in time_slots[place].get(weekday) and flag_option == 0:
        date_l = create_date(int(date), current_month, current_year)
        msg_gsht = gsheet.insert(date_l, time, place, name, flag_month)
        msg = bot.send_message(message.from_user.id, msg_gsht)
        if msg.text == 'Нажаль, ця зміна заповнена.' \
                or msg.text == 'Ви вже записані в цю зміну.'\
                or msg.text == 'Ви вже записані на цей час в іншому місці для служіння!':
            select_markup_timezone(weekday, message)
        else:
            partner = gsheet.list_of_partner(place, date_l, time, name, flag_month)
            if partner != '':
                msg = 'З вами на зміні служить вісник ' + partner + '.'
                bot.send_message(message.from_user.id, msg)
            markup_main_menu(message)

    elif time in time_slots[place].get(weekday) and flag_option == 1:
        date_l = create_date(int(date), current_month, current_year)
        msg_gsht = gsheet.delete(date_l, time, place, name, flag_month)
        bot.send_message(message.from_user.id, msg_gsht)
        if msg_gsht == 'Ви не були записані на цю зміну!':
            select_markup_timezone(weekday, message)
        else:
            markup_main_menu(message)

    elif time not in time_slots[place].get(weekday) and re.fullmatch(r'\d\d[:]\d\d[-]\d\d[:]\d\d', time):
        if flag_option == 0:
            msg = bot.send_message(message.from_user.id,
                                   'На цю зміну обмежено запис! Оберіть будь-ласка іншу зміну:')
        elif flag_option == 1:
            msg = bot.send_message(message.from_user.id,
                                   'На цю зміну було обмежено запис! Оберіть будь-ласка іншу зміну:')
        bot.register_next_step_handler(msg, record_time)

    elif message.text == '/start':
        start(message)

    else:
        msg = bot.send_message(message.from_user.id, 'Ви ввели неправильне значення. Оберіть будь-ласка зміну у меню:')
        bot.register_next_step_handler(msg, record_time)


while True:
    try:
        logging.basicConfig(filename="log_" + str(datetime.date.today()) + ".txt",
                            level=logging.DEBUG,
                            format='%(asctime)s %(message)s',
                            filemode='w')
        logging.info('Bot running..')
        print('Bot running..')
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(e)
        bot.stop_polling()
        sleep(3)
        print(str(e))
        print('Running again!')
        logging.info('Running again!')
