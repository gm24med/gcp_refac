"""
Reply service - application entry point for reply generation
"""

import time
import logging
from typing import Dict, Any, Optional
from ..core.interfaces import (
    IClassifier, 
    IReplyGenerator, 
    ClassificationResult, 
    ReplyResult
)
from ..utils.logger import create_logger
from ..utils.exceptions import ClassificationError, ValidationError


class ReplyService:
    """Main service for text classification and reply generation"""
    
    def __init__(self, 
                 classifier: IClassifier,
                 reply_generator: IReplyGenerator):
        """Initialize with dependencies"""
        self.classifier = classifier
        self.reply_generator = reply_generator
        self.logger = create_logger(__name__)
        self.request_count = 0
        self.reply_count = 0
    
    def classify_and_reply(self, 
                          message: str, 
                          generate_reply: bool = True,
                          language: str = None,
                          **kwargs) -> ReplyResult:
        """Classify message and optionally generate reply"""
        self._validate_message_input(message)
        
        start_time = time.time()
        
        try:
            self.logger.info(f"Processing classify-and-reply request {self.request_count + 1}")
            self.request_count += 1
            
            # Step 1: Classify the message
            classification_result = self.classifier.predict(message, **kwargs)
            self.logger.info(
                f"Classification completed: {classification_result.category} "
                f"(confidence: {classification_result.confidence:.2%})"
            )
            
            # Step 2: Generate reply if requested
            generated_reply = ""
            confidence_score = classification_result.confidence
            
            if generate_reply and self.reply_generator.is_service_ready():
                try:
                    generated_reply = self.reply_generator.generate_reply(
                        message, language, classification_result
                    )
                    self.reply_count += 1
                    self.logger.info("Reply generated successfully")
                except Exception as e:
                    self.logger.warning(f"Reply generation failed: {e}, continuing without reply")
                    generated_reply = ""
            
            # Step 3: Create result
            processing_time = time.time() - start_time
            
            # Detect language if not provided
            if not language and hasattr(self.reply_generator, 'language_detector'):
                language = self.reply_generator.language_detector.detect_language(message)
            
            result = ReplyResult(
                original_message=message,
                classification_result=classification_result,
                generated_reply=generated_reply,
                language_detected=language or 'fr',
                processing_time=processing_time,
                confidence_score=confidence_score,
                metadata={
                    'reply_generated': bool(generated_reply),
                    'service_ready': self.reply_generator.is_service_ready(),
                    'request_id': self.request_count
                }
            )
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"Classify-and-reply failed for message: {message[:50]}... Error: {e}")
            raise ClassificationError(f"Classify-and-reply failed: {e}", text=message)
    
    def classify_only(self, message: str, **kwargs) -> ClassificationResult:
        """Classify message only without generating reply"""
        return self.classify_and_reply(message, generate_reply=False, **kwargs).classification_result
    
    def reply_only(self, 
                   message: str, 
                   language: str = None,
                   classification_result: ClassificationResult = None) -> str:
        """Generate reply only (classification is optional)"""
        self._validate_message_input(message)
        
        if not self.reply_generator.is_service_ready():
            raise ValidationError("Reply generator service is not ready")
        
        try:
            self.logger.info("Processing reply-only request")
            reply = self.reply_generator.generate_reply(message, language, classification_result)
            self.reply_count += 1
            self.logger.info("Reply-only generation completed")
            return reply
        except Exception as e:
            self.logger.error(f"Reply-only generation failed: {e}")
            raise ClassificationError(f"Reply generation failed: {e}", text=message)
    
    def _validate_message_input(self, message: str) -> None:
        """Validate message input"""
        if not message or not isinstance(message, str):
            raise ValidationError("Message must be a non-empty string", field="message", value=str(message))
        
        if len(message.strip()) == 0:
            raise ValidationError("Message cannot be empty or whitespace only", field="message")
        
        # Check message length limits
        if len(message) > 5000:  # Reasonable limit for customer service messages
            raise ValidationError("Message too long (max 5000 characters)", field="message")
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            'total_requests': self.request_count,
            'total_replies': self.reply_count,
            'classification_service_status': 'active',
            'reply_service_status': 'active' if self.reply_generator.is_service_ready() else 'inactive',
            'reply_success_rate': (self.reply_count / max(self.request_count, 1)) * 100
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all services"""
        return {
            'classifier_ready': hasattr(self.classifier, 'prediction_engine') and self.classifier.prediction_engine is not None,
            'reply_generator_ready': self.reply_generator.is_service_ready(),
            'service_operational': True,
            'last_check': time.time()
        } 