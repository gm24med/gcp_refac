"""
Interface definitions for clean architecture and dependency injection
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ClassificationResult:
    """Standardized classification result"""
    text: str
    predicted_class: str
    category: str
    confidence: float
    probabilities: Dict[str, float]
    uncertainty_metrics: Dict[str, float]
    method: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ModelConfig:
    """Model configuration parameters"""
    model_id: str
    cache_dir: str
    device: str
    torch_dtype: str
    temperature: float = 0.1


@dataclass
class GeminiConfig:
    """Gemini configuration parameters"""
    model_name: str
    project_id: Optional[str]
    secret_name: str
    temperature: float
    top_p: float
    top_k: int
    max_output_tokens: int
    candidate_count: int
    safety_settings: Dict[str, str]
    retry_config: Dict[str, Any]


@dataclass
class ReplyResult:
    """Standardized reply result"""
    original_message: str
    classification_result: ClassificationResult
    generated_reply: str
    language_detected: str
    processing_time: float
    confidence_score: float
    metadata: Optional[Dict[str, Any]] = None


class ITextProcessor(ABC):
    """Interface for text processing operations"""
    
    @abstractmethod
    def preprocess(self, text: str) -> str:
        """Preprocess text for classification"""
        pass
    
    @abstractmethod
    def build_prompt(self, text: str) -> str:
        """Build classification prompt"""
        pass


class IModelLoader(ABC):
    """Interface for model loading operations"""
    
    @abstractmethod
    def load_model(self, config: ModelConfig) -> Any:
        """Load the classification model"""
        pass
    
    @abstractmethod
    def is_model_ready(self) -> bool:
        """Check if model is loaded and ready"""
        pass


class IClassifier(ABC):
    """Interface for text classification"""
    
    @abstractmethod
    def predict(self, text: str) -> ClassificationResult:
        """Classify single text"""
        pass
    
    @abstractmethod
    def predict_batch(self, texts: List[str]) -> List[ClassificationResult]:
        """Classify batch of texts"""
        pass


class ILanguageDetector(ABC):
    """Interface for language detection"""
    
    @abstractmethod
    def detect_language(self, text: str) -> str:
        """Detect the language of the input text"""
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        pass


class IReplyGenerator(ABC):
    """Interface for reply generation"""
    
    @abstractmethod
    def generate_reply(self, 
                      message: str, 
                      classification_result: ClassificationResult,
                      language: str = None) -> str:
        """Generate a reply based on the message and classification"""
        pass
    
    @abstractmethod
    def is_service_ready(self) -> bool:
        """Check if the reply service is ready"""
        pass


class IGeminiClient(ABC):
    """Interface for Gemini client operations"""
    
    @abstractmethod
    def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate content using Gemini"""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to Gemini service"""
        pass 