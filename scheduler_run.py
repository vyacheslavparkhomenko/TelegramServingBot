import schedule
import gsheet
import datetime

date_update = 24


schedule.every().day.at("20:30").do(gsheet.sheet_reinitialize, date_update)
schedule.every().day.at("20:30").do(gsheet.sheet_delete)

while True:
    schedule.run_pending()