import asyncio
from datetime import datetime, timedelta
from typing import List
from zoneinfo import ZoneInfo

from telegram import Update
from telegram.ext import ContextTypes, CallbackContext
from telegram.error import NetworkError

from utils.logs import log
from services.google import Google


class Bot:
    MAX_RETRIES = 3  # Set the maximum number of retries
    RETRY_DELAY = 5  # Delay between retries in seconds

    @classmethod
    async def handle_message(
            cls,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        if update.edited_message is not None:
            log.info(f"Received update with ID: {update.update_id}")
            log.info(f"Updated message: {update.edited_message.text}")
            
            chat_id = update.edited_message.chat_id
            message_id = update.edited_message.message_id
            text = update.edited_message.text
            
            utc_date_time = update.edited_message.date
            gmt_plus_3 = ZoneInfo('Etc/GMT-3')  # 'Etc/GMT-3' corresponds to GMT+3
            local_date_time = utc_date_time.astimezone(gmt_plus_3)

            date_time = local_date_time.strftime('%Y-%m-%d %H:%M')

            if text.startswith('#'):
                log.info(f"Message from chat {chat_id}: \n{text}\n---------------------")
                parsed_msg = cls.message_parser(
                    msg=text,
                    date_time=date_time,
                    message_id=message_id
                )
                # log.info(f"Parsed message: {parsed_msg}")

                Google.update_row_in_sht(parsed_msg)
        
        else:
            if update.message is None:
                log.info("Received an update without message")
                return

            chat_id = update.message.chat_id
            message_id = update.message.message_id
            text = update.message.text

            utc_date_time = update.message.date
            gmt_plus_3 = ZoneInfo('Etc/GMT-3')  # 'Etc/GMT-3' corresponds to GMT+3
            local_date_time = utc_date_time.astimezone(gmt_plus_3)

            date_time = local_date_time.strftime('%Y-%m-%d %H:%M')

            if text.startswith('#'):
                log.info(f"Message from chat {chat_id}: \n{text}\n---------------------")
                parsed_msg = cls.message_parser(
                    msg=text,
                    date_time=date_time,
                    message_id=message_id
                )
                # log.info(f"Parsed message: {parsed_msg}")

                Google.update_sht(parsed_msg)

    @classmethod
    def message_parser(cls, msg: str, date_time: str, message_id: str) -> List:
        res: List = list()
        msg: List = msg.split("\n")

        # Check if the second row contains the word "tomorrow"
        if len(msg) > 1 and "tomorrow" in msg[1].lower():
            caps_date = cls.parse_date(date_time, True)
            log.info("Is for tomorrow?: Yes")
        else:
            caps_date = cls.parse_date(date_time, False)
            log.info("Is for tomorrow?: No")

        for line in msg:
            if "#" in line:
                title = line.strip().lstrip("#")[:-4]
            elif (line.count("-") == 0 or line.count("-") == 1) and ("total" not in line.lower()):
                continue
            elif "-" in line:
                l = [x.strip() for x in line.split("-")]
                res_t = {
                    "Message timestamp": date_time,
                    "Cap day": caps_date,
                    "title": title,
                    "country": None,
                    "total_caps": None,
                    "start_time": None,
                    "end_time": None,
                    "time_zone": None,
                    "cpa": None,
                    "note": None,
                    "message_id": message_id
                }
                for i in l:
                    if i == l[0] and ("Total" not in i or "total" not in i):
                        res_t["country"] = i.strip()
                    elif "Total" in i or "total" in i:
                        res_t["total_caps"] = i.split(" ")[1]
                    elif (":" in i or "." in i or ";" in i) and "gmt" not in i.lower():
                        res_t["start_time"] = i.strip()
                    elif (":" in i or "." in i or ";" in i) and "gmt" in i.lower():
                        res_t["end_time"] = i.strip().split(" ", 1)[0]
                        res_t["time_zone"] = i.strip().split(" ", 1)[1]
                    elif res_t.get("time_zone") is not None and i == l[-2]:
                        res_t["cpa"] = i.strip()
                    elif res_t.get("time_zone") is not None and i == l[-1]:
                        res_t["note"] = i.strip()
                    elif res_t.get("time_zone") is None and i == l[-2]:
                        res_t["cpa"] = i.strip()
                    elif res_t.get("time_zone") is None and i == l[-1]:
                        res_t["note"] = i.strip()
                res.append(res_t)
        return res

    @staticmethod
    def parse_date(date_time: str, is_tomorrow: bool) -> str:
        """
            Parsing str of datetime to change structure
            and if it's tomorrow it will add one more day
        """
        datetime_obj = datetime.strptime(date_time, "%Y-%m-%d %H:%M")
        if is_tomorrow:
            datetime_obj = datetime_obj + timedelta(days=1)
        new_datetime_str = datetime_obj.strftime("%Y-%m-%d")
        return new_datetime_str

    @staticmethod
    async def error_handler(update: object, context: CallbackContext):
        """Log the error and handle it gracefully."""
        log.error(f"ERROR HANDLER! An error occurred: {context.error}")
        
        # Handle specific network errors
        if isinstance(context.error, NetworkError):
            log.warning("A network error occurred. Attempting retries...")

            # Retrieve the update and context from the failed attempt
            update = context.update

            for attempt in range(1, Bot.MAX_RETRIES + 1):
                try:
                    await Bot.handle_message(update, context)
                    log.info(f"Retry attempt {attempt} successful.")
                    break
                except NetworkError as e:
                    log.warning(f"Retry attempt {attempt} failed: {e}")
                    if attempt == Bot.MAX_RETRIES:
                        log.error("Max retries reached. Could not recover from the network error.")
                    else:
                        await asyncio.sleep(Bot.RETRY_DELAY)
