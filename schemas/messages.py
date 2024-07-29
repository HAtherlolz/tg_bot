from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class MessageSchema(BaseModel):
    chat_id: Optional[int]
    name: Optional[str]
    message: Optional[str]
    username: Optional[str]
    created_at: datetime
