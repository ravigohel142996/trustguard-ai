# AI Engine Usage Guide

## Overview

The TrustGuard AI Engine provides advanced scam detection using a combination of Machine Learning and optional Retrieval-Augmented Generation (RAG). This guide shows you how to use the AI Engine effectively.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Train the AI Engine (First Time Only)

```bash
cd backend/ai_engine
python train.py
```

This will:
- Train the ML classifier on sample scam/safe data (30 examples)
- Create a model file at `backend/data/scam_classifier.pkl`
- Optionally initialize RAG with trusted documents (if network available)

### 3. Start the Server

```bash
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

## API Usage

### Check Health and AI Engine Status

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "bedrock_available": true,
  "ai_engine_available": true
}
```

### Analyze Content with AI Engine

**Endpoint:** `POST /analyze-ai`

```bash
curl -X POST http://localhost:8000/analyze-ai \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Pay 5000 rupees now to claim your prize immediately",
    "language": "en"
  }'
```

**Response:**
```json
{
  "trust_score": 28,
  "risk_level": "Dangerous",
  "category": "Lottery Scam",
  "explanation": "HIGH RISK DETECTED! Trust score: 28/100. AI analysis identified this content as a potential scam. ML model confidence: 96.3%.",
  "details": {
    "ml_score": 1.8,
    "rag_score": 50,
    "keyword_score": 40,
    "content_score": 50,
    "ml_confidence": 0.96,
    "rag_matches": 0
  }
}
```

### Examples

#### Example 1: Scam Detection

```bash
curl -X POST http://localhost:8000/analyze-ai \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Pay 3000 for internship registration. Get job immediately",
    "language": "en"
  }'
```

**Result:** Trust Score: 35/100, Risk: Dangerous, Category: Job Scam

#### Example 2: Safe Content

```bash
curl -X POST http://localhost:8000/analyze-ai \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Your order has been confirmed and will be delivered tomorrow",
    "language": "en"
  }'
```

**Result:** Trust Score: 77/100, Risk: Safe, Category: Other

#### Example 3: Hindi Content

```bash
curl -X POST http://localhost:8000/analyze-ai \
  -H "Content-Type: application/json" \
  -d '{
    "content": "5000 रुपये का भुगतान करें और पुरस्कार प्राप्त करें",
    "language": "hi"
  }'
```

## Python Client Usage

```python
import requests

def analyze_text(content, language='en'):
    url = 'http://localhost:8000/analyze-ai'
    payload = {
        'content': content,
        'language': language
    }
    response = requests.post(url, json=payload)
    return response.json()

# Test with scam content
result = analyze_text("Pay 5000 rupees now to get job")
print(f"Trust Score: {result['trust_score']}")
print(f"Risk Level: {result['risk_level']}")
print(f"Category: {result['category']}")
print(f"Explanation: {result['explanation']}")
```

## Understanding the Results

### Trust Score (0-100)
- **70-100**: Safe - Content appears legitimate
- **40-69**: Suspicious - Exercise caution
- **0-39**: Dangerous - Likely scam or fraud

### Risk Levels
- **Safe**: Content shows no significant red flags
- **Suspicious**: Some warning signs detected
- **Dangerous**: Multiple scam indicators present

### Categories
- Job Scam
- Phishing
- Fake Offer
- Investment Fraud
- Lottery Scam
- Tech Support Scam
- Romance Scam
- Other

### Details Object
- `ml_score`: ML classifier contribution (0-100)
- `rag_score`: RAG relevance contribution (0-100)
- `keyword_score`: Keyword analysis contribution (0-100)
- `content_score`: Content features contribution (0-100)
- `ml_confidence`: ML model confidence (0-1)
- `rag_matches`: Number of relevant documents found

## Programmatic Usage

### Direct AI Engine Usage

```python
from ai_engine import get_ai_engine

# Get AI Engine instance
engine = get_ai_engine()

# Analyze content
result = engine.analyze(
    content="Pay money to claim prize",
    language='en'
)

print(result)
```

### Using Individual Components

```python
# ML Classifier only
from ai_engine import MLClassifier

classifier = MLClassifier()
prediction = classifier.predict("Suspicious text here")
print(f"Scam probability: {prediction['scam_probability']}")

# RAG Module only
from ai_engine import RAGModule

rag = RAGModule()
results = rag.search_relevant_info("job scam payment", k=3)
for result in results:
    print(f"Relevance: {result['relevance_score']}")
    print(f"Content: {result['content'][:100]}")

# Trust Calculator only
from ai_engine import TrustCalculator

calculator = TrustCalculator()
result = calculator.calculate_trust_score(
    content="Test content",
    ml_prediction={'scam_probability': 0.8, 'confidence': 0.9},
    rag_results=[...],
    language='en'
)
```

