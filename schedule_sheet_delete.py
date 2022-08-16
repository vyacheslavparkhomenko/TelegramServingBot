import gsheet
import datetime

current_date = datetime.date.today().day
current_month = datetime.date.today().month
date_update = 24
if current_month % 2 == 0 and current_month not in (8, 2):
    max_current_date = 30
elif current_month == 2:
    max_current_date = 28
else:
    max_current_date = 31

gsheet.sheet_delete(current_date, max_current_date)