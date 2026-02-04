"""
TrustGuard AI - Scam Detection Classifier
Purpose: Train and use ML model to detect scam messages
"""

import os
import re
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Paths
DATASET_PATH = os.path.join(os.path.dirname(__file__), 'data', 'dataset', 'scam_dataset.csv')
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'scam_model.pkl')
VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), 'scam_vectorizer.pkl')

def preprocess_text(text):
    """
    Preprocess text for ML model
    - Convert to lowercase
    - Remove special characters (keep only alphanumeric and spaces)
    
    Args:
        text: Input text string
    
    Returns:
        Preprocessed text string
    """
    # Convert to lowercase
    text = text.lower()
    # Remove special characters, keep only letters, numbers, and spaces
    text = re.sub(r'[^a-z0-9\s]', '', text)
    # Remove extra whitespaces
    text = ' '.join(text.split())
    return text

def load_and_preprocess_data(dataset_path):
    """
    Load CSV dataset and preprocess text
    
    Args:
        dataset_path: Path to the CSV file
    
    Returns:
        Tuple of (texts, labels)
    """
    print(f"Loading dataset from: {dataset_path}")
    df = pd.read_csv(dataset_path)
    
    print(f"Dataset shape: {df.shape}")
    print(f"Label distribution:\n{df['label'].value_counts()}")
    
    # Preprocess all text
    df['text'] = df['text'].apply(preprocess_text)
    
    return df['text'].values, df['label'].values

def train_model():
    """
    Train the scam detection model
    - Load and preprocess data
    - Split into train/test sets
    - Train TF-IDF vectorizer and Logistic Regression model
    - Save trained model and vectorizer
    """
    print("\n=== Training Scam Detection Model ===\n")
    
    # Load data
    texts, labels = load_and_preprocess_data(DATASET_PATH)
    
    # Split data into train and test sets (80/20 split)
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    print(f"\nTraining set size: {len(X_train)}")
    print(f"Test set size: {len(X_test)}")
    
    # Create TF-IDF vectorizer
    print("\nCreating TF-IDF vectorizer...")
    vectorizer = TfidfVectorizer(
        max_features=1000,  # Use top 1000 features
        ngram_range=(1, 2),  # Use unigrams and bigrams
        min_df=2  # Minimum document frequency
    )
    
    # Fit vectorizer on training data and transform
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    
    print(f"TF-IDF feature shape: {X_train_tfidf.shape}")
    
    # Train Logistic Regression model
    print("\nTraining Logistic Regression model...")
    model = LogisticRegression(
        max_iter=1000,
        random_state=42,
        class_weight='balanced'  # Handle class imbalance
    )
    
    model.fit(X_train_tfidf, y_train)
    
    # Make predictions on test set
    y_pred = model.predict(X_test_tfidf)
    
    # Calculate accuracy
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n=== Model Performance ===")
    print(f"Accuracy: {accuracy:.4f}")
    
    # Print detailed classification report
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save model and vectorizer
    print(f"\nSaving model to: {MODEL_PATH}")
    joblib.dump(model, MODEL_PATH)
    
    print(f"Saving vectorizer to: {VECTORIZER_PATH}")
    joblib.dump(vectorizer, VECTORIZER_PATH)
    
    print("\n=== Training Complete ===")
    print(f"Model saved: {MODEL_PATH}")
    print(f"Vectorizer saved: {VECTORIZER_PATH}")
    
    return accuracy

# Global variables for loaded model and vectorizer
_model = None
_vectorizer = None

def load_model():
    """
    Load trained model and vectorizer from disk
    """
    global _model, _vectorizer
    
    if _model is None or _vectorizer is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. Please run train_model() first."
            )
        if not os.path.exists(VECTORIZER_PATH):
            raise FileNotFoundError(
                f"Vectorizer not found at {VECTORIZER_PATH}. Please run train_model() first."
            )
        
        _model = joblib.load(MODEL_PATH)
        _vectorizer = joblib.load(VECTORIZER_PATH)
        print("Model and vectorizer loaded successfully")
    
    return _model, _vectorizer

def predict_scam(text):
    """
    Predict probability that a text is a scam
    
    Args:
        text: Input text string to analyze
    
    Returns:
        Float probability between 0 and 1 (0=safe, 1=scam)
    """
    # Load model if not already loaded
    model, vectorizer = load_model()
    
    # Preprocess input text
    processed_text = preprocess_text(text)
    
    # Transform text using TF-IDF vectorizer
    text_tfidf = vectorizer.transform([processed_text])
    
    # Get probability predictions
    # predict_proba returns [prob_safe, prob_scam]
    probabilities = model.predict_proba(text_tfidf)[0]
    
    # Return probability of scam class
    scam_probability = probabilities[1]
    
    return float(scam_probability)

if __name__ == "__main__":
    # Train the model when script is run directly
    train_model()
    
    # Test predictions
    print("\n=== Testing Predictions ===\n")
    
    test_cases = [
        "Pay fee to get job",
        "Exam result published",
        "Send money now to claim prize",
        "Meeting scheduled for tomorrow",
        "Your account will be suspended. Verify now",
        "Assignment deadline is next week"
    ]
    
    for test_text in test_cases:
        prob = predict_scam(test_text)
        label = "SCAM" if prob > 0.5 else "SAFE"
        print(f"Text: '{test_text}'")
        print(f"Scam Probability: {prob:.4f} [{label}]\n")
