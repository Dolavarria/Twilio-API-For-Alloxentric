from fastapi import APIRouter, HTTPException
import httpx
import os
from models.message import (
    MessageReceiveRequest, 
    MessageReceiveResponse, 
    ProcessedMessageData,
    MessageSendRequest,
    MessageSendResponse
)
from database.db_service import db_service
from services.twilio_service import twilio_service

router = APIRouter(
    prefix="/message",
    tags=["Mensajes"],
)

@router.post("/receive", response_model=MessageReceiveResponse)
async def receive_message(message_request: MessageReceiveRequest):
    """Procesar mensaje entrante desde webhook de Twilio"""
    try:
        # Validar existencia del dispositivo por webhook
        device = db_service.get_device_by_webhook(message_request.device_webhook)
        if not device:
            raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
        
        # Persistir mensaje recibido en MongoDB
        message_log_id = db_service.log_received_message({
            "device_webhook": message_request.device_webhook,
            "contact_account": message_request.data.message_sender,
            "message_content": message_request.data.message_content,
            "raw_data": message_request.dict()
        })
        
        # Convertir a formato estándar para sistema de flujo de conversación
        processed_data = ProcessedMessageData(
            channel_account=message_request.device_webhook,
            contact_account=message_request.data.message_sender,
            id_contact=message_request.data.message_sender,
            contact_message=message_request.data.message_content
        )
        
        # Enviar a endpoint externo si está configurado
        external_endpoint = os.getenv("EXTERNAL_MESSAGE_ENDPOINT")
        if external_endpoint:
            try:
                # Enviar datos procesados al sistema de flujo de conversación
                async with httpx.AsyncClient() as client:
                    await client.post(
                        external_endpoint,
                        json=processed_data.dict(),
                        timeout=10.0
                    )
            except Exception:
                # Continuar si el endpoint externo no está disponible
                pass
        
        # Marcar como procesado
        db_service.mark_as_processed(message_log_id)
        
        return MessageReceiveResponse()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando mensaje: {str(e)}")

@router.post("/send", response_model=MessageSendResponse)
async def send_message(message_request: MessageSendRequest):
    """Enviar SMS a través del dispositivo Twilio especificado"""
    try:
        # Validar existencia del dispositivo
        device = db_service.get_device_by_webhook(message_request.device_webhook)
        if not device:
            raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
        
        # Extraer número de teléfono del dispositivo
        from_number = device.get("device_number")
        if not from_number:
            raise HTTPException(status_code=400, detail="Dispositivo no tiene número configurado")
        
        # Ejecutar envío de SMS a través de Twilio
        message_sid = twilio_service.send_message(
            from_number=from_number,
            to_number=message_request.contact_account,
            message_body=message_request.message
        )
        
        if not message_sid:
            raise HTTPException(status_code=500, detail="Error enviando mensaje")
        
        # Registrar mensaje enviado en historial
        db_service.log_sent_message(
            device_webhook=message_request.device_webhook,
            contact_account=message_request.contact_account,
            message=message_request.message,
            external_id=message_sid,
            status="sent"
        )
        
        return MessageSendResponse(message=f"Mensaje enviado. ID: {message_sid}")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enviando mensaje: {str(e)}")
