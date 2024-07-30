import asyncio

from typing import List
from datetime import datetime, timedelta

from cfg.celery_conf import celery_app

from services.bot import Bot
from repositories.mongodb import MessageRepository, UserRepository, UserSchema


@celery_app.task()
def check_msg():
    time_delta = datetime.now() - timedelta(minutes=15)

    last_messages = MessageRepository.get_last_message_from_all_group_chats()
    moderators = UserRepository.get_all_moderators()
    moderators_usernames = [moderator.username for moderator in moderators]
    
    advertisers = []
    for last_message in last_messages:
        if (
                (last_message.created_at < time_delta)
                and
                (last_message.username not in moderators_usernames)
                and
                (not last_message.is_notified)
        ):
            advertisers.append(f"ADV name {last_message.name}")
            MessageRepository.mark_msg_as_notified(last_message)  # Set msg to notified

    notification_message = (
        "These are the advertisers that are waiting for a reply:\n" +
        "\n".join(advertisers)
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
        await Bot.send_message_to_chat(
            moderator.chat_id, notification_message
        )
