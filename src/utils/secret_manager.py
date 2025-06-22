"""
Secure secret management using Google Cloud Secret Manager
"""

import logging
from typing import Optional
from google.cloud import secretmanager
from google.api_core import exceptions as gcp_exceptions
from .exceptions import ConfigurationError


class SecretManagerClient:
    """Secure client for Google Cloud Secret Manager"""
    
    def __init__(self, project_id: Optional[str] = None):
        """Initialize Secret Manager client"""
        self.logger = logging.getLogger(__name__)
        self.project_id = project_id
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the Secret Manager client"""
        try:
            self.client = secretmanager.SecretManagerServiceClient()
            
            # Auto-detect project ID if not provided
            if not self.project_id:
                self.project_id = self._get_project_id()
            
            self.logger.info(f"Secret Manager client initialized for project: {self.project_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Secret Manager client: {e}")
            raise ConfigurationError(f"Secret Manager initialization failed: {e}")
    
    def _get_project_id(self) -> str:
        """Auto-detect GCP project ID"""
        try:
            import subprocess
            result = subprocess.run(
                ["gcloud", "config", "get-value", "project"],
                capture_output=True,
                text=True,
                check=True
            )
            project_id = result.stdout.strip()
            if not project_id:
                raise ConfigurationError("Could not detect GCP project ID")
            return project_id
        except Exception as e:
            raise ConfigurationError(f"Failed to auto-detect project ID: {e}")
    
    def get_secret(self, secret_name: str, version: str = "latest") -> str:
        """
        Retrieve a secret from Google Secret Manager
        
        Args:
            secret_name: Name of the secret
            version: Version of the secret (default: "latest")
            
        Returns:
            The secret value as string
            
        Raises:
            ConfigurationError: If secret cannot be retrieved
        """
        try:
            # Build the resource name
            name = f"projects/{self.project_id}/secrets/{secret_name}/versions/{version}"
            
            # Access the secret version
            response = self.client.access_secret_version(request={"name": name})
            
            # Decode the secret payload
            secret_value = response.payload.data.decode("UTF-8")
            
            self.logger.info(f"Successfully retrieved secret: {secret_name}")
            return secret_value
            
        except gcp_exceptions.NotFound:
            raise ConfigurationError(f"Secret '{secret_name}' not found in project '{self.project_id}'")
        except gcp_exceptions.PermissionDenied:
            raise ConfigurationError(f"Permission denied accessing secret '{secret_name}'. Check IAM roles.")
        except Exception as e:
            self.logger.error(f"Failed to retrieve secret '{secret_name}': {e}")
            raise ConfigurationError(f"Failed to retrieve secret: {e}")
    
    def create_secret_if_not_exists(self, secret_name: str, secret_value: str) -> bool:
        """
        Create a secret if it doesn't exist (for setup purposes)
        
        Args:
            secret_name: Name of the secret to create
            secret_value: Value of the secret
            
        Returns:
            True if secret was created, False if it already existed
        """
        try:
            # Check if secret exists
            try:
                self.get_secret(secret_name)
                self.logger.info(f"Secret '{secret_name}' already exists")
                return False
            except ConfigurationError:
                # Secret doesn't exist, create it
                pass
            
            # Create the secret
            parent = f"projects/{self.project_id}"
            secret = {"replication": {"automatic": {}}}
            
            response = self.client.create_secret(
                request={
                    "parent": parent,
                    "secret_id": secret_name,
                    "secret": secret
                }
            )
            
            # Add the secret version
            self.client.add_secret_version(
                request={
                    "parent": response.name,
                    "payload": {"data": secret_value.encode("UTF-8")}
                }
            )
            
            self.logger.info(f"Successfully created secret: {secret_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create secret '{secret_name}': {e}")
            raise ConfigurationError(f"Failed to create secret: {e}")


class GeminiSecretManager:
    """Specialized secret manager for Gemini API keys"""
    
    def __init__(self, project_id: Optional[str] = None, secret_name: str = "gemini-api-key"):
        """Initialize Gemini secret manager"""
        self.secret_name = secret_name
        self.secret_client = SecretManagerClient(project_id)
        self.logger = logging.getLogger(__name__)
    
    def get_api_key(self) -> str:
        """Get Gemini API key from Secret Manager"""
        try:
            api_key = self.secret_client.get_secret(self.secret_name)
            
            # Basic validation
            if not api_key or len(api_key.strip()) < 10:
                raise ConfigurationError("Retrieved API key appears to be invalid")
            
            self.logger.info("Gemini API key retrieved successfully from Secret Manager")
            return api_key.strip()
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve Gemini API key: {e}")
            raise ConfigurationError(f"Could not get Gemini API key from Secret Manager: {e}")
    
    def setup_api_key(self, api_key: str) -> bool:
        """Setup Gemini API key in Secret Manager (one-time setup)"""
        try:
            created = self.secret_client.create_secret_if_not_exists(self.secret_name, api_key)
            if created:
                self.logger.info("Gemini API key stored in Secret Manager")
            else:
                self.logger.info("Gemini API key already exists in Secret Manager")
            return created
        except Exception as e:
            self.logger.error(f"Failed to setup API key: {e}")
            raise ConfigurationError(f"Could not setup API key in Secret Manager: {e}") 