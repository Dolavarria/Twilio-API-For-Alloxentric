from typing import Optional, Dict, Any, List
from database.device_db import DeviceDB
from database.message_db import MessageDB

class DatabaseService:
    """Servicio unificado para operaciones de base de datos"""
    
    def __init__(self):
        # Inicializar gestores de colecciones MongoDB
        self.device_db = DeviceDB()
        self.message_db = MessageDB()
    
    # Métodos para dispositivos
    def create_device(self, device_data: Dict[str, Any]) -> str:
        """Crear un nuevo dispositivo"""
        return self.device_db.create_device(device_data)
    
    def get_device_by_webhook(self, device_webhook: str) -> Optional[Dict[str, Any]]:
        """Obtener dispositivo por webhook"""
        return self.device_db.get_device_by_webhook(device_webhook)
    
    def get_device_by_id(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Obtener dispositivo por ID"""
        return self.device_db.get_device_by_id(device_id)
    
    def list_devices(self, limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """Listar dispositivos"""
        return self.device_db.list_devices(limit, skip)
    
    def update_device(self, device_webhook: str, update_data: Dict[str, Any]) -> bool:
        """Actualizar un dispositivo"""
        return self.device_db.update_device(device_webhook, update_data)
    
    def delete_device(self, device_webhook: str) -> bool:
        """Eliminar un dispositivo"""
        return self.device_db.delete_device(device_webhook)
    
    # Métodos para mensajes
    def log_received_message(self, message_data: Dict[str, Any]) -> str:
        """Registrar mensaje recibido"""
        return self.message_db.log_received_message(message_data)
    
    def log_sent_message(self, device_webhook: str, contact_account: str, 
                        message: str, external_id: Optional[str] = None, 
                        status: str = "sent") -> str:
        """Registrar mensaje enviado"""
        return self.message_db.log_sent_message(
            device_webhook, contact_account, message, external_id, status
        )
    
    def get_conversation_history(self, device_webhook: str, contact_account: str, 
                               limit: int = 50) -> List[Dict[str, Any]]:
        """Obtener historial de conversación"""
        return self.message_db.get_conversation_history(device_webhook, contact_account, limit)
    
    def mark_as_processed(self, message_id: str) -> bool:
        """Marcar mensaje como procesado"""
        return self.message_db.mark_as_processed(message_id)

# Instancia global del servicio de base de datos (inicialización lazy)
_db_service = None

def get_db_service():
    """Obtener la instancia del servicio de base de datos"""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service

# Mantener compatibilidad con el código existente
class DatabaseServiceProxy:
    def __getattr__(self, name):
        return getattr(get_db_service(), name)

db_service = DatabaseServiceProxy()
