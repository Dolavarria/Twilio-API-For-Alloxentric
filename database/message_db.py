from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from pymongo.collection import Collection
from database.config import get_database

class MessageDB:
    """Clase para manejar operaciones de mensajes en la base de datos"""
    
    def __init__(self):
        self.db = None
        self.collection = None
    
    def _get_collection(self):
        """Obtener la colección (lazy loading)"""
        if self.collection is None:
            self.db = get_database()
            self.collection = self.db.messages
            
            # Crear índices para optimizar consultas
            try:
                self.collection.create_index("device_webhook")
                self.collection.create_index("contact_account")
                self.collection.create_index("created_at")
                self.collection.create_index([("device_webhook", 1), ("contact_account", 1)])
            except Exception:
                # Los índices ya existen, ignorar
                pass
        return self.collection
    
    def log_received_message(self, message_data: Dict[str, Any]) -> str:
        """
        Registrar un mensaje recibido
        
        Args:
            message_data: Datos del mensaje recibido
            
        Returns:
            str: ID del registro creado
        """
        log_entry = {
            "type": "received",
            "device_webhook": message_data.get("device_webhook"),
            "contact_account": message_data.get("contact_account", message_data.get("message_sender")),
            "message_content": message_data.get("message_content", message_data.get("contact_message")),
            "raw_data": message_data,
            "created_at": datetime.utcnow(),
            "processed": False
        }
        
        collection = self._get_collection()
        result = collection.insert_one(log_entry)
        return str(result.inserted_id)
    
    def log_sent_message(self, device_webhook: str, contact_account: str, 
                        message: str, external_id: Optional[str] = None, 
                        status: str = "sent") -> str:
        """
        Registrar un mensaje enviado
        
        Args:
            device_webhook: Webhook del dispositivo
            contact_account: Cuenta del contacto (número de teléfono)
            message: Contenido del mensaje
            external_id: ID externo del mensaje (ej: MessageSid de Twilio)
            status: Estado del mensaje
            
        Returns:
            str: ID del registro creado
        """
        log_entry = {
            "type": "sent",
            "device_webhook": device_webhook,
            "contact_account": contact_account,
            "message_content": message,
            "external_id": external_id,
            "status": status,
            "created_at": datetime.utcnow()
        }
        
        collection = self._get_collection()
        result = collection.insert_one(log_entry)
        return str(result.inserted_id)
    
    def get_conversation_history(self, device_webhook: str, contact_account: str, 
                               limit: int = 50) -> list:
        """
        Obtener historial de conversación entre un dispositivo y un contacto
        
        Args:
            device_webhook: Webhook del dispositivo
            contact_account: Cuenta del contacto
            limit: Número máximo de mensajes a retornar
            
        Returns:
            list: Lista de mensajes ordenados por fecha
        """
        collection = self._get_collection()
        messages = list(collection.find({
            "device_webhook": device_webhook,
            "contact_account": contact_account
        }).sort("created_at", -1).limit(limit))
        
        for message in messages:
            message["_id"] = str(message["_id"])
        
        return messages
    
    def mark_as_processed(self, message_id: str) -> bool:
        """
        Marcar un mensaje como procesado
        
        Args:
            message_id: ID del mensaje
            
        Returns:
            bool: True si se actualizó, False si no se encontró
        """
        try:
            collection = self._get_collection()
            result = collection.update_one(
                {"_id": ObjectId(message_id)},
                {"$set": {"processed": True, "processed_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    def get_unprocessed_messages(self, device_webhook: Optional[str] = None) -> list:
        """
        Obtener mensajes no procesados
        
        Args:
            device_webhook: Filtrar por dispositivo específico (opcional)
            
        Returns:
            list: Lista de mensajes no procesados
        """
        query = {"type": "received", "processed": False}
        if device_webhook:
            query["device_webhook"] = device_webhook
        
        collection = self._get_collection()
        messages = list(collection.find(query).sort("created_at", 1))
        for message in messages:
            message["_id"] = str(message["_id"])
        
        return messages
