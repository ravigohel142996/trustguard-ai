# AWS Bedrock Integration Guide

This guide explains how to use the AWS Bedrock integration for AI-powered scam detection in TrustGuard AI.

## Overview

The TrustGuard AI backend now supports Amazon Bedrock for enhanced scam detection using Claude AI models. The system automatically falls back to keyword-based analysis if Bedrock is unavailable.

## Prerequisites

1. AWS Account with access to Amazon Bedrock
2. IAM User with `AmazonBedrockFullAccess` policy
3. AWS Access Key and Secret Key
4. boto3 Python package (included in requirements.txt)

## AWS Setup

### Step 1: Create IAM User

1. Go to AWS Console → IAM → Users → Create User
2. Enable **Programmatic access**
3. Attach policy: `AmazonBedrockFullAccess`
4. Download Access Key and Secret Key
5. **Important**: Save credentials securely

### Step 2: Configure AWS Credentials

#### On Local PC (Windows PowerShell)
```powershell
setx AWS_ACCESS_KEY_ID "YOUR_KEY"
setx AWS_SECRET_ACCESS_KEY "YOUR_SECRET"
setx AWS_DEFAULT_REGION "us-east-1"
```

After setting environment variables, restart your terminal or IDE (e.g., VS Code).

#### On Local PC (Linux/Mac)
```bash
export AWS_ACCESS_KEY_ID="YOUR_KEY"
export AWS_SECRET_ACCESS_KEY="YOUR_SECRET"
export AWS_DEFAULT_REGION="us-east-1"
```

To make these permanent, add them to your `~/.bashrc` or `~/.zshrc` file.

#### Using AWS CLI Configuration
```bash
aws configure
# Enter your Access Key, Secret Key, and Region when prompted
```

## Installation

### Install Dependencies
```bash
pip install -r requirements.txt
```

This will install boto3 along with other required packages.

## Configuration

The following environment variables can be configured:

| Variable | Default | Description |
|----------|---------|-------------|
| `AWS_ACCESS_KEY_ID` | - | AWS Access Key (required for Bedrock) |
| `AWS_SECRET_ACCESS_KEY` | - | AWS Secret Key (required for Bedrock) |
| `AWS_DEFAULT_REGION` | `us-east-1` | AWS Region for Bedrock |
| `BEDROCK_MODEL_ID` | `anthropic.claude-3-haiku-20240307-v1:0` | Bedrock model to use |
| `BEDROCK_TIMEOUT` | `30` | Timeout in seconds for Bedrock API calls |
| `BEDROCK_MAX_TOKENS` | `500` | Maximum tokens for AI response |
| `BEDROCK_TEMPERATURE` | `0.3` | Temperature for AI response (0.0-1.0) |

### Supported Models

- `anthropic.claude-3-haiku-20240307-v1:0` (Default - Fast and cost-effective)
- `anthropic.claude-3-sonnet-20240229-v1:0` (Balanced performance)
- `anthropic.claude-3-opus-20240229-v1:0` (Most capable)
- Amazon Titan models (requires different request format)

## Usage

### Start the Server
```bash
uvicorn backend.main:app --reload
# Or with custom host/port
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Check Health Status
```bash
curl http://127.0.0.1:8000/health
```

Response includes Bedrock availability:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "bedrock_available": true
}
```

### Test Bedrock Integration

#### Example 1: Job Scam Detection
```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"content": "You are selected for internship. Pay 3000 now.", "language": "en"}'
```

Expected Response (with Bedrock):
```json
{
  "trust_score": 25,
  "risk_level": "Dangerous",
  "category": "Job Scam",
  "explanation": "This message exhibits classic job scam characteristics. Legitimate companies never ask for payment upfront for internships or jobs. The urgent tone and request for immediate payment are red flags. This is likely a scam attempting to extract money from job seekers. Do not engage or send money."
}
```

#### Example 2: Safe Content
```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello friend, how are you today?", "language": "en"}'
```

Expected Response:
```json
{
  "trust_score": 75,
  "risk_level": "Safe",
  "category": "Other",
  "explanation": "This is a friendly greeting with no suspicious elements or scam indicators. The message appears to be genuine social communication."
}
```

#### Example 3: Hindi Content
```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"content": "तुरंत 5000 रुपये भुगतान करें", "language": "hi"}'
```

## How It Works

### Architecture

1. **Request Reception**: API receives text content for analysis
2. **Bedrock Analysis**: System attempts to analyze using AWS Bedrock
3. **Fallback Mechanism**: If Bedrock fails, falls back to keyword-based analysis
4. **Response Generation**: Returns structured analysis with trust score, risk level, category, and explanation

### AI Prompt Structure

The system sends structured prompts to Bedrock:

