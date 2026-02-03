# TrustGuard AI Engine

A modular AI engine for advanced scam detection combining three powerful components:

1. **RAG (Retrieval-Augmented Generation)** - Using FAISS + LangChain
2. **ML Classifier** - Using scikit-learn
3. **Trust Score Calculator** - Combining all signals

## Architecture

```
┌─────────────────────────────────────────────────┐
│              TrustGuard AI Engine               │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────┐  ┌──────────────┐            │
│  │ RAG Module   │  │ ML Classifier│            │
│  │              │  │              │            │
│  │ FAISS + LC   │  │  sklearn     │            │
│  │ Vector Store │  │  TF-IDF      │            │
│  │ Doc Search   │  │  Naive Bayes │            │
│  └──────┬───────┘  └──────┬───────┘            │
│         │                 │                     │
│         └────────┬────────┘                     │
│                  │                              │
│          ┌───────▼────────┐                     │
│          │ Trust          │                     │
│          │ Calculator     │                     │
│          │                │                     │
│          │ Weighted Score │                     │
│          │ Risk Analysis  │                     │
│          └────────────────┘                     │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Components

### 1. RAG Module (`rag_module.py`)

**Purpose**: Search trusted documents for relevant information

**Features**:
- Load documents from files or in-memory
- Create vector embeddings using sentence-transformers
- FAISS vector store for fast similarity search
- Return relevant document chunks with relevance scores

**Key Methods**:
```python
rag = RAGModule()
rag.load_documents()  # Load trusted documents
results = rag.search_relevant_info("job scam payment", k=3)
```

### 2. ML Classifier (`ml_classifier.py`)

**Purpose**: Classify text as scam or safe using machine learning

**Features**:
- TF-IDF vectorization for text features
- Naive Bayes classifier for fast predictions
- Text preprocessing and cleaning
- Fallback to keyword-based analysis
- Model persistence (save/load)

**Key Methods**:
```python
classifier = MLClassifier()
classifier.train(texts, labels)  # Train on labeled data
prediction = classifier.predict("Pay money to get job")
# Returns: {'scam_probability': 0.85, 'confidence': 0.7}
```

### 3. Trust Calculator (`trust_calculator.py`)

**Purpose**: Combine multiple signals into comprehensive trust score

**Features**:
- Weighted combination of ML, RAG, keywords, and content features
- Risk level determination (Safe/Suspicious/Dangerous)
- Category detection (Job Scam, Phishing, etc.)
- Detailed explanation generation
- Support for English and Hindi

**Scoring Weights**:
- ML Prediction: 40%
- RAG Relevance: 30%
- Keyword Analysis: 20%
- Content Features: 10%

**Key Methods**:
```python
calculator = TrustCalculator()
result = calculator.calculate_trust_score(
    content="Pay 5000 to claim prize",
    ml_prediction={'scam_probability': 0.9, 'confidence': 0.8},
    rag_results=[...],
    language='en'
)
# Returns: trust_score, risk_level, category, explanation, details
```

### 4. AI Engine (`engine.py`)

**Purpose**: Unified interface for the complete pipeline

**Features**:
- Singleton pattern for resource efficiency
- Automatic component initialization
- Graceful fallback if components unavailable
- Status monitoring

**Usage**:
```python
from ai_engine import get_ai_engine

engine = get_ai_engine()
result = engine.analyze("Suspicious text here", language='en')
status = engine.get_status()
```

## Setup and Training

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `langchain` - For RAG functionality
- `faiss-cpu` - For vector storage
- `sentence-transformers` - For embeddings
- `scikit-learn` - For ML classification
- `numpy` - For numerical operations

### 2. Prepare Trusted Documents

Place trusted documents in `backend/data/trusted_docs/`:
- `scam_patterns.txt` - English scam patterns
- `scam_patterns_hindi.txt` - Hindi scam patterns
- `safe_practices.txt` - Safe business practices

### 3. Train the AI Engine

```bash
cd backend/ai_engine
python train.py
```

This will:
1. Load trusted documents into FAISS index
2. Train ML classifier on sample data
3. Save models for reuse

## API Integration

### New Endpoint: `/analyze-ai`

**Full AI Engine analysis** with RAG + ML + Trust Calculator

```bash
curl -X POST http://localhost:8000/analyze-ai \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Pay 5000 rupees now to get job",
    "language": "en"
  }'
