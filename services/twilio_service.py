import uuid
from typing import Optional, Dict, Any
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from config.settings import settings

class TwilioService:
    """Servicio para integrar con Twilio SMS"""
    
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.client = None
        
        # Inicializar cliente Twilio si las credenciales están disponibles
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
    
    def is_configured(self) -> bool:
        """Verificar si Twilio está configurado"""
        return self.client is not None
    
    def create_device_data(self, device_name: str, device_description: str, 
                          twilio_number: str) -> Dict[str, Any]:
        """Crear estructura de datos del dispositivo para MongoDB"""
        # Generar webhook único para el dispositivo
        device_webhook = str(uuid.uuid4())
        
        return {
            "device_name": device_name,
            "device_description": device_description,
            "device_webhook": device_webhook,
            "device_number": twilio_number,
            "device_account": {
                "account_sid": self.account_sid,
                "auth_token": self.auth_token
            },
            "platform": "twilio",
            "status": "active"
        }
    
    def send_message(self, from_number: str, to_number: str, message_body: str) -> Optional[str]:
        """Enviar SMS a través de Twilio y retornar SID del mensaje"""
        if not self.client:
            raise Exception("Cliente de Twilio no configurado")
        
        try:
            # Enviar mensaje SMS usando la API de Twilio
            message = self.client.messages.create(
                body=message_body,
                from_=from_number,
                to=to_number
            )
            return message.sid
        except TwilioException as e:
            raise Exception(f"Error enviando mensaje con Twilio: {e}")
    
    def list_phone_numbers(self) -> list:
        """Obtener lista de números de teléfono disponibles en la cuenta"""
        if not self.client:
            return []
        
        try:
            # Obtener números de teléfono configurados en Twilio
            phone_numbers = self.client.incoming_phone_numbers.list()
            return [
                {
                    "sid": number.sid,
                    "phone_number": number.phone_number,
                    "friendly_name": number.friendly_name
                }
                for number in phone_numbers
            ]
        except TwilioException:
            return []

# Instancia global del servicio
twilio_service = TwilioService()
