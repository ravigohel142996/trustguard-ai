"""
TrustGuard AI - FastAPI Backend
Purpose: Analyze text/links and return scam risk analysis
"""

# 🚀 WEEK 1C – MASTER COPILOT PROMPT (BEDROCK)
#
# Integrate Amazon Bedrock with FastAPI backend
#
# Requirements:
# - Use boto3 to connect to Amazon Bedrock Runtime
# - Use Claude/Titan model for text analysis
# - Create function: analyze_with_bedrock(text)
# - Send prompt to LLM asking:
#   "Analyze if this message is a scam. Give risk level, reason, category."
#
# - Parse response
# - Convert output to:
#   trust_score
#   risk_level
#   category
#   explanation
#
# - Replace mock logic in /analyze endpoint
# - Add fallback to mock if Bedrock fails
# - Add timeout + error handling
#
# Write clean, production-style code

import hashlib
import json
import logging
import os
import random
import re
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import AI Engine
try:
    from ai_engine import get_ai_engine
    AI_ENGINE_AVAILABLE = True
    logger.info("AI Engine imported successfully")
except ImportError as e:
    logger.warning(f"AI Engine not available: {e}")
    AI_ENGINE_AVAILABLE = False

# AWS Bedrock Configuration
AWS_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')
BEDROCK_TIMEOUT = int(os.getenv('BEDROCK_TIMEOUT', '30'))
BEDROCK_MAX_TOKENS = int(os.getenv('BEDROCK_MAX_TOKENS', '500'))
BEDROCK_TEMPERATURE = float(os.getenv('BEDROCK_TEMPERATURE', '0.3'))

# Trust score constants
TRUST_SCORE_DANGEROUS = 25
TRUST_SCORE_SAFE = 75
TRUST_SCORE_SUSPICIOUS = 50
MAX_EXPLANATION_LENGTH = 500

# Initialize Bedrock client with timeout configuration
try:
    bedrock_config = Config(
        region_name=AWS_REGION,
        connect_timeout=BEDROCK_TIMEOUT,
        read_timeout=BEDROCK_TIMEOUT,
        retries={'max_attempts': 2, 'mode': 'standard'}
    )
    bedrock_runtime = boto3.client('bedrock-runtime', config=bedrock_config)
    logger.info(f"AWS Bedrock client initialized for region: {AWS_REGION}")
except Exception as e:
    logger.warning(f"Failed to initialize AWS Bedrock client: {str(e)}")
    bedrock_runtime = None

# Initialize FastAPI app
app = FastAPI(
    title="TrustGuard AI API",
    description="API for analyzing text and links for scam detection",
    version="1.0.0"
)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Risk keywords for boosting detection
RISK_KEYWORDS = {
    "en": [
        "pay", "urgent", "click", "immediately", "limited time", "act now",
        "verify account", "suspended", "winner", "prize", "lottery",
        "bank account", "credit card", "password", "confirm identity",
        "cash", "money", "transfer", "fund", "investment", "guarantee",
        "free", "congratulations", "claim", "offer expires", "rupees"
    ],
    "hi": [
        "भुगतान", "तुरंत", "क्लिक", "जल्दी", "सीमित समय", "अभी करें",
        "खाता सत्यापित", "निलंबित", "विजेता", "पुरस्कार", "लॉटरी",
        "बैंक खाता", "क्रेडिट कार्ड", "पासवर्ड", "पहचान की पुष्टि",
        "नकद", "पैसा", "स्थानांतरण", "निधि", "निवेश", "गारंटी",
        "मुफ्त", "बधाई", "दावा", "ऑफर समाप्त", "रुपये"
    ]
}

# Scam categories
SCAM_CATEGORIES = {
    "en": [
        "Job Scam",
        "Phishing",
        "Fake Offer",
        "Investment Fraud",
        "Lottery Scam",
        "Tech Support Scam",
        "Romance Scam",
        "Other"
    ],
    "hi": [
        "नौकरी स्कैम",
        "फिशिंग",
        "नकली ऑफर",
        "निवेश धोखाधड़ी",
        "लॉटरी स्कैम",
        "तकनीकी सहायता स्कैम",
        "रोमांस स्कैम",
        "अन्य"
    ]
}

