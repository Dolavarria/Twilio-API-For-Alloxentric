from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class MessageData(BaseModel):
    """Modelo para los datos del mensaje recibido de CloudCall"""
    message_sender: str
    message_content: str
    class Config:
        extra = "allow" 

class MessageReceiveRequest(BaseModel):
    """Modelo para la solicitud de recepción de mensaje"""
    device_webhook: str
    data: MessageData

class MessageReceiveResponse(BaseModel):
    """Modelo para la respuesta al recibir un mensaje"""
    message: str = "Mensaje recibido"

class ProcessedMessageData(BaseModel):
    """Modelo para los datos procesados que se enviarán a otro endpoint"""
    #contact valor constante
    transmitter: str = "contact"
    #sms valor constante
    channel: str = "sms"
    #channel_account se asigna device_webhook en routes/message.py
    channel_account: str
    #channel_settings se inicializa como diccionario (dict)
    #acepta string como clave y cualquier tipo de dato como valor
    #field es para inicializar con un diccionario vacío por defecto
    channel_settings: Dict[str, Any] = Field(default_factory=dict)
    #contact_account asigna message_sender en routes/message.py
    contact_account: str
    #id_contact asigna message_sender en routes/message.py
    id_contact: str
    #contact_details es opcional y puede ser None
    contact_details: Optional[str] = None
    type_message: str = "new_message"
    contact_message_event: Optional[str] = None
    #contact_message asigna message_content en routes/message.py
    contact_message: str
    action: Optional[str] = None
    id_file: Optional[str] = None
    contact_message_metadata: Dict[str, Any] = Field(default_factory=dict)

class MessageSendRequest(BaseModel):
    """Modelo para la solicitud de envío de mensaje"""
    device_webhook: str
    contact_account: str
    message: str

class MessageSendResponse(BaseModel):
    """Modelo para la respuesta al enviar un mensaje"""
    message: str = "Mensaje enviado"
