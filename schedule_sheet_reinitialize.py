import gsheet
import datetime

current_date = datetime.date.today().day
gsheet.sheet_reinitialize(current_date, 24)