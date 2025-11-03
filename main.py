from fastapi import FastAPI
from routes import sms, phone_numbers
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SMS Sender API",
    description="API para enviar mensajes SMS vía Twilio y almacenarlos en MongoDB",
    version="0.4.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sms.router)
app.include_router(phone_numbers.router)


@app.get("/")
async def root():
    return {
        "message": "Bienvenido a la API de envío de SMS",
        "documentation": "/docs",
        "endpoints": {
            "send_sms": "/sms/send",
            "receive_sms_webhook": "/sms/webhook/incoming",
            "sent_history": "/sms/history/sent/{phone_number}",
            "received_history": "/sms/history/received/{phone_number}",
            "search_numbers": "/phone-numbers/search",
            "purchase_number": "/phone-numbers/purchase",
            "my_numbers": "/phone-numbers/my-numbers",
            "release_number": "/phone-numbers/{phone_number_sid}",
        },
    }
