import pygsheets
import numpy as np
import pandas as pd
import datetime

# token for google sheets
gc = pygsheets.authorize(service_account_file='token.json')


# function which delete every last day of month lists for current month and rename lists for new monnths
def sheet_delete(current_date, max_current_date):
    if current_date != max_current_date:
        return
    new_month = datetime.date.today().month + 1
    year = str(datetime.date.today().year + 1) if new_month == 12 else str(datetime.date.today().year)
    new_month = '0' + str(new_month) if new_month < 10 else str(new_month)
    sh = gc.open('Графік Служіння')
    sh.del_worksheet(sh.worksheet_by_title('Автостанція'))
    sh.del_worksheet(sh.worksheet_by_title('Лікарня'))
    sh.worksheet_by_title('Автостанція ' + new_month + '.' + year).title = 'Автостанція'
    sh.worksheet_by_title('Лікарня ' + new_month + '.' + year).title = 'Лікарня'


# function which create new lists for new month every 24 date of current month
def sheet_reinitialize(current_date, date_update):
    if current_date < date_update:
        return
    new_month = datetime.date.today().month + 1
    year = str(datetime.date.today().year + 1) if new_month == 12 else str(datetime.date.today().year)

    if new_month % 2 == 0 and new_month not in (8, 2):
        max_day = 30
    elif new_month == 2:
        max_day = 28
    else:
        max_day = 31

    new_month = '0' + str(new_month) if new_month < 10 else str(new_month)
    daydate = pd.DataFrame(np.array(['0' + str(i) + '.' + new_month + '.' + year if i < 10 else str(i) + '.' + new_month + '.' + year for i in range(1, max_day + 1)]))
    times_zone = pd.DataFrame(np.array(['08:00-10:00', '10:00-12:00', '12:00-14:00', '14:00-16:00', '16:00-18:00', '18:00-20:00']))

    data = pd.DataFrame.merge(daydate, times_zone, how='cross')
    data.columns = ['Дата', 'Зміна']
    data['Служитель1'] = ''
    data['Служитель2'] = ''

    sh = gc.open('Графік Служіння')
    ws1 = sh.add_worksheet('Автостанція ' + new_month + '.' + year)
    ws2 = sh.add_worksheet('Лікарня ' + new_month + '.' + year)
    ws1.set_dataframe(data, (1, 1))
    ws2.set_dataframe(data, (1, 1))

    return data


# function for inserting data into gogglesheet
def insert(date, time, place, name, flag_month):
    cnt = 0
    sh = gc.open('Графік Служіння')
    ws = sh[place + flag_month]
    msg = ''
    for row in ws:
        cnt = cnt + 1
        if row[2] == '' and row[3] != name and row[0] == date and row[1] == time:
            index_x = cnt
            index_y = 3
            ws.update_value((index_x, index_y), name)
            msg = 'Ви були успішно записані на ' + date + ' число ' + time
        elif row[3] == '' and row[2] != name and row[0] == date and row[1] == time:
            index_x = cnt
            index_y = 4
            ws.update_value((index_x, index_y), name)
            msg = 'Ви були успішно записані на ' + date + ' число ' + time
        elif row[2] != '' and row[3] != '' and cnt != 1 and row[2] != name and row[3] != name:
            msg = 'Нажаль, ця зміна заповнена.'
        elif (row[3] == name or row[2] == name) and row[0] == date and row[1] == time:
            msg = 'Ви вже записані в цю зміну.'

    return msg


# function for deleting data from googlesheet
def delete(date, time, place, name, flag_month):
    cnt = 0
    sh = gc.open('Графік Служіння')
    ws = sh[place + flag_month]
    msg = ''
    for row in ws:
        cnt = cnt + 1
        if row[2] == name and row[0] == date and row[1] == time:
            index_x = cnt
            index_y = 3
            ws.update_value((index_x, index_y), '')
            msg = 'Ви були успішно виписані на ' + date + ' число ' + time
        elif row[3] == name and row[0] == date and row[1] == time:
            index_x = cnt
            index_y = 4
            ws.update_value((index_x, index_y), '')
            msg = 'Ви були успішно виписані на ' + date + ' число ' + time
        elif row[2] != name and row[3] != name and row[0] == date and row[1] == time:
            msg = 'Ви не були записані на цю зміну!'
    return msg


# function which output data only for user
def my_records(name, flag_month=0):
    sh = gc.open('Графік Служіння')
    ws1 = sh[0 + flag_month]
    msg = 'Автостанція:' + chr(10)
    for row in ws1:
        if row[2] == name or row[3] == name:
            msg = msg + row[0] + ' ' + row[1] + ' ' + chr(10)

    ws2 = sh[1 + flag_month]
    msg = msg + 'Лікарня:' + chr(10)
    for row in ws2:
        if row[2] == name or row[3] == name:
            msg = msg + row[0] + ' ' + row[1] + ' ' + chr(10)

    if msg == 'Автостанція:' + chr(10) + 'Лікарня:' + chr(10):
        msg = 'Нажаль, поки що у вас немає жодної зміни.'

    return msg


# function which prepared report for place of serving and current or next month
def report(flag_month, place):
    sh = gc.open('Графік Служіння')
    ws = sh[flag_month + place]
    msg = ''
    msg_arr = []
    cnt = -1
    for row in ws:
        if cnt == -1:
            msg = msg + row[0] + '            ' + row[1] + '           ' + row[2] + '                      ' + row[3] + chr(10)
            header = msg
        if cnt < 50 and cnt != -1:
            msg = msg + row[0] + '  ' + row[1] + '  ' + row[2] + '  ' + row[3] + chr(10)
        if cnt == 50 and cnt != -1:
            msg_arr.append(msg)
            cnt = 0
            msg = header
        cnt = cnt + 1
    msg_arr.append(msg)

    return msg_arr


def list_of_partner(place, date, time, flag_month):
    sh = gc.open('Графік Служіння')
    ws = sh[flag_month + place]
    partner = ''
    for row in ws:
        if row[0] == date and row[1] == time:
            if row[2] != '':
                partner = row[2]
            elif row[3] != '':
                partner = row[3]

    return partner
