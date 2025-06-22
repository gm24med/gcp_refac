# Darija Text Classification System + Gemini Reply Service with Gemini Reply Service

🚀 **Production-Ready AI Customer Service Solution**

A sophisticated, enterprise-grade system for classifying Moroccan Darija text messages and generating intelligent replies using Google Gemini. Built with clean architecture principles and designed for GCP Compute Engine deployment.

## 🌟 Key Features

### 🔍 **Advanced Text Classification**
- **Multi-language support**: French, Arabic, Darija (Moroccan Arabic)
- **High accuracy**: Uses Atlas-Chat-9B model fine-tuned for Darija
- **Three categories**: Technical Support, Financial Transactions, General Information
- **Uncertainty quantification**: Entropy, margin, confidence metrics
- **Batch processing**: Efficient handling of multiple messages

### 💬 **Intelligent Reply Generation**
- **Google Gemini integration**: Powered by Gemini 1.5 Pro/Flash
- **Context-aware responses**: Replies based on classification results
- **Multi-language replies**: Automatic language detection and matching
- **Safety controls**: Built-in content filtering and validation
- **Fallback mechanisms**: Graceful degradation when AI fails

### 🏗️ **Production-Ready Architecture**
- **Clean Architecture**: SOLID principles, dependency injection
- **Scalable design**: Modular components, easy to extend
- **Comprehensive logging**: Detailed monitoring and debugging
- **Error handling**: Robust exception management
- **GCP optimized**: Native Compute Engine integration

## 📋 Categories

| Category | Description | Examples |
|----------|-------------|----------|
| **Support technique** | Technical issues, bugs, access problems | "service offline", "connexion problème" |
| **Transactions financières** | Billing, payments, subscriptions | "annuler abonnement", "problème paiement" |
| **Informations, feedback et demandes** | General info, feedback, requests | "horaires ouverture", "merci service" |

## 🚀 Quick Start

### 1. **GCP Compute Engine Setup**

   ```bash
# Clone the repository
git clone <your-repo-url>
cd gcp_refac

# Run the automated setup script
python setup_gcp.py
```

### 2. **Manual Setup** (if needed)

   ```bash
# Install dependencies
   pip install -r requirements.txt

# Authenticate with GCP
gcloud auth login
gcloud auth application-default login

# Set up environment
export GOOGLE_CLOUD_PROJECT=your-project-id
export PYTHONPATH=$(pwd)
```

### 3. **Basic Usage**

```python
from src.registry import ServiceRegistry

# Initialize the service
registry = ServiceRegistry()
reply_service = registry.get_reply_service()

# Classify and generate reply
result = reply_service.classify_and_reply(
    message="salam, service dial internet tayh ma kay5dmch",
    generate_reply=True
)

print(f"Category: {result.classification_result.category}")
print(f"Confidence: {result.classification_result.confidence:.1%}")
print(f"Reply: {result.generated_reply}")
```

## 🔧 Configuration

### **Main Configuration** (`config/settings.yaml`)

```yaml
# Model settings
model:
  id: "MBZUAI-Paris/Atlas-Chat-9B"
  device: "cuda:0"  # auto, cuda, or cpu
  cache_dir: "models/cache"
  torch_dtype: "float16"

# Gemini settings
gemini:
  model_name: "gemini-1.5-pro"  # or gemini-1.5-flash
  project_id: null  # Auto-detected from GCP
  location: "us-central1"
  parameters:
    temperature: 0.7
    max_output_tokens: 1024
  safety_settings:
    harassment: "BLOCK_MEDIUM_AND_ABOVE"
    hate_speech: "BLOCK_MEDIUM_AND_ABOVE"
    sexually_explicit: "BLOCK_MEDIUM_AND_ABOVE"
    dangerous_content: "BLOCK_MEDIUM_AND_ABOVE"

# Reply service settings
reply_service:
  enabled: true
  default_language: "fr"
  supported_languages: ["fr", "ar", "en"]
  max_context_length: 2000
  include_classification: true
```

### **Prompts Configuration** (`config/prompt.yaml`)

Contains specialized prompts for:
- Darija text classification
- Reply generation by category
- Language-specific templates
- Safety and content guidelines

## 💻 Examples

### **Complete Classification + Reply**

```python
# examples/classify_and_reply.py
from src.registry import ServiceRegistry

registry = ServiceRegistry()
reply_service = registry.get_reply_service()

# Test different scenarios
messages = [
    "Bonjour, j'ai un problème avec ma connexion internet",
    "bghit nweqqef l'abonnement w n7bes les paiements", 
    "chokran bzaf, khdma nqiya w zwina"
]

for message in messages:
    result = reply_service.classify_and_reply(message)
    print(f"Message: {message}")
    print(f"Category: {result.classification_result.category}")
    print(f"Reply: {result.generated_reply}")
    print("-" * 50)
```

### **Classification Only**

```python
# For cases where you only need classification
result = reply_service.classify_only("wach kayn chi problème m3a réseau?")
print(f"Category: {result.category}")
print(f"Confidence: {result.confidence:.1%}")
```

### **Reply Only**

```python
# For pre-classified messages
classification = reply_service.classify_only(message)
reply = reply_service.reply_only(message, classification, language="fr")
print(f"Generated reply: {reply}")
```

## 🏗️ Architecture

### **Clean Architecture Layers**

