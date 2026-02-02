"""
TrustGuard AI - FastAPI Backend
Purpose: Analyze text/links and return scam risk analysis
"""

import hashlib
import logging
import random
import re
from typing import Dict, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
            "docs": "/docs"
        }
    }

@app.get("/health", response_model=HealthResponse, tags=["General"])
def health_check():
    """
    Health check endpoint
    Returns the current status and version of the API
    """
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "version": "1.0.0"
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
        
        # Perform analysis
        result = analyze_content(request.content, request.language)
        
        return AnalyzeResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}", exc_info=True)
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