# Request and Response Models
class AnalyzeRequest(BaseModel):
    """Request model for analyze endpoint"""
    content: str = Field(..., min_length=1, description="Text content to analyze")
    language: str = Field("en", description="Language code (en/hi)")

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Pay 2000 rupees to get internship immediately",
                "language": "en"
            }
        }

class AnalyzeResponse(BaseModel):
    """Response model for analyze endpoint"""
    trust_score: int = Field(..., ge=0, le=100, description="Trust score from 0-100")
    risk_level: str = Field(..., description="Risk level: Safe/Suspicious/Dangerous")
    category: str = Field(..., description="Detected scam category")
    explanation: str = Field(..., description="Detailed explanation of the analysis")

    class Config:
        json_schema_extra = {
            "example": {
                "trust_score": 25,
                "risk_level": "Dangerous",
                "category": "Job Scam",
                "explanation": "HIGH RISK: Multiple suspicious keywords detected including 'pay', 'immediately', and 'rupees'. This appears to be a job scam attempting to extract money from victims."
            }
        }

class HealthResponse(BaseModel):
    """Response model for health endpoint"""
    status: str
    version: str
    bedrock_available: bool = Field(default=False, description="Whether AWS Bedrock is available")
    ai_engine_available: bool = Field(default=False, description="Whether AI Engine is available")

def analyze_with_bedrock(content: str, language: str) -> Optional[Dict]:
    """
    Analyze content using Amazon Bedrock AI
    
    Args:
        content: Text content to analyze
        language: Language code (en/hi)
    
    Returns:
        Dictionary with trust_score, risk_level, category, and explanation
        None if Bedrock is unavailable or fails
    """
    if bedrock_runtime is None:
        logger.warning("Bedrock client not initialized")
        return None
    
    try:
        # Construct AI prompt for scam analysis
        if language == "hi":
            prompt = f"""You are a cybersecurity assistant for India.

Analyze this content:

"{content}"

Return:
1. Risk Level (Safe/Suspicious/Dangerous)
2. Scam Category (नौकरी स्कैम, फिशिंग, नकली ऑफर, निवेश धोखाधड़ी, लॉटरी स्कैम, तकनीकी सहायता स्कैम, रोमांस स्कैम, अन्य)
3. Reason
4. Safety Advice

Provide your response in Hindi and be specific about the risk level."""
        else:
            prompt = f"""You are a cybersecurity assistant for India.

Analyze this content:

"{content}"

Return:
1. Risk Level (Safe/Suspicious/Dangerous)
2. Scam Category (Job Scam, Phishing, Fake Offer, Investment Fraud, Lottery Scam, Tech Support Scam, Romance Scam, Other)
3. Reason
4. Safety Advice

Be specific and concise in your analysis."""
        
        # Prepare request body for Claude model
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": BEDROCK_MAX_TOKENS,
            "temperature": BEDROCK_TEMPERATURE,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        logger.info(f"Calling Bedrock API with model: {BEDROCK_MODEL_ID}")
        
        # Invoke Bedrock model
        response = bedrock_runtime.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps(request_body)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        ai_response = response_body.get('content', [{}])[0].get('text', '')
        
        logger.info(f"Bedrock response received: {ai_response[:100]}...")
        
        # Parse AI response to extract structured data
        parsed_result = parse_bedrock_response(ai_response, language)
        
        return parsed_result
    
    except (BotoCoreError, ClientError) as e:
        logger.error(f"AWS Bedrock API error: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Bedrock response: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error calling Bedrock: {str(e)}", exc_info=True)
        return None

