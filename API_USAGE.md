# TrustGuard AI - Backend API Usage Guide

## Overview
FastAPI backend for analyzing text and links to detect scams and fraudulent information.

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Server
```bash
# From the repository root
uvicorn backend.main:app --reload

# Or specify host and port
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## API Endpoints

### 1. Root Endpoint
**GET /**

Returns basic API information.

```bash
curl http://127.0.0.1:8000/
```

Response:
```json
{
  "message": "TrustGuard AI Backend API",
  "version": "1.0.0",
  "endpoints": {
    "health": "/health",
    "analyze": "/analyze",
    "docs": "/docs"
  }
}
```

### 2. Health Check
**GET /health**

Returns the API health status and version.

```bash
curl http://127.0.0.1:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 3. Analyze Content
**POST /analyze**

Analyzes text content for scam detection.

#### Request Body
```json
{
  "content": "string (required, min length: 1)",
  "language": "string (optional, default: 'en', values: 'en' or 'hi')"
}
```

#### Response
```json
{
  "trust_score": "integer (0-100)",
  "risk_level": "string (Safe/Suspicious/Dangerous)",
  "category": "string (scam category)",
  "explanation": "string (detailed explanation)"
}
```

#### Example 1: Dangerous Content (Job Scam)
```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"content": "Pay 2000 rupees to get internship immediately", "language": "en"}'
```

Response:
```json
{
  "trust_score": 10,
  "risk_level": "Dangerous",
  "category": "Job Scam",
  "explanation": "HIGH RISK: 3 suspicious keywords detected including 'pay', 'immediately', and 'rupees'. Trust score: 10/100. This appears to be a potential scam. Do not share personal information or send money."
}
```

#### Example 2: Safe Content
```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello friend, how are you today?", "language": "en"}'
```

Response:
```json
{
  "trust_score": 76,
  "risk_level": "Safe",
  "category": "Other",
  "explanation": "Content appears relatively safe. Trust score: 76/100. No major red flags detected, but always remain vigilant."
}
```

#### Example 3: Hindi Content
```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"content": "तुरंत 5000 रुपये भुगतान करें और बड़ा पुरस्कार जीतें", "language": "hi"}'
```

Response:
```json
{
  "trust_score": 19,
  "risk_level": "Dangerous",
  "category": "अन्य",
  "explanation": "उच्च जोखिम: 4 संदिग्ध कीवर्ड पाए गए जिनमें शामिल हैं: भुगतान, तुरंत, पुरस्कार। विश्वास स्कोर: 19/100। यह संभावित रूप से एक घोटाला है। व्यक्तिगत जानकारी साझा न करें या पैसे न भेजें।"
}
```

## Interactive API Documentation

### Swagger UI
Open your browser and navigate to:
```
http://127.0.0.1:8000/docs
```

This provides an interactive interface where you can:
- View all available endpoints
- See request/response schemas
- Test API calls directly from the browser
- View example requests and responses

### OpenAPI Schema
Get the raw OpenAPI (Swagger) schema:
```
http://127.0.0.1:8000/openapi.json
```

## Error Handling

### Empty Content
```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"content": "", "language": "en"}'
```

Response (422 Unprocessable Entity):
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "content"],
      "msg": "String should have at least 1 character",
      "input": "",
      "ctx": {"min_length": 1}
    }
  ]
}
```

### Invalid Language
```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"content": "test", "language": "invalid"}'
```

Response (400 Bad Request):
```json
{
  "detail": "Invalid language. Supported languages: en, hi"
}
```

## Scam Categories

The API can detect the following scam categories:

### English
- Job Scam
- Phishing
- Fake Offer
- Investment Fraud
- Lottery Scam
- Tech Support Scam
- Romance Scam
- Other

### Hindi
- नौकरी स्कैम (Job Scam)
- फिशिंग (Phishing)
- नकली ऑफर (Fake Offer)
- निवेश धोखाधड़ी (Investment Fraud)
- लॉटरी स्कैम (Lottery Scam)
- तकनीकी सहायता स्कैम (Tech Support Scam)
- रोमांस स्कैम (Romance Scam)
- अन्य (Other)

## Risk Keywords

The analysis engine looks for suspicious keywords in both languages:

### English Keywords
pay, urgent, click, immediately, limited time, act now, verify account, suspended, winner, prize, lottery, bank account, credit card, password, confirm identity, cash, money, transfer, fund, investment, guarantee, free, congratulations, claim, offer expires, rupees

### Hindi Keywords
भुगतान, तुरंत, क्लिक, जल्दी, सीमित समय, अभी करें, खाता सत्यापित, निलंबित, विजेता, पुरस्कार, लॉटरी, बैंक खाता, क्रेडिट कार्ड, पासवर्ड, पहचान की पुष्टि, नकद, पैसा, स्थानांतरण, निधि, निवेश, गारंटी, मुफ्त, बधाई, दावा, ऑफर समाप्त, रुपये

## Features

- ✅ **Deterministic Analysis**: Same content always produces the same result
- ✅ **Bilingual Support**: English and Hindi language support
- ✅ **CORS Enabled**: Can be accessed from frontend applications
- ✅ **Comprehensive Logging**: All requests and analyses are logged
- ✅ **Input Validation**: Pydantic models ensure data integrity
- ✅ **Error Handling**: Clear error messages for invalid inputs
- ✅ **OpenAPI Documentation**: Auto-generated interactive docs

## Development Notes

- The current implementation uses keyword-based detection for demonstration purposes
- Trust scores are calculated using content hash + keyword penalties for consistency
- The system is designed to be easily extended with ML models in the future
- CORS is currently configured to allow all origins (suitable for development)
