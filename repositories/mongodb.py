from typing import List

from pymongo.collection import Collection

from schemas.chats import ChatSchema
from schemas.messages import MessageSchema

from cfg.database import msg_db, chat_db


class ChatRepository:
    db: Collection = chat_db

    @classmethod
    def get_chats_by_id(cls, chat_id: int) -> List[ChatSchema]:
        chats = cls.db.find({"chat_id": chat_id})
        return [ChatSchema(**chat) for chat in chats]

    @classmethod
    def create_chat(cls, chat: ChatSchema) -> bool:
        chats = cls.get_chats_by_id(chat.chat_id)
        if chats:
            return False

        if chat.chat_id < 0:  # Group chats have negative ids
            cls.db.insert_one(chat.dict())
            return True

        return False


class MessageRepository:
    db: Collection = msg_db

    @classmethod
    def get_msgs_by_id(cls, chat_id: int) -> List[MessageSchema]:
        msgs = cls.db.find({"chat_id": chat_id})
        return [MessageSchema(**msg) for msg in msgs]

    @classmethod
    def create_msg(cls, msg: MessageSchema) -> bool:
        cls.db.insert_one(msg.dict())
        return True