def parse_bedrock_response(response_text: str, language: str) -> Dict:
    """
    Parse Bedrock AI response and convert to structured format
    
    Args:
        response_text: Raw text response from Bedrock
        language: Language code (en/hi)
    
    Returns:
        Dictionary with trust_score, risk_level, category, and explanation
    """
    # Initialize default values
    risk_level = "Suspicious"
    category = "अन्य" if language == "hi" else "Other"
    trust_score = 50
    explanation = response_text
    
    # Extract risk level
    response_lower = response_text.lower()
    if any(word in response_lower for word in ["dangerous", "high risk", "खतरनाक", "उच्च जोखिम"]):
        risk_level = "Dangerous"
        trust_score = TRUST_SCORE_DANGEROUS
    elif any(word in response_lower for word in ["safe", "low risk", "सुरक्षित", "कम जोखिम"]):
        risk_level = "Safe"
        trust_score = TRUST_SCORE_SAFE
    else:
        risk_level = "Suspicious"
        trust_score = TRUST_SCORE_SUSPICIOUS
    
    # Extract category based on keywords in response
    if language == "hi":
        if "नौकरी" in response_text or "job" in response_lower:
            category = "नौकरी स्कैम"
        elif "फिशिंग" in response_text or "phishing" in response_lower:
            category = "फिशिंग"
        elif "ऑफर" in response_text or "offer" in response_lower:
            category = "नकली ऑफर"
        elif "निवेश" in response_text or "investment" in response_lower:
            category = "निवेश धोखाधड़ी"
        elif "लॉटरी" in response_text or "lottery" in response_lower:
            category = "लॉटरी स्कैम"
        elif "तकनीकी" in response_text or "tech" in response_lower:
            category = "तकनीकी सहायता स्कैम"
        elif "रोमांस" in response_text or "romance" in response_lower:
            category = "रोमांस स्कैम"
    else:
        if "job" in response_lower or "employment" in response_lower or "internship" in response_lower:
            category = "Job Scam"
        elif "phishing" in response_lower:
            category = "Phishing"
        elif "offer" in response_lower:
            category = "Fake Offer"
        elif "investment" in response_lower or "fraud" in response_lower:
            category = "Investment Fraud"
        elif "lottery" in response_lower:
            category = "Lottery Scam"
        elif "tech support" in response_lower:
            category = "Tech Support Scam"
        elif "romance" in response_lower:
            category = "Romance Scam"
    
    # Clean up explanation - use first MAX_EXPLANATION_LENGTH chars
    explanation = response_text.strip()[:MAX_EXPLANATION_LENGTH]
    
    return {
        "trust_score": trust_score,
        "risk_level": risk_level,
        "category": category,
        "explanation": explanation
    }

def analyze_content(content: str, language: str) -> Dict:
    """
    Analyze content for scam indicators
    Returns: Dictionary with trust_score, risk_level, category, and explanation
    """
    logger.info(f"Analyzing content in language: {language}")
    
    # Normalize content to lowercase for keyword matching
    content_lower = content.lower()
    
    # Generate deterministic base score using content hash
    # This ensures same content gets same base score while still appearing varied
    content_hash = int(hashlib.md5(content.encode()).hexdigest()[:8], 16)
    base_score = 40 + (content_hash % 51)  # Range: 40-90
    
    # Get appropriate keyword list
    keywords = RISK_KEYWORDS.get(language, RISK_KEYWORDS["en"])
    
    # Count matching risk keywords
    keyword_matches = []
    for keyword in keywords:
        if keyword.lower() in content_lower:
            keyword_matches.append(keyword)
    
    # Reduce trust score based on keyword matches
    keyword_penalty = min(len(keyword_matches) * 15, 60)
    trust_score = max(0, base_score - keyword_penalty)
    
    # Determine risk level
    if trust_score >= 70:
        risk_level = "Safe"
    elif trust_score >= 40:
        risk_level = "Suspicious"
    else:
        risk_level = "Dangerous"
    
    # Determine category based on keywords and content
    category = determine_category(content_lower, language, keyword_matches)
    
    # Generate explanation
    explanation = generate_explanation(
        trust_score, risk_level, keyword_matches, language
    )
    
    logger.info(f"Analysis complete. Trust score: {trust_score}, Risk: {risk_level}")
    
    return {
        "trust_score": trust_score,
        "risk_level": risk_level,
        "category": category,
        "explanation": explanation
    }

