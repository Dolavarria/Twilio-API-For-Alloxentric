from pydantic import BaseModel, Field
from typing import Optional, List


class PhoneNumberSearch(BaseModel):

    country_code: str = Field(
        default="US", description="Código de país (ej: US, MX, ES)"
    )
    area_code: Optional[str] = Field(
        None, description="Código de área para filtrar números"
    )
    limit: int = Field(default=10, description="Cantidad de números a mostrar")


class PhoneNumberPurchase(BaseModel):

    phone_number: str = Field(..., description="Número de teléfono a comprar")
    friendly_name: Optional[str] = Field(
        None, description="Nombre descriptivo para el número"
    )


class PhoneNumberResponse(BaseModel):
    success: bool
    phone_number: Optional[str] = None
    sid: Optional[str] = None
    friendly_name: Optional[str] = None
    error: Optional[str] = None


class AvailablePhoneNumber(BaseModel):

    phone_number: str
    friendly_name: str
    locality: Optional[str] = None  
    region: Optional[str] = None 
    capabilities: dict
