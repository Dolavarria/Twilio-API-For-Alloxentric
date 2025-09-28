from pydantic import BaseModel
from typing import Optional

class DeviceCreate(BaseModel):
    """Modelo para crear un nuevo dispositivo/canal de comunicación"""
    device_name: str
    device_description: str
    
    class Config:
        extra = "allow"

class DeviceResponse(BaseModel):
    """Modelo para la respuesta al crear un dispositivo"""
    message: str = "Dispositivo creado exitosamente"
    device_id: Optional[str] = None
    device_webhook: Optional[str] = None
