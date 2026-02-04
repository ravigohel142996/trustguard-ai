# trustguard-ai
AI TrustScore – Fake News, Scam & Info Verification for Bharat  
"An AI system that verifies messages, ads, news, and offers before people trust them."

## Features

- 🤖 **AI-Powered Analysis**: Uses AWS Bedrock with Claude AI for intelligent scam detection
- 📚 **RAG Integration**: Enhanced with Retrieval Augmented Generation for context-aware analysis
- 🔄 **Smart Fallback**: Automatically falls back to keyword-based analysis if AI is unavailable
- 🌐 **Bilingual Support**: Supports both English and Hindi languages
- ⚡ **Fast API**: Built with FastAPI for high performance
- 📊 **Comprehensive Analysis**: Provides trust score, risk level, category, and detailed explanation

## Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Run the Server
```bash
uvicorn backend.main:app --reload
```

### Test the API
```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"content": "You are selected for internship. Pay 3000 now.", "language": "en"}'
```

## Documentation

- [API Usage Guide](API_USAGE.md) - How to use the API
- [AWS Bedrock Integration](BEDROCK_INTEGRATION.md) - Setup and configure AWS Bedrock for AI-powered analysis
- [RAG Integration Guide](RAG_INTEGRATION.md) - Retrieval Augmented Generation system documentation
- [Quick Start Guide](QUICKSTART.md) - Get started quickly

## AWS Bedrock Integration

TrustGuard AI now supports AWS Bedrock for enhanced AI-powered scam detection. See [BEDROCK_INTEGRATION.md](BEDROCK_INTEGRATION.md) for:
- Setup instructions
- Configuration options
- Usage examples
- Troubleshooting guide

Without AWS credentials, the system automatically uses keyword-based analysis.
