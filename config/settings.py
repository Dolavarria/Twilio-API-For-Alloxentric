import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Configuración global de la aplicación"""
    
    # Configuración de MongoDB
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "sms_api")
    
    # Configuración de Twilio
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    
    # Configuración de la API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_RELOAD: bool = os.getenv("API_RELOAD", "true").lower() == "true"
    
    # Endpoint externo para procesar mensajes
    EXTERNAL_MESSAGE_ENDPOINT: str = os.getenv("EXTERNAL_MESSAGE_ENDPOINT", "")
    
    def is_twilio_configured(self) -> bool:
        """Verificar si Twilio está configurado"""
        return bool(self.TWILIO_ACCOUNT_SID and self.TWILIO_AUTH_TOKEN)
    
    def get_twilio_config(self) -> dict:
        """Obtener configuración de Twilio"""
        return {
            "account_sid": self.TWILIO_ACCOUNT_SID,
            "auth_token": self.TWILIO_AUTH_TOKEN
        }

# Instancia global de configuración
settings = Settings()
