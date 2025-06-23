"""
One-time setup script to store Gemini API key in Google Secret Manager

Usage:
    python setup_secret.py YOUR_API_KEY_HERE
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from src.utils.secret_manager import GeminiSecretManager


def main():
    """Setup Gemini API key in Secret Manager"""
    
    if len(sys.argv) != 2:
        print("Usage: python setup_secret.py YOUR_API_KEY_HERE")
        sys.exit(1)
    
    api_key = sys.argv[1].strip()
    
    if len(api_key) < 10:
        print("❌ API key seems too short. Please check your API key.")
        sys.exit(1)
    
    try:
        print("🔐 Setting up Gemini API key in Google Secret Manager...")
        
        secret_manager = GeminiSecretManager()
        created = secret_manager.setup_api_key(api_key)
        
        if created:
            print("✅ API key stored successfully in Secret Manager!")
        else:
            print("✅ API key already exists in Secret Manager!")
        
        print("🚀 Setup complete! You can now use the system securely.")
        print("   Run: python main.py --reply 'your message here'")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        print("\nMake sure you have:")
        print("  1. Enabled Secret Manager API in your GCP project")
        print("  2. Proper IAM permissions (Secret Manager Admin)")
        print("  3. Authenticated with gcloud")
        sys.exit(1)


if __name__ == "__main__":
    main() 