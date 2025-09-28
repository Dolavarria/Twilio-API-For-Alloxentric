from fastapi import APIRouter, HTTPException
from models.device import DeviceCreate, DeviceResponse
from database.db_service import db_service
from services.twilio_service import twilio_service

router = APIRouter(
    prefix="/device",
    tags=["Dispositivos"],
)

@router.post("/create", response_model=DeviceResponse)
async def create_device(device: DeviceCreate):
    """Crear dispositivo/canal de comunicación SMS con Twilio"""
    
    try:
        # Verificar disponibilidad de números Twilio
        phone_numbers = twilio_service.list_phone_numbers()
        if not phone_numbers:
            raise HTTPException(status_code=400, detail="No hay números de Twilio disponibles")
        
        # Asignar primer número disponible al dispositivo
        twilio_number = phone_numbers[0]['phone_number']
        
        # Generar estructura de datos para el dispositivo
        device_data = twilio_service.create_device_data(
            device_name=device.device_name,
            device_description=device.device_description,
            twilio_number=twilio_number
        )
        
        # Persistir dispositivo en MongoDB
        device_id = db_service.create_device(device_data)
        
        return DeviceResponse(
            message="Dispositivo creado exitosamente",
            device_id=device_id,
            device_webhook=device_data["device_webhook"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando dispositivo: {str(e)}")