```

**Response**:
```json
{
  "trust_score": 15,
  "risk_level": "Dangerous",
  "category": "Job Scam",
  "explanation": "HIGH RISK DETECTED! Trust score: 15/100. AI analysis identified this content as a potential scam. ML model confidence: 85%...",
  "details": {
    "ml_score": 12.5,
    "rag_score": 25.0,
    "keyword_score": 10.0,
    "content_score": 40.0,
    "ml_confidence": 0.85,
    "rag_matches": 3
  }
}
```

### Health Check Enhancement

The `/health` endpoint now includes AI Engine status:

```bash
curl http://localhost:8000/health
```

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "bedrock_available": false,
  "ai_engine_available": true
}
```

## Data Flow

```
User Input
    ↓
┌───────────────────────┐
│   FastAPI Endpoint    │
│   /analyze-ai         │
└───────────┬───────────┘
            ↓
┌───────────────────────┐
│   AI Engine           │
└───────────┬───────────┘
            ↓
    ┌───────┴───────┐
    ↓               ↓
┌───────┐     ┌──────────┐
│  RAG  │     │   ML     │
│Search │     │Classifier│
└───┬───┘     └────┬─────┘
    │              │
    └──────┬───────┘
           ↓
  ┌────────────────┐
  │ Trust Calc     │
  │ • Combine      │
  │ • Weight       │
  │ • Score        │
  └────────┬───────┘
           ↓
    Final Result
```

## Modular Design

Each component is independent and reusable:

✅ **Decoupled**: Components can work standalone
✅ **Testable**: Each module has clear interfaces
✅ **Extensible**: Easy to add new scoring methods
✅ **Fallback-ready**: Graceful degradation if dependencies missing

## Example Usage

### Standalone RAG
```python
from ai_engine import RAGModule

rag = RAGModule()
rag.load_documents(['Doc 1 content', 'Doc 2 content'])
results = rag.search_relevant_info("search query")
```

### Standalone ML Classifier
```python
from ai_engine import MLClassifier

classifier = MLClassifier()
classifier.train(texts, labels)
prediction = classifier.predict("test text")
```

### Full Pipeline
```python
from ai_engine import get_ai_engine

engine = get_ai_engine()
result = engine.analyze("Suspicious message", language='en')
print(f"Trust Score: {result['trust_score']}")
print(f"Risk: {result['risk_level']}")
```

## Performance Considerations

- **RAG**: First load is slow (embedding generation), subsequent searches are fast
- **ML Classifier**: Very fast predictions once trained
- **Singleton Pattern**: AI Engine components are initialized once and reused
- **Fallback Mode**: If dependencies unavailable, uses keyword-based analysis

## Extending the Engine

### Add New Data Sources
```python
# Add documents dynamically
rag = RAGModule()
rag.load_documents(['New trusted document'])
```

### Add Training Data
```python
# Retrain with new examples
classifier = MLClassifier()
classifier.train(new_texts, new_labels)
```

### Customize Weights
```python
# Adjust scoring weights
calculator = TrustCalculator()
calculator.weights = {
    'ml_prediction': 0.5,
    'rag_relevance': 0.3,
    'keyword_analysis': 0.1,
    'content_features': 0.1
}
```

## Troubleshooting

### AI Engine not available
- Check dependencies are installed: `pip install -r requirements.txt`
- Run training script: `python backend/ai_engine/train.py`

### RAG not working
- Ensure langchain, faiss-cpu, sentence-transformers are installed
- Check trusted documents exist in `backend/data/trusted_docs/`

### ML Classifier not trained
- Run training script to create model
- Check model file exists: `backend/data/scam_classifier.pkl`

## Future Enhancements

- [ ] Support for more languages
- [ ] Real-time model updates
- [ ] Advanced feature engineering
- [ ] Integration with external threat databases
- [ ] Confidence calibration
- [ ] Explainability improvements
