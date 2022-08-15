import telebot
import gsheet
import datetime
import schedule
from telebot import types

# token for Telegram
bot = telebot.TeleBot('5324290474:AAFqcVvBOy2tHsrrrRjho9JL9SZB8cZzcwk')

# global variable updating date
date_update = 15

# global variables for user
name = 'x'
date = 'x'
time = 'x'
place = 'x'

# flag_month show which month has been selected by user 0 current, 2 next
flag_month = 0

# flag_option deleting or inserting data: 0-insert, 1-delete
flag_option = 0

# calculating current date, month and next month
current_date = datetime.date.today().day
current_month = datetime.date.today().month
next_month = datetime.date.today().month + 1

# calculating max date for month
if current_month % 2 == 0 and current_month not in (8, 2):
    max_current_date = 30
elif current_month == 2:
    max_current_date = 28
else:
    max_current_date = 31

if next_month % 2 == 0 and next_month not in (8, 2):
    max_next_date = 30
elif current_month == 2:
    max_next_date = 28
else:
    max_next_date = 31


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
    elif message.text == 'Наступний місяць':
        msg = gsheet.my_records(name, flag_month=2)
        bot.send_message(message.from_user.id, msg)


# ---------------------------------------markup functions---------------------------------------
# function is to build markup for main menu
def markup_main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    create = types.KeyboardButton('Записатися на зміну')
    drop = types.KeyboardButton('Видалитися зі зміни')
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


def markup_time_zone(message):
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


# ---------------------------------------bot states functions---------------------------------------
# bot start working (state 0)
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    create = types.KeyboardButton('Записатися на зміну')
    drop = types.KeyboardButton('Видалитися зі зміни')
    alter = types.KeyboardButton('Мої зміни')
    graph = types.KeyboardButton('Графік стенду')

    markup.add(create, drop, alter, graph)
    bot.send_message(message.chat.id,
                     'Раді вітати. Розпочніть роботу з ботом. Виберіть команду з меню.',
                     reply_markup=markup)


# start 1 of bot (calc name and select place or month for recording (available from 24th every month)
# state 1 of bot: select my serving times
@bot.message_handler()
def handle_text(message):
    global name, flag_option, date_update
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
            msg = bot.send_message(message.from_user.id, 'Оберіть за який ви хочете переглянути свої зміни:',
                                   reply_markup=markup)
            bot.register_next_step_handler(msg, view_month)

    # Output schedule (from 24 available for current and next month)
    elif message.text == 'Графік стенду':
        msg_arr = gsheet.report(flag_month=0) if current_date < 24 else gsheet.report(flag_month=2)
        for msg in msg_arr:
            bot.send_message(message.chat.id, msg)

    elif message.text == 'Видалитися зі зміни':
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
    else:
        markup_main_menu(message)

    if message.text in ('Поточний місяць', 'Наступний місяць'):
        # if entered not return button
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        place1 = types.KeyboardButton('Автостанція')
        place2 = types.KeyboardButton('Лікарня')
        item1 = types.KeyboardButton('Назад')
        markup.add(place1, place2, item1)
        if flag_option == 0:
            msg = bot.send_message(message.from_user.id, 'Оберіть місце служіння:', reply_markup=markup)
        elif flag_option == 1:
            msg = bot.send_message(message.from_user.id, 'Виберіть місце служіння, з якого ви хочете виписатися:', reply_markup=markup)
        bot.register_next_step_handler(msg, record_place)


# state 2 of bot if current_date < 24: select place of serving
# state 3 of bot if current_date >= 24: select place of serving
def record_place(message):
    global place
    if message.text == 'Автостанція':
        place = 0
    elif message.text == 'Лікарня':
        place = 1
    elif message.text == 'Назад':
        if current_date >= date_update:
            markup_month_menu(message)
        else:
            markup_main_menu(message)
    if message.text in ('Лікарня', 'Автостанція'):
        if flag_option == 0:
            msg = bot.send_message(message.from_user.id, 'Введіть дату на яку ви хочете записатися:')
        elif flag_option == 1:
            msg = bot.send_message(message.from_user.id, 'Введіть дату на яку ви хочете виписатися:')
        bot.register_next_step_handler(msg, record_date)
    elif message.text not in ('Лікарня', 'Автостанція', 'Назад'):
        msg = bot.send_message(message.from_user.id, 'Ви ввели невірне місце служіння. Будь-ласка, оберіть значення в меню:')
        bot.register_next_step_handler(msg, record_place)