```
┌─────────────────────────────────────────┐
│                Examples                 │  ← Application Entry Points
├─────────────────────────────────────────┤
│            Services Layer               │  ← Business Logic
│  • ReplyService                        │
│  • ClassificationService               │
│  • ReplyServiceFactory                 │
├─────────────────────────────────────────┤
│              Core Layer                 │  ← Domain Logic
│  • Interfaces (IClassifier, IReply)    │
│  • Models (GeminiClient, Classifiers)  │
│  • Processors (Language, Reply)        │
├─────────────────────────────────────────┤
│           Infrastructure                │  ← External Dependencies
│  • Config (YAML loaders)               │
│  • Utils (Logging, Exceptions)         │
│  • Data (Processors, Formatters)       │
└─────────────────────────────────────────┘
```

### **Key Components**

- **ServiceRegistry**: Centralized dependency injection container
- **ReplyService**: Main application service for classification + reply
- **GeminiClient**: Google Gemini API integration with retry logic
- **LanguageDetector**: Multi-language text analysis
- **ReplyGenerator**: Context-aware response generation
- **ConfigLoader**: Centralized configuration management

## 📊 Performance & Monitoring

### **Built-in Metrics**

```python
# Service statistics
stats = reply_service.get_service_stats()
print(f"Total requests: {stats['total_requests']}")
print(f"Reply success rate: {stats['reply_success_rate']:.1f}%")

# Health check
health = reply_service.health_check()
print(f"Service operational: {health['service_operational']}")
```

### **Logging**

- **Structured logging**: JSON format for production
- **Multiple levels**: DEBUG, INFO, WARNING, ERROR
- **Request tracking**: Unique request IDs
- **Performance metrics**: Processing times, success rates

## 🔒 Security & Safety

### **Content Safety**
- **Gemini safety filters**: Harassment, hate speech, explicit content
- **Input validation**: Message length, format checks
- **Output sanitization**: Removes sensitive information patterns
- **Fallback responses**: Safe defaults when AI fails

### **Authentication**
- **GCP IAM integration**: Uses Compute Engine service account
- **API key management**: Secure credential handling
- **Access controls**: Role-based permissions

## 🚀 Deployment

### **GCP Compute Engine**

1. **Create VM instance** with GPU (optional)
2. **Enable APIs**: AI Platform, Generative AI
3. **Set up authentication**: Service account with proper roles
4. **Run setup script**: `python setup_gcp.py`
5. **Test deployment**: `python examples/classify_and_reply.py`

### **Production Considerations**

- **Scaling**: Use load balancers for high traffic
- **Monitoring**: Set up Cloud Monitoring alerts
- **Logging**: Forward logs to Cloud Logging
- **Backup**: Regular model and config backups
- **Updates**: Rolling deployment strategy

## 📈 Advanced Usage

### **Batch Processing**

```python
# Process multiple messages efficiently
messages = ["message1", "message2", "message3"]
results = []

for message in messages:
    result = reply_service.classify_and_reply(message)
    results.append(result)

# Analyze batch results
categories = [r.classification_result.category for r in results]
avg_confidence = sum(r.confidence_score for r in results) / len(results)
```

### **Custom Configuration**

```python
# Use custom configuration
from config.loader import ConfigLoader

config = ConfigLoader("custom_config")
registry = ServiceRegistry(config)
reply_service = registry.get_reply_service()
```

### **Integration with External Systems**

```python
# Example: Webhook integration
from flask import Flask, request, jsonify

app = Flask(__name__)
registry = ServiceRegistry()
reply_service = registry.get_reply_service()

@app.route('/classify-and-reply', methods=['POST'])
def classify_and_reply():
    message = request.json.get('message')
    result = reply_service.classify_and_reply(message)
    
    return jsonify({
        'category': result.classification_result.category,
        'confidence': result.classification_result.confidence,
        'reply': result.generated_reply,
        'language': result.language_detected
    })
```

## 🛠️ Development

### **Adding New Languages**

1. Update `config/settings.yaml` supported languages
2. Add language patterns to `LanguageDetector`
3. Create language-specific templates in `config/prompt.yaml`
4. Test with sample messages

### **Extending Categories**

1. Update prompts in `config/prompt.yaml`
2. Add category mappings in `config/settings.yaml`
3. Train/fine-tune classification model if needed
4. Update reply templates

### **Custom Reply Generators**

```python
from src.core.interfaces import IReplyGenerator

class CustomReplyGenerator(IReplyGenerator):
    def generate_reply(self, message, classification, language=None):
        # Your custom logic here
        return "Custom reply"
```

## 📚 API Reference

### **ReplyService**

```python
class ReplyService:
    def classify_and_reply(message: str, generate_reply: bool = True, 
                          language: str = None) -> ReplyResult
    def classify_only(message: str) -> ClassificationResult
    def reply_only(message: str, classification: ClassificationResult, 
                  language: str = None) -> str
    def get_service_stats() -> Dict[str, Any]
    def health_check() -> Dict[str, Any]
```

### **ServiceRegistry**

```python
class ServiceRegistry:
    def get_reply_service() -> ReplyService
    def get_classification_service() -> ClassificationService
    def get_gemini_client() -> GeminiClient
    def health_check() -> Dict[str, Any]
    def cleanup() -> None
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Follow coding standards**: Clean architecture, type hints, docstrings
4. **Add tests**: Unit tests for new functionality
5. **Update documentation**: README, docstrings, examples
6. **Submit pull request**: Detailed description of changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Atlas-Chat-9B**: MBZUAI-Paris for the Darija language model
- **Google Gemini**: Advanced AI capabilities for reply generation
- **GCP**: Robust cloud infrastructure and AI services
- **Open Source Community**: Libraries and tools that made this possible

---

**🚀 Ready to deploy your AI-powered customer service solution!**

For support, please open an issue or contact the development team.
