"""
Training script for AI Engine components
Initializes RAG index and trains ML classifier with sample data
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_engine.rag_module import RAGModule
from ai_engine.ml_classifier import MLClassifier
from ai_engine.trust_calculator import TrustCalculator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_training_data():
    """Create sample training data for ML classifier"""
    
    # Scam examples (label = 1)
    scam_texts = [
        "Pay 2000 rupees now to get selected for internship. Limited time offer!",
        "Urgent! Your bank account has been suspended. Click here to verify immediately.",
        "Congratulations! You won 50 lakh rupees in lottery. Pay processing fee to claim.",
        "Invest 10000 and get 50000 return guaranteed in 30 days. Join now!",
        "Your Netflix account will be closed. Update payment information immediately.",
        "You are pre-approved for 5 lakh loan. Click link to claim now.",
        "Send money to this account urgently. Government tax notice.",
        "Hot job opportunity! Pay registration fee 3000 rupees to start work from home.",
        "Your phone number won prize of 20 lakh. Send bank details to claim.",
        "Bitcoin investment opportunity - 500% returns guaranteed. Join telegram group.",
        "Account verification required immediately. Confirm your password now.",
        "Free iPhone winner! Pay shipping charges 2000 rupees only.",
        "Your Aadhaar card will be blocked. Click to update details.",
        "Work from home and earn 50000 per month. Pay training fee 5000.",
        "Claim your refund of 15000 rupees. Enter credit card details.",
    ]
    
    # Safe examples (label = 0)
    safe_texts = [
        "Your order has been confirmed. Track your shipment using order ID.",
        "Meeting scheduled for tomorrow at 10 AM. Please confirm your availability.",
        "Thank you for your purchase. Your invoice is attached.",
        "Welcome to our service. You can reset password anytime from settings.",
        "Your monthly statement is ready to view in the app.",
        "Reminder: Your subscription renews on the 15th of this month.",
        "New features added to the app. Check them out in the updates section.",
        "Your appointment is confirmed for next Monday at 2 PM.",
        "Class schedule has been updated. Please check the timetable.",
        "Project deadline extended by one week. New date: March 15th.",
        "Your ticket booking is successful. E-ticket sent to your email.",
        "Product delivery scheduled for tomorrow between 10 AM to 5 PM.",
        "Weather alert: Heavy rain expected. Plan your travel accordingly.",
        "Meeting notes from today's discussion are now available.",
        "Your feedback has been received. Thank you for your input.",
    ]
    
    # Combine data
    texts = scam_texts + safe_texts
    labels = [1] * len(scam_texts) + [0] * len(safe_texts)
    
    return texts, labels


def train_ai_engine():
    """Train all AI engine components"""
    
    logger.info("Starting AI Engine training...")
    
    # 1. Initialize and load RAG Module
    logger.info("\n=== Training RAG Module ===")
    rag = RAGModule()
    
    if rag.is_available():
        docs_loaded = rag.load_documents()
        logger.info(f"Loaded {docs_loaded} documents into RAG")
        
        # Test search
        test_query = "job scam payment"
        results = rag.search_relevant_info(test_query, k=2)
        logger.info(f"Test search for '{test_query}' returned {len(results)} results")
        if results:
            logger.info(f"Top result preview: {results[0]['content'][:100]}...")
    else:
        logger.warning("RAG module not available (LangChain dependencies missing)")
    
    # 2. Train ML Classifier
    logger.info("\n=== Training ML Classifier ===")
    classifier = MLClassifier()
    
    if classifier.is_available():
        logger.warning("Model already trained")
    else:
        texts, labels = create_sample_training_data()
        logger.info(f"Training with {len(texts)} samples ({sum(labels)} scam, {len(labels)-sum(labels)} safe)")
        
        metrics = classifier.train(texts, labels, save=True)
        logger.info(f"Training complete: {metrics}")
        
        # Test prediction
        test_text = "Pay money to get job opportunity"
        prediction = classifier.predict(test_text)
        logger.info(f"Test prediction for '{test_text}': {prediction}")
    
    # 3. Test Trust Calculator
    logger.info("\n=== Testing Trust Calculator ===")
    calculator = TrustCalculator()
    
    test_content = "Urgent! Pay 5000 rupees to claim your prize now!"
    
    # Get predictions
    ml_pred = classifier.predict(test_content) if classifier.is_available() else None
    rag_results = rag.search_relevant_info(test_content, k=3) if rag.is_available() else None
    
    # Calculate trust score
    result = calculator.calculate_trust_score(
        content=test_content,
        ml_prediction=ml_pred,
        rag_results=rag_results,
        language='en'
    )
    
    logger.info(f"Trust calculation test:")
    logger.info(f"  Trust Score: {result['trust_score']}/100")
    logger.info(f"  Risk Level: {result['risk_level']}")
    logger.info(f"  Category: {result['category']}")
    logger.info(f"  Explanation: {result['explanation'][:100]}...")
    
    logger.info("\n=== AI Engine training completed successfully ===")


if __name__ == "__main__":
    train_ai_engine()
