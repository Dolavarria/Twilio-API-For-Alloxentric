from pydantic import BaseModel, Field
from typing import Optional


class SMSResponse(BaseModel):
    success: bool
    message_sid: Optional[str] = None
    error: Optional[str] = None