def determine_category(content: str, language: str, keywords: List[str]) -> str:
    """Determine the scam category based on content analysis"""
    categories = SCAM_CATEGORIES.get(language, SCAM_CATEGORIES["en"])
    
    # Simple keyword-based category detection
    if any(word in content for word in ["job", "internship", "hiring", "employment", "नौकरी"]):
        return categories[0]  # Job Scam
    elif any(word in content for word in ["verify", "account", "login", "password", "सत्यापित", "खाता"]):
        return categories[1]  # Phishing
    elif any(word in content for word in ["offer", "free", "discount", "deal", "ऑफर", "मुफ्त"]):
        return categories[2]  # Fake Offer
    elif any(word in content for word in ["invest", "profit", "return", "निवेश", "लाभ"]):
        return categories[3]  # Investment Fraud
    elif any(word in content for word in ["lottery", "winner", "prize", "लॉटरी", "विजेता"]):
        return categories[4]  # Lottery Scam
    elif any(word in content for word in ["tech", "support", "computer", "तकनीकी", "सहायता"]):
        return categories[5]  # Tech Support Scam
    elif any(word in content for word in ["love", "relationship", "dating", "प्यार", "रिश्ता"]):
        return categories[6]  # Romance Scam
    else:
        return categories[7]  # Other

def generate_explanation(
    trust_score: int, 
    risk_level: str, 
    keywords: List[str],
    language: str
) -> str:
    """Generate detailed explanation based on analysis"""
    
    if language == "hi":
        if risk_level == "Dangerous":
            explanation = f"उच्च जोखिम: {len(keywords)} संदिग्ध कीवर्ड पाए गए"
            if keywords:
                explanation += f" जिनमें शामिल हैं: {', '.join(keywords[:3])}"
            explanation += f"। विश्वास स्कोर: {trust_score}/100। यह संभावित रूप से एक घोटाला है। व्यक्तिगत जानकारी साझा न करें या पैसे न भेजें।"
        elif risk_level == "Suspicious":
            explanation = f"चेतावनी: {len(keywords)} संदिग्ध संकेत मिले"
            if keywords:
                explanation += f": {', '.join(keywords[:2])}"
            explanation += f"। विश्वास स्कोर: {trust_score}/100। आगे बढ़ने से पहले सावधानी बरतें और स्रोत की पुष्टि करें।"
        else:
            explanation = f"सामग्री अपेक्षाकृत सुरक्षित दिखती है। विश्वास स्कोर: {trust_score}/100। कोई बड़ा लाल झंडा नहीं मिला, लेकिन हमेशा सतर्क रहें।"
    else:
        if risk_level == "Dangerous":
            explanation = f"HIGH RISK: {len(keywords)} suspicious keywords detected"
            if keywords:
                explanation += f" including '{keywords[0]}'"
                if len(keywords) > 1:
                    explanation += f", '{keywords[1]}'"
                if len(keywords) > 2:
                    explanation += f", and '{keywords[2]}'"
            explanation += f". Trust score: {trust_score}/100. This appears to be a potential scam. Do not share personal information or send money."
        elif risk_level == "Suspicious":
            explanation = f"WARNING: {len(keywords)} suspicious indicators found"
            if keywords:
                explanation += f": '{keywords[0]}'"
                if len(keywords) > 1:
                    explanation += f" and '{keywords[1]}'"
            explanation += f". Trust score: {trust_score}/100. Exercise caution and verify the source before proceeding."
        else:
            explanation = f"Content appears relatively safe. Trust score: {trust_score}/100. No major red flags detected, but always remain vigilant."
    
    return explanation

