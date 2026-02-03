"""
Trust Calculator Module
Combines RAG outputs, ML predictions, and other signals to calculate comprehensive trust score
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class TrustCalculator:
    """
    Trust Score Calculator
    Combines multiple signals to produce a comprehensive trust assessment
    """
    
    def __init__(self):
        """Initialize Trust Calculator"""
        self.weights = {
            'ml_prediction': 0.4,      # ML classifier weight
            'rag_relevance': 0.3,      # RAG similarity weight
            'keyword_analysis': 0.2,   # Keyword-based analysis
            'content_features': 0.1    # Content features (length, URLs, etc.)
        }
    
    def calculate_trust_score(
        self,
        content: str,
        ml_prediction: Optional[Dict[str, float]] = None,
        rag_results: Optional[List[Dict]] = None,
        language: str = 'en'
    ) -> Dict:
        """
        Calculate comprehensive trust score
        
        Args:
            content: Text content to analyze
            ml_prediction: ML classifier prediction results
            rag_results: RAG search results
            language: Content language
        
        Returns:
            Dictionary with trust_score, risk_level, category, explanation, and details
        """
        try:
            # Initialize component scores
            scores = {
                'ml_score': 50,
                'rag_score': 50,
                'keyword_score': 50,
                'content_score': 50
            }
            
            # 1. ML Classifier Score
            if ml_prediction and 'scam_probability' in ml_prediction:
                scam_prob = ml_prediction['scam_probability']
                # Convert scam probability to trust score (inverse)
                scores['ml_score'] = (1 - scam_prob) * 100
            
            # 2. RAG Relevance Score
            if rag_results:
                scores['rag_score'] = self._calculate_rag_score(content, rag_results)
            
            # 3. Keyword Analysis Score
            scores['keyword_score'] = self._analyze_keywords(content, language)
            
            # 4. Content Features Score
            scores['content_score'] = self._analyze_content_features(content)
            
            # Calculate weighted trust score
            trust_score = (
                scores['ml_score'] * self.weights['ml_prediction'] +
                scores['rag_score'] * self.weights['rag_relevance'] +
                scores['keyword_score'] * self.weights['keyword_analysis'] +
                scores['content_score'] * self.weights['content_features']
            )
            
            # Ensure score is in valid range
            trust_score = max(0, min(100, int(trust_score)))
            
            # Determine risk level
            risk_level = self._determine_risk_level(trust_score)
            
            # Determine category
            category = self._determine_category(content, language)
            
            # Generate explanation
            explanation = self._generate_explanation(
                trust_score, risk_level, scores, ml_prediction, rag_results, language
            )
            
            return {
                'trust_score': trust_score,
                'risk_level': risk_level,
                'category': category,
                'explanation': explanation,
                'details': {
                    'ml_score': round(scores['ml_score'], 1),
                    'rag_score': round(scores['rag_score'], 1),
                    'keyword_score': round(scores['keyword_score'], 1),
                    'content_score': round(scores['content_score'], 1),
                    'ml_confidence': ml_prediction.get('confidence', 0) if ml_prediction else 0,
                    'rag_matches': len(rag_results) if rag_results else 0
                }
            }
        
        except Exception as e:
            logger.error(f"Error calculating trust score: {e}")
            # Return safe default
            return {
                'trust_score': 50,
                'risk_level': 'Suspicious',
                'category': 'Unknown',
                'explanation': 'Unable to complete full analysis. Please verify manually.',
                'details': {}
            }
    
    def _calculate_rag_score(self, content: str, rag_results: List[Dict]) -> float:
        """
        Calculate score based on RAG results
        Higher relevance to trusted documents = higher score
        """
        if not rag_results:
            return 50  # Neutral score if no results
        
        # Average relevance score from top results
        avg_relevance = sum(r.get('relevance_score', 0) for r in rag_results) / len(rag_results)
        
        # Convert to trust score (0-100)
        # High relevance to trusted docs = high trust
        score = avg_relevance * 100
        
        return max(0, min(100, score))
    
    def _analyze_keywords(self, content: str, language: str) -> float:
        """Analyze content for scam keywords"""
        scam_keywords = {
            'en': [
                'pay', 'urgent', 'click', 'immediately', 'limited time',
                'verify account', 'suspended', 'winner', 'prize', 'lottery',
                'bank account', 'credit card', 'password', 'confirm identity',
                'cash', 'money', 'transfer', 'investment', 'guarantee',
                'free', 'congratulations', 'claim', 'expires'
            ],
            'hi': [
                'भुगतान', 'तुरंत', 'क्लिक', 'सीमित समय',
                'खाता सत्यापित', 'निलंबित', 'विजेता', 'पुरस्कार',
                'बैंक खाता', 'क्रेडिट कार्ड', 'पासवर्ड',
                'नकद', 'पैसा', 'स्थानांतरण', 'निवेश',
                'मुफ्त', 'बधाई', 'दावा'
            ]
        }
        
        keywords = scam_keywords.get(language, scam_keywords['en'])
        content_lower = content.lower()
        
        # Count matches
        matches = sum(1 for keyword in keywords if keyword in content_lower)
        
        # Calculate score (more matches = lower score)
        if matches == 0:
            return 100
        elif matches <= 2:
            return 70
        elif matches <= 4:
            return 40
        else:
            return 10
    
    def _analyze_content_features(self, content: str) -> float:
        """Analyze content features like length, URLs, special characters"""
        score = 50  # Start neutral
        
        # Check for URLs (often in phishing)
        url_count = content.lower().count('http')
        url_count += content.lower().count('www.')
        if url_count > 0:
            score -= min(url_count * 10, 30)
        
        # Check for excessive punctuation (!!!!, ????)
        exclamation_count = content.count('!')
        question_count = content.count('?')
        if exclamation_count > 3 or question_count > 3:
            score -= 10
        
        # Check for excessive uppercase (URGENTTT)
        upper_ratio = sum(1 for c in content if c.isupper()) / max(len(content), 1)
        if upper_ratio > 0.3:
            score -= 15
        
        # Very short messages can be suspicious
        if len(content) < 20:
            score -= 10
        
        return max(0, min(100, score))
    
    def _determine_risk_level(self, trust_score: int) -> str:
        """Determine risk level from trust score"""
        if trust_score >= 70:
            return 'Safe'
        elif trust_score >= 40:
            return 'Suspicious'
        else:
            return 'Dangerous'
    
    def _determine_category(self, content: str, language: str) -> str:
        """Determine scam category"""
        categories = {
            'en': {
                'job': 'Job Scam',
                'phishing': 'Phishing',
                'offer': 'Fake Offer',
                'investment': 'Investment Fraud',
                'lottery': 'Lottery Scam',
                'tech': 'Tech Support Scam',
                'romance': 'Romance Scam',
                'other': 'Other'
            },
            'hi': {
                'job': 'नौकरी स्कैम',
                'phishing': 'फिशिंग',
                'offer': 'नकली ऑफर',
                'investment': 'निवेश धोखाधड़ी',
                'lottery': 'लॉटरी स्कैम',
                'tech': 'तकनीकी सहायता स्कैम',
                'romance': 'रोमांस स्कैम',
                'other': 'अन्य'
            }
        }
        
        cats = categories.get(language, categories['en'])
        content_lower = content.lower()
        
        # Check for category keywords
        if any(word in content_lower for word in ['job', 'internship', 'hiring', 'नौकरी']):
            return cats['job']
        elif any(word in content_lower for word in ['verify', 'account', 'login', 'सत्यापित']):
            return cats['phishing']
        elif any(word in content_lower for word in ['offer', 'free', 'discount', 'ऑफर', 'मुफ्त']):
            return cats['offer']
        elif any(word in content_lower for word in ['invest', 'profit', 'निवेश']):
            return cats['investment']
        elif any(word in content_lower for word in ['lottery', 'winner', 'prize', 'लॉटरी']):
            return cats['lottery']
        elif any(word in content_lower for word in ['tech', 'support', 'computer', 'तकनीकी']):
            return cats['tech']
        elif any(word in content_lower for word in ['love', 'dating', 'प्यार']):
            return cats['romance']
        else:
            return cats['other']
    
    def _generate_explanation(
        self,
        trust_score: int,
        risk_level: str,
        scores: Dict[str, float],
        ml_prediction: Optional[Dict],
        rag_results: Optional[List],
        language: str
    ) -> str:
        """Generate detailed explanation"""
        
        if language == 'hi':
            if risk_level == 'Dangerous':
                explanation = f"उच्च जोखिम का पता चला! विश्वास स्कोर: {trust_score}/100। "
                explanation += f"AI विश्लेषण ने इस सामग्री को संभावित घोटाला के रूप में पहचाना। "
            elif risk_level == 'Suspicious':
                explanation = f"चेतावनी! विश्वास स्कोर: {trust_score}/100। "
                explanation += f"सामग्री में संदिग्ध तत्व पाए गए। "
            else:
                explanation = f"सामग्री अपेक्षाकृत सुरक्षित प्रतीत होती है। विश्वास स्कोर: {trust_score}/100। "
            
            if ml_prediction:
                conf = ml_prediction.get('confidence', 0)
                explanation += f"ML मॉडल विश्वास: {conf:.1%}। "
            
            if rag_results:
                explanation += f"विश्वसनीय दस्तावेज़ों से {len(rag_results)} मिलान पाए गए। "
        else:
            if risk_level == 'Dangerous':
                explanation = f"HIGH RISK DETECTED! Trust score: {trust_score}/100. "
                explanation += f"AI analysis identified this content as a potential scam. "
            elif risk_level == 'Suspicious':
                explanation = f"WARNING! Trust score: {trust_score}/100. "
                explanation += f"Suspicious elements detected in content. "
            else:
                explanation = f"Content appears relatively safe. Trust score: {trust_score}/100. "
            
            if ml_prediction:
                conf = ml_prediction.get('confidence', 0)
                explanation += f"ML model confidence: {conf:.1%}. "
            
            if rag_results:
                explanation += f"Found {len(rag_results)} matches in trusted documents. "
        
        return explanation
