from fastapi import APIRouter, Depends, HTTPException, Form, Request
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from twilio.twiml.messaging_response import MessagingResponse
from models.device import SMSMessage
from models.message import SMSResponse
from models.mongo_models import SMSRecord
from models.incoming_sms import IncomingSMS, IncomingSMSRecord
from database.mongodb import (
    insert_sms_record,
    find_sms_by_number,
    insert_incoming_sms,
    find_incoming_sms_by_number,
    get_all_incoming_sms,
    incoming_sms_collection,
)
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import List

load_dotenv()

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
    """
    Envía un SMS a un número específico
    """
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
        sms_record = {
            "to_number": sms.to_number,
            "message_body": sms.message_body,
            "sent_at": datetime.now(),
            "status": "error",
            "message_sid": None,
            "error": f"Twilio error: {e.msg}",
        }
        insert_sms_record(sms_record)
        return SMSResponse(success=False, error=f"Twilio error: {e.msg}")
    except Exception as e:
        sms_record = {
            "to_number": sms.to_number,
            "message_body": sms.message_body,
            "sent_at": datetime.now(),
            "status": "error",
            "message_sid": None,
            "error": f"Error: {str(e)}",
        }
        insert_sms_record(sms_record)
        return SMSResponse(success=False, error=f"Error: {str(e)}")


@router.post("/webhook/incoming")
async def receive_sms(
    MessageSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    Body: str = Form(...),
    NumMedia: str = Form(default="0"),
    client: Client = Depends(get_twilio_client),
):
    """
    WEBHOOK para recibir SMS entrantes desde Twilio

    Cuando alguien envía un SMS:
    1. Twilio llama a esta ruta automáticamente
    2. Guardamos el mensaje en MongoDB
    3. Enviamos una respuesta automática
    4. Devolvemos TwiML (formato XML que Twilio entiende)
    """
    try:
        print(f"SMS recibido de {From}: {Body}")

        # Guardar el mensaje recibido en MongoDB
        incoming_record = {
            "from_number": From,
            "to_number": To,
            "message_body": Body,
            "received_at": datetime.now().isoformat(),
            "message_sid": MessageSid,
            "auto_reply_sent": False,
            "auto_reply_sid": None,
        }

        insert_incoming_sms(incoming_record)
        print(f"Mensaje guardado en MongoDB")

        # Crear respuesta automática personalizada
        auto_reply_text = f"¡Hola! Recibimos tu mensaje: '{Body}'. Gracias por contactarnos, te responderemos pronto."

        # Enviar respuesta automática usando el cliente de Twilio
        try:
            print(f"Intentando enviar respuesta automática a {From}")

            reply_message = client.messages.create(
                body=auto_reply_text,
                from_=To,
                to=From,
            )

            print(f"Respuesta enviada con SID: {reply_message.sid}")

            # Actualizar el registro en MongoDB
            incoming_sms_collection.update_one(
                {"message_sid": MessageSid},
                {
                    "$set": {
                        "auto_reply_sent": True,
                        "auto_reply_sid": reply_message.sid,
                    }
                },
            )

            print(f"Registro actualizado en MongoDB")

        except TwilioRestException as reply_error:
            print(f"Error de Twilio al enviar respuesta: {reply_error.msg}")
            print(f"   Código de error: {reply_error.code}")
        except Exception as reply_error:
            print(f"Error general al enviar respuesta: {str(reply_error)}")

        resp = MessagingResponse()
        return str(resp)

    except Exception as e:
        print(f"Error procesando SMS entrante: {str(e)}")
        import traceback

        traceback.print_exc()

        resp = MessagingResponse()
        resp.message("Error procesando tu mensaje. Por favor intenta más tarde.")
        return str(resp)


@router.get("/history/sent/{phone_number}", response_model=List[dict])
async def get_sms_history_by_number(phone_number: str):
    """
    Obtiene el historial de mensajes SMS ENVIADOS a un número específico
    """
    return find_sms_by_number(phone_number)


@router.get("/history/received/{phone_number}", response_model=List[dict])
async def get_incoming_sms_by_number(phone_number: str):
    """
    Obtiene el historial de mensajes SMS RECIBIDOS desde un número específico
    """
    return find_incoming_sms_by_number(phone_number)
