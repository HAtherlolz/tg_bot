import re

from typing import List

from telegram import Update
from telegram.ext import ContextTypes

from utils.logs import log
from services.google import Google


class Bot:
    @classmethod
    async def handle_message(
            cls,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        chat_id = update.message.chat_id
        text = update.message.text

        date_time = str(update.message.date)[:16]

        if text.startswith('#'):
            log.info(f"Message from chat {chat_id}: {text}")
            parsed_msg = cls.message_parser(msg=text, date_time=date_time)
            log.info(f"Parsed message: {parsed_msg}")

            Google.update_sht(parsed_msg)

    @staticmethod
    def message_parser(msg: str, date_time: str) -> List:
        res = list()
        title = msg.split(" ")[0]
        title = title[1:-4]
        log.info(f"title: {title}")

        pattern = re.compile(
            r"(?P<country>[A-Z]{2}(?: [A-Z]{2})?) - Total (?P<total_caps>\d+) cap"
            r"( - (?P<start_time>\d{2}:\d{2}) - (?P<end_time>\d{2}:\d{2})( gmt \+ \d+)?)?"
            r"( - (?P<cpa>.*))?",
            re.IGNORECASE
        )

        for match in pattern.finditer(msg):
            res.append({
                "date": date_time,
                "title": title,
                "country": match.group("country"),
                "total_caps": match.group("total_caps"),
                "start_time": match.group("start_time"),
                "end_time": match.group("end_time"),
                "time_zone": match.group(5).strip(" ") if match.group(5) else None,  # Optional time zone
                "cpa": match.group("cpa").split("\n")[0].split("-")[0] if match.group("cpa") else None,  # Optional note
                "note": match.group("cpa").split("\n")[0].split("-")[1] if match.group("cpa") else None  # Optional note
            })
        return res

