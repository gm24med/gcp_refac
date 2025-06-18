"""
Service factory for dependency injection and object creation
"""

import logging
from ..core.classifier import TextClassifier
from ..core.models import ModelFactory
from ..core.processors import TextProcessor
from config.loader import ConfigLoader
from ..utils.logger import setup_logging
from .classification_service import ClassificationService


class ServiceFactory:
    """Factory for creating services with proper dependency injection"""
    
    def __init__(self, config_dir: str = "config", log_level: str = "INFO"):
        """Initialize factory with configuration"""
        # Setup logging first
        setup_logging(log_level)
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.config_loader = ConfigLoader(config_dir)
        self.logger.info("Configuration loaded successfully")
    
    def create_classification_service(self) -> ClassificationService:
        """Create fully configured classification service"""
        self.logger.info("Creating classification service...")
        
        # Create dependencies
        text_processor = TextProcessor(self.config_loader)
        model_loader = ModelFactory.create_loader(self.config_loader)
        # Create classifier
        classifier = TextClassifier(config_loader=self.config_loader,model_loader=model_loader,text_processor=text_processor)
        # Create service
        service = ClassificationService(classifier)
        self.logger.info("Classification service created successfully")
        return service


# Convenience function for quick service creation
def create_service(config_dir: str = "config", log_level: str = "INFO") -> ClassificationService:
    """Quick service creation function"""
    factory = ServiceFactory(config_dir, log_level)
    return factory.create_classification_service() 