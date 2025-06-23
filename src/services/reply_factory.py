"""
Factory for creating reply service components
"""

from typing import Optional
from config.loader import ConfigLoader
from ..core.interfaces import IClassifier, IReplyGenerator, ILanguageDetector
from ..core.reply_models import GeminiClient, GeminiModelFactory
from ..core.reply_processors import LanguageDetector, ReplyGenerator
from .reply_service import ReplyService
from .factory import ServiceFactory
from ..utils.logger import create_logger


class ReplyServiceFactory:
    """Factory for creating reply service components"""
    
    def __init__(self, config_loader: Optional[ConfigLoader] = None):
        """Initialize factory with configuration"""
        self.config_loader = config_loader or ConfigLoader()
        self.logger = create_logger(__name__)
        self._gemini_client = None
        self._language_detector = None
        self._reply_generator = None
    
    def create_gemini_client(self) -> GeminiClient:
        """Create Gemini client instance"""
        if self._gemini_client is None:
            self.logger.info("Creating Gemini client...")
            self._gemini_client = GeminiModelFactory.create_client(self.config_loader)
            self.logger.info("Gemini client created successfully")
        return self._gemini_client
    
    def create_language_detector(self) -> ILanguageDetector:
        """Create language detector instance"""
        if self._language_detector is None:
            self.logger.info("Creating language detector...")
            reply_config = self.config_loader.get_reply_service_config()
            supported_languages = reply_config.get('supported_languages', ['fr', 'ar', 'en'])
            self._language_detector = LanguageDetector(supported_languages)
            self.logger.info("Language detector created successfully")
        return self._language_detector
    
    def create_reply_generator(self) -> IReplyGenerator:
        """Create reply generator instance"""
        if self._reply_generator is None:
            self.logger.info("Creating reply generator...")
            gemini_client = self.create_gemini_client()
            language_detector = self.create_language_detector()
            
            self._reply_generator = ReplyGenerator(
                config_loader=self.config_loader,
                gemini_client=gemini_client,
                language_detector=language_detector
            )
            self.logger.info("Reply generator created successfully")
        return self._reply_generator
    
    def create_reply_service(self, classifier: Optional[IClassifier] = None) -> ReplyService:
        """Create complete reply service"""
        self.logger.info("Creating reply service...")
        
        # Create classifier if not provided
        if classifier is None:
            service_factory = ServiceFactory(self.config_loader)
            classifier = service_factory.create_classifier()
        
        # Create reply generator
        reply_generator = self.create_reply_generator()
        
        # Create reply service
        reply_service = ReplyService(
            classifier=classifier,
            reply_generator=reply_generator
        )
        
        self.logger.info("Reply service created successfully")
        return reply_service
    
    def create_standalone_reply_service(self) -> ReplyService:
        """Create reply service with all dependencies"""
        return self.create_reply_service()
    
    def get_service_health(self) -> dict:
        """Get health status of all services"""
        health = {
            'gemini_client_initialized': self._gemini_client is not None,
            'language_detector_initialized': self._language_detector is not None,
            'reply_generator_initialized': self._reply_generator is not None,
        }
        
        if self._gemini_client:
            health['gemini_client_connected'] = self._gemini_client.is_connected()
        
        if self._reply_generator:
            health['reply_service_ready'] = self._reply_generator.is_service_ready()
        
        return health
    
    def cleanup(self) -> None:
        """Cleanup resources"""
        self.logger.info("Cleaning up reply service factory resources")
        self._gemini_client = None
        self._language_detector = None
        self._reply_generator = None 