"""
Text processing components with single responsibility
"""

import re
from typing import Dict, Any
from .interfaces import ITextProcessor
from config.loader import ConfigLoader


class TextCleaner:
    """Handles text cleaning operations - max 50 lines"""
    
    def __init__(self):
        """Initialize text cleaner"""
        self.patterns = {
            'extra_spaces': re.compile(r'\s+'),
            'special_chars': re.compile(r'[^\w\s\u0600-\u06FF]'),
            'numbers': re.compile(r'\d+')
        }
    
    def clean(self, text: str) -> str:
        """Clean text for processing"""
        if not text or not isinstance(text, str):
            raise ValueError("Invalid input text")
        
        # Remove extra whitespace
        text = self.patterns['extra_spaces'].sub(' ', text.strip())
        
        # Handle special characters (keep Arabic)
        text = self.patterns['special_chars'].sub(' ', text)
        
        return text.strip()
    
    def normalize_darija(self, text: str) -> str:
        """Normalize Darija-specific patterns"""
        # Common Darija normalizations
        replacements = {
            'wach': 'واش',
            'kayn': 'كاين', 
            'chi': 'شي',
            'dial': 'ديال'
        }
        
        for latin, arabic in replacements.items():
            text = text.replace(latin, arabic)
        
        return text


class PromptBuilder:
    """Builds classification prompts - max 50 lines"""
    
    def __init__(self, config_loader: ConfigLoader):
        """Initialize with configuration"""
        self.config = config_loader
        self.template = self.config.get_prompt_template()
        self.system_prompt = self.config.get_classification_prompt()
    
    def build(self, text: str) -> str:
        """Build classification prompt"""
        if not text:
            raise ValueError("Text cannot be empty")
        
        return self.template.format(
            system_prompt=self.system_prompt,
            message=text
        )
    
    def build_batch(self, texts: list) -> list:
        """Build prompts for batch processing"""
        return [self.build(text) for text in texts]


class TextProcessor(ITextProcessor):
    """Main text processor - orchestrates cleaning and prompt building"""
    
    def __init__(self, config_loader: ConfigLoader):
        """Initialize processor with dependencies"""
        self.cleaner = TextCleaner()
        self.prompt_builder = PromptBuilder(config_loader)
    
    def preprocess(self, text: str) -> str:
        """Preprocess text for classification"""
        cleaned = self.cleaner.clean(text)
        normalized = self.cleaner.normalize_darija(cleaned)
        return normalized
    
    def build_prompt(self, text: str) -> str:
        """Build classification prompt"""
        preprocessed = self.preprocess(text)
        return self.prompt_builder.build(preprocessed) 