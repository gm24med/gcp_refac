"""
Reply processing components with single responsibility
"""

import re
import time
import logging
from typing import Dict, Any, List
from .interfaces import ILanguageDetector, IReplyGenerator, ClassificationResult
from .reply_models import GeminiClient
from config.loader import ConfigLoader
from ..utils.exceptions import ValidationError, ClassificationError


class LanguageDetector(ILanguageDetector):
    """Detects language from text patterns - max 50 lines"""
    
    def __init__(self, supported_languages: List[str]):
        """Initialize language detector"""
        self.supported_languages = supported_languages
        self.language_patterns = {
            'ar': re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+'),
            'fr': re.compile(r'\b(le|la|les|un|une|des|et|ou|de|du|dans|pour|avec|sur|par|sans|sous|entre|chez|vers|pendant|depuis|jusqu|avant|après|selon|contre|malgré|sauf|hormis|excepté|moyennant|nonobstant|outre|parmi|suivant|touchant|via|voici|voilà|merci|bonjour|bonsoir|salut|au revoir|comment|pourquoi|quand|où|qui|que|quoi|quel|quelle|combien|beaucoup|peu|très|assez|trop|plus|moins|aussi|encore|déjà|jamais|toujours|souvent|parfois|rarement|peut-être|sûrement|certainement|probablement|évidemment|naturellement|heureusement|malheureusement|finalement|enfin|donc|alors|ainsi|cependant|pourtant|néanmoins|toutefois|en effet|par exemple|notamment|surtout|particulièrement|spécialement|généralement|habituellement|normalement|actuellement|maintenant|aujourd|hier|demain|bientôt|récemment|autrefois|jadis|naguère|désormais|dorénavant)\b', re.IGNORECASE),
            'en': re.compile(r'\b(the|a|an|and|or|of|in|on|at|to|for|with|by|from|about|into|through|during|before|after|above|below|up|down|out|off|over|under|again|further|then|once|here|there|when|where|why|how|all|any|both|each|few|more|most|other|some|such|no|nor|not|only|own|same|so|than|too|very|can|will|just|should|now|good|new|first|last|long|great|little|public|same|able|back|call|came|come|could|did|each|find|get|give|go|had|has|have|he|her|him|his|how|its|like|look|made|make|man|may|most|move|much|must|name|need|never|now|number|off|old|only|other|our|out|over|own|said|same|see|she|should|since|some|still|such|take|than|that|the|their|them|then|there|these|they|this|those|three|through|time|two|up|use|very|want|water|way|we|well|were|what|when|where|which|while|who|will|with|work|would|year|you|your)\b', re.IGNORECASE)
        }
        self.darija_patterns = re.compile(r'\b(wach|kayn|chi|dial|baghi|n3ref|chno|ndir|ila|bghit|wash|ndkoum|problème|réseau|service|client|offline|solution|résiliation|type|compte|andy|n7bes|lkhedma|meakom|tayh|tay7|kifach|nweqqef|arrêter|bug|page|paiement|refused|facture|reçue|garantie|ordinateur|planning|technicien|chhal|mn|achmen|offline|tayha|montant|tarif|abonnement|changer|annuler|où|quand|disponibilité|chokran|nadi|nedditi|khdma|nqiya|zwina)\b', re.IGNORECASE)
    
    def detect_language(self, text: str) -> str:
        """Detect language from text patterns"""
        if not text or not isinstance(text, str):
            return 'fr'  # Default to French
        
        text_lower = text.lower()
        
        # Check for Darija patterns first (mix of Arabic and Latin)
        if self.darija_patterns.search(text):
            return 'ar'  # Treat Darija as Arabic for response templates
        
        # Count matches for each language
        scores = {}
        for lang, pattern in self.language_patterns.items():
            matches = len(pattern.findall(text))
            scores[lang] = matches
        
        # Return language with highest score, default to French
        if scores:
            detected = max(scores, key=scores.get)
            return detected if scores[detected] > 0 else 'fr'
        
        return 'fr'
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return self.supported_languages.copy()


class PromptBuilder:
    """Builds prompts for reply generation - max 50 lines"""
    
    def __init__(self, config_loader: ConfigLoader):
        """Initialize prompt builder"""
        self.config = config_loader
        self.reply_prompts = self.config.get_reply_prompts()
        self.category_prompts = self.reply_prompts.get('category_prompts', {})
        self.language_templates = self.reply_prompts.get('language_templates', {})
    
    def build_reply_prompt(self, 
                          message: str, 
                          classification_result: ClassificationResult,
                          language: str) -> str:
        """Build prompt for reply generation"""
        if not message:
            raise ValidationError("Message cannot be empty")
        
        # Get system prompt
        system_prompt = self.reply_prompts.get('system_prompt', '')
        
        # Get category-specific prompt
        category_prompt = self.category_prompts.get(classification_result.category, '')
        
        # Build the complete prompt
        prompt = f"{system_prompt}\n\n{category_prompt}\n\n"
        prompt += self.reply_prompts.get('reply_template', '').format(
            category=classification_result.category,
            confidence=classification_result.confidence,
            message=message
        )
        
        return prompt
    
    def format_final_reply(self, generated_reply: str, language: str) -> str:
        """Format the final reply with language-specific template"""
        template = self.language_templates.get(language, self.language_templates.get('fr', '{response}'))
        return template.format(response=generated_reply.strip())


