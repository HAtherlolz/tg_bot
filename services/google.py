from datetime import datetime, timedelta
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
            titles = [
                "Message timestamp", "Cap day", "Affiliate Name", "GEO", "CAP",
                "Start Time", "End Time", "GMT", "CPA Cost", "Notes"
            ]
            worksheet.append_row(titles)
        return worksheet
    
    @classmethod
    def update_sht(cls, data: List):
        gc = gspread.service_account(filename='tg-bot-token.json')
        sht = gc.open_by_key(settings.GGL_SHEET_TOKEN)

        # Generate the worksheet name based on the current day and date
        sheet_name = cls._get_ggl_sheet_name()
        worksheet = cls.get_or_create_worksheet(sht, sheet_name)

        for row in data:
            worksheet.append_row(list(row.values()))

    @classmethod
    def _get_ggl_sheet_name(cls) -> str:
        today = datetime.today()

        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        start_date_str = start_of_week.strftime("%d.%m")
        end_date_str = end_of_week.strftime("%d.%m")

        return f"Mon-Sun {start_date_str[:2]}-{end_date_str}"
