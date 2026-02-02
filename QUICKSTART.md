# TrustGuard AI - Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Start the Backend Server
```bash
uvicorn backend.main:app --reload
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
INFO:     Application startup complete.
```

### Step 3: Test the API

#### Open Swagger UI (Recommended)
Open your browser and navigate to:
```
http://127.0.0.1:8000/docs
```

You'll see an interactive API documentation where you can test all endpoints!

#### Or Test via Command Line

**Test the analyze endpoint:**
```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"content": "Pay 2000 rupees to get internship immediately", "language": "en"}'
```

**Expected Response:**
```json
{
  "trust_score": 10,
  "risk_level": "Dangerous",
  "category": "Job Scam",
  "explanation": "HIGH RISK: 3 suspicious keywords detected including 'pay', 'immediately', and 'rupees'. Trust score: 10/100. This appears to be a potential scam. Do not share personal information or send money."
}
```

## ✅ Verification Checklist

- [ ] Dependencies installed successfully
- [ ] Server starts without errors
- [ ] Can access http://127.0.0.1:8000/docs in browser
- [ ] /analyze endpoint returns scam analysis
- [ ] /health endpoint returns {"status": "healthy"}

## 📚 What's Included

### API Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `POST /analyze` - Scam detection analysis

### Features
- ✅ English and Hindi language support
- ✅ Keyword-based scam detection
- ✅ Category classification (Job Scam, Phishing, etc.)
- ✅ Trust score (0-100)
- ✅ Risk level (Safe/Suspicious/Dangerous)
- ✅ CORS enabled for frontend integration
- ✅ Comprehensive error handling
- ✅ Structured logging

## 📖 More Information

- Full API documentation: See `API_USAGE.md`
- Code implementation: See `backend/main.py`
- Dependencies: See `requirements.txt`

## 🎯 Example Test Cases

### Dangerous Content (Job Scam)
```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"content": "Pay 2000 rupees to get internship immediately", "language": "en"}'
```
→ Trust Score: 10/100, Risk: Dangerous

### Suspicious Content (Phishing)
```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"content": "Verify your account or it will be suspended", "language": "en"}'
```
→ Trust Score: ~30/100, Risk: Dangerous or Suspicious

### Safe Content
```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello, how are you today?", "language": "en"}'
```
→ Trust Score: 76/100, Risk: Safe

### Hindi Content
```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"content": "तुरंत 5000 रुपये भुगतान करें", "language": "hi"}'
```
→ Analysis in Hindi

## 🐛 Troubleshooting

### Port Already in Use
If port 8000 is already in use, specify a different port:
```bash
uvicorn backend.main:app --reload --port 8001
```

### Module Not Found
Make sure you're in the repository root directory and dependencies are installed:
```bash
cd /path/to/trustguard-ai
pip install -r requirements.txt
```

## 🎉 Success!

If you can see the Swagger UI and the analyze endpoint works, you've successfully set up the TrustGuard AI backend!

**Next Steps:**
- Integrate with the frontend (Streamlit app in `frontend/app.py`)
- Add more sophisticated ML models for analysis
- Deploy to production