class ReplyValidator:
    """Validates generated replies - max 50 lines"""
    
    def __init__(self, max_length: int = 2000):
        """Initialize reply validator"""
        self.max_length = max_length
        self.min_length = 10
        self.forbidden_patterns = [
            r'(?i)(hack|crack|illegal|fraud|scam)',
            r'(?i)(password|mot de passe|login|connexion)\s*[:=]\s*\w+',
            r'(?i)(credit card|carte de crédit|numéro de carte)',
        ]
        self.compiled_patterns = [re.compile(pattern) for pattern in self.forbidden_patterns]
    
    def validate_reply(self, reply: str) -> bool:
        """Validate generated reply"""
        if not reply or not isinstance(reply, str):
            return False
        
        reply_clean = reply.strip()
        
        # Check length constraints
        if len(reply_clean) < self.min_length or len(reply_clean) > self.max_length:
            return False
        
        # Check for forbidden content
        for pattern in self.compiled_patterns:
            if pattern.search(reply_clean):
                return False
        
        return True
    
    def sanitize_reply(self, reply: str) -> str:
        """Sanitize reply content"""
        if not reply:
            return ""
        
        # Remove excessive whitespace
        reply = re.sub(r'\s+', ' ', reply.strip())
        
        # Remove potential sensitive information patterns
        for pattern in self.compiled_patterns:
            reply = pattern.sub('[REDACTED]', reply)
        
        return reply


class ReplyGenerator(IReplyGenerator):
    """Main reply generator - orchestrates reply generation process"""
    
    def __init__(self, 
                 config_loader: ConfigLoader,
                 gemini_client: GeminiClient,
                 language_detector: LanguageDetector):
        """Initialize with dependencies"""
        self.config_loader = config_loader
        self.gemini_client = gemini_client
        self.language_detector = language_detector
        self.prompt_builder = PromptBuilder(config_loader)
        self.validator = ReplyValidator()
        self.logger = logging.getLogger(__name__)
    
    def generate_reply(self, 
                      message: str, 
                      classification_result: ClassificationResult,
                      language: str = None) -> str:
        """Generate reply based on message and classification"""
        try:
            # Detect language if not provided
            if not language:
                language = self.language_detector.detect_language(message)
            
            # Build prompt for reply generation
            prompt = self.prompt_builder.build_reply_prompt(
                message, classification_result, language
            )
            
            # Generate reply using Gemini
            generated_reply = self.gemini_client.generate_content(prompt)
            
            # Validate and sanitize reply
            if not self.validator.validate_reply(generated_reply):
                self.logger.warning("Generated reply failed validation, using fallback")
                generated_reply = self._get_fallback_reply(classification_result.category, language)
            
            sanitized_reply = self.validator.sanitize_reply(generated_reply)
            
            # Format final reply with language template
            final_reply = self.prompt_builder.format_final_reply(sanitized_reply, language)
            
            self.logger.info(f"Reply generated successfully for category: {classification_result.category}")
            return final_reply
            
        except Exception as e:
            self.logger.error(f"Reply generation failed: {e}")
            return self._get_fallback_reply(classification_result.category, language or 'fr')
    
    def _get_fallback_reply(self, category: str, language: str) -> str:
        """Get fallback reply when generation fails"""
        fallbacks = {
            'fr': {
                'Support technique': "Merci pour votre message. Notre équipe technique va examiner votre demande et vous contacter rapidement.",
                'Transactions financières': "Merci pour votre demande. Notre service facturation va traiter votre requête dans les plus brefs délais.",
                'Informations, feedback et demandes': "Merci pour votre message. Nous avons bien reçu votre demande et vous répondrons prochainement."
            },
            'ar': {
                'Support technique': "شكراً لرسالتكم. فريق الدعم التقني سيفحص طلبكم ويتواصل معكم قريباً.",
                'Transactions financières': "شكراً لطلبكم. خدمة الفوترة ستعالج استفساركم في أقرب وقت ممكن.",
                'Informations, feedback et demandes': "شكراً لرسالتكم. لقد استلمنا طلبكم وسنرد عليكم قريباً."
            },
            'en': {
                'Support technique': "Thank you for your message. Our technical team will review your request and contact you shortly.",
                'Transactions financières': "Thank you for your request. Our billing service will process your inquiry as soon as possible.",
                'Informations, feedback et demandes': "Thank you for your message. We have received your request and will respond to you soon."
            }
        }
        
        return fallbacks.get(language, fallbacks['fr']).get(
            category, 
            "Merci pour votre message. Nous vous répondrons prochainement."
        )
    
    def is_service_ready(self) -> bool:
        """Check if reply service is ready"""
        return self.gemini_client.is_connected()
