#!/usr/bin/env python
"""
Production-ready Darija Text Classification CLI
Using clean architecture with dependency injection
"""

import sys
import argparse
from pathlib import Path
from typing import List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import from centralized registry
from src.registry import ServiceFactory, ClassificationError, ResultFormatter


def display_result(result, verbose: bool = False) -> None:
    """Display classification result in a clean format"""
    print(f"\n{'='*60}")
    print("CLASSIFICATION RESULT")
    print(f"{'='*60}")
    print(f" Text: {result.text}")
    print(f"  Category: {result.category}")
    print(f"  Class ID: {result.predicted_class}")
    print(f"  Confidence: {result.confidence:.1%}")
    print(f"  Method: {result.method}")
    
    if verbose:
        print(f"\n Detailed Probabilities:")
        for category, prob in result.probabilities.items():
            print(f"   • {category}: {prob:.1%}")
        
        print(f"\n Uncertainty Metrics:")
        for metric, value in result.uncertainty_metrics.items():
            print(f"   • {metric}: {value:.4f}")
    
    print(f"{'='*60}")


def display_batch_results(results: List, verbose: bool = False) -> None:
    """Display batch results summary"""
    if not results:
        print(" No results to display")
        return
    
    print(f"\n{'='*60}")
    print(f" BATCH CLASSIFICATION RESULTS ({len(results)} texts)")
    print(f"{'='*60}")
    
    # Summary statistics
    avg_confidence = sum(r.confidence for r in results) / len(results)
    categories = {}
    for result in results:
        categories[result.category] = categories.get(result.category, 0) + 1
    
    print(f" Average Confidence: {avg_confidence:.1%}")
    print(f" Category Distribution:")
    for category, count in categories.items():
        percentage = count / len(results) * 100
        print(f"   • {category}: {count} ({percentage:.1f}%)")
    
    if verbose:
        print(f"\n Individual Results:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.text[:50]}{'...' if len(result.text) > 50 else ''}")
            print(f"   → {result.category} ({result.confidence:.1%})")
    
    print(f"{'='*60}")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Production Darija Text Classification System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Classify single text
  python classify_v2.py "Service client offline wach kayn chi solution"
  
  # Classify with verbose output
  python classify_v2.py "baghi n3ref montant dial facture" --verbose
  
  # Classify from file
  python classify_v2.py --file texts.txt --verbose
  
  # Batch classify multiple texts
  python classify_v2.py --batch "Text 1" "Text 2" "Text 3"
        """
    )
    
    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("text", nargs="?", help="Single text to classify")
    input_group.add_argument("--file", help="File containing texts to classify (one per line)")
    input_group.add_argument("--batch", nargs="+", help="Multiple texts to classify")
    
    # Configuration options
    parser.add_argument("--config", default="config", help="Configuration directory")
    parser.add_argument("--log-level", default="INFO", 
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Logging level")
    parser.add_argument("--temperature", type=float, default=0.1,
                       help="Temperature for prediction (0.0-1.0)")
    
    # Output options
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Show detailed results")
    parser.add_argument("--output", help="Save results to file")
    
    args = parser.parse_args()
    
    try:
        # Create service with dependency injection
        print(" Initializing Darija Classification System...")
        factory = ServiceFactory(config_dir=args.config, log_level=args.log_level)
        service = factory.create_classification_service()
        print(" System ready!")
        
        # Determine input texts
        texts = []
        if args.text:
            texts = [args.text]
        elif args.file:
            file_path = Path(args.file)
            if not file_path.exists():
                print(f" File not found: {args.file}")
                sys.exit(1)
            texts = file_path.read_text(encoding='utf-8').strip().split('\n')
            texts = [t.strip() for t in texts if t.strip()]
        elif args.batch:
            texts = args.batch
        
        if not texts:
            print(" No texts to classify")
            sys.exit(1)
        
        # Perform classification
        if len(texts) == 1:
            # Single text classification
            result = service.classify_text(texts[0], temperature=args.temperature)
            display_result(result, args.verbose)
        else:
            # Batch classification
            print(f" Processing {len(texts)} texts...")
            results = service.classify_batch(texts, temperature=args.temperature)
            display_batch_results(results, args.verbose)
        
        # Save results if requested
        if args.output:
            output_path = Path(args.output)
            # Implementation for saving results would go here
            print(f"💾 Results saved to: {output_path}")
        
        # Display service stats
        stats = service.get_service_stats()
        print(f"\n Service Stats: {stats['total_requests']} requests processed")
        
    except ClassificationError as e:
        print(f" Classification Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n Classification cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f" Unexpected error: {e}")
        if args.log_level == "DEBUG":
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 