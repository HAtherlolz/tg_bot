from typing import List
from zoneinfo import ZoneInfo

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

        utc_date_time = update.message.date
        gmt_plus_3 = ZoneInfo('Etc/GMT-3')  # 'Etc/GMT-3' corresponds to GMT+3
        local_date_time = utc_date_time.astimezone(gmt_plus_3)

        date_time = local_date_time.strftime('%Y-%m-%d %H:%M')

        if text.startswith('#'):
            log.info(f"Message from chat {chat_id}: {text}")
            parsed_msg = cls.message_parser(msg=text, date_time=date_time)
            log.info(f"Parsed message: {parsed_msg}")

            Google.update_sht(parsed_msg)

    @staticmethod
    def message_parser(msg: str, date_time: str) -> List:
        res = list()
        msg = msg.split("\n")
        for line in msg:
            if "#" in line:
                title = line.strip().lstrip("#")[:-4]
            elif (line.count("-") == 0 or line.count("-") == 1) and ("total" not in line.lower()):
                continue
            elif "-" in line:
                l = [x.strip() for x in line.split("-")]
                print(l)
                res_t = {
                    "Message timestamp": date_time,
                    "Cap day": date_time,
                    "title": title,
                    "country": None,
                    "total_caps": None,
                    "start_time": None,
                    "end_time": None,
                    "time_zone": None,
                    "cpa": None,
                    "note": None
                }
                for i in l:
                    if i == l[0] and ("Total" not in i or "total" not in i):
                        res_t["country"] = i.strip()
                    elif "Total" in i or "total" in i:
                        res_t["total_caps"] = i.split(" ")[1]
                    elif ":" in i and "gmt" not in i:
                        res_t["start_time"] = i.strip()
                    elif ":" in i and "gmt" in i:
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

        # title = msg.split(" ")[0]
        # title = title[1:-4]
        # log.info(f"title: {title}")
        
        # pattern = re.compile(
        #     r"(?P<country>[A-Z]{2}(?: [A-Z]{2})?) - Total (?P<total_caps>\d+) cap"
        #     r"( - (?P<start_time>\d{2}:\d{2}) - (?P<end_time>\d{2}:\d{2})( gmt \+ \d+)?)?"
        #     r"( - (?P<cpa>.*))?",
        #     re.IGNORECASE
        # )

        # for match in pattern.finditer(msg):
        #     res.append({
        #         "date": date_time,
        #         "title": title,
        #         "country": match.group("country"),
        #         "total_caps": match.group("total_caps"),
        #         "start_time": match.group("start_time"),
        #         "end_time": match.group("end_time"),
        #         "time_zone": match.group(5).strip(" ") if match.group(5) else None,  # Optional time zone
        #         "cpa": match.group("cpa").split("\n")[0].split("-")[0] if match.group("cpa") else None,  # Optional note
        #         "note": match.group("cpa").split("\n")[0].split("-")[1] if match.group("cpa") else None  # Optional note
        #     })