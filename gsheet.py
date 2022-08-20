import pygsheets
import pandas as pd
import datetime

# token for google sheets
gc = pygsheets.authorize(service_account_file='token.json')

# dictionary of time slots: 0-Monday, 5-Saturday and available timeslots
time_slots = [{
    1: ['10:00-12:00', '12:00-14:00'],
    5: ['09:00-11:00', '11:00-13:00']
},
    {
    1: ['08:00-10:00', '10:00-12:00', '12:00-14:00'],
    5: ['08:00-10:00', '10:00-12:00', '12:00-14:00']
}]


# function get weekday for any date
def get_weekday(date):
    weekday = datetime.datetime.strptime(date, '%d.%m.%Y').weekday()
    return weekday


# function which output information about schedule of public serving
def schedule_public(place):
    msg = ''
    for rec in time_slots[place]:
        if place == 0:
            msg = 'Автостанція:' + chr(10)
        else:
            msg = msg + 'Лікарня:' + chr(10)
        d_rec = dict(rec)
        if d_rec.get(0):
            msg = msg + 'Понеділок:' + chr(10)
            for ar in d_rec.get(1):
                msg = msg + str(ar) + chr(10)
        if d_rec.get(1):
            msg = msg + 'Вівторок:' + chr(10)
            for ar in d_rec.get(1):
                msg = msg + str(ar) + chr(10)
        if d_rec.get(2):
            msg = msg + 'Середа:' + chr(10)
            for ar in d_rec.get(1):
                msg = msg + str(ar) + chr(10)
        if d_rec.get(3):
            msg = msg + 'Четвер:' + chr(10)
            for ar in d_rec.get(1):
                msg = msg + str(ar) + chr(10)
        if d_rec.get(4):
            msg = msg + 'П''ятниця:' + chr(10)
            for ar in d_rec.get(1):
                msg = msg + str(ar) + chr(10)
        if d_rec.get(5):
            msg = msg + 'Субота:' + chr(10)
            for ar in d_rec.get(1):
                msg = msg + str(ar) + chr(10)
        if d_rec.get(6):
            msg = msg + 'Неділя:' + chr(10)
            for ar in d_rec.get(1):
                msg = msg + str(ar) + chr(10)
    return msg


# function which delete every last day of month lists for current month and rename lists for new monnths
def sheet_delete():
    current_date = datetime.date.today().day
    current_month = datetime.date.today().month
    if current_month % 2 == 0 and current_month not in (8, 2):
        max_current_date = 30
    elif current_month == 2:
        max_current_date = 28
    else:
        max_current_date = 31
    if current_date != max_current_date:
        return
    new_month = datetime.date.today().month + 1 if datetime.date.today().month < 12 else 1
    year = str(datetime.date.today().year + 1) if new_month == 1 else str(datetime.date.today().year)
    new_month = '0' + str(new_month) if new_month < 10 else str(new_month)
    sh = gc.open('Графік Служіння')
    sh.del_worksheet(sh.worksheet_by_title('Автостанція'))
    sh.del_worksheet(sh.worksheet_by_title('Лікарня'))
    sh.worksheet_by_title('Автостанція ' + new_month + '.' + year).title = 'Автостанція'
    sh.worksheet_by_title('Лікарня ' + new_month + '.' + year).title = 'Лікарня'


# function which create new lists for new month every 24 date of current month
def sheet_reinitialize(date_update):
    current_date = datetime.date.today().day
    if current_date < date_update:
        return
    new_month = datetime.date.today().month + 1 if datetime.date.today().month < 12 else 1
    year = datetime.date.today().year + 1 if new_month == 1 else datetime.date.today().year

    if new_month in (1, 3, 5, 7, 8, 10, 12):
        max_day = 31
    elif new_month in (4, 6, 9, 11):
        max_day = 30
    elif new_month == 2 and year % 4 != 0:
        max_day = 28
    elif new_month == 2 and year % 4 == 0:
        max_day = 29

    new_month = '0' + str(new_month) if new_month < 10 else str(new_month)
    year = str(year)
    daydate = []
    for i in range(1, max_day):
        x = '0' + str(i) + '.' + new_month + '.' + year if i < 10 else str(i) + '.' + new_month + '.' + year
        if get_weekday(x) in time_slots[0]:
            daydate.append(x)

    segments = []
    segment1 = []
    segment5 = []

    for d in daydate:
        weekday = get_weekday(d)
        for x in time_slots[0].get(weekday):
            if weekday == 1:
                segment1.append([d, x])
            if weekday == 5:
                segment5.append([d, x])

    segments.append(segment1)
    segments.append(segment5)

    data1 = pd.DataFrame([])

    col1 = []
    col2 = []
    for segment in segments:
        for elem in segment:
            col1.append(elem[0])
            col2.append(elem[1])

    data1['Дата'] = col1
    data1['Зміна'] = col2
    data1['Служитель1'] = ''
    data1['Служитель2'] = ''

    segments = []
    segment1 = []
    segment5 = []

    for d in daydate:
        weekday = get_weekday(d)
        for x in time_slots[1].get(weekday):
            if weekday == 1:
                segment1.append([d, x])
            if weekday == 5:
                segment5.append([d, x])

    segments.append(segment1)
    segments.append(segment5)

    data2 = pd.DataFrame([])

    col1 = []
    col2 = []
    for segment in segments:
        for elem in segment:
            col1.append(elem[0])
            col2.append(elem[1])

    data2['Дата'] = col1
    data2['Зміна'] = col2
    data2['Служитель1'] = ''
    data2['Служитель2'] = ''

    data1 = data1.sort_values(by=['Дата', 'Зміна'])
    data2 = data2.sort_values(by=['Дата', 'Зміна'])

    sh = gc.open('Графік Служіння')
    ws1 = sh.add_worksheet('Автостанція ' + new_month + '.' + year)
    ws2 = sh.add_worksheet('Лікарня ' + new_month + '.' + year)
    ws1.set_dataframe(data1, (1, 1))
    ws2.set_dataframe(data2, (1, 1))


# function for inserting data into googlesheet
def insert(date, time, place, name, flag_month):
    cnt = 0
    flg_rec = 0
    sh = gc.open('Графік Служіння')
    ws = sh[place + flag_month]
    msg = ''
    if place == 0:
        ws1 = sh[place + flag_month + 1]
    elif place == 1:
        ws1 = sh[place + flag_month - 1]

    # check date and time in other place for serving and compare that server has been recorded or not
    for row in ws1:
        if (row[2] == name or row[3] == name) and row[0] == date and (row[1] == time or
                                                                      row[1][0:2] <= time[0:2] <= row[1][6:8] or
                                                                      row[1][0:2] <= time[6:8] <= row[1][6:8]):
            flg_rec = 2

    if flg_rec != 2:
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
    else:
        msg = 'Ви вже записані на цю зміну в іншому місці для служіння!'
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


def list_of_partner(place, date, time, name, flag_month):
    sh = gc.open('Графік Служіння')
    ws = sh[flag_month + place]
    partner = ''
    for row in ws:
        if row[0] == date and row[1] == time:
            if row[2] != '' and row[2] != name:
                partner = row[2]
            elif row[3] != '' and row[3] != name:
                partner = row[3]

    return partner