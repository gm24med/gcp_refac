"""
Result formatting utilities for classification outputs
"""

import torch
from typing import Dict, Any
from ..core.interfaces import ClassificationResult
from config.loader import ConfigLoader


class ResultFormatter:
    """Formats classification results into standardized format - max 50 lines"""
    
    def __init__(self, config_loader: ConfigLoader):
        """Initialize with configuration"""
        self.config_loader = config_loader
        self.category_map = config_loader.get_categories()
    
    def format_result(self, 
                     text: str,
                     probabilities: torch.Tensor,
                     predicted_idx: torch.Tensor,
                     uncertainty_metrics: Dict[str, float],
                     temperature: float) -> ClassificationResult:
        """Format prediction result into standardized structure"""
        
        # Get predicted class and category
        predicted_class = str(predicted_idx.item() + 1)
        category = self.category_map[predicted_class]
        
        # Format probabilities as dictionary
        prob_dict = self._format_probabilities(probabilities)
        
        # Get confidence
        confidence = float(probabilities.max())
        
        # Create method identifier
        method = f"llm-t{temperature:.1f}"
        
        return ClassificationResult(
            text=text,
            predicted_class=predicted_class,
            category=category,
            confidence=confidence,
            probabilities=prob_dict,
            uncertainty_metrics=uncertainty_metrics,
            method=method
        )
    
    def _format_probabilities(self, probabilities: torch.Tensor) -> Dict[str, float]:
        """Format probabilities as category dictionary"""
        probs = probabilities.detach().cpu().numpy()
        
        return {
            self.category_map["1"]: float(probs[0]),
            self.category_map["2"]: float(probs[1]),
            self.category_map["3"]: float(probs[2])
        }
    
    def format_batch_results(self, results: list) -> Dict[str, Any]:
        """Format batch results with summary statistics"""
        if not results:
            return {'results': [], 'summary': {}}
        
        avg_confidence = sum(r.confidence for r in results) / len(results)
        avg_entropy = sum(r.uncertainty_metrics['entropy'] for r in results) / len(results)
        
        return {
            'results': [self._result_to_dict(r) for r in results],
            'summary': {
                'total_predictions': len(results),
                'average_confidence': avg_confidence,
                'average_entropy': avg_entropy
            }
        }
    
    def _result_to_dict(self, result: ClassificationResult) -> Dict[str, Any]:
        """Convert ClassificationResult to dictionary"""
        return {
            'text': result.text,
            'predicted_class': result.predicted_class,
            'category': result.category,
            'confidence': result.confidence,
            'probabilities': result.probabilities,
            'uncertainty_metrics': result.uncertainty_metrics,
            'method': result.method
        } 