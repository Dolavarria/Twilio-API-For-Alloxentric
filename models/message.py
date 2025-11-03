from pydantic import BaseModel, Field
from typing import Optional


class SMSResponse(BaseModel):
    """
    Modelo de respuesta estándar para envío de SMS

    Este modelo se usa como respuesta en los endpoints de la API cuando se intenta
    enviar un SMS. Informa si la operación fue exitosa o falló, junto con detalles relevantes.

    Casos de uso:
        1. SMS enviado correctamente success=True, message_sid=valor, error=None
        2. Error success=False, message_sid=None, error=descripción

    Ejemplos de respuestas:

        Éxito:
        {
            "success": true,
            "message_sid": "SM1234567890abcdef1234567890abcdef",
            "error": null
        }

        Error:
        {
            "success": false,
            "message_sid": null,
            "error": "Twilio error: Invalid phone number"
        }
    """

    # Campo success: Indica si la operación fue exitosa o no
    # Field(...): Indica que siempre debe estar presente
    success: bool = Field(
        ...,
        description="Indica si el SMS se envió correctamente (true) o falló (false)",
        examples=[True, False],
    )

    # Campo message_sid: ID único del mensaje en Twilio
    # Optional[str]: Puede ser un string o None (si hubo error)
    # default=None: Si no se proporciona, asume None
    # Solo tiene valor cuando success=True
    message_sid: Optional[str] = Field(
        default=None,
        description="ID único del mensaje en Twilio",
        examples=["SM1234567890abcdef1234567890abcdef", None],
    )

    # Campo error: Mensaje descriptivo del error ocurrido
    # Optional[str]: Puede ser un string (descripción del error) o None (si todo fue bien)
    # Solo tiene valor cuando success=False
    error: Optional[str] = Field(
        default=None,
        description="Mensaje de error descriptivo si la operación falló. None si fue exitosa",
        examples=[
            "Twilio error: The 'To' number is not a valid phone number",
            "Twilio phone number not configured",
            "Error: Connection timeout",
            None,
        ],
    )
