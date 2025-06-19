"""
Configuration loader for the classification system
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.core.interfaces import ModelConfig, GeminiConfig
from src.utils.exceptions import ConfigurationError

class ConfigLoader:
    """Centralized configuration management"""
    
    def __init__(self, config_dir: str = "config"):
        """Initialize configuration loader"""
        self.config_dir = Path(config_dir)
        self._settings = self._load_yaml("settings.yaml")
        self._prompts = self._load_yaml("prompt.yaml")
        self._validate()
    
    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load YAML configuration file"""
        with open(self.config_dir / filename, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _validate(self):
        if not self._settings.get('model', {}).get('id'): raise ConfigurationError("Model ID required")
        if set(self._settings.get('categories', {}).keys()) != {"1", "2", "3"}: raise ConfigurationError("Need categories 1,2,3")
    
    def get_model_config(self) -> ModelConfig:
        """Get model configuration"""
        m = self._settings['model']
        return ModelConfig(m['id'], m['cache_dir'], m['device'], m.get('torch_dtype', 'float16'), m['parameters']['temperature'])
    
    def get_gemini_config(self) -> GeminiConfig:
        """Get Gemini configuration"""
        gemini_settings = self._settings.get("gemini", {})
        return GeminiConfig(
            model_name=gemini_settings.get("model_name", "gemini-1.5-pro"),
            project_id=gemini_settings.get("project_id"),
            location=gemini_settings.get("location", "us-central1"),
            temperature=gemini_settings.get("parameters", {}).get("temperature", 0.7),
            top_p=gemini_settings.get("parameters", {}).get("top_p", 0.9),
            top_k=gemini_settings.get("parameters", {}).get("top_k", 40),
            max_output_tokens=gemini_settings.get("parameters", {}).get("max_output_tokens", 1024),
            candidate_count=gemini_settings.get("parameters", {}).get("candidate_count", 1),
            safety_settings=gemini_settings.get("safety_settings", {}),
            retry_config=gemini_settings.get("retry_config", {})
        )
    
    def get_reply_prompts(self) -> Dict[str, Any]:
        """Get reply service prompts"""
        return self._prompts.get("reply_prompts", {})
    
    def get_reply_service_config(self) -> Dict[str, Any]:
        """Get reply service configuration"""
        return self._settings.get("reply_service", {})
    
    def get_classification_prompt(self) -> str:
        """Get classification prompt"""
        return self._prompts.get("classifier_prompt", "")
    
    def get_prompt_template(self) -> str:
        """Get prompt template"""
        return self._prompts['prompt_template']
    
    def get_categories(self) -> Dict[str, str]:
        """Get category mappings"""
        return self._settings['categories']
    
    def get_model_parameters(self) -> Dict[str, Any]:
        """Get model generation parameters"""
        return self._settings['model']['parameters']
    
    def get_temperatures(self) -> List[float]:
        return self._settings['model']['parameters']['temperatures']
    
    def get_max_attempts(self) -> int:
        return self._settings['model']['parameters']['max_attempts'] 