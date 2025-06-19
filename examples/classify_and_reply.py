"""
Example: Text Classification with Gemini Reply Generation

This example demonstrates how to use the enhanced system that combines:
1. Darija text classification using Atlas-Chat-9B
2. Intelligent reply generation using Google Gemini
3. Multi-language support (French, Arabic, English)
4. Production-ready error handling and logging

Prerequisites:
- GCP Compute Engine with authentication configured
- Google AI API enabled
- Atlas-Chat-9B model accessible
"""

import sys
import os
import time
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.registry import ServiceRegistry
from config.loader import ConfigLoader
from src.utils.logger import setup_logging


def demonstrate_classify_and_reply():
    """Demonstrate the complete classify-and-reply workflow"""
    
    # Setup logging
    setup_logging(level="INFO")
    
    print("🚀 Darija Classification + Gemini Reply Service Demo")
    print("=" * 60)
    
    try:
        # Initialize the service registry
        print("\n📋 Initializing services...")
        config_loader = ConfigLoader()
        registry = ServiceRegistry(config_loader)
        
        # Get the reply service (includes classification)
        reply_service = registry.get_reply_service()
        
        # Check service health
        print("\n🏥 Checking service health...")
        health = reply_service.health_check()
        print(f"   ✅ Classifier ready: {health['classifier_ready']}")
        print(f"   ✅ Reply generator ready: {health['reply_generator_ready']}")
        print(f"   ✅ Service operational: {health['service_operational']}")
        
        if not health['service_operational']:
            print("   ❌ Services not ready. Please check configuration.")
            return
        
        # Test messages in different languages and categories
        test_messages = [
            # Technical support (French)
            {
                "message": "Bonjour, j'ai un problème avec ma connexion internet, ça ne marche pas",
                "description": "Technical support issue in French"
            },
            
            # Technical support (Darija)
            {
                "message": "salam, service dial internet tayh ma kay5dmch",
                "description": "Technical support issue in Darija"
            },
            
            # Financial transaction (French)
            {
                "message": "Je veux annuler mon abonnement et arrêter les paiements",
                "description": "Financial/billing request in French"
            },
            
            # Financial transaction (Darija)
            {
                "message": "bghit nweqqef l'abonnement w n7bes les paiements",
                "description": "Financial/billing request in Darija"
            },
            
            # Information request (French)
            {
                "message": "Bonjour, pouvez-vous me donner les horaires d'ouverture?",
                "description": "Information request in French"
            },
            
            # Feedback (Darija)
            {
                "message": "chokran bzaf, khdma nqiya w zwina",
                "description": "Positive feedback in Darija"
            }
        ]
        
        print(f"\n🧪 Testing {len(test_messages)} messages...")
        print("=" * 60)
        
        results = []
        
        for i, test_case in enumerate(test_messages, 1):
            print(f"\n📝 Test {i}: {test_case['description']}")
            print(f"   Message: \"{test_case['message']}\"")
            
            start_time = time.time()
            
            try:
                # Classify and generate reply
                result = reply_service.classify_and_reply(
                    message=test_case['message'],
                    generate_reply=True
                )
                
                processing_time = time.time() - start_time
                
                # Display results
                print(f"\n   📊 Classification Results:")
                print(f"      Category: {result.classification_result.category}")
                print(f"      Confidence: {result.classification_result.confidence:.1%}")
                print(f"      Language detected: {result.language_detected}")
                
                print(f"\n   💬 Generated Reply:")
                print(f"      {result.generated_reply}")
                
                print(f"\n   ⏱️  Processing time: {processing_time:.2f}s")
                
                results.append({
                    'test_case': test_case,
                    'result': result,
                    'processing_time': processing_time,
                    'success': True
                })
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results.append({
                    'test_case': test_case,
                    'error': str(e),
                    'success': False
                })
            
            print("-" * 60)
        
        # Summary
        print(f"\n📈 Summary:")
        successful = sum(1 for r in results if r['success'])
        print(f"   ✅ Successful: {successful}/{len(results)}")
        
        if successful > 0:
            avg_time = sum(r['processing_time'] for r in results if r['success']) / successful
            print(f"   ⏱️  Average processing time: {avg_time:.2f}s")
        
        # Service statistics
        stats = reply_service.get_service_stats()
        print(f"\n📊 Service Statistics:")
        print(f"   Total requests: {stats['total_requests']}")
        print(f"   Total replies: {stats['total_replies']}")
        print(f"   Reply success rate: {stats['reply_success_rate']:.1f}%")
        
        return results
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        return None


def demonstrate_classification_only():
    """Demonstrate classification without reply generation"""
    
    print("\n🔍 Classification-Only Demo")
    print("=" * 40)
    
    try:
        registry = ServiceRegistry()
        reply_service = registry.get_reply_service()
        
        message = "wach kayn chi problème m3a réseau?"
        print(f"Message: \"{message}\"")
        
        # Classify only
        result = reply_service.classify_only(message)
        
        print(f"\nClassification:")
        print(f"  Category: {result.category}")
        print(f"  Confidence: {result.confidence:.1%}")
        print(f"  Method: {result.method}")
        
        return result
        
    except Exception as e:
        print(f"❌ Classification failed: {e}")
        return None


def demonstrate_reply_only():
    """Demonstrate reply generation for pre-classified message"""
    
    print("\n💬 Reply-Only Demo")
    print("=" * 40)
    
    try:
        registry = ServiceRegistry()
        reply_service = registry.get_reply_service()
        
        # First classify
        message = "Merci beaucoup pour votre excellent service!"
        classification = reply_service.classify_only(message)
        
        print(f"Message: \"{message}\"")
        print(f"Classification: {classification.category}")
        
        # Then generate reply
        reply = reply_service.reply_only(message, classification)
        
        print(f"\nGenerated Reply:")
        print(f"  {reply}")
        
        return reply
        
    except Exception as e:
        print(f"❌ Reply generation failed: {e}")
        return None


def main():
    """Main demo function"""
    
    print("🌟 Darija Classification + Gemini Reply System")
    print("🔧 Production-Ready AI Customer Service Solution")
    print("=" * 80)
    
    # Run main demo
    results = demonstrate_classify_and_reply()
    
    if results:
        print("\n" + "=" * 80)
        
        # Additional demos
        demonstrate_classification_only()
        demonstrate_reply_only()
        
        print("\n✨ Demo completed successfully!")
        print("\n📚 Key Features Demonstrated:")
        print("   • Multi-language text classification (French, Arabic, Darija)")
        print("   • Intelligent reply generation with Gemini")
        print("   • Production-ready error handling")
        print("   • Comprehensive logging and monitoring")
        print("   • Clean architecture with dependency injection")
        print("   • GCP Compute Engine integration")
        
        print("\n🚀 Ready for production deployment!")
    else:
        print("\n❌ Demo failed. Please check your configuration.")


if __name__ == "__main__":
    main() 