## Training with Custom Data

### Add More Training Examples

```python
from ai_engine import MLClassifier

classifier = MLClassifier()

# Prepare your data
scam_texts = [
    "Your scam example 1",
    "Your scam example 2",
    # ... more examples
]

safe_texts = [
    "Your safe example 1",
    "Your safe example 2",
    # ... more examples
]

texts = scam_texts + safe_texts
labels = [1] * len(scam_texts) + [0] * len(safe_texts)

# Train
metrics = classifier.train(texts, labels, save=True)
print(f"Test accuracy: {metrics['test_accuracy']}")
```

### Add Trusted Documents

Create text files in `backend/data/trusted_docs/` with your trusted content:

```
backend/data/trusted_docs/
  ├── scam_patterns.txt
  ├── safe_practices.txt
  └── your_custom_docs.txt
```

Then reload RAG:

```python
from ai_engine import RAGModule

rag = RAGModule()
count = rag.load_documents()  # Loads all .txt files
print(f"Loaded {count} documents")
```

## Performance Optimization

### Singleton Pattern
The AI Engine uses a singleton pattern, so components are initialized once:

```python
# First call - initializes everything
engine1 = get_ai_engine()  # Takes ~2-3 seconds

# Subsequent calls - instant
engine2 = get_ai_engine()  # Returns cached instance
```

### Async Usage
For high-traffic applications, consider async patterns:

```python
from fastapi import FastAPI
import asyncio

app = FastAPI()

@app.post("/analyze")
async def analyze_async(request: dict):
    # Run in thread pool to not block event loop
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None, 
        lambda: get_ai_engine().analyze(request['content'], request['language'])
    )
    return result
```

## Troubleshooting

### AI Engine Not Available

**Problem:** `ai_engine_available: false` in health check

**Solution:**
1. Check dependencies are installed: `pip install -r requirements.txt`
2. Train the model: `python backend/ai_engine/train.py`
3. Verify model file exists: `backend/data/scam_classifier.pkl`

### Low Accuracy

**Problem:** ML model giving poor predictions

**Solution:**
1. Add more training data (at least 100+ examples)
2. Balance your dataset (equal scam/safe examples)
3. Retrain the model

### RAG Not Working

**Problem:** RAG module showing as unavailable

**Solution:**
- RAG requires internet access to download sentence-transformers model
- This is optional - the system works fine without RAG using ML classifier
- If needed offline, pre-download the model and cache it

## Best Practices

### 1. Train with Domain-Specific Data
Add examples from your specific use case for better accuracy.

### 2. Regular Retraining
As new scam patterns emerge, retrain the model periodically.

### 3. Human Review for High-Stakes Decisions
Use AI as a tool, not sole decision maker. Review flagged content manually.

### 4. Monitor Performance
Track false positives and false negatives to improve the system.

### 5. Use Appropriate Thresholds
Adjust trust score thresholds based on your risk tolerance:
- High security: Flag anything < 70 as suspicious
- Balanced: Use default thresholds (70/40)
- Permissive: Only flag < 30 as dangerous

## Integration Examples

### With Database

```python
import sqlite3
from ai_engine import get_ai_engine

def analyze_and_store(content, user_id):
    engine = get_ai_engine()
    result = engine.analyze(content, 'en')
    
    conn = sqlite3.connect('scans.db')
    conn.execute('''
        INSERT INTO scans (user_id, content, trust_score, risk_level, category)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, content, result['trust_score'], result['risk_level'], result['category']))
    conn.commit()
    conn.close()
    
    return result
```

### With Queue System

```python
from celery import Celery
from ai_engine import get_ai_engine

app = Celery('tasks')

@app.task
def analyze_content_async(content, language='en'):
    engine = get_ai_engine()
    result = engine.analyze(content, language)
    return result

# Usage
task = analyze_content_async.delay("Check this text", "en")
result = task.get()  # Blocks until complete
```

### Batch Processing

```python
from ai_engine import get_ai_engine

def analyze_batch(contents, language='en'):
    engine = get_ai_engine()
    results = []
    
    for content in contents:
        result = engine.analyze(content, language)
        results.append(result)
    
    return results

# Process multiple texts
texts = ["Text 1", "Text 2", "Text 3"]
results = analyze_batch(texts)
```

## API Reference

See [AI_ENGINE_README.md](backend/ai_engine/README.md) for detailed API documentation.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review server logs for error details
3. Open an issue on GitHub with error details and sample input
