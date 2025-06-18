#!/usr/bin/env python
"""Example script for classifying text using the new registry system."""

import sys
import os
from pathlib import Path

# Add src to Python path  
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import from centralized registry
from src.registry import ServiceFactory, ClassificationError, setup_logging

def main():
    """Run classification examples using the new architecture."""
    print("Darija Text Classification Example")
    print("=================================\n")
    
    try:
        # Setup logging
        setup_logging(level="INFO")
        
        # Initialize service factory and classification service
        print("Initializing classification service...")
        factory = ServiceFactory(config_dir="config", log_level="INFO")
        service = factory.create_classification_service()
        print("Service initialized.\n")
        
        # Example texts
        example_texts = [
            "Service client offline wach kayn chi solution",
            "wach kayn kifach ndir résiliation",
            "baghi n3ref achmen type de compte 3andy",
            "chno ndir ila bghit n7bes lkhedma meakom",
            "Wash 3ndkoum chi problème m3a réseau"
        ]
        
        # Classify each example
        print("Classifying example texts:")
        print("-------------------------\n")
        
        for i, text in enumerate(example_texts, 1):
            # Classify text using the service
            result = service.classify_text(text)
            
            # Print results
            print(f"Example {i}:")
            print(f"Text: {text}")
            print(f"Category: {result.category} (Class {result.predicted_class})")
            print(f"Confidence: {result.confidence:.2%}")
            print(f"Method: {result.method}")
            print()
            
            # Print probabilities for each class
            print("Class probabilities:")
            for class_name, prob in result.probabilities.items():
                print(f"- {class_name}: {prob:.2%}")
            print("\n" + "-" * 50 + "\n")
        
        # Get service statistics
        stats = service.get_service_stats()
        print("Session Statistics:")
        print(f"Total classifications: {stats['total_requests']}")
        print(f"Cache hits: {stats.get('cache_hits', 0)}")
        print("✅ Example completed successfully!")
        
    except ClassificationError as e:
        print(f"❌ Classification Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()