# state 3(<24): select date of serving
# state 4(>=24): select date of serving
def record_date(message):
    global date, place, max_current_date, max_next_date
    place = place + flag_month
    date = message.text
    if date == 'Назад':
        markup_place_menu(message)
    elif (flag_month == 0 and date.isdigit() and current_date <= int(date) <= max_current_date and message.text != 'Назад') or \
            (flag_month == 2 and date.isdigit() and 1 <= int(date) <= max_next_date and message.text != 'Назад'):
        # recording for new month is available from 24th of current moth
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton('08:00-10:00')
        item2 = types.KeyboardButton('10:00-12:00')
        item3 = types.KeyboardButton('12:00-14:00')
        item4 = types.KeyboardButton('14:00-16:00')
        item5 = types.KeyboardButton('16:00-18:00')
        item6 = types.KeyboardButton('18:00-20:00')
        item7 = types.KeyboardButton('Назад')
        markup.add(item1, item2, item3, item4, item5, item6, item7)
        if flag_option == 0:
            msg = bot.send_message(message.chat.id, 'Виберіть зміну на яку ви хочете записатися:', reply_markup=markup)
        elif flag_option == 1:
            msg = bot.send_message(message.chat.id, 'Виберіть зміну з якої ви хочете виписатися:', reply_markup=markup)
        bot.register_next_step_handler(msg, record_time)
    else:
        bot.send_message(message.chat.id, 'Невірна дата. Будь ласка, спробуйте ще раз!')
        msg = bot.send_message(message.from_user.id, 'Введіть бажаєму дату запису:')
        bot.register_next_step_handler(msg, record_date)


# state 4(<24): select time of serving
# state 5(>=24): select time of serving
def record_time(message):
    global date, time
    date_l = ''
    time = message.text
    if time == 'Назад':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton('Назад')

        markup.add(item1)
        if flag_option == 0:
            msg = bot.send_message(message.chat.id, 'Введіть іншу дату на яку ви хочете записатися:', reply_markup=markup)
        elif flag_option == 1:
            msg = bot.send_message(message.chat.id, 'Введіть іншу дату на яку ви хочете виписатися:', reply_markup=markup)
        bot.register_next_step_handler(msg, record_date)

    elif time in ('08:00-10:00', '10:00-12:00', '12:00-14:00', '14:00-16:00', '16:00-18:00', '18:00-20:00') and flag_option == 0:
        date_l = date + '.0' + str(datetime.date.today().month) + '.' + str(datetime.date.today().year)
        msg_gsht = gsheet.insert(date_l, time, place, name, flag_month)
        msg = bot.send_message(message.from_user.id, msg_gsht)
        if msg.text == 'Нажаль, ця зміна заповнена.' or msg.text == 'Ви вже записані в цю зміну.':
            markup_time_zone(message)
        else:
            markup_main_menu(message)

    elif time in ('08:00-10:00', '10:00-12:00', '12:00-14:00', '14:00-16:00', '16:00-18:00', '18:00-20:00') and flag_option == 1:
        date_l = date + '.0' + str(datetime.date.today().month) + '.' + str(datetime.date.today().year)
        msg_gsht = gsheet.delete(date_l, time, place, name, flag_month)
        bot.send_message(message.from_user.id, msg_gsht)
        if msg_gsht == 'Ви не були записані на цю зміну!':
            markup_time_zone(message)
        else:
            markup_main_menu(message)

    else:
        msg = bot.send_message(message.from_user.id, 'Ви ввели неправильне значення. Оберіть будь-ласка зміну у меню:')
        bot.register_next_step_handler(msg, record_time)


bot.polling(none_stop=True)

schedule.every().day.at("22:00").do(gsheet.sheet_reinitialize, current_date, date_update - 1)
schedule.every().day.at("22:00").do(gsheet.sheet_delete, current_date, max_current_date)

while True:
    schedule.run_pending()
