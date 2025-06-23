"""
Main Entry Point for Darija Classification + Gemini Reply Service

Simple usage:
    python main.py --classify "your text here"
    python main.py --reply "your text here"
    python main.py --classify-and-reply "your text here"
"""

import sys
import argparse
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from src.registry import ServiceRegistry


def classify_text(text):
    """Classify text only"""
    try:
        registry = ServiceRegistry()
        classification_service = registry.get_classification_service()
        
        result = classification_service.classify(text)
        
        print(f"Text: {text}")
        print(f"Category: {result.category}")
        print(f"Confidence: {result.confidence:.2%}")
        print(f"Processing Time: {result.processing_time:.2f}s")
        
    except Exception as e:
        print(f"Error: {e}")


def generate_reply(text):
    """Generate reply only (without classification)"""
    try:
        registry = ServiceRegistry()
        reply_service = registry.get_reply_service()
        
        reply = reply_service.reply_only(text)
        
        print(f"Text: {text}")
        print(f"Reply: {reply}")
        
    except Exception as e:
        print(f"Error: {e}")


def classify_and_reply(text):
    """Classify text and generate reply"""
    try:
        registry = ServiceRegistry()
        reply_service = registry.get_reply_service()
        
        result = reply_service.classify_and_reply(text)
        
        print(f"Text: {text}")
        print(f"Category: {result.classification_result.category}")
        print(f"Confidence: {result.classification_result.confidence:.2%}")
        print(f"Language: {result.language_detected}")
        print(f"Reply: {result.generated_reply}")
        print(f"Processing Time: {result.processing_time:.2f}s")
        
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Darija Classification + Gemini Reply Service")
    parser.add_argument("--classify", type=str, help="Classify text only")
    parser.add_argument("--reply", type=str, help="Generate reply only (no classification)")
    parser.add_argument("--classify-and-reply", type=str, help="Classify text and generate reply")
    
    args = parser.parse_args()
    
    if args.classify:
        classify_text(args.classify)
    elif args.reply:
        generate_reply(args.reply)
    elif getattr(args, 'classify_and_reply'):
        classify_and_reply(getattr(args, 'classify_and_reply'))
    else:
        print("Usage:")
        print("  python main.py --classify 'your text here'")
        print("  python main.py --reply 'your text here'")
        print("  python main.py --classify-and-reply 'your text here'")


if __name__ == "__main__":
    main() 