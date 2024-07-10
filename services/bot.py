import re

from typing import List, Dict, Union

from telegram import Update
from telegram.ext import ContextTypes

from utils.logs import log


class Bot:
    @classmethod
    async def handle_message(
            cls,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE,
    ):
        chat_id = update.message.chat_id
        text = update.message.text

        if text.startswith('#'):
            log.info(f"Message from chat {chat_id}: {text}")
            parsed_msg = cls.message_parser(msg=text)

            log.info(f"Parsed message: {parsed_msg}")

    @staticmethod
    def message_parser(msg: str) -> Dict:

        title = msg.split(" ")[0]
        title = title[1:-4]
        log.info(f"title: {title}")

        pattern = re.compile(
            r"(?P<country>[A-Z]{2}) - Total (?P<total_caps>\d+) cap - "
            r"(?P<start_time>\d{2}:\d{2}) - (?P<end_time>\d{2}:\d{2})( gmt \+ \d+)?"
        )

        res = {"title": title, "data": []}

        for match in pattern.finditer(msg):

            res["data"].append({
                "country": match.group("country"),
                "total_caps": match.group("total_caps"),
                "start_time": match.group("start_time"),
                "end_time": match.group("end_time"),
                "time_zone": match.group(5) if match.group(5) else None  # Optional time zone
            })

        return res

