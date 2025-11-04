"""
Módulo de base de datos con Firestore
Gestiona usuarios y sus datos
"""
import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from google.cloud import firestore
from google.oauth2 import service_account
from google.auth import default as google_auth_default
import json
import subprocess

logger = logging.getLogger(__name__)

class Database:
    """Cliente de Firestore para gestionar usuarios"""
    
    def __init__(self):
        self.db = None
        self._init_firestore()
    
    def _init_firestore(self):
        """Inicializa el cliente de Firestore"""
        try:
            # Obtener project_id si está configurado
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT")
            
            # Opción 1: Usar credenciales por defecto de aplicación (gcloud auth application-default login)
            # Esta es la forma más simple y recomendada para desarrollo local
            try:
                if project_id:
                    self.db = firestore.Client(project=project_id)
                    logger.info(f"Firestore inicializado con credenciales por defecto (proyecto: {project_id})")
                else:
                    self.db = firestore.Client()
                    logger.info("Firestore inicializado con credenciales por defecto")
                return
            except Exception as e:
                logger.debug(f"No se pudieron cargar credenciales por defecto: {e}")
            
            # Opción 1.5: Intentar usar token de gcloud directamente
            try:
                import subprocess
                # Obtener token de acceso de gcloud
                result = subprocess.run(
                    ['gcloud', 'auth', 'print-access-token'],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=5
                )
                access_token = result.stdout.strip()
                
                # Crear credenciales desde el token
                from google.oauth2 import credentials as oauth2_creds
                from google.auth.transport.requests import Request
                
                # Usar el token para crear credenciales temporales
                creds = oauth2_creds.Credentials(token=access_token)
                
                # Detectar proyecto si no está configurado
                if not project_id:
                    try:
                        proj_result = subprocess.run(
                            ['gcloud', 'config', 'get-value', 'project'],
                            capture_output=True,
                            text=True,
                            check=True,
                            timeout=5
                        )
                        project_id = proj_result.stdout.strip()
                    except:
                        pass
                
                if project_id:
                    self.db = firestore.Client(credentials=creds, project=project_id)
                    logger.info(f"Firestore inicializado usando token de gcloud (proyecto: {project_id})")
                else:
                    self.db = firestore.Client(credentials=creds)
                    logger.info("Firestore inicializado usando token de gcloud")
                return
            except Exception as e:
                logger.debug(f"No se pudo usar token de gcloud: {e}")
            
            # Opción 2: Usar credenciales desde variable de entorno (JSON)
            firestore_credentials = os.getenv("FIRESTORE_CREDENTIALS")
            if firestore_credentials:
                try:
                    creds_dict = json.loads(firestore_credentials)
                    credentials = service_account.Credentials.from_service_account_info(creds_dict)
                    if project_id:
                        self.db = firestore.Client(credentials=credentials, project=project_id)
                    else:
                        self.db = firestore.Client(credentials=credentials)
                    logger.info("Firestore inicializado con credenciales desde variable de entorno")
                    return
                except json.JSONDecodeError:
                    logger.warning("FIRESTORE_CREDENTIALS no es un JSON válido, intentando otra opción")
            
            # Opción 3: Usar archivo de credenciales
            creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if creds_path and os.path.exists(creds_path):
                if project_id:
                    self.db = firestore.Client(project=project_id)
                else:
                    self.db = firestore.Client()
                logger.info(f"Firestore inicializado con credenciales desde {creds_path}")
                return
            
            # Si llegamos aquí, no hay credenciales válidas
            logger.error("No se pudieron inicializar las credenciales de Firestore")
            logger.error("Para configurar desde consola, ejecuta:")
            logger.error("  gcloud auth application-default login")
            logger.error("  gcloud config set project TU_PROJECT_ID")
            logger.error("O configura GOOGLE_CLOUD_PROJECT y las credenciales necesarias")
            self.db = None
            
        except Exception as e:
            logger.error(f"Error inicializando Firestore: {str(e)}")
            self.db = None
    
    def is_connected(self) -> bool:
        """Verifica si la base de datos está conectada"""
        return self.db is not None
    
    async def get_user(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un usuario por número de teléfono
        
        Args:
            phone_number: Número de teléfono del usuario
            
        Returns:
            Diccionario con los datos del usuario o None si no existe
        """
        if not self.db:
            logger.error("Firestore no está inicializado")
            return None
        
        try:
            doc_ref = self.db.collection("users").document(phone_number)
            doc = doc_ref.get()
            
            if doc.exists:
                user_data = doc.to_dict()
                user_data["phone_number"] = phone_number
                return user_data
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo usuario {phone_number}: {str(e)}")
            return None
    
    async def create_user(self, phone_number: str, name: str, interests: str) -> bool:
        """
        Crea un nuevo usuario en la base de datos
        
        Args:
            phone_number: Número de teléfono del usuario
            name: Nombre del usuario
            interests: Párrafo de intereses del usuario
            
        Returns:
            True si se creó correctamente, False en caso contrario
        """
        if not self.db:
            logger.error("Firestore no está inicializado")
            return False
        
        try:
            user_data = {
                "name": name,
                "interests": interests,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "onboarding_completed": True,
                "last_challenge_date": None,
                "challenges_completed": 0
            }
            
            doc_ref = self.db.collection("users").document(phone_number)
            doc_ref.set(user_data)
            
            logger.info(f"Usuario creado: {phone_number} - {name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creando usuario {phone_number}: {str(e)}")
            return False
    
    async def update_user_interests(self, phone_number: str, interests: str) -> bool:
        """
        Actualiza los intereses de un usuario
        
        Args:
            phone_number: Número de teléfono del usuario
            interests: Nuevo párrafo de intereses
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        if not self.db:
            logger.error("Firestore no está inicializado")
            return False
        
        try:
            doc_ref = self.db.collection("users").document(phone_number)
            doc_ref.update({
                "interests": interests,
                "updated_at": datetime.now()
            })
            
            logger.info(f"Intereses actualizados para usuario {phone_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando intereses de {phone_number}: {str(e)}")
            return False
    
    async def update_last_challenge_date(self, phone_number: str, date: datetime) -> bool:
        """
        Actualiza la fecha del último reto asignado
        
        Args:
            phone_number: Número de teléfono del usuario
            date: Fecha del reto
            
        Returns:
            True si se actualizó correctamente
        """
        if not self.db:
            return False
        
        try:
            doc_ref = self.db.collection("users").document(phone_number)
            doc_ref.update({
                "last_challenge_date": date,
                "updated_at": datetime.now()
            })
            return True
        except Exception as e:
            logger.error(f"Error actualizando fecha de reto: {str(e)}")
            return False
    
    async def increment_challenges_completed(self, phone_number: str) -> bool:
        """
        Incrementa el contador de retos completados
        
        Args:
            phone_number: Número de teléfono del usuario
            
        Returns:
            True si se actualizó correctamente
        """
        if not self.db:
            return False
        
        try:
            doc_ref = self.db.collection("users").document(phone_number)
            doc = doc_ref.get()
            
            if doc.exists:
                current_count = doc.to_dict().get("challenges_completed", 0)
                doc_ref.update({
                    "challenges_completed": current_count + 1,
                    "updated_at": datetime.now()
                })
                return True
            return False
        except Exception as e:
            logger.error(f"Error incrementando retos completados: {str(e)}")
            return False

# Instancia global
database = Database()

