"""
Service factory for dependency injection and object creation
"""

import logging
from ..core.classifier import TextClassifier
from ..core.models import ModelFactory
from ..core.processors import TextProcessor
from ..utils.device_manager import DeviceManager
from ..utils.uncertainty_calculator import UncertaintyCalculator
from ..utils.result_formatter import ResultFormatter
from config.loader import ConfigLoader
from ..utils.logger import setup_logging
from .classification_service import ClassificationService
from typing import Union


class ServiceFactory:
    """Factory for creating services with proper dependency injection"""
    
    def __init__(self, config_loader_or_dir: Union[ConfigLoader, str] = "config", log_level: str = "INFO"):
        """Initialize factory with configuration"""
        # Setup logging first
        setup_logging(log_level)
        self.logger = logging.getLogger(__name__)
        
        # Handle both ConfigLoader object and config directory string
        if isinstance(config_loader_or_dir, ConfigLoader):
            self.config_loader = config_loader_or_dir
        else:
            self.config_loader = ConfigLoader(config_loader_or_dir)
        self.logger.info("Configuration loaded successfully")
    
    def create_device_manager(self) -> DeviceManager:
        """Create device manager"""
        return DeviceManager()
    
    def create_text_processor(self) -> TextProcessor:
        """Create text processor"""
        return TextProcessor(self.config_loader)
    
    def create_model_loader(self):
        """Create model loader"""
        return ModelFactory.create_loader(self.config_loader)
    
    def create_classifier(self) -> TextClassifier:
        """Create classifier"""
        text_processor = self.create_text_processor()
        model_loader = self.create_model_loader()
        return TextClassifier(config_loader=self.config_loader, model_loader=model_loader, text_processor=text_processor)
    
    def create_uncertainty_calculator(self) -> UncertaintyCalculator:
        """Create uncertainty calculator"""
        return UncertaintyCalculator()
    
    def create_result_formatter(self) -> ResultFormatter:
        """Create result formatter"""
        return ResultFormatter(self.config_loader)
    
    def create_classification_service(self) -> ClassificationService:
        """Create fully configured classification service"""
        self.logger.info("Creating classification service...")
        
        # Create classifier
        classifier = self.create_classifier()
        # Create service
        service = ClassificationService(classifier)
        self.logger.info("Classification service created successfully")
        return service


# Convenience function for quick service creation
def create_service(config_dir: str = "config", log_level: str = "INFO") -> ClassificationService:
    """Quick service creation function"""
    factory = ServiceFactory(config_dir, log_level)
    return factory.create_classification_service() 