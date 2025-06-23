# Darija Classification + Gemini Reply System

AI-powered Moroccan Darija text classification and reply generation using Atlas-Chat-9B and Google Gemini.

## Features

- **Text Classification**: Categorize Darija messages into 3 classes using Atlas-Chat-9B
- **Reply Generation**: Generate contextual responses in Darija using Google Gemini
- **Language Detection**: Automatic language detection (Arabic, French, English, Darija)
- **Secure API Management**: Google Secret Manager integration for API keys

## Quick Start

### 1. Setup
```bash
git clone <repository>
cd gcp_refac
pip install -r requirements.txt
```

### 2. Configure API Key
```bash
python setup_secret.py YOUR_GEMINI_API_KEY
```

### 3. Usage
```bash
# Classify text only
python main.py --classify "salam, kifach nta?"

# Generate reply only
python main.py --reply "salam, kifach nta?"

# Both classification and reply
python main.py --classify-and-reply "salam, kifach nta?"
```

## Architecture

```
main.py → ServiceRegistry → {ClassificationService, ReplyService}
                          ↓
                     Atlas-Chat-9B + Gemini
```

## Configuration

- **Model**: `config/settings.yaml`
- **Prompts**: `config/prompt.yaml`
- **Dependencies**: `requirements.txt`

## Requirements

- Python 3.9+
- Google Cloud Project with Secret Manager API
- CUDA-compatible GPU (recommended)
- Gemini API key

## Output Format

**Classification:**
```
Text: salam, kifach nta?
Category: greeting
Confidence: 92.34%
Processing Time: 1.23s
```

**Reply:**
```
Text: salam, kifach nta?
Language: darija
Reply: Salam! Ana bikhir, hamdullah. Nta kifach?
```

## Security

- API keys stored in Google Secret Manager
- No hardcoded credentials
- Secure authentication flow

## License

MIT License
