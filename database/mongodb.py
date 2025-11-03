from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()


# os.getenv(): Obtiene el valor de una variable de entorno
# "MONGODB_URL": Nombre de la variable a buscar en .env
# Formato de URL MongoDB: mongodb://[usuario:contraseña@]host:puerto[/base_de_datos]
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

# MongoClient(MONGODB_URL):
#   - Crea una conexión con el servidor MongoDB
client = MongoClient(MONGODB_URL)

# client.sms_service_db:
#   - Accede o crea si no existe a una base de datos llamada "sms_service_db"
db = client.sms_service_db


# COLECCIONES (un similar a tablas en SQL)

# db.sms_records:
#   - Accede o crea una colección llamada "sms_records" dentro de la BD
#   - Esta colección almacenará los SMS ENVIADOS por nuestra aplicación
#   - Estructura de documentos: {to_number, message_body, sent_at, status, message_sid, error}
sms_collection = db.sms_records

# db.incoming_sms_records:
#   - Accede o crea una colección llamada "incoming_sms_records"
#   - Esta colección almacenará los SMS RECIBIDOS en nuestra aplicación
#   - Estructura: {from_number, to_number, message_body, received_at, message_sid, auto_reply_sent, auto_reply_sid}
incoming_sms_collection = db.incoming_sms_records


def insert_sms_record(sms_record: dict):
    """
    Inserta un nuevo registro de SMS ENVIADO en la base de datos

    Parámetros:
        sms_record (dict): Diccionario con la información del SMS enviado
                          Debe contener: to_number, message_body, sent_at,
                                        status, message_sid,error

    Retorna:
        Objeto con información de la inserción
                    - inserted_id: El _id del documento insertado
                    - acknowledged: True si la operación fue confirmada

    Ej:
        sms_record = {
            "to_number": "+56948372612",
            "message_body": "Hola mundo",
            "sent_at": datetime.now(),
            "status": "sent",
            "message_sid": "SM123...",
            "error": None
        }
        result = insert_sms_record(sms_record)
    """
    # sms_collection.insert_one():
    #   - Inserta el diccionario a la colección
    return sms_collection.insert_one(sms_record)


def find_sms_by_number(phone_number: str):
    """
    Busca todos los SMS ENVIADOS a un número de teléfono específico

    Parámetros:
        phone_number (str): Número de teléfono a buscar (ej +56942341243)

    Retorna:
        list: Lista de diccionarios con los SMS encontrados

    Ej:
        mensajes = find_sms_by_number("+56948372612")
        # Retorna: [
        #   {"to_number": "+56948372612", "message_body": "Hola", ...},
        #   {"to_number": "+56948372612", "message_body": "Adiós", ...}
        # ]
    """
    # sms_collection.find():
    #   - Busca documentos que cumplan con el criterio
    #   - Primer parámetro: Filtro de búsqueda
    #     {"to_number": phone_number} Busca donde el campo "to_number" sea igual al número dado
    #   - Segundo parámetro: Qué campos incluir/excluir
    #     {"_id": 0} → Excluye el campo "_id" de los resultados (0 = excluir, 1 = incluir)
    # list():
    #   - Convierte el resultado una lista
    return list(sms_collection.find({"to_number": phone_number}, {"_id": 0}))


def insert_incoming_sms(sms_record: dict):
    """
    Inserta un nuevo registro de SMS RECIBIDO en la base de datos

    Parámetros:
        sms_record (dict): Diccionario con la información del SMS recibido
                          Debe contener: from_number, to_number, message_body,
                                        received_at, message_sid, auto_reply_sent,
                                        auto_reply_sid

    Retorna:
        InsertOneResult: Objeto con información de la inserción

    Ejemplo de uso:
        incoming = {
            "from_number": "+56948372612",
            "to_number": "+18153965488",
            "message_body": "Hola, necesito ayuda",
            "received_at": "2025-11-01T12:00:00",
            "message_sid": "SM456...",
            "auto_reply_sent": True,
            "auto_reply_sid": "SM789..."
        }
        result = insert_incoming_sms(incoming)
    """
    # incoming_sms_collection.insert_one():
    #   - Inserta un documento en la colección incoming_sms_records
    return incoming_sms_collection.insert_one(sms_record)


def find_incoming_sms_by_number(phone_number: str):
    """
    Busca todos los SMS RECIBIDOS desde un número de teléfono específico

    Parámetros:
        phone_number (str): Número desde el cual se recibieron los SMS

    Retorna:
        list: Lista de diccionarios con los SMS recibidos de ese número

    Ejemplo de uso:
        mensajes = find_incoming_sms_by_number("+56948372612")
        # Retorna todos los mensajes que ese número nos envió
    """
    # incoming_sms_collection.find():
    #   - Busca en la colección de SMS recibidos
    #   - {"from_number": phone_number} Filtra por el remitente del mensaje
    #   - {"_id": 0} → Excluye el _id de MongoDB de los resultados
    return list(incoming_sms_collection.find({"from_number": phone_number}, {"_id": 0}))
