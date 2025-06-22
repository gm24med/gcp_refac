"""
Centralized registry for all package exports
Moved from __init__.py files for cleaner architecture
"""

import time
from typing import Optional, Dict, Any

__version__ = "1.0.0"
__author__ = "Your Team"
__email__ = "your.email@domain.com"

# ===== CORE COMPONENTS =====
try:
    # Try relative imports first (when imported as a package)
    from .core.interfaces import IClassifier, IModelLoader, ITextProcessor
    from .core.classifier import TextClassifier
    from .core.models import ModelFactory, ModelLoader
    from .core.processors import TextProcessor, PromptBuilder
except ImportError:
    try:
        # Fallback for direct execution or when src is in path
        from core.interfaces import IClassifier, IModelLoader, ITextProcessor
        from core.classifier import TextClassifier
        from core.models import ModelFactory, ModelLoader
        from core.processors import TextProcessor, PromptBuilder
    except ImportError as e:
        # If still failing, provide a more helpful error
        raise ImportError(f"Could not import core components. Ensure dependencies are installed and paths are correct: {e}")

# ===== SERVICES =====
try:
    from .services.classification_service import ClassificationService
    from .services.factory import ServiceFactory
    from .services.reply_factory import ReplyServiceFactory
    from .services.reply_service import ReplyService
except ImportError:
    try:
        from services.classification_service import ClassificationService
        from services.factory import ServiceFactory
        from services.reply_factory import ReplyServiceFactory
        from services.reply_service import ReplyService
    except ImportError as e:
        raise ImportError(f"Could not import services. Check dependencies: {e}")

# ===== CONFIGURATION =====
try:
    from config.loader import ConfigLoader
except ImportError as e:
    raise ImportError(f"Could not import config loader: {e}")

# ===== UTILITIES =====
try:
    from .utils.device_manager import DeviceManager
    from .utils.uncertainty_calculator import UncertaintyCalculator
    from .utils.result_formatter import ResultFormatter
    from .utils.exceptions import (
        ClassificationError,
        ModelLoadError,
        ConfigurationError,
        ValidationError
    )
    from .utils.logger import create_logger, setup_logging
except ImportError:
    try:
        from utils.device_manager import DeviceManager
        from utils.uncertainty_calculator import UncertaintyCalculator
        from utils.result_formatter import ResultFormatter
        from utils.exceptions import (
            ClassificationError,
            ModelLoadError,
            ConfigurationError,
            ValidationError
        )
        from utils.logger import create_logger, setup_logging
    except ImportError as e:
        raise ImportError(f"Could not import utilities: {e}")


# ===== EXPORTS BY CATEGORY =====

CORE_EXPORTS = [
    'IClassifier',
    'IModelLoader', 
    'ITextProcessor',
    'TextClassifier',
    'ModelFactory',
    'ModelLoader',
    'TextProcessor',
    'PromptBuilder'
]

SERVICE_EXPORTS = [
    'ClassificationService',
    'ServiceFactory',
    'ReplyServiceFactory',
    'ReplyService'
]

CONFIG_EXPORTS = [
    'ConfigLoader'
]

UTILITY_EXPORTS = [
    'DeviceManager',
    'UncertaintyCalculator', 
    'ResultFormatter',
    'ClassificationError',
    'ModelLoadError',
    'ConfigurationError',
    'ValidationError',
    'create_logger',
    'setup_logging'
]

# ===== COMPLETE EXPORT LIST =====
__all__ = (
    CORE_EXPORTS +
    SERVICE_EXPORTS + 
    CONFIG_EXPORTS +
    UTILITY_EXPORTS
)


# ===== CONVENIENCE FUNCTIONS =====

def get_main_classifier():
    """Get the main text classifier - most common use case"""
    return TextClassifier

def get_classification_service():
    """Get the high-level classification service"""  
    return ClassificationService

def get_all_exceptions():
    """Get all custom exception classes"""
    return [
        ClassificationError,
        ModelLoadError,
        ConfigurationError,
        ValidationError
    ]

def check_imports():
    """Check if all imports are working properly"""
    try:
        # Test core imports
        TextClassifier
        ModelFactory
        
        # Test service imports  
        ClassificationService
        ServiceFactory
        ReplyServiceFactory
        ReplyService
        
        # Test utility imports
        DeviceManager
        ClassificationError
        
        return True, "All imports successful"
    except NameError as e:
        return False, f"Import error: {e}"

