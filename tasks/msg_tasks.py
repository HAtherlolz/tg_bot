import asyncio

from typing import List
from datetime import datetime, timedelta

from telegram.error import TimedOut

from cfg.celery_conf import celery_app
from utils.logs import log

from services.bot import Bot, TGBot
from repositories.mongodb import MessageRepository, UserRepository, UserSchema


@celery_app.task()
def check_msg():
    time_delta = datetime.now() - timedelta(minutes=1)
    log.info(f"time_delta, {time_delta}")

    last_messages = MessageRepository.get_last_message_from_all_group_chats()
    moderators = UserRepository.get_all_moderators()
    moderators_usernames = [moderator.username for moderator in moderators]
    
    advertisers = []
    for last_message in last_messages:
        first_name = last_message.first_name if last_message.first_name else ''
        last_name = last_message.last_name if last_message.last_name else ''

        if (
                (last_message.created_at < time_delta)
                and
                (last_message.username not in moderators_usernames)
                and
                (not last_message.is_notified)
                and
                (
                    ("stark" not in first_name.lower())
                    and
                    (last_name.lower() != "stark")
                )
        ):
            advertisers.append({
                "chat_id": last_message.chat_id,
                "username": last_message.username,
                "name": last_message.name,
            })
            MessageRepository.mark_msg_as_notified(last_message)  # Set msg to notified

    if advertisers:
        # Build the notification message
        notification_message = (
            "These are the advertisers that are waiting for a reply:\n" +
            "\n".join(f"- ADV @{adv['username']} from chat - {adv['name']}" for adv in advertisers)
        )

    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if advertisers:
        loop.run_until_complete(send_msg_to_moderators(moderators, notification_message))


async def send_msg_to_moderators(
        moderators: List[UserSchema],
        notification_message: str
) -> None:
    for moderator in moderators:
        try:
            await Bot.send_message_to_chat(
                moderator.chat_id, notification_message
            )
        except TimedOut as e:
            log.info("Error: ", e)
            log.info("Retrying ...: ", e)
            await Bot.send_message_to_chat(
                moderator.chat_id, notification_message
            )

