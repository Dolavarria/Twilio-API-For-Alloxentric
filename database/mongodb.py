from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# Obtener la URL de MongoDB
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

# Crear cliente de MongoDB
client = MongoClient(MONGODB_URL)

# Base de datos
db = client.sms_service_db

# Colecciones
sms_collection = db.sms_records


# Función para insertar un registro de SMS
def insert_sms_record(sms_record: dict):
    """
    Inserta un registro de mensaje SMS en la base de datos
    """
    return sms_collection.insert_one(sms_record)


# Función para buscar SMS por número
def find_sms_by_number(phone_number: str):
    """
    Busca mensajes SMS por número de teléfono
    """
    return list(sms_collection.find({"to_number": phone_number}, {"_id": 0}))
