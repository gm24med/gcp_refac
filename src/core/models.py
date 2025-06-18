"""
Model loading and management with clean separation of concerns
"""

import torch
import time
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from transformers import AutoTokenizer, AutoModelForCausalLM

from .interfaces import IModelLoader, ModelConfig
from config.loader import ConfigLoader
from ..utils.device_manager import DeviceManager
from ..utils.exceptions import ModelLoadError


class ModelValidator:
    """Validates model files and configuration - max 50 lines"""
    
    def __init__(self):
        """Initialize validator"""
        self.required_files = [
            "config.json", "tokenizer.json", "tokenizer_config.json",
            "special_tokens_map.json", "model.safetensors.index.json",
            "model-00001-of-00004.safetensors", "model-00002-of-00004.safetensors",
            "model-00003-of-00004.safetensors", "model-00004-of-00004.safetensors"
        ]
    
    def validate_model_files(self, model_dir: Path) -> list:
        """Check for missing model files"""
        missing = []
        for file in self.required_files:
            if not (model_dir / file).exists():
                missing.append(file)
        return missing
    
    def validate_config(self, config: ModelConfig) -> bool:
        """Validate model configuration"""
        required_attrs = ['model_id', 'cache_dir', 'device', 'torch_dtype']
        return all(hasattr(config, attr) for attr in required_attrs)


class TokenizerLoader:
    """Handles tokenizer loading - max 50 lines"""
    
    def __init__(self, logger: logging.Logger):
        """Initialize tokenizer loader"""
        self.logger = logger
    
    def load(self, model_id: str, cache_dir: str) -> Any:
        """Load tokenizer"""
        try:
            self.logger.info("Loading tokenizer...")
            
            tokenizer = AutoTokenizer.from_pretrained(
                model_id,
                cache_dir=cache_dir
            )
            
            self.logger.info("Tokenizer loaded successfully")
            return tokenizer
            
        except Exception as e:
            self.logger.error(f"Failed to load tokenizer: {e}")
            raise ModelLoadError(f"Tokenizer loading failed: {e}")
    
    def setup_class_tokens(self, tokenizer: Any) -> Dict[str, int]:
        """Setup classification tokens"""
        return {
            "1": tokenizer("1")['input_ids'][-1],
            "2": tokenizer("2")['input_ids'][-1], 
            "3": tokenizer("3")['input_ids'][-1]
        }


class ModelLoader(IModelLoader):
    """Main model loader - orchestrates model loading process"""
    
    def __init__(self, config_loader: ConfigLoader, device_manager: DeviceManager):
        """Initialize with dependencies"""
        self.config_loader = config_loader
        self.device_manager = device_manager
        self.validator = ModelValidator()
        self.tokenizer_loader = TokenizerLoader(logging.getLogger(__name__))
        self.model = None
        self.tokenizer = None
        self.class_tokens = None
    
    def load_model(self, config: ModelConfig) -> tuple:
        """Load model and tokenizer"""
        if not self.validator.validate_config(config):
            raise ModelLoadError("Invalid model configuration")
        
        start_time = time.time()
        
        # Load tokenizer
        self.tokenizer = self.tokenizer_loader.load(config.model_id, config.cache_dir)
        self.class_tokens = self.tokenizer_loader.setup_class_tokens(self.tokenizer)
        
        # Load model (continued in next method due to 50-line limit)
        self._load_main_model(config)
        
        elapsed = time.time() - start_time
        logging.getLogger(__name__).info(f"Model loaded in {elapsed:.2f}s")
        
        return self.model, self.tokenizer, self.class_tokens
    
    def _load_main_model(self, config: ModelConfig) -> None:
        """Load the main model"""
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                config.model_id,
                cache_dir=config.cache_dir,
                torch_dtype=getattr(torch, config.torch_dtype),
                device_map="auto",
                trust_remote_code=True
            )
            self.model.eval()
            
        except Exception as e:
            raise ModelLoadError(f"Model loading failed: {e}")
    
    def is_model_ready(self) -> bool:
        """Check if model is ready"""
        return all([self.model, self.tokenizer, self.class_tokens])


class ModelFactory:
    """Factory for creating model instances"""
    
    @staticmethod
    def create_loader(config_loader: ConfigLoader) -> ModelLoader:
        """Create model loader with dependencies"""
        device_manager = DeviceManager()
        return ModelLoader(config_loader, device_manager) 