**English Prompt:**
```
You are a cybersecurity assistant for India.

Analyze this content:

"{user_input}"

Return:
1. Risk Level (Safe/Suspicious/Dangerous)
2. Scam Category (Job Scam, Phishing, Fake Offer, Investment Fraud, Lottery Scam, Tech Support Scam, Romance Scam, Other)
3. Reason
4. Safety Advice

Be specific and concise in your analysis.
```

**Hindi Prompt:**
```
You are a cybersecurity assistant for India.

Analyze this content:

"{user_input}"

Return:
1. Risk Level (Safe/Suspicious/Dangerous)
2. Scam Category (नौकरी स्कैम, फिशिंग, नकली ऑफर, निवेश धोखाधड़ी, लॉटरी स्कैम, तकनीकी सहायता स्कैम, रोमांस स्कैम, अन्य)
3. Reason
4. Safety Advice

Provide your response in Hindi and be specific about the risk level.
```

### Response Parsing

The system parses AI responses to extract:
- **Risk Level**: Safe, Suspicious, or Dangerous
- **Trust Score**: 25 (Dangerous), 50 (Suspicious), or 75 (Safe)
- **Category**: Detected scam type
- **Explanation**: AI-generated detailed analysis

## Fallback Mechanism

If Bedrock is unavailable (no credentials, API error, timeout), the system automatically falls back to keyword-based analysis:

1. Scans content for risk keywords
2. Calculates trust score based on keyword matches
3. Determines risk level and category
4. Generates explanation

This ensures the API continues to function even without Bedrock access.

## Troubleshooting

### Issue: "Bedrock client not initialized"

**Solution**: 
- Verify AWS credentials are set correctly
- Check if the AWS region supports Bedrock
- Ensure IAM user has `AmazonBedrockFullAccess` policy

### Issue: "AWS Bedrock API error"

**Solutions**:
- Verify AWS credentials are valid and not expired
- Check if you have Bedrock quota/permissions
- Verify the model ID is correct and available in your region
- Check AWS Bedrock service status

### Issue: Slow Response Times

**Solutions**:
- Increase `BEDROCK_TIMEOUT` if requests are timing out
- Use faster model like Claude 3 Haiku (default)
- Reduce `BEDROCK_MAX_TOKENS` for shorter responses

### Issue: Always Falling Back to Mock Analysis

**Check**:
1. AWS credentials are set correctly
2. Internet connectivity to AWS
3. Check logs for specific error messages
4. Verify `/health` endpoint shows `"bedrock_available": true`

## Monitoring

### Check Logs

The application logs all Bedrock interactions:
- Successful API calls: `"Successfully analyzed with AWS Bedrock"`
- Fallback usage: `"Bedrock unavailable, falling back to keyword-based analysis"`
- Errors: Detailed error messages with exception info

### Health Check

Monitor the `/health` endpoint to verify Bedrock availability:
```bash
curl http://127.0.0.1:8000/health
```

## Cost Considerations

AWS Bedrock charges based on:
- **Input tokens**: Text sent to the model
- **Output tokens**: Text generated by the model

**Claude 3 Haiku** (Default):
- Most cost-effective option
- Fast response times
- Suitable for production use

**Cost Optimization Tips**:
1. Use Claude 3 Haiku for production
2. Adjust `BEDROCK_MAX_TOKENS` to limit response length
3. Implement caching for repeated queries
4. Monitor usage via AWS CloudWatch

## Security Best Practices

1. **Never commit AWS credentials** to version control
2. Use environment variables or AWS IAM roles
3. Rotate access keys regularly
4. Use least-privilege IAM policies
5. Enable CloudTrail logging for audit
6. Monitor for unusual API usage patterns

## Production Deployment

### Recommended Configuration

```bash
# Use environment variables
export AWS_ACCESS_KEY_ID="YOUR_KEY"
export AWS_SECRET_ACCESS_KEY="YOUR_SECRET"
export AWS_DEFAULT_REGION="us-east-1"
export BEDROCK_MODEL_ID="anthropic.claude-3-haiku-20240307-v1:0"
export BEDROCK_TIMEOUT="30"
export BEDROCK_MAX_TOKENS="500"
export BEDROCK_TEMPERATURE="0.3"

# Start server
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY backend backend

ENV AWS_DEFAULT_REGION=us-east-1
ENV BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Pass AWS credentials at runtime:
```bash
docker run -e AWS_ACCESS_KEY_ID="..." -e AWS_SECRET_ACCESS_KEY="..." -p 8000:8000 trustguard-ai
```

## Testing

Run the included test script:
```bash
python /tmp/test_bedrock_integration.py
```

This tests:
- Job scam detection
- Safe content detection
- Phishing detection
- Hindi content analysis
- Investment fraud detection

## Support

For issues related to:
- **AWS Bedrock**: Check AWS Documentation and Support
- **Application**: Open an issue on the GitHub repository
- **API Usage**: Refer to API_USAGE.md

## References

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Claude API Documentation](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)
- [boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
