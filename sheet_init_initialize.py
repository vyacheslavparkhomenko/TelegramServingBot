import pygsheets
import datetime
import pandas as pd

time_slots = [{
    1: ['10:00-12:00', '12:00-14:00'],
    5: ['09:00-11:00', '11:00-13:00']
}
,{
    1: ['08:00-10:00', '10:00-12:00', '12:00-14:00'],
    5: ['08:00-10:00', '10:00-12:00', '12:00-14:00']
}]

table_name = 'Тест'

# token for google sheets
gc = pygsheets.authorize(service_account_file='token.json')


def get_weekday(date):
    weekday = datetime.datetime.strptime(date, '%d.%m.%Y').weekday()
    return weekday


new_month = datetime.date.today().month
year = str(datetime.date.today().year)

if new_month % 2 == 0 and new_month not in (8, 2):
    max_day = 30
elif new_month == 2:
    max_day = 28
else:
    max_day = 31

new_month = '0' + str(new_month) if new_month < 10 else str(new_month)
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

sh = gc.open(table_name)
ws1 = sh.add_worksheet('Автостанція')
ws2 = sh.add_worksheet('Лікарня')
ws1.set_dataframe(data1, (1, 1))
ws2.set_dataframe(data2, (1, 1))