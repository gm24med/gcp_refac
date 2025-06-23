"""
Uncertainty calculation utilities for classification results

This module calculates various uncertainty metrics from probability distributions,
with proper handling of edge cases like zero probabilities to avoid mathematical
errors (log(0), division by zero).
"""

import torch
import numpy as np
from typing import Dict, Any


class UncertaintyCalculator:
    """Calculates uncertainty metrics for predictions - max 50 lines"""
    
    def __init__(self):
        """Initialize uncertainty calculator"""
        self.epsilon = 1e-8
    
    def calculate(self, probabilities: torch.Tensor) -> Dict[str, float]:
        """Calculate uncertainty metrics from probabilities"""
        if not isinstance(probabilities, torch.Tensor):
            raise ValueError("Probabilities must be a torch.Tensor")
        
        probs = probabilities.detach().cpu().numpy()
        
        if np.any(probs < 0):
            raise ValueError("Probabilities cannot be negative")
        if np.any(np.isnan(probs)) or np.any(np.isinf(probs)):
            raise ValueError("Probabilities contain NaN or infinite values")
        
        prob_sum = np.sum(probs)
        if prob_sum > self.epsilon:
            probs = probs / prob_sum
        
        entropy = self._calculate_entropy(probs)
        margin = self._calculate_margin(probs)
        max_confidence = float(np.max(probs))
        min_confidence = float(np.min(probs))
        cv = self._calculate_coefficient_variation(probs)
        
        return {
            'entropy': entropy,
            'margin': margin,
            'max_confidence': max_confidence,
            'min_confidence': min_confidence,
            'coefficient_variation': cv
        }
    
    def _calculate_entropy(self, probs: np.ndarray) -> float:
        """Calculate entropy of probability distribution"""
        nonzero_mask = probs > self.epsilon
        entropy = 0.0
        if np.any(nonzero_mask):
            safe_probs = probs[nonzero_mask]
            entropy = -np.sum(safe_probs * np.log(safe_probs))
        return float(entropy)
    
    def _calculate_margin(self, probs: np.ndarray) -> float:
        """Calculate margin between top 2 predictions"""
        sorted_probs = np.sort(probs)[::-1]
        margin = sorted_probs[0] - sorted_probs[1]
        return float(margin)
    
    def _calculate_coefficient_variation(self, probs: np.ndarray) -> float:
        """Calculate coefficient of variation"""
        mean_prob = np.mean(probs)
        std_prob = np.std(probs)
        if mean_prob < self.epsilon:
            return 0.0
        cv = std_prob / mean_prob
        return float(cv)
    
    def is_high_uncertainty(self, metrics: Dict[str, float], threshold: float = 0.5) -> bool:
        """Determine if prediction has high uncertainty"""
        return metrics['entropy'] > threshold or metrics['margin'] < 0.1 