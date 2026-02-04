"""
TrustGuard AI - Trust Engine
Purpose: Combine LLM result, ML score, and RAG evidence into final trust score
"""

from typing import List, Dict, Tuple


# Base scores for LLM risk levels
LLM_BASE_SCORES = {
    "Safe": 80,
    "Suspicious": 50,
    "Dangerous": 20
}

# Penalty and bonus weights
ML_PENALTY_WEIGHT = 40
RAG_BONUS_WEIGHT = 20

# Red flag penalties
RED_FLAG_PENALTIES = {
    "payment_request": 15,
    "pay_now": 15,
    "urgent": 10,
    "short_link": 10,
    "suspicious_link": 10,
    "no_website": 8,
    "unofficial_domain": 8,
    "verify_account": 10,
    "limited_time": 10,
    "act_now": 10,
    "claim_prize": 12,
    "winner": 12,
    "lottery": 12,
    "password_request": 15,
    "credit_card": 15,
    "bank_account": 15
}

# Default red flag penalty for unknown flags
DEFAULT_FLAG_PENALTY = 5


def calculate_trust(
    llm_risk: str,
    ml_score: float,
    rag_confidence: float,
    red_flags: List[str]
) -> Dict:
    """
    Calculate trust score by combining LLM result, ML score, and RAG evidence
    
    Args:
        llm_risk: Risk level from LLM ("Safe", "Suspicious", "Dangerous")
        ml_score: ML scam probability (0-1, where 1 = high scam probability)
        rag_confidence: RAG evidence strength (0-1, where 1 = high confidence)
        red_flags: List of detected warning signs/red flags
    
    Returns:
        Dictionary containing:
            - trust_score: Final score (0-100)
            - risk_level: Risk level classification
            - explanation: Human-readable explanation
            - breakdown: Detailed score breakdown
    """
    # 1. Get base score from LLM risk level
    base_score = LLM_BASE_SCORES.get(llm_risk, 50)
    
    # 2. Calculate ML penalty (higher ml_score = more dangerous)
    ml_penalty = ml_score * ML_PENALTY_WEIGHT
    
    # 3. Calculate RAG bonus (higher confidence = better)
    rag_bonus = rag_confidence * RAG_BONUS_WEIGHT
    
    # 4. Calculate red flag penalties
    flag_penalty = 0
    flag_details = []
    for flag in red_flags:
        penalty = RED_FLAG_PENALTIES.get(flag, DEFAULT_FLAG_PENALTY)
        flag_penalty += penalty
        flag_details.append(f"{flag} (-{penalty})")
    
    # 5. Calculate final score
    final_score = base_score - ml_penalty + rag_bonus - flag_penalty
    
    # Clamp score to 0-100 range
    final_score = max(0, min(100, int(final_score)))
    
    # 6. Determine risk level based on final score
    if final_score <= 30:
        risk_level = "Dangerous"
    elif final_score <= 70:
        risk_level = "Suspicious"
    else:
        risk_level = "Safe"
    
    # 7. Generate explanation
    explanation = _generate_explanation(
        final_score,
        risk_level,
        llm_risk,
        ml_score,
        rag_confidence,
        red_flags,
        base_score,
        ml_penalty,
        rag_bonus,
        flag_penalty
    )
    
    # Create detailed breakdown for debugging/transparency
    breakdown = {
        "base_score": base_score,
        "ml_penalty": round(ml_penalty, 2),
        "rag_bonus": round(rag_bonus, 2),
        "flag_penalty": flag_penalty,
        "flag_details": flag_details,
        "components": {
            "llm_risk": llm_risk,
            "ml_score": round(ml_score, 4),
            "rag_confidence": round(rag_confidence, 4),
            "red_flags_count": len(red_flags)
        }
    }
    
    return {
        "trust_score": final_score,
        "risk_level": risk_level,
        "explanation": explanation,
        "breakdown": breakdown
    }


def _generate_explanation(
    final_score: int,
    risk_level: str,
    llm_risk: str,
    ml_score: float,
    rag_confidence: float,
    red_flags: List[str],
    base_score: int,
    ml_penalty: float,
    rag_bonus: float,
    flag_penalty: float
) -> str:
    """
    Generate human-readable explanation of the trust score
    
    Args:
        final_score: Final calculated trust score
        risk_level: Final risk level classification
        llm_risk: LLM's risk assessment
        ml_score: ML scam probability
        rag_confidence: RAG confidence score
        red_flags: List of detected red flags
        base_score: Base score from LLM
        ml_penalty: Penalty from ML score
        rag_bonus: Bonus from RAG
        flag_penalty: Penalty from red flags
    
    Returns:
        Human-readable explanation string
    """
    explanation_parts = []
    
    # Start with risk level assessment
    if risk_level == "Dangerous":
        explanation_parts.append(f"⚠️ HIGH RISK (Score: {final_score}/100)")
    elif risk_level == "Suspicious":
        explanation_parts.append(f"⚡ CAUTION ADVISED (Score: {final_score}/100)")
    else:
        explanation_parts.append(f"✓ RELATIVELY SAFE (Score: {final_score}/100)")
    
    # Explain LLM assessment
    explanation_parts.append(f"AI Analysis: {llm_risk} (base: {base_score})")
    
    # Explain ML model contribution
    if ml_score > 0.7:
        explanation_parts.append(f"ML model detected high scam probability ({ml_score:.2f}) - penalty: -{ml_penalty:.0f}")
    elif ml_score > 0.4:
        explanation_parts.append(f"ML model shows moderate scam indicators ({ml_score:.2f}) - penalty: -{ml_penalty:.0f}")
    else:
        explanation_parts.append(f"ML model shows low scam risk ({ml_score:.2f})")
    
    # Explain RAG contribution
    if rag_confidence > 0.7:
        explanation_parts.append(f"Strong evidence from trusted sources (confidence: {rag_confidence:.2f}) - bonus: +{rag_bonus:.0f}")
    elif rag_confidence > 0.3:
        explanation_parts.append(f"Moderate evidence from trusted sources (confidence: {rag_confidence:.2f})")
    
    # Explain red flags
    if red_flags:
        flag_names = [flag.replace("_", " ").title() for flag in red_flags[:3]]
        if len(red_flags) > 3:
            explanation_parts.append(
                f"{len(red_flags)} red flags detected including: {', '.join(flag_names)} and {len(red_flags) - 3} more - total penalty: -{flag_penalty}"
            )
        else:
            explanation_parts.append(
                f"{len(red_flags)} red flag(s) detected: {', '.join(flag_names)} - penalty: -{flag_penalty}"
            )
    
    # Add actionable advice based on risk level
    if risk_level == "Dangerous":
        explanation_parts.append("⛔ DO NOT proceed. Do not share personal information or send money.")
    elif risk_level == "Suspicious":
        explanation_parts.append("⚠️ Verify the source carefully before taking any action.")
    else:
        explanation_parts.append("✓ No major threats detected, but always remain vigilant.")
    
    return " | ".join(explanation_parts)