class ServiceRegistry:
    """Centralized registry for all services and components"""
    
    def __init__(self, config_loader: Optional[ConfigLoader] = None):
        """Initialize registry with configuration"""
        self.config_loader = config_loader or ConfigLoader()
        self.logger = create_logger("ServiceRegistry")
        
        # Service factories
        self._service_factory = None
        self._reply_service_factory = None
        
        # Core services
        self._classification_service = None
        self._reply_service = None
        
        # Models and processors
        self._device_manager = None
        self._text_processor = None
        self._model_loader = None
        self._classifier = None
        self._uncertainty_calculator = None
        self._result_formatter = None
        
        # Reply service components
        self._gemini_client = None
        self._language_detector = None
        self._reply_generator = None
        
        self.logger.info("Service registry initialized")

    def get_reply_service_factory(self) -> ReplyServiceFactory:
        """Get reply service factory"""
        if self._reply_service_factory is None:
            self.logger.info("Creating reply service factory...")
            self._reply_service_factory = ReplyServiceFactory(self.config_loader)
        return self._reply_service_factory
    
    def get_reply_service(self) -> ReplyService:
        """Get reply service"""
        if self._reply_service is None:
            self.logger.info("Creating reply service...")
            reply_factory = self.get_reply_service_factory()
            classifier = self.get_classifier()
            self._reply_service = reply_factory.create_reply_service(classifier)
        return self._reply_service
    
    def get_gemini_client(self):
        """Get Gemini client"""
        if self._gemini_client is None:
            reply_factory = self.get_reply_service_factory()
            self._gemini_client = reply_factory.create_gemini_client()
        return self._gemini_client
    
    def get_language_detector(self):
        """Get language detector"""
        if self._language_detector is None:
            reply_factory = self.get_reply_service_factory()
            self._language_detector = reply_factory.create_language_detector()
        return self._language_detector
    
    def get_reply_generator(self):
        """Get reply generator"""
        if self._reply_generator is None:
            reply_factory = self.get_reply_service_factory()
            self._reply_generator = reply_factory.create_reply_generator()
        return self._reply_generator

    def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check of all services"""
        health = {
            'timestamp': time.time(),
            'registry_status': 'healthy',
            'services': {}
        }
        
        try:
            # Check classification service
            if self._classification_service:
                health['services']['classification'] = {
                    'status': 'active',
                    'model_loaded': self.get_classifier() is not None
                }
            
            # Check reply service
            if self._reply_service:
                health['services']['reply'] = {
                    'status': 'active',
                    'gemini_connected': self.get_gemini_client().is_connected() if self._gemini_client else False,
                    'service_ready': self.get_reply_service().health_check()
                }
            
            # Check device manager
            if self._device_manager:
                device_info = self.get_device_manager().get_device_info()
                health['services']['device'] = {
                    'status': 'active',
                    'device': device_info['device'],
                    'memory_available': device_info.get('memory_available', 'unknown')
                }
            
        except Exception as e:
            health['registry_status'] = 'degraded'
            health['error'] = str(e)
            self.logger.error(f"Health check failed: {e}")
        
        return health
    
    def get_service_factory(self) -> ServiceFactory:
        """Get service factory"""
        if self._service_factory is None:
            self.logger.info("Creating service factory...")
            self._service_factory = ServiceFactory(self.config_loader)
        return self._service_factory
    
    def get_classification_service(self) -> ClassificationService:
        """Get classification service"""
        if self._classification_service is None:
            self.logger.info("Creating classification service...")
            service_factory = self.get_service_factory()
            self._classification_service = service_factory.create_classification_service()
        return self._classification_service
    
    def get_device_manager(self):
        """Get device manager"""
        if self._device_manager is None:
            service_factory = self.get_service_factory()
            self._device_manager = service_factory.create_device_manager()
        return self._device_manager
    
    def get_text_processor(self):
        """Get text processor"""
        if self._text_processor is None:
            service_factory = self.get_service_factory()
            self._text_processor = service_factory.create_text_processor()
        return self._text_processor
    
    def get_model_loader(self):
        """Get model loader"""
        if self._model_loader is None:
            service_factory = self.get_service_factory()
            self._model_loader = service_factory.create_model_loader()
        return self._model_loader
    
    def get_classifier(self):
        """Get classifier"""
        if self._classifier is None:
            service_factory = self.get_service_factory()
            self._classifier = service_factory.create_classifier()
        return self._classifier
    
    def get_uncertainty_calculator(self):
        """Get uncertainty calculator"""
        if self._uncertainty_calculator is None:
            service_factory = self.get_service_factory()
            self._uncertainty_calculator = service_factory.create_uncertainty_calculator()
        return self._uncertainty_calculator
    
    def get_result_formatter(self):
        """Get result formatter"""
        if self._result_formatter is None:
            service_factory = self.get_service_factory()
            self._result_formatter = service_factory.create_result_formatter()
        return self._result_formatter
    
    def cleanup(self) -> None:
        """Cleanup all services and free resources"""
        self.logger.info("Cleaning up service registry...")
        
        # Cleanup reply service components
        if self._reply_service_factory:
            self._reply_service_factory.cleanup()
        
        # Reset all services
        self._service_factory = None
        self._reply_service_factory = None
        self._classification_service = None
        self._reply_service = None
        self._device_manager = None
        self._text_processor = None
        self._model_loader = None
        self._classifier = None
        self._uncertainty_calculator = None
        self._result_formatter = None
        self._gemini_client = None
        self._language_detector = None
        self._reply_generator = None
        
        self.logger.info("Service registry cleanup completed")