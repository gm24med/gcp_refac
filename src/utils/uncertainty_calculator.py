"""
Uncertainty calculation utilities for classification results
"""

import torch
import numpy as np
from typing import Dict, Any


class UncertaintyCalculator:
    """Calculates uncertainty metrics for predictions - max 50 lines"""
    
    def __init__(self):
        """Initialize uncertainty calculator"""
        self.epsilon = 1e-8  # Small value to prevent log(0)
    
    def calculate(self, probabilities: torch.Tensor) -> Dict[str, float]:
        """Calculate uncertainty metrics from probabilities"""
        if not isinstance(probabilities, torch.Tensor):
            raise ValueError("Probabilities must be a torch.Tensor")
        
        # Convert to numpy for calculations
        probs = probabilities.detach().cpu().numpy()
        
        # Calculate entropy (measure of uncertainty)
        entropy = self._calculate_entropy(probs)
        
        # Calculate confidence margin (gap between top 2 predictions)
        margin = self._calculate_margin(probs)
        
        # Calculate max confidence
        max_confidence = float(np.max(probs))
        
        # Calculate min confidence  
        min_confidence = float(np.min(probs))
        
        # Calculate coefficient of variation
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
        # Add epsilon to prevent log(0)
        safe_probs = probs + self.epsilon
        entropy = -np.sum(safe_probs * np.log(safe_probs))
        return float(entropy)
    
    def _calculate_margin(self, probs: np.ndarray) -> float:
        """Calculate margin between top 2 predictions"""
        sorted_probs = np.sort(probs)[::-1]  # Sort descending
        margin = sorted_probs[0] - sorted_probs[1]
        return float(margin)
    
    def _calculate_coefficient_variation(self, probs: np.ndarray) -> float:
        """Calculate coefficient of variation"""
        mean_prob = np.mean(probs)
        std_prob = np.std(probs)
        cv = std_prob / (mean_prob + self.epsilon)
        return float(cv)
    
    def is_high_uncertainty(self, metrics: Dict[str, float], threshold: float = 0.5) -> bool:
        """Determine if prediction has high uncertainty"""
        return metrics['entropy'] > threshold or metrics['margin'] < 0.1 