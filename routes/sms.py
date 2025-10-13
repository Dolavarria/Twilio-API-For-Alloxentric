from fastapi import APIRouter, Depends, HTTPException
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from models.device import SMSMessage
from models.message import SMSResponse
from models.mongo_models import SMSRecord
from database.mongodb import insert_sms_record, find_sms_by_number
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import List

load_dotenv()  # cargar datos de env

router = APIRouter(
    prefix="/sms",
    tags=["SMS"],
    responses={404: {"description": "Not found"}},
)


def get_twilio_client():
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")

    if not account_sid or not auth_token:
        raise HTTPException(status_code=500, detail="Twilio credentials not configured")

    return Client(account_sid, auth_token)


@router.post("/send", response_model=SMSResponse)
async def send_sms(sms: SMSMessage, client: Client = Depends(get_twilio_client)):
    try:
        from_number = os.getenv("TWILIO_PHONE_NUMBER")

        if not from_number:
            raise HTTPException(
                status_code=500, detail="Twilio phone number not configured"
            )

        message = client.messages.create(
            body=sms.message_body, from_=from_number, to=sms.to_number
        )

        # Crear un registro para MongoDB
        sms_record = {
            "to_number": sms.to_number,
            "message_body": sms.message_body,
            "sent_at": datetime.now(),
            "status": "sent",
            "message_sid": message.sid,
            "error": None,
        }

        # Guardar en MongoDB
        insert_sms_record(sms_record)

        return SMSResponse(success=True, message_sid=message.sid)

    except TwilioRestException as e:
        # Registrar el error también
        sms_record = {
            "to_number": sms.to_number,
            "message_body": sms.message_body,
            "sent_at": datetime.now(),
            "status": "error",
            "message_sid": None,
            "error": f"Twilio error: {e.msg}",
        }

        # Guardar el error en MongoDB
        insert_sms_record(sms_record)

        return SMSResponse(success=False, error=f"Twilio error: {e.msg}")
    except Exception as e:
        # Registrar cualquier otro error
        sms_record = {
            "to_number": sms.to_number,
            "message_body": sms.message_body,
            "sent_at": datetime.now(),
            "status": "error",
            "message_sid": None,
            "error": f"Error: {str(e)}",
        }

        # Guardar el error en MongoDB
        insert_sms_record(sms_record)

        return SMSResponse(success=False, error=f"Error: {str(e)}")


@router.get("/history/{phone_number}", response_model=List[dict])
async def get_sms_history_by_number(phone_number: str):
    """
    Obtiene el historial de mensajes SMS enviados a un número específico
    """
    return find_sms_by_number(phone_number)
