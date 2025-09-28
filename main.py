from fastapi import FastAPI
from routes.device import router as device_router
from routes.message import router as message_router
from database.db_service import db_service
from services.twilio_service import twilio_service

# Crear aplicación FastAPI con documentación automática
app = FastAPI(
    title="API de Mensajería SMS",
    description="API para envío y recepción de SMS usando Twilio",
    version="1.0.0"
)

# Registrar rutas de endpoints
app.include_router(device_router)  # /device/*
app.include_router(message_router)  # /message/*

@app.get("/")
def read_root():
    """Endpoint de estado de la API y servicios conectados"""
    return {
        "message": "API de Mensajería SMS",
        "version": "1.0.0",
        "status": {
            "database": "connected",
            "twilio": "configured" if twilio_service.is_configured() else "not_configured"
        }
    }
