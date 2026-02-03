"""
AI Engine Integration
Provides a unified interface to use RAG, ML Classifier, and Trust Calculator
"""

import logging
from typing import Dict, Optional
from .rag_module import RAGModule
from .ml_classifier import MLClassifier
from .trust_calculator import TrustCalculator

logger = logging.getLogger(__name__)


class AIEngine:
    """
    Unified AI Engine that combines RAG, ML Classification, and Trust Scoring
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to reuse initialized components"""
        if cls._instance is None:
            cls._instance = super(AIEngine, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize AI Engine components"""
        if self._initialized:
            return
        
        logger.info("Initializing AI Engine...")
        
        # Initialize components
        self.rag = RAGModule()
        self.classifier = MLClassifier()
        self.calculator = TrustCalculator()
        
        # Check availability
        self.rag_available = self.rag.is_available()
        self.classifier_available = self.classifier.is_available()
        
        logger.info(f"AI Engine initialized - RAG: {self.rag_available}, ML: {self.classifier_available}")
        
        self._initialized = True
    
    def analyze(self, content: str, language: str = 'en') -> Dict:
        """
        Analyze content using full AI Engine pipeline
        
        Args:
            content: Text content to analyze
            language: Language code (en/hi)
        
        Returns:
            Dictionary with trust_score, risk_level, category, explanation, and details
        """
        try:
            logger.info(f"Analyzing content with AI Engine (language: {language})")
            
            # Step 1: Get ML classifier prediction
            ml_prediction = None
            if self.classifier_available:
                ml_prediction = self.classifier.predict(content)
                logger.info(f"ML prediction: scam_prob={ml_prediction.get('scam_probability', 0):.2f}")
            else:
                logger.info("ML classifier not available, using fallback")
                ml_prediction = self.classifier.predict(content)  # Will use fallback
            
            # Step 2: Get RAG results
            rag_results = None
            if self.rag_available:
                rag_results = self.rag.search_relevant_info(content, k=3)
                logger.info(f"RAG search returned {len(rag_results)} results")
            else:
                logger.info("RAG not available, skipping document search")
            
            # Step 3: Calculate comprehensive trust score
            result = self.calculator.calculate_trust_score(
                content=content,
                ml_prediction=ml_prediction,
                rag_results=rag_results,
                language=language
            )
            
            logger.info(f"Final trust score: {result['trust_score']}, risk: {result['risk_level']}")
            
            return result
        
        except Exception as e:
            logger.error(f"Error in AI Engine analysis: {e}", exc_info=True)
            # Return safe fallback
            return {
                'trust_score': 50,
                'risk_level': 'Suspicious',
                'category': 'Unknown',
                'explanation': 'Analysis completed with limited information. Please verify manually.',
                'details': {}
            }
    
    def get_status(self) -> Dict:
        """Get status of AI Engine components"""
        return {
            'rag_available': self.rag_available,
            'ml_classifier_available': self.classifier_available,
            'fully_operational': self.rag_available and self.classifier_available
        }


# Global AI Engine instance
_ai_engine = None


def get_ai_engine() -> AIEngine:
    """Get or create global AI Engine instance"""
    global _ai_engine
    if _ai_engine is None:
        _ai_engine = AIEngine()
    return _ai_engine
