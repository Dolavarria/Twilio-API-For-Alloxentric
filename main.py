from fastapi import FastAPI
from routes import sms
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SMS Sender API",
    description="API para enviar mensajes SMS vía Twilio y almacenarlos en MongoDB",
    version="0.2.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sms.router)


@app.get("/")
async def root():
    return {
        "message": "Bienvenido a la API de envío de SMS",
        "documentation": "/docs",
        "endpoints": {
            "send_sms": "/sms/send",
            "sms_history_by_number": "/sms/history/{phone_number}",
        },
    }
