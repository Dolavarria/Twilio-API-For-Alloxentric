from pydantic import BaseModel, Field


class SMSMessage(BaseModel):
    to_number: str = Field(
        ...,
        description="Phone number to send the message to, in E.164 format (e.g., +1234567890)",
    )
    message_body: str = Field(..., description="The content of the SMS message")
