"""
Centralized registry for all package exports
Moved from __init__.py files for cleaner architecture
"""

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
except ImportError:
    try:
        from services.classification_service import ClassificationService
        from services.factory import ServiceFactory
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
    'ServiceFactory'
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
        
        # Test utility imports
        DeviceManager
        ClassificationError
        
        return True, "All imports successful"
    except NameError as e:
        return False, f"Import error: {e}" 