# API Endpoints

@app.get("/", tags=["General"])
def read_root():
    """Root endpoint"""
    return {
        "message": "TrustGuard AI Backend API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze",
            "analyze-ai": "/analyze-ai",
            "docs": "/docs"
        }
    }

@app.get("/health", response_model=HealthResponse, tags=["General"])
def health_check():
    """
    Health check endpoint
    Returns the current status, version, Bedrock availability, and AI Engine availability of the API
    """
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "version": "1.0.0",
        "bedrock_available": bedrock_runtime is not None,
        "ai_engine_available": AI_ENGINE_AVAILABLE
    }

@app.post("/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
def analyze(request: AnalyzeRequest):
    """
    Analyze text content for scam detection
    
    Args:
        request: AnalyzeRequest containing content and language
    
    Returns:
        AnalyzeResponse with trust_score, risk_level, category, and explanation
    
    Raises:
        HTTPException: If content is invalid or analysis fails
    """
    try:
        # Validate language
        if request.language not in ["en", "hi"]:
            logger.warning(f"Invalid language requested: {request.language}")
            raise HTTPException(
                status_code=400,
                detail="Invalid language. Supported languages: en, hi"
            )
        
        # Validate content length
        if len(request.content.strip()) == 0:
            logger.warning("Empty content provided")
            raise HTTPException(
                status_code=400,
                detail="Content cannot be empty"
            )
        
        # Try Bedrock analysis first
        logger.info("Attempting analysis with AWS Bedrock")
        result = analyze_with_bedrock(request.content, request.language)
        
        # Fallback to mock analysis if Bedrock fails
        if result is None:
            logger.info("Bedrock unavailable, falling back to keyword-based analysis")
            result = analyze_content(request.content, request.language)
        else:
            logger.info("Successfully analyzed with AWS Bedrock")
        
        return AnalyzeResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while analyzing the content. Please try again."
        )

@app.post("/analyze-ai", response_model=AnalyzeResponse, tags=["Analysis"])
def analyze_with_ai_engine(request: AnalyzeRequest):
    """
    Analyze text content using full AI Engine (RAG + ML + Trust Calculator)
    
    This endpoint uses the complete AI Engine pipeline combining:
    - RAG (Retrieval-Augmented Generation) with FAISS for document search
    - ML Classifier for scam probability prediction
    - Trust Calculator for comprehensive scoring
    
    Args:
        request: AnalyzeRequest containing content and language
    
    Returns:
        AnalyzeResponse with trust_score, risk_level, category, and explanation
    
    Raises:
        HTTPException: If content is invalid or analysis fails
    """
    try:
        # Validate language
        if request.language not in ["en", "hi"]:
            logger.warning(f"Invalid language requested: {request.language}")
            raise HTTPException(
                status_code=400,
                detail="Invalid language. Supported languages: en, hi"
            )
        
        # Validate content length
        if len(request.content.strip()) == 0:
            logger.warning("Empty content provided")
            raise HTTPException(
                status_code=400,
                detail="Content cannot be empty"
            )
        
        # Use AI Engine if available
        if AI_ENGINE_AVAILABLE:
            logger.info("Analyzing with AI Engine")
            ai_engine = get_ai_engine()
            result = ai_engine.analyze(request.content, request.language)
        else:
            # Fallback to Bedrock, then keyword analysis
            logger.info("AI Engine not available, falling back to Bedrock")
            result = analyze_with_bedrock(request.content, request.language)
            if result is None:
                logger.info("Bedrock unavailable, falling back to keyword-based analysis")
                result = analyze_content(request.content, request.language)
        
        return AnalyzeResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during AI Engine analysis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while analyzing the content. Please try again."
        )

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return {
        "error": "Not Found",
        "message": "The requested endpoint does not exist",
        "path": str(request.url)
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {exc}")
    return {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred"
    }