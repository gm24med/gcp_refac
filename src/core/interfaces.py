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