"""
Main text classifier with clean architecture
"""

import torch
import torch.nn.functional as F
import logging
from typing import Dict, List, Any
from functools import lru_cache

from .interfaces import IClassifier, ClassificationResult, ModelConfig
from .models import ModelLoader
from .processors import TextProcessor
from config.loader import ConfigLoader
from ..utils.uncertainty_calculator import UncertaintyCalculator
from ..utils.result_formatter import ResultFormatter
from ..utils.exceptions import ClassificationError


class PredictionEngine:
    """Handles model inference"""
    
    def __init__(self, model, tokenizer, class_tokens, device):
        """Initialize prediction engine"""
        self.model = model
        self.tokenizer = tokenizer
        self.class_tokens = class_tokens
        self.device = device
        self.logger = logging.getLogger(__name__)
    
    def predict_single(self, prompt: str, temperature: float) -> tuple:
        """Make single prediction"""
        try:
            # Tokenize
            inputs = self.tokenizer(prompt, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Inference
            with torch.no_grad():
                outputs = self.model(**inputs, return_dict=True)
                logits = outputs.logits[0, -1, :]
                
                # Extract class logits
                class_logits = torch.tensor([
                    logits[self.class_tokens["1"]],
                    logits[self.class_tokens["2"]],
                    logits[self.class_tokens["3"]]
                ]).to(self.device)
                
                # Apply softmax
                probs = F.softmax(class_logits / temperature, dim=-1)
                predicted_idx = torch.argmax(probs)
                
                return probs, predicted_idx
                
        except Exception as e:
            self.logger.error(f"Prediction failed: {e}")
            raise ClassificationError(f"Prediction failed: {e}")


class PredictionCache:
    """Handles prediction caching"""
    
    def __init__(self, max_size: int = 1000):
        """Initialize cache"""
        self.max_size = max_size
        self.cache = {}
    
    @lru_cache(maxsize=1000)
    def get_cached_result(self, text: str, temperature: float) -> Dict:
        """Get cached prediction result"""
        cache_key = f"{hash(text)}_{temperature}"
        return self.cache.get(cache_key)
    
    def cache_result(self, text: str, temperature: float, result: Dict) -> None:
        """Cache prediction result"""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        cache_key = f"{hash(text)}_{temperature}"
        self.cache[cache_key] = result
    
    def clear_cache(self) -> None:
        """Clear prediction cache"""
        self.cache.clear()


class TextClassifier(IClassifier):
    """Main text classifier - orchestrates classification process"""
    
    def __init__(self, config_loader: ConfigLoader,model_loader: ModelLoader,text_processor: TextProcessor):
        """Initialize classifier with dependencies"""
        self.config_loader = config_loader
        self.model_loader = model_loader
        self.text_processor = text_processor
        self.uncertainty_calc = UncertaintyCalculator()
        self.result_formatter = ResultFormatter(config_loader)
        self.cache = PredictionCache()
        self.logger = logging.getLogger(__name__)
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self) -> None:
        """Initialize classifier components"""
        model_config = self.config_loader.get_model_config()
        model, tokenizer, class_tokens = self.model_loader.load_model(model_config)
        
        self.prediction_engine = PredictionEngine(
            model, tokenizer, class_tokens, model_config.device
        )
    
    def predict(self, text: str, temperature: float = 0.1) -> ClassificationResult:
        """Classify single text"""
        # Check cache first
        cached = self.cache.get_cached_result(text, temperature)
        if cached:
            return cached
        
        # Process text and get prediction
        prompt = self.text_processor.build_prompt(text)
        probs, predicted_idx = self.prediction_engine.predict_single(prompt, temperature)
        
        # Calculate uncertainty and format result
        uncertainty_metrics = self.uncertainty_calc.calculate(probs)
        result = self.result_formatter.format_result(
            text, probs, predicted_idx, uncertainty_metrics, temperature
        )
        
        # Cache and return
        self.cache.cache_result(text, temperature, result)
        return result
    
    def predict_batch(self, texts: List[str], temperature: float = 0.1) -> List[ClassificationResult]:
        """Classify batch of texts"""
        return [self.predict(text, temperature) for text in texts] 