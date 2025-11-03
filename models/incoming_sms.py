from pydantic import BaseModel, Field
from typing import Optional


# MODELO PARA RECIBIR SMS DESDE TWILIO (Webhook)
class IncomingSMS(BaseModel):
    """
    Modelo para validar los datos que Twilio envía al webhook cuando se recibe un SMS

    Este modelo representa los campos que Twilio envía en su petición HTTP
    POST cuando alguien manda un mensaje.

    Uso:
        - FastAPI valida automáticamente que Twilio envíe todos los campos requeridos
        - Los campos opcionales tienen valores por defecto
        - Si falta un campo requerido (...), FastAPI retorna error 422

    Ejemplo de datos que llegan de Twilio:
        {
            "MessageSid": "SM1234567890abcdef1234567890abcdef",
            "From": "+56984731209",
            "To": "+18153965488",
            "Body": "Hola, necesito ayuda",
            "NumMedia": "0"
        }
    """

    # Field(...): El "..." significa que el campo es OBLIGATORIO (no tiene valor por defecto)
    MessageSid: str = Field(
        ...,
        description="ID único del mensaje en Twilio (formato: SM + 32 caracteres hexadecimales)",
        examples=["SM1234567890abcdef1234567890abcdef"],
    )

    From: str = Field(
        ...,
        description="Número de teléfono que envió el mensaje (formato +[código_país][número])",
        examples=["+56943318531", "+18005551234"],
    )

    # To: El número de Twilio que recibió el mensaje
    To: str = Field(
        ...,
        description="Número de Twilio que recibió el mensaje",
        examples=["+18153965488"],
    )

    # Body: El contenido del mensaje de texto
    Body: str = Field(
        ...,
        description="Contenido del mensaje de texto enviado por el usuario",
        examples=["Hola, necesito información", "¿Están abiertos?"],
    )

    # NumMedia: Campo OPCIONAL que indica cuántas imágenes/videos vienen adjuntos
    # default="0": Si Twilio no lo envía, asume que son 0 archivos multimedia
    # Optional[str]: Puede ser string o None
    NumMedia: Optional[str] = Field(
        default="0",
        description="Número de archivos multimedia (imágenes/videos) adjuntos al mensaje (0 para SMS simple)",
        examples=["0", "1", "2"],
    )


class IncomingSMSRecord(BaseModel):
    """
    Modelo para almacenar SMS recibidos en la base de datos MongoDB

    Uso:
        - Se crea después de recibir un IncomingSMS del webhook
        - Se convierte a diccionario antes de insertar en MongoDB

    Ejemplo de documento:
        {
            "from_number": "+56984731209",
            "to_number": "+18153965488",
            "message_body": "Hola, necesito ayuda",
            "received_at": "2025-11-01T12:00:00",
            "message_sid": "SM1234567890abcdef",
            "auto_reply_sent": true,
            "auto_reply_sid": "SM9876543210fedcba"
        }
    """

    from_number: str = Field(
        ...,
        description="Número de teléfono que envió el mensaje (origen del SMS)",
        examples=["+56984731209", "+18005551234"],
    )

    to_number: str = Field(
        ...,
        description="Número de Twilio que recibió el mensaje (destino del SMS)",
        examples=["+18153965488"],
    )

    message_body: str = Field(
        ...,
        description="Contenido del mensaje de texto recibido",
        examples=["Hola, ¿me pueden ayudar?", "Necesito información sobre precios"],
    )

    received_at: str = Field(
        ...,
        description="Fecha y hora cuando se recibió el mensaje",
        examples=["2025-11-01T12:00:00", "2025-11-01T15:30:45.123456"],
    )

    message_sid: str = Field(
        ...,
        description="ID único del mensaje en Twilio",
        examples=["SM1234567890abcdef1234567890abcdef"],
    )

    auto_reply_sent: bool = Field(
        default=False,
        description="Indica si ya se envió una respuesta automática a este mensaje",
        examples=[True, False],
    )

    auto_reply_sid: Optional[str] = Field(
        default=None,
        description="ID del mensaje de respuesta automática enviado (None si no se envió respuesta)",
        examples=["SM9876543210fedcba9876543210fedcba", None],
    )
