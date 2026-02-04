# RAG (Retrieval Augmented Generation) Integration Guide

## Overview

TrustGuard AI now includes a RAG (Retrieval Augmented Generation) system that enhances scam detection by providing relevant context from trusted documents. The system uses TF-IDF embeddings with cosine similarity for fast and efficient document retrieval.

## Architecture

```
ai_engine/
├── __init__.py
├── rag.py                    # RAG system implementation
├── data/
│   └── trusted_docs/         # Directory for trusted documents
│       ├── scam_warning_signs.txt
│       ├── digital_safety_practices.txt
│       └── scam_categories_guide.txt
└── cache/
    └── rag_cache.pkl         # Cached index (auto-generated)
```

## Features

- **Document Loading**: Automatically loads all `.txt` files from `ai_engine/data/trusted_docs/`
- **Intelligent Chunking**: Splits documents into 500-character chunks with 50-character overlap
- **TF-IDF Embeddings**: Uses scikit-learn's TfidfVectorizer for efficient text representation
- **Similarity Search**: Returns top-k most relevant passages using cosine similarity
- **Disk Caching**: Caches the index to disk for faster subsequent loads
- **Modular Design**: Easy to use and integrate with existing code

## Usage

### Basic Usage

```python
from ai_engine.rag import search_docs

# Search for relevant passages
results = search_docs("job scam warning signs", top_k=3)

for result in results:
    print(f"Source: {result['source']}")
    print(f"Score: {result['score']}")
    print(f"Content: {result['content']}")
    print()
```

### Advanced Usage

```python
from ai_engine.rag import RAGSystem

# Create a custom RAG instance
rag = RAGSystem(
    docs_dir="/path/to/trusted_docs",
    cache_dir="/path/to/cache"
)

# Initialize the system
rag.initialize(force_rebuild=False)

# Search documents
results = rag.search_docs("phishing detection", top_k=5)
```

## Backend Integration

The RAG system is automatically integrated with the TrustGuard AI backend. When analyzing content:

1. The backend searches the RAG system for relevant passages
2. Top 2 most relevant excerpts are included as context
3. Context is sent to Amazon Bedrock along with the user's content
4. Bedrock generates a more informed analysis using this context

### Example API Request

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Pay 5000 rupees for Google internship",
    "language": "en"
  }'
```

The backend will:
1. Search RAG for context about job scams
2. Include relevant passages in the Bedrock prompt
3. Return enhanced analysis with trust score and explanation

## Adding New Documents

To add new trusted documents:

1. Create a `.txt` file in `ai_engine/data/trusted_docs/`
2. Add your content (clear, factual information about scams, safety tips, etc.)
3. Restart the backend or force rebuild the index:

```python
from ai_engine.rag import get_rag_system

rag = get_rag_system()
rag.initialize(force_rebuild=True)
```

### Document Content Guidelines

- **Be Specific**: Include concrete examples and red flags
- **Use Clear Language**: Write in simple, understandable terms
- **Organize by Topic**: Group related information together
- **Include Sources**: Reference authoritative sources when possible
- **Update Regularly**: Keep information current and relevant

## Configuration

Key configuration options in `ai_engine/rag.py`:

```python
CHUNK_SIZE = 500           # Size of document chunks
CHUNK_OVERLAP = 50         # Overlap between chunks
TOP_K_RESULTS = 3          # Default number of results to return
```

## Cache Management

The RAG system caches the index to disk for faster loading:

- **Cache Location**: `ai_engine/cache/rag_cache.pkl`
- **Cache Rebuild**: Automatically rebuilds if documents change
- **Force Rebuild**: Set `force_rebuild=True` in `initialize()`

To clear the cache:

```bash
rm -rf ai_engine/cache/
```

## Performance

- **Initial Build**: ~1-2 seconds for small document collections
- **Cache Load**: ~100-200ms from disk
- **Search Time**: ~10-50ms per query
- **Memory Usage**: Minimal (~1-5MB for typical document sets)

## Health Check

Check if RAG is available:

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "bedrock_available": true,
  "rag_available": true
}
```

## Troubleshooting

### RAG system not initializing

**Problem**: Backend logs show "Failed to initialize RAG system"

**Solution**:
1. Check that `ai_engine/data/trusted_docs/` exists
2. Ensure there are `.txt` files in the directory
3. Verify file permissions

### No results from searches

**Problem**: `search_docs()` returns empty list

**Solution**:
1. Check that documents contain relevant keywords
2. Try different search queries
3. Rebuild the index with `force_rebuild=True`

### Cache errors

**Problem**: Errors loading from cache

**Solution**:
1. Delete the cache directory: `rm -rf ai_engine/cache/`
2. Restart the backend to rebuild the cache

## Dependencies

Required packages:
- `langchain` - Document loading and text splitting
- `langchain-community` - Community document loaders
- `langchain-text-splitters` - Text splitting utilities
- `scikit-learn` - TF-IDF vectorization and similarity
- `numpy` - Numerical operations

Install all dependencies:
```bash
pip install -r requirements.txt
```

## Future Enhancements

Potential improvements:
- Support for PDF, DOCX, and other document formats
- Multiple language support for RAG documents
- Semantic embeddings using Amazon Bedrock embeddings
- Real-time document indexing
- Query expansion and synonym matching
- Feedback-based relevance tuning

## Contributing

To contribute to the RAG system:

1. Add new trusted documents to `ai_engine/data/trusted_docs/`
2. Improve the chunking strategy in `_split_documents()`
3. Enhance the search algorithm in `search_docs()`
4. Add support for new document formats

## License

This RAG implementation is part of TrustGuard AI and follows the same license.
