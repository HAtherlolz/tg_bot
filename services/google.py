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
                "Start Time", "End Time", "GMT", "CPA Cost", "Notes", "message_id"
            ]
            worksheet.append_row(titles)
        return worksheet
    
    @classmethod
    def update_sht(cls, data: List):
        gc = gspread.service_account(filename='tg-bot-token.json')
        sht = gc.open_by_key(settings.GGL_SHEET_TOKEN)
        
        caps_date = data[0].get("Cap day")
        if datetime.today() < datetime.strptime(caps_date, "%Y-%m-%d"):
            caps_tomorrow = True
            print("Caps for tomorrow")
        else:
            caps_tomorrow = False
            print("Caps for today")

        # Generate the worksheet name based on the current day and date
        sheet_name = cls._get_ggl_sheet_name(caps_tomorrow)
        worksheet = cls.get_or_create_worksheet(sht, sheet_name)

        for row in data:
            worksheet.append_row(list(row.values()))
    
    @classmethod
    def update_row_in_sht(cls, data: List):
        gc = gspread.service_account(filename='tg-bot-token.json')
        sht = gc.open_by_key(settings.GGL_SHEET_TOKEN)
        
        # Get all the worksheets in the spreadsheet
        sheets = sht.worksheets()

        # Loop through the sheets in reverse order
        log.info(f"DATA: {data}")
        
        for sheet in reversed(sheets):
            log.info(f"Sheet: {sheet.title}")
            try:
                # Find all cells containing the message_id in column K (11)
                cells = sheet.findall(str(data[0].get('message_id')), in_column=11)
                if cells and len(cells) == len(data):
                    cell_counter = 0
                    for cell in cells:
                        sheet.update(f'A{cell.row}:K{cell.row}', [list(data[cell_counter].values())])
                        cell_counter += 1
                break
            except Exception as e:
                log.error(f"Error processing sheet {sheet.title}: {e}")

    @classmethod
    def _get_ggl_sheet_name(cls, caps_tomorrow: bool) -> str:
        if caps_tomorrow:
            today = datetime.today() + timedelta(days=1)
        else:
            today = datetime.today()

        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        start_date_str = start_of_week.strftime("%d.%m")
        end_date_str = end_of_week.strftime("%d.%m")

        return f"Mon-Sun {start_date_str[:2]}-{end_date_str}"