def detect_red_flags(content: str) -> List[str]:
    """
    Detect red flags in content for trust score calculation
    
    Args:
        content: Text content to analyze
    
    Returns:
        List of detected red flag identifiers
    """
    content_lower = content.lower()
    detected_flags = []
    
    # Payment-related red flags
    if any(word in content_lower for word in ["pay now", "payment required", "send money", "transfer funds"]):
        detected_flags.append("payment_request")
    
    # Urgency red flags
    if any(word in content_lower for word in ["urgent", "immediately", "right now", "hurry", "limited time", "act now"]):
        detected_flags.append("urgent")
    
    # Link-related red flags
    if any(word in content_lower for word in ["bit.ly", "tinyurl", "goo.gl", "short.link"]):
        detected_flags.append("short_link")
    
    # Account verification red flags
    if any(word in content_lower for word in ["verify account", "verify your", "confirm identity", "suspended account"]):
        detected_flags.append("verify_account")
    
    # Prize/lottery red flags
    if any(word in content_lower for word in ["claim prize", "you won", "you're a winner", "lottery", "jackpot"]):
        detected_flags.append("winner")
    
    # Sensitive information requests
    if any(word in content_lower for word in ["password", "pin", "cvv", "security code"]):
        detected_flags.append("password_request")
    
    if any(word in content_lower for word in ["credit card", "debit card", "card number"]):
        detected_flags.append("credit_card")
    
    if any(word in content_lower for word in ["bank account", "account number", "routing number"]):
        detected_flags.append("bank_account")
    
    # Unofficial domain indicators
    if any(word in content_lower for word in ["unofficial", "temporary link", "alternate site"]):
        detected_flags.append("unofficial_domain")
    
    return detected_flags


if __name__ == "__main__":
    """Test the trust engine with sample data"""
    
    print("=" * 60)
    print("TRUSTGUARD AI - TRUST ENGINE TEST")
    print("=" * 60)
    
    # Test Case 1: Dangerous content
    print("\n[TEST 1] Dangerous Content:")
    print("Content: 'Pay 2000 rupees immediately to claim your lottery prize!'")
    result1 = calculate_trust(
        llm_risk="Dangerous",
        ml_score=0.9,
        rag_confidence=0.2,
        red_flags=["payment_request", "urgent", "winner"]
    )
    print(f"Trust Score: {result1['trust_score']}")
    print(f"Risk Level: {result1['risk_level']}")
    print(f"Explanation: {result1['explanation']}")
    print(f"Breakdown: {result1['breakdown']}")
    
    # Test Case 2: Safe content
    print("\n" + "=" * 60)
    print("[TEST 2] Safe Content:")
    print("Content: 'Meeting scheduled for tomorrow at 10 AM'")
    result2 = calculate_trust(
        llm_risk="Safe",
        ml_score=0.1,
        rag_confidence=0.8,
        red_flags=[]
    )
    print(f"Trust Score: {result2['trust_score']}")
    print(f"Risk Level: {result2['risk_level']}")
    print(f"Explanation: {result2['explanation']}")
    print(f"Breakdown: {result2['breakdown']}")
    
    # Test Case 3: Suspicious content
    print("\n" + "=" * 60)
    print("[TEST 3] Suspicious Content:")
    print("Content: 'Verify your account to prevent suspension'")
    result3 = calculate_trust(
        llm_risk="Suspicious",
        ml_score=0.6,
        rag_confidence=0.4,
        red_flags=["verify_account", "urgent"]
    )
    print(f"Trust Score: {result3['trust_score']}")
    print(f"Risk Level: {result3['risk_level']}")
    print(f"Explanation: {result3['explanation']}")
    print(f"Breakdown: {result3['breakdown']}")
    
    # Test Case 4: Test red flag detection
    print("\n" + "=" * 60)
    print("[TEST 4] Red Flag Detection:")
    test_content = "Pay now! Verify your bank account immediately to claim your prize. Limited time offer!"
    flags = detect_red_flags(test_content)
    print(f"Content: '{test_content}'")
    print(f"Detected Red Flags: {flags}")
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
