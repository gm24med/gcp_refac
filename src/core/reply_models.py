"""
Reply service models with clean separation of concerns
"""

import google.generativeai as genai
import time
import logging
from typing import Dict, Any, Optional
from google.cloud import aiplatform
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from .interfaces import IGeminiClient, GeminiConfig
from config.loader import ConfigLoader
from ..utils.exceptions import ModelLoadError, ConfigurationError


class GeminiClientValidator:
    """Validates Gemini configuration and credentials - max 50 lines"""
    
    def __init__(self):
        """Initialize validator"""
        self.required_config_fields = [
            'model_name', 'location', 'temperature', 'top_p', 'top_k',
            'max_output_tokens', 'candidate_count'
        ]
    
    def validate_config(self, config: GeminiConfig) -> bool:
        """Validate Gemini configuration"""
        for field in self.required_config_fields:
            if not hasattr(config, field) or getattr(config, field) is None:
                raise ConfigurationError(f"Missing required Gemini config field: {field}")
        
        # Validate parameter ranges
        if not 0.0 <= config.temperature <= 2.0:
            raise ConfigurationError("Temperature must be between 0.0 and 2.0")
        
        if not 0.0 <= config.top_p <= 1.0:
            raise ConfigurationError("top_p must be between 0.0 and 1.0")
        
        if config.top_k < 1:
            raise ConfigurationError("top_k must be >= 1")
        
        return True
    
    def validate_credentials(self) -> bool:
        """Validate GCP credentials"""
        try:
            # Try to initialize aiplatform (will use default credentials)
            aiplatform.init()
            return True
        except Exception as e:
            raise ConfigurationError(f"GCP credentials validation failed: {e}")


class GeminiSafetyManager:
    """Manages Gemini safety settings - max 50 lines"""
    
    def __init__(self, safety_settings: Dict[str, str]):
        """Initialize safety manager"""
        self.safety_settings = safety_settings
        self.harm_categories = {
            'harassment': HarmCategory.HARM_CATEGORY_HARASSMENT,
            'hate_speech': HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            'sexually_explicit': HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            'dangerous_content': HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT
        }
        self.thresholds = {
            'BLOCK_NONE': HarmBlockThreshold.BLOCK_NONE,
            'BLOCK_LOW_AND_ABOVE': HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            'BLOCK_MEDIUM_AND_ABOVE': HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            'BLOCK_ONLY_HIGH': HarmBlockThreshold.BLOCK_ONLY_HIGH
        }
    
    def get_safety_settings(self) -> Dict:
        """Convert safety settings to Gemini format"""
        safety_config = {}
        for category, threshold in self.safety_settings.items():
            if category in self.harm_categories:
                safety_config[self.harm_categories[category]] = self.thresholds.get(
                    threshold, HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                )
        return safety_config


class GeminiRetryManager:
    """Manages retry logic for Gemini API calls - max 50 lines"""
    
    def __init__(self, retry_config: Dict[str, Any]):
        """Initialize retry manager"""
        self.max_retries = retry_config.get('max_retries', 3)
        self.initial_delay = retry_config.get('initial_delay', 1.0)
        self.max_delay = retry_config.get('max_delay', 60.0)
        self.multiplier = retry_config.get('multiplier', 2.0)
        self.logger = logging.getLogger(__name__)
    
    def execute_with_retry(self, func, *args, **kwargs):
        """Execute function with exponential backoff retry"""
        last_exception = None
        delay = self.initial_delay
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt == self.max_retries:
                    break
                
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                time.sleep(delay)
                delay = min(delay * self.multiplier, self.max_delay)
        
        raise ModelLoadError(f"All retry attempts failed. Last error: {last_exception}")


class GeminiClient(IGeminiClient):
    """Main Gemini client - orchestrates Gemini operations"""
    
    def __init__(self, config_loader: ConfigLoader):
        """Initialize with dependencies"""
        self.config_loader = config_loader
        self.validator = GeminiClientValidator()
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.is_initialized = False
        
        # Initialize client
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize Gemini client"""
        try:
            # Get configuration
            gemini_config = self.config_loader.get_gemini_config()
            
            # Validate configuration and credentials
            self.validator.validate_config(gemini_config)
            self.validator.validate_credentials()
            
            # Configure Gemini
            genai.configure()  # Uses default GCP credentials
            
            # Setup safety and retry managers
            self.safety_manager = GeminiSafetyManager(gemini_config.safety_settings)
            self.retry_manager = GeminiRetryManager(gemini_config.retry_config)
            
            # Initialize model
            self.model = genai.GenerativeModel(
                model_name=gemini_config.model_name,
                safety_settings=self.safety_manager.get_safety_settings()
            )
            
            self.generation_config = genai.types.GenerationConfig(
                temperature=gemini_config.temperature,
                top_p=gemini_config.top_p,
                top_k=gemini_config.top_k,
                max_output_tokens=gemini_config.max_output_tokens,
                candidate_count=gemini_config.candidate_count
            )
            
            self.is_initialized = True
            self.logger.info("Gemini client initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini client: {e}")
            raise ModelLoadError(f"Gemini client initialization failed: {e}")
    
    def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate content using Gemini"""
        if not self.is_initialized:
            raise ModelLoadError("Gemini client not initialized")
        
        def _generate():
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config,
                **kwargs
            )
            return response.text
        
        return self.retry_manager.execute_with_retry(_generate)
    
    def is_connected(self) -> bool:
        """Check if connected to Gemini service"""
        return self.is_initialized and self.model is not None


class GeminiModelFactory:
    """Factory for creating Gemini client instances"""
    
    @staticmethod
    def create_client(config_loader: ConfigLoader) -> GeminiClient:
        """Create Gemini client with dependencies"""
        return GeminiClient(config_loader) 