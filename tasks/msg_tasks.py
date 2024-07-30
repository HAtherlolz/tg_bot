from datetime import datetime, timedelta

from cfg.celery_conf import celery_app

from services.bot import Bot
from repositories.mongodb import MessageRepository, UserRepository


@celery_app.task()
def check_msg():
    time_delta = datetime.now() - timedelta(minutes=15)

    last_messages = MessageRepository.get_last_message_from_all_group_chats()
    moderators = UserRepository.get_all_moderators()
    moderators_usernames = [moderator.username for moderator in moderators]
    
    advertisers = []
    for last_message in last_messages:
        if last_message.created_at < time_delta and not last_message.username in moderators_usernames:
            advertisers.append(f"ADV name {last_message.name}")

    notification_message = (
        "These are the advertisers that are waiting for a reply:\n" +
        "\n".join(advertisers)
    )
    
    for moderator in moderators:
        Bot.send_message_to_chat(moderator.chat_id, notification_message)
