"""
Example: Using the Centralized Registry
Shows how to import and use components from the new registry system
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import from centralized registry instead of individual __init__.py files
from src.registry import (
    # Core components
    TextClassifier,
    ModelFactory,
    
    # Services
    ClassificationService,
    ServiceFactory,
    
    # Configuration
    ConfigLoader,
    
    # Utilities
    DeviceManager,
    setup_logging,
    
    # Exceptions
    ClassificationError,
    ModelLoadError,
    
    # Convenience functions
    get_main_classifier,
    get_classification_service,
    get_all_exceptions
)


def main():
    """Demonstrate registry usage"""
    print("🚀 Registry Usage Example")
    print("=" * 40)
    
    # 1. Use convenience functions
    print("\n1️⃣ Using convenience functions:")
    main_classifier_class = get_main_classifier()
    service_class = get_classification_service()
    exceptions = get_all_exceptions()
    
    print(f"   • Main classifier: {main_classifier_class.__name__}")
    print(f"   • Service class: {service_class.__name__}")
    print(f"   • Available exceptions: {[e.__name__ for e in exceptions]}")
    
    # 2. Direct class usage
    print("\n2️⃣ Direct class usage:")
    try:
        # Setup logging
        setup_logging(level="INFO")
        
        # Check device availability
        device_manager = DeviceManager()
        device = device_manager.get_optimal_device()
        print(f"   • Optimal device: {device}")
        
        # Create service factory
        factory = ServiceFactory()
        print(f"   • Service factory created: {factory.__class__.__name__}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Show what was moved from __init__.py files
    print("\n3️⃣ Previously in __init__.py files:")
    print("   • src/config/loader.py → config/loader.py")
    print("   • src/__init__.py → src/registry.py")
    print("   • src/core/__init__.py → src/registry.py")
    print("   • src/services/__init__.py → src/registry.py")
    print("   • src/utils/__init__.py → src/registry.py")
    print("   • All config logic → config/loader.py")
    
    # 4. Clean __init__.py files
    print("\n4️⃣ All __init__.py files are now empty! ✨")
    print("   • Better separation of concerns")
    print("   • Centralized import management")
    print("   • Easier debugging and maintenance")
    
    print("\n✅ Registry example completed!")


if __name__ == "__main__":
    main() 