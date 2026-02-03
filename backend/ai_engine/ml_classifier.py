"""
ML Classifier Module using scikit-learn
Trains and uses a machine learning model for scam text classification
"""

import os
import pickle
import logging
from typing import Dict, List, Optional, Tuple
import re

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import train_test_split
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)


class MLClassifier:
    """
    Machine Learning Classifier for scam detection
    Uses TF-IDF vectorization and Naive Bayes classification
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize ML Classifier
        
        Args:
            model_path: Path to save/load trained model
        """
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn not available. ML classifier will operate in limited mode.")
            self.model = None
            return
        
        self.model_path = model_path or os.path.join(
            os.path.dirname(__file__), '../data/scam_classifier.pkl'
        )
        
        # Initialize model pipeline
        self.model = None
        self._load_or_create_model()
    
    def _load_or_create_model(self):
        """Load existing model or create new one"""
        try:
            if os.path.exists(self.model_path):
                logger.info(f"Loading existing model from {self.model_path}")
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info("Model loaded successfully")
            else:
                logger.info("Creating new model pipeline")
                self.model = Pipeline([
                    ('tfidf', TfidfVectorizer(
                        max_features=1000,
                        ngram_range=(1, 2),
                        stop_words='english'
                    )),
                    ('classifier', MultinomialNB(alpha=0.1))
                ])
                logger.info("New model pipeline created")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text for classification
        
        Args:
            text: Input text
        
        Returns:
            Preprocessed text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def train(self, texts: List[str], labels: List[int], save: bool = True) -> Dict[str, float]:
        """
        Train the classifier on labeled data
        
        Args:
            texts: List of text samples
            labels: List of labels (0 = safe, 1 = scam)
            save: Whether to save the trained model
        
        Returns:
            Dictionary with training metrics
        """
        if not SKLEARN_AVAILABLE or self.model is None:
            logger.warning("ML classifier not available. Cannot train model.")
            return {'error': 'Classifier not available'}
        
        try:
            # Preprocess texts
            processed_texts = [self.preprocess_text(text) for text in texts]
            
            # Split data for evaluation
            X_train, X_test, y_train, y_test = train_test_split(
                processed_texts, labels, test_size=0.2, random_state=42
            )
            
            # Train model
            logger.info(f"Training model on {len(X_train)} samples")
            self.model.fit(X_train, y_train)
            
            # Evaluate
            train_score = self.model.score(X_train, y_train)
            test_score = self.model.score(X_test, y_test)
            
            logger.info(f"Training accuracy: {train_score:.3f}")
            logger.info(f"Test accuracy: {test_score:.3f}")
            
            # Save model
            if save:
                os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
                with open(self.model_path, 'wb') as f:
                    pickle.dump(self.model, f)
                logger.info(f"Model saved to {self.model_path}")
            
            return {
                'train_accuracy': float(train_score),
                'test_accuracy': float(test_score),
                'samples_trained': len(X_train)
            }
        
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return {'error': str(e)}
    
    def predict(self, text: str) -> Dict[str, float]:
        """
        Predict scam probability for text
        
        Args:
            text: Input text to classify
        
        Returns:
            Dictionary with scam probability and confidence
        """
        if not SKLEARN_AVAILABLE or self.model is None:
            logger.warning("ML classifier not available. Using fallback.")
            return self._fallback_prediction(text)
        
        try:
            # Check if model is trained
            if not hasattr(self.model, 'classes_'):
                logger.warning("Model not trained. Using fallback.")
                return self._fallback_prediction(text)
            
            # Preprocess and predict
            processed_text = self.preprocess_text(text)
            probabilities = self.model.predict_proba([processed_text])[0]
            
            # Get scam probability (class 1)
            scam_prob = probabilities[1] if len(probabilities) > 1 else 0.5
            
            # Calculate confidence (distance from 0.5)
            confidence = abs(scam_prob - 0.5) * 2
            
            return {
                'scam_probability': float(scam_prob),
                'confidence': float(confidence)
            }
        
        except Exception as e:
            logger.error(f"Error predicting: {e}")
            return self._fallback_prediction(text)
    
    def _fallback_prediction(self, text: str) -> Dict[str, float]:
        """
        Fallback prediction using simple keyword matching
        
        Args:
            text: Input text
        
        Returns:
            Dictionary with scam probability and confidence
        """
        scam_keywords = [
            'pay', 'urgent', 'click', 'verify', 'account', 'suspended',
            'winner', 'prize', 'lottery', 'bank', 'credit card', 'password',
            'cash', 'money', 'transfer', 'investment', 'guarantee', 'free',
            'congratulations', 'claim', 'expires', 'rupees', 'immediately'
        ]
        
        text_lower = text.lower()
        matches = sum(1 for keyword in scam_keywords if keyword in text_lower)
        
        # Calculate probability based on keyword matches
        scam_prob = min(matches * 0.15, 0.9)
        confidence = min(matches * 0.1, 0.7)
        
        return {
            'scam_probability': scam_prob,
            'confidence': confidence
        }
    
    def is_available(self) -> bool:
        """Check if ML classifier is available and trained"""
        if not SKLEARN_AVAILABLE or self.model is None:
            return False
        return hasattr(self.model, 'classes_')
