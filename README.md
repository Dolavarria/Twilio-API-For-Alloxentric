# API de Mensajería SMS

API REST para envío y recepción de mensajes SMS utilizando Twilio como proveedor de servicios de mensajería.

## Descripción

Esta aplicación proporciona una interfaz REST para gestionar dispositivos de comunicación SMS y procesar mensajes entrantes y salientes. Está diseñada para integrarse con sistemas de flujo de conversación y almacenar todos los datos en MongoDB.

## Arquitectura

- **Framework**: FastAPI
- **Base de datos**: MongoDB
- **Proveedor SMS**: Twilio
- **Lenguaje**: Python 3.8+

## Estructura del Proyecto

```
API_SMS/
├── main.py                 # Aplicación principal FastAPI
├── config/
│   └── settings.py         # Configuración global
├── database/
│   ├── config.py          # Configuración MongoDB
│   ├── db_service.py      # Servicio unificado de BD
│   ├── device_db.py       # Operaciones de dispositivos
│   └── message_db.py      # Operaciones de mensajes
├── models/
│   ├── device.py          # Modelos de dispositivos
│   └── message.py         # Modelos de mensajes
├── routes/
│   ├── device.py          # Endpoints de dispositivos
│   └── message.py         # Endpoints de mensajes
├── services/
│   └── twilio_service.py  # Integración con Twilio
└── .env                   # Variables de entorno
```

## Configuración

### 1. Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
# Configuración de MongoDB
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=sms_api

# Configuración de Twilio
TWILIO_ACCOUNT_SID=tu_account_sid_aqui
TWILIO_AUTH_TOKEN=tu_auth_token_aqui

# Configuración de la API
API_HOST=127.0.0.1
API_PORT=8000
API_RELOAD=true

```

### 2. Instalación de Dependencias

Crear un entorno virtual e instalar las dependencias:

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# o
source .venv/bin/activate  # Linux/Mac

pip install fastapi uvicorn pymongo twilio python-dotenv httpx
```

### 3. Configuración de MongoDB

Instalar y ejecutar MongoDB:

1. Descargar MongoDB Community Server
2. Crear directorio de datos: `mkdir C:\data\db` (Windows)
3. Ejecutar MongoDB: `mongod --dbpath "C:\data\db"`

### 4. Configuración de Twilio

1. Crear cuenta en Twilio
2. Obtener Account SID y Auth Token del dashboard
3. Configurar un número de teléfono para SMS
4. Agregar las credenciales al archivo `.env`

## Ejecución

### Desarrollo

```bash
# Activar entorno virtual
.venv\Scripts\activate

# Ejecutar servidor de desarrollo
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

## API Endpoints

### Dispositivos

#### POST /device/create
Crear un nuevo dispositivo de comunicación.

**Request Body:**
```json
{
    "device_name": "Dispositivo 1",
    "device_description": "Este es un dispositivo de prueba"
}
```

**Response:**
```json
{
    "message": "Dispositivo creado exitosamente",
    "device_id": "609a82f2e9ee9e4fef18950c",
    "device_webhook": "xxxx-xxxx-xxxx-xxxx"
}
```

### Mensajes

#### POST /message/receive
Recibir un mensaje desde Twilio.

**Request Body:**
```json
{
    "device_webhook": "xxxx-xxxx-xxxx-xxxx",
    "data": {
        "message_sender": "569XXXXXXXX",
        "message_content": "Este es un mensaje de prueba"
    }
}
```

**Response:**
```json
{
    "message": "Mensaje recibido"
}
```

#### POST /message/send
Enviar un mensaje a través de Twilio.

**Request Body:**
```json
{
    "device_webhook": "xxxx-xxxx-xxxx-xxxx",
    "contact_account": "569XXXXXXXX",
    "message": "Este es un mensaje de prueba"
}
```

**Response:**
```json
{
    "message": "Mensaje enviado"
}
```

## Documentación Interactiva

Una vez ejecutada la aplicación, la documentación interactiva estará disponible en:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## Base de Datos

### Colecciones MongoDB

#### devices
Almacena información de los dispositivos de comunicación:

```json
{
    "_id": "ObjectId",
    "device_name": "string",
    "device_description": "string",
    "device_webhook": "string",
    "device_number": "string",
    "device_account": {
        "account_sid": "string",
        "auth_token": "string"
    },
    "platform": "twilio",
    "status": "active",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

#### messages
Registra todos los mensajes enviados y recibidos:

```json
{
    "_id": "ObjectId",
    "type": "sent|received",
    "device_webhook": "string",
    "contact_account": "string",
    "message_content": "string",
    "external_id": "string",
    "status": "string",
    "processed": "boolean",
    "created_at": "datetime"
}
```

## Integración con Sistemas Externos

La API puede enviar datos procesados a un endpoint externo configurado en `EXTERNAL_MESSAGE_ENDPOINT`. Los datos se envían en el siguiente formato:

```json
{
    "transmitter": "contact",
    "channel": "sms",
    "channel_account": "device_webhook",
    "channel_settings": {},
    "contact_account": "numero_telefono",
    "id_contact": "numero_telefono",
    "contact_details": null,
    "type_message": "new_message",
    "contact_message_event": null,
    "contact_message": "contenido_mensaje",
    "action": null,
    "id_file": null,
    "contact_message_metadata": {}
}
```
