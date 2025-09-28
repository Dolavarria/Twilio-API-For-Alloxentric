import os
from pymongo import MongoClient
from pymongo.database import Database
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class DatabaseConfig:
    """Configuración de la base de datos MongoDB"""
    
    def __init__(self):
        self.mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        self.database_name = os.getenv("DATABASE_NAME", "sms_api")
        self.client = None
        self.database = None
    
    def connect(self) -> Database:
        """Establecer conexión con MongoDB"""
        try:
            # Crear cliente MongoDB y seleccionar base de datos
            self.client = MongoClient(self.mongodb_uri)
            self.database = self.client[self.database_name]
            
            # Verificar conectividad con ping
            self.client.admin.command('ping')
            return self.database
            
        except Exception as e:
            raise Exception(f"Error conectando a MongoDB: {e}")
    
    def disconnect(self):
        """Cerrar conexión con MongoDB"""
        if self.client:
            self.client.close()

# Instancia global de la configuración
db_config = DatabaseConfig()

def get_database() -> Database:
    """Obtener la instancia de la base de datos"""
    if db_config.database is None:
        return db_config.connect()
    return db_config.database
