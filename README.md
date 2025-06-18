# Darija Text Classification System

A production-grade system for classifying Moroccan Darija text messages using the Atlas-Chat-9B language model. The system implements a robust classification pipeline with uncertainty quantification, comprehensive analysis tools, and production-ready deployment capabilities.

## System Overview

The system is designed for high-performance text classification with a focus on:
- Accurate categorization of Darija text messages
- Quantification of prediction uncertainty
- Comprehensive performance analysis
- Production deployment readiness

### Core Components

1. **Classification Engine**
   - Atlas-Chat-9B model integration
   - Prompt-based classification with probability extraction
   - Batch processing capabilities
   - Uncertainty metrics (entropy, margin, confidence)

2. **Analysis Framework**
   - Uncertainty analysis and visualization
   - Performance metrics calculation
   - Error analysis and case mining
   - Comprehensive reporting

3. **Production Infrastructure**
   - Modular, extensible architecture
   - Configuration management
   - Logging and monitoring
   - Export and deployment utilities

## Technical Requirements

- Python 3.8+
- CUDA-capable GPU (recommended)
- 16GB+ RAM
- 50GB+ disk space (for model and data)

## Installation

1. **Environment Setup**
   ```bash
   git clone https://github.com/yourusername/DARIJA_CALL_CENTER.git
   cd DARIJA_CALL_CENTER
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   ```

2. **Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration**
   - Model settings: `config/settings.yaml`
   - Classification prompts: `config/prompt.yaml`
   - Data paths: Update in settings.yaml

## Usage

### Classification API (New Architecture)

```python
# Modern approach using the new registry system
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.registry import ServiceFactory, ClassificationService

# Initialize service with dependency injection
factory = ServiceFactory()
service = factory.create_service()

# Single prediction
result = service.classify_text("Your Darija text here")
print(f"Category: {result.category}")
print(f"Confidence: {result.confidence:.2%}")

# Batch processing
results = service.classify_batch(["Text 1", "Text 2", ...])
```

### Command Line Interface

1. **Single Text Classification**
   ```bash
   python classify_v2.py "Your message in Darija"
   ```

2. **Batch Classification**
   ```bash
   python classify_v2.py --batch "Text 1" "Text 2" "Text 3"
   ```

3. **File-based Classification**
   ```bash
   python classify_v2.py --file texts.txt --verbose
   ```

## Architecture

The system follows **Clean Architecture** principles with these layers:

- `src/core/`: Business logic (interfaces, classifiers, models, processors)
- `src/services/`: Application layer (high-level workflows, dependency injection)
- `src/config/`: Configuration management
- `src/utils/`: Supporting utilities (device management, logging, exceptions)
- `src/registry.py`: Centralized exports and imports

### Key Architectural Improvements

✅ **Before**: 398-line monolithic `DarijaClassifier`
✅ **After**: Multiple focused classes (<50 lines each)
✅ **SOLID Principles**: Single responsibility, dependency injection
✅ **Clean Imports**: Centralized registry system
✅ **Easy Testing**: Interface-based design

## Performance Metrics

The system provides comprehensive performance analysis:

- Classification accuracy and F1 scores
- Uncertainty metrics (entropy, margin)
- Confidence calibration
- Error analysis and case mining
- Category-wise performance breakdown

## Examples

See the `examples/` directory for working code samples:
- `examples/classify_text.py`: Basic classification example
- `examples/using_registry.py`: Registry system demonstration

## Development

### Adding New Features

1. **Model Extensions**
   - Implement new models in `src/core/models.py`
   - Update configuration in `config/settings.yaml`

2. **Analysis Tools**
   - Add utilities in `src/utils/`
   - Follow interface patterns from `src/core/interfaces.py`

3. **Service Extensions**
   - Extend `ClassificationService` in `src/services/`
   - Use dependency injection via `ServiceFactory`

### Testing

```bash
# Run examples to verify system works
python examples/classify_text.py
python examples/using_registry.py

# Test main CLI
python classify_v2.py "test text" --verbose
```

## Architecture Documentation

For detailed architecture information and diagrams:
- `REFACTORED_ARCHITECTURE.md`: Complete architectural documentation with Mermaid diagrams
- `VIEW_DIAGRAMS.md`: Instructions for viewing architectural diagrams

## Production Deployment

The system is designed for production deployment with:

- Modular architecture for easy scaling
- Comprehensive logging and monitoring
- Configuration management
- Error handling and validation
