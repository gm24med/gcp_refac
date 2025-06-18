import yaml
from pathlib import Path
from typing import Dict, Any, List
from src.core.interfaces import ModelConfig
from src.utils.exceptions import ConfigurationError

class ConfigLoader:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self._settings = self._load_yaml("settings.yaml")
        self._prompts = self._load_yaml("prompt.yaml")
        self._validate()
    
    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        with open(self.config_dir / filename, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _validate(self):
        if not self._settings.get('model', {}).get('id'): raise ConfigurationError("Model ID required")
        if set(self._settings.get('categories', {}).keys()) != {"1", "2", "3"}: raise ConfigurationError("Need categories 1,2,3")
    
    def get_model_config(self) -> ModelConfig:
        m = self._settings['model']
        return ModelConfig(m['id'], m['cache_dir'], m['device'], m.get('torch_dtype', 'float16'), m['parameters']['temperature'])
    
    def get_model_parameters(self) -> Dict[str, Any]:
        return self._settings['model']['parameters']
    
    def get_category_mapping(self) -> Dict[str, str]:
        return self._settings['categories']
    
    def get_prompt_template(self) -> str:
        return self._prompts['prompt_template']
    
    def get_system_prompt(self) -> str:
        return self._prompts['classifier_prompt']
    
    def get_temperatures(self) -> List[float]:
        return self._settings['model']['parameters']['temperatures']
    
    def get_max_attempts(self) -> int:
        return self._settings['model']['parameters']['max_attempts'] 