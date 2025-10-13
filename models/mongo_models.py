from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class SMSRecord(BaseModel):
    to_number: str
    message_body: str
    sent_at: datetime = Field(default_factory=datetime.now)
    status: str
    message_sid: Optional[str] = None
    error: Optional[str] = None
