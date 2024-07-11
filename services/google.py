from datetime import datetime
from typing import List

import gspread

from utils.logs import log
from cfg.config import settings


class Google:
    
    @staticmethod
    def get_data_from_google_sheet():
        gc = gspread.service_account(filename='tg-bot-token.json')
        sht = gc.open_by_key(settings.GGL_SHEET_TOKEN)
        worksheet = sht.get_worksheet(0)
        list_of_lists = worksheet.get_all_records()
        log.info(list_of_lists)

    @classmethod
    def get_or_create_worksheet(cls, sht, sheet_name):
        try:
            worksheet = sht.worksheet(sheet_name)
            log.info(f"Worksheet '{sheet_name}' found.")
        except gspread.exceptions.WorksheetNotFound:
            worksheet = sht.add_worksheet(title=sheet_name, rows="100", cols="20")
            log.info(f"Worksheet '{sheet_name}' created.")

            # Adding titles to the newly created worksheet
            titles = ["Affiliate Name", "GEO", "CAP", "Start Time", "End Time", "GMT", "CPA Cost", "Notes"]
            worksheet.append_row(titles)
        return worksheet
    
    @classmethod
    def update_sht(cls, data: List):
        gc = gspread.service_account(filename='tg-bot-token.json')
        sht = gc.open_by_key(settings.GGL_SHEET_TOKEN)

        # Generate the worksheet name based on the current day and date
        sheet_name = datetime.now().strftime("%A-%d-%m-%y")

        worksheet = cls.get_or_create_worksheet(sht, sheet_name)

        for row in data:
            worksheet.append_row(list(row.values()))
