from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from pymongo.collection import Collection
from database.config import get_database

class DeviceDB:
    """Clase para manejar operaciones de dispositivos en la base de datos"""
    
    def __init__(self):
        self.db = None
        self.collection = None
    
    def _get_collection(self):
        """Obtener la colección (lazy loading)"""
        if self.collection is None:
            self.db = get_database()
            self.collection = self.db.devices
            
            # Crear índice único para device_webhook
            try:
                self.collection.create_index("device_webhook", unique=True)
            except Exception:
                # El índice ya existe, ignorar
                pass
        return self.collection
    
    def create_device(self, device_data: Dict[str, Any]) -> str:
        """
        Crear un nuevo dispositivo en la base de datos
        
        Args:
            device_data: Diccionario con los datos del dispositivo
            
        Returns:
            str: ID del dispositivo creado
        """
        # Agregar timestamps
        device_data["created_at"] = datetime.utcnow()
        device_data["updated_at"] = datetime.utcnow()
        
        # Insertar en la base de datos
        collection = self._get_collection()
        result = collection.insert_one(device_data)
        return str(result.inserted_id)
    
    def get_device_by_webhook(self, device_webhook: str) -> Optional[Dict[str, Any]]:
        """
        Obtener un dispositivo por su webhook
        
        Args:
            device_webhook: Webhook del dispositivo
            
        Returns:
            Dict o None: Datos del dispositivo encontrado
        """
        collection = self._get_collection()
        device = collection.find_one({"device_webhook": device_webhook})
        if device:
            device["_id"] = str(device["_id"])
        return device
    
    def get_device_by_id(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtener un dispositivo por su ID
        
        Args:
            device_id: ID del dispositivo
            
        Returns:
            Dict o None: Datos del dispositivo encontrado
        """
        try:
            collection = self._get_collection()
            device = collection.find_one({"_id": ObjectId(device_id)})
            if device:
                device["_id"] = str(device["_id"])
            return device
        except Exception:
            # Retornar None si el ID no es válido o no existe
            return None
    
    def update_device(self, device_webhook: str, update_data: Dict[str, Any]) -> bool:
        """
        Actualizar un dispositivo
        
        Args:
            device_webhook: Webhook del dispositivo
            update_data: Datos a actualizar
            
        Returns:
            bool: True si se actualizó, False si no se encontró
        """
        update_data["updated_at"] = datetime.utcnow()
        collection = self._get_collection()
        result = collection.update_one(
            {"device_webhook": device_webhook},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    def delete_device(self, device_webhook: str) -> bool:
        """
        Eliminar un dispositivo
        
        Args:
            device_webhook: Webhook del dispositivo
            
        Returns:
            bool: True si se eliminó, False si no se encontró
        """
        collection = self._get_collection()
        result = collection.delete_one({"device_webhook": device_webhook})
        return result.deleted_count > 0
    
    def list_devices(self, limit: int = 100, skip: int = 0) -> list:
        """
        Listar dispositivos con paginación
        
        Args:
            limit: Número máximo de dispositivos a retornar
            skip: Número de dispositivos a saltar
            
        Returns:
            list: Lista de dispositivos
        """
        collection = self._get_collection()
        devices = list(collection.find().skip(skip).limit(limit))
        for device in devices:
            device["_id"] = str(device["_id"])
        return devices
