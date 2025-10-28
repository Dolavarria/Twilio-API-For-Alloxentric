from fastapi import APIRouter, Depends, HTTPException
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from models.phone_number import (
    PhoneNumberSearch,
    PhoneNumberPurchase,
    PhoneNumberResponse,
    AvailablePhoneNumber,
)
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(
    prefix="/phone-numbers",
    tags=["Phone Numbers"],
    responses={404: {"description": "Not found"}},
)


def get_twilio_client():
    """
    Reutilizamos la misma función para obtener el cliente de Twilio
    """
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")

    if not account_sid or not auth_token:
        raise HTTPException(status_code=500, detail="Twilio credentials not configured")

    return Client(account_sid, auth_token)


@router.post("/search", response_model=List[AvailablePhoneNumber])
async def search_available_numbers(
    search: PhoneNumberSearch, client: Client = Depends(get_twilio_client)
):
    """
    BUSCAR NÚMEROS DISPONIBLES

    Esta ruta te muestra qué números puedes comprar antes de gastar créditos.

    Ejemplo de uso:
    POST /phone-numbers/search
    {
        "country_code": "US",
        "area_code": "815",
        "limit": 5
    }
    """
    try:
        search_params = {}
        if search.area_code:
            search_params["area_code"] = search.area_code

        available_numbers = client.available_phone_numbers(
            search.country_code
        ).local.list(limit=search.limit, **search_params)

        result = []
        for number in available_numbers:
            result.append(
                AvailablePhoneNumber(
                    phone_number=number.phone_number,
                    friendly_name=number.friendly_name,
                    locality=number.locality,
                    region=number.region,
                    capabilities={
                        "voice": number.capabilities.get("voice", False),
                        "sms": number.capabilities.get("SMS", False),
                        "mms": number.capabilities.get("MMS", False),
                    },
                )
            )

        return result

    except TwilioRestException as e:
        raise HTTPException(status_code=400, detail=f"Twilio error: {e.msg}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/purchase", response_model=PhoneNumberResponse)
async def purchase_phone_number(
    purchase: PhoneNumberPurchase, client: Client = Depends(get_twilio_client)
):
    """
    COMPRAR UN NÚMERO

    IMPORTANTE: Consume créditos Twilio

    Busca con /search para ver números disponibles,
    luego usa esta ruta para comprar el que te guste.

    Ejemplo:
    POST /phone-numbers/purchase
    {
        "phone_number": "+18153965488",
        "friendly_name": "Mi número para SMS"
    }
    """
    try:
        incoming_phone_number = client.incoming_phone_numbers.create(
            phone_number=purchase.phone_number,
            friendly_name=purchase.friendly_name or purchase.phone_number,
        )

        return PhoneNumberResponse(
            success=True,
            phone_number=incoming_phone_number.phone_number,
            sid=incoming_phone_number.sid,
            friendly_name=incoming_phone_number.friendly_name,
        )

    except TwilioRestException as e:
        return PhoneNumberResponse(success=False, error=f"Twilio error: {e.msg}")
    except Exception as e:
        return PhoneNumberResponse(success=False, error=f"Error: {str(e)}")


@router.get("/my-numbers", response_model=List[dict])
async def list_my_phone_numbers(client: Client = Depends(get_twilio_client)):

    try:
        phone_numbers = client.incoming_phone_numbers.list()

        result = []
        for number in phone_numbers:
            result.append(
                {
                    "phone_number": number.phone_number,
                    "friendly_name": number.friendly_name,
                    "sid": number.sid,
                    "capabilities": {
                        "voice": number.capabilities.get("voice", False),
                        "sms": number.capabilities.get("sms", False),
                        "mms": number.capabilities.get("mms", False),
                    },
                    "status": number.status,
                    "date_created": str(number.date_created),
                }
            )

        return result

    except TwilioRestException as e:
        raise HTTPException(status_code=400, detail=f"Twilio error: {e.msg}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.delete("/{phone_number_sid}", response_model=PhoneNumberResponse)
async def release_phone_number(
    phone_number_sid: str, client: Client = Depends(get_twilio_client)
):
    """

    Esto elimina un número, necesitas el SID del número, que obtienes con /my-numbers

    Ejemplo:
    DELETE /phone-numbers/PN1234567890abcdef1234567890abcdef
    """
    try:
        client.incoming_phone_numbers(phone_number_sid).delete()

        return PhoneNumberResponse(
            success=True, sid=phone_number_sid, phone_number=None
        )

    except TwilioRestException as e:
        return PhoneNumberResponse(success=False, error=f"Twilio error: {e.msg}")
    except Exception as e:
        return PhoneNumberResponse(success=False, error=f"Error: {str(e)}")
