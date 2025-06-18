"""
Main classification service - application entry point
"""

import logging
from typing import List, Dict, Any, Optional
from ..core.interfaces import IClassifier, ClassificationResult
from ..utils.logger import create_logger
from ..utils.exceptions import ClassificationError, ValidationError


class ClassificationService:
    """Main service for text classification operations"""
    
    def __init__(self, classifier: IClassifier):
        """Initialize with classifier dependency"""
        self.classifier = classifier
        self.logger = create_logger(__name__)
        self.request_count = 0
    
    def classify_text(self, text: str, **kwargs) -> ClassificationResult:
        """Classify single text """
        self._validate_text_input(text)
        try:
            self.logger.info(f"Processing classification request {self.request_count + 1}")
            self.request_count += 1
            result = self.classifier.predict(text, **kwargs)
            self.logger.info(
                f"Classification completed: {result.category} "
                f"(confidence: {result.confidence:.2%})"
            )
            return result
        except Exception as e:
            self.logger.error(f"Classification failed for text: {text[:50]}... Error: {e}")
            raise ClassificationError(f"Classification failed: {e}", text=text)
    
    def classify_batch(self, texts: List[str], **kwargs) -> List[ClassificationResult]:
        """Classify batch of texts with progress tracking"""
        if not texts:
            raise ValidationError("Text list cannot be empty")
        
        self.logger.info(f"Starting batch classification of {len(texts)} texts")
        results = []
        for i, text in enumerate(texts):
            try:
                result = self.classify_text(text, **kwargs)
                results.append(result)
                
                if (i + 1) % 10 == 0:  # Log progress every 10 items
                    self.logger.info(f"Processed {i + 1}/{len(texts)} texts")
                    
            except Exception as e:
                self.logger.warning(f"Failed to classify text {i + 1}: {e}")
                # Continue with other texts
                continue
        
        self.logger.info(f"Batch classification completed: {len(results)}/{len(texts)} successful")
        return results
    
    def _validate_text_input(self, text: str) -> None:
        """Validate text input"""
        if not text or not isinstance(text, str):
            raise ValidationError("Text must be a non-empty string", field="text", value=str(text))
        
        if len(text.strip()) == 0:
            raise ValidationError("Text cannot be empty or whitespace only", field="text")
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            'total_requests': self.request_count,
            'service_status': 'active' # hadi normalement khas twli dynamique
        } 