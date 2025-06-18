"""
Custom exceptions for better error handling and debugging
"""


class DarijaClassifierError(Exception):
    """Base exception for all classifier errors"""
    pass


class ModelLoadError(DarijaClassifierError):
    """Raised when model loading fails"""
    
    def __init__(self, message: str, model_id: str = None):
        """Initialize with error message and optional model ID"""
        self.model_id = model_id
        super().__init__(message)


class ClassificationError(DarijaClassifierError):
    """Raised during classification process"""
    
    def __init__(self, message: str, text: str = None):
        """Initialize with error message and optional input text"""
        self.text = text
        super().__init__(message)


class ConfigurationError(DarijaClassifierError):
    """Raised when configuration is invalid"""
    
    def __init__(self, message: str, config_key: str = None):
        """Initialize with error message and optional config key"""
        self.config_key = config_key
        super().__init__(message)


class ValidationError(DarijaClassifierError):
    """Raised during data validation"""
    
    def __init__(self, message: str, field: str = None, value: str = None):
        """Initialize with error details"""
        self.field = field
        self.value = value
        super().__init__(message)


class DeviceError(DarijaClassifierError):
    """Raised for device-related issues"""
    pass


class CacheError(DarijaClassifierError):
    """Raised for caching issues"""
    pass 