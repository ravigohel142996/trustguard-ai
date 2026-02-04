"""
TrustGuard AI - RAG (Retrieval Augmented Generation) Module
Purpose: Load documents, create TF-IDF index, and search for relevant passages
"""

import os
import logging
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
DOCS_DIR = os.path.join(os.path.dirname(__file__), "data", "trusted_docs")
CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
CACHE_FILE = os.path.join(CACHE_DIR, "rag_cache.pkl")
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_RESULTS = 3

# TF-IDF Configuration
# Max features limits vocabulary size for efficiency while maintaining quality
# 500 is sufficient for scam-related terminology without excessive memory use
TFIDF_MAX_FEATURES = 500


class RAGSystem:
    """RAG System for document retrieval and search"""
    
    def __init__(self, docs_dir: str = DOCS_DIR, cache_dir: str = CACHE_DIR):
        """
        Initialize RAG System
        
        Args:
            docs_dir: Directory containing trusted documents
            cache_dir: Directory for caching index
        """
        self.docs_dir = docs_dir
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "rag_cache.pkl")
        self.vectorizer = None
        self.document_chunks = []
        self.tfidf_matrix = None
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        
        logger.info(f"RAG System initialized with docs_dir: {docs_dir}")
    
    def _load_documents(self) -> List:
        """
        Load text documents from the trusted_docs directory
        
        Returns:
            List of Document objects
        """
        logger.info(f"Loading documents from: {self.docs_dir}")
        
        if not os.path.exists(self.docs_dir):
            logger.warning(f"Documents directory not found: {self.docs_dir}")
            return []
        
        # Load all .txt files from the directory
        loader = DirectoryLoader(
            self.docs_dir,
            glob="**/*.txt",
            loader_cls=TextLoader,
            show_progress=False
        )
        
        try:
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} documents")
            return documents
        except Exception as e:
            logger.error(f"Error loading documents: {str(e)}")
            return []
    
    def _split_documents(self, documents: List) -> List:
        """
        Split documents into smaller chunks for embedding
        
        Args:
            documents: List of Document objects
        
        Returns:
            List of split Document chunks
        """
        logger.info("Splitting documents into chunks")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        
        splits = text_splitter.split_documents(documents)
        logger.info(f"Created {len(splits)} document chunks")
        
        return splits
    
    def _build_index(self, document_chunks: List):
        """
        Build TF-IDF index from document chunks
        
        Args:
            document_chunks: List of split Document chunks
        """
        logger.info("Building TF-IDF index from document chunks")
        
        try:
            # Extract text content from chunks
            texts = [chunk.page_content for chunk in document_chunks]
            
            # Create TF-IDF vectorizer
            self.vectorizer = TfidfVectorizer(
                max_features=TFIDF_MAX_FEATURES,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            # Fit and transform documents
            self.tfidf_matrix = self.vectorizer.fit_transform(texts)
            self.document_chunks = document_chunks
            
            logger.info("TF-IDF index built successfully")
        except Exception as e:
            logger.error(f"Error building index: {str(e)}")
            raise
    
    def _save_cache(self):
        """Save index to disk for caching"""
        if self.vectorizer is None or self.tfidf_matrix is None:
            logger.warning("No index to save")
            return
        
        try:
            logger.info(f"Saving cache to: {self.cache_file}")
            cache_data = {
                'vectorizer': self.vectorizer,
                'tfidf_matrix': self.tfidf_matrix,
                'document_chunks': self.document_chunks
            }
            with open(self.cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            logger.info("Cache saved successfully")
        except Exception as e:
            logger.error(f"Error saving cache: {str(e)}")
    
    def _load_cache(self) -> bool:
        """
        Load index from disk cache
        
        Returns:
            True if cache loaded successfully, False otherwise
        """
        if not os.path.exists(self.cache_file):
            logger.info("No cached index found")
            return False
        
        try:
            logger.info(f"Loading cache from: {self.cache_file}")
            
            with open(self.cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            self.vectorizer = cache_data['vectorizer']
            self.tfidf_matrix = cache_data['tfidf_matrix']
            self.document_chunks = cache_data['document_chunks']
            
            logger.info("Cache loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading cache: {str(e)}")
            return False
    
    def initialize(self, force_rebuild: bool = False):
        """
        Initialize the RAG system - load or build index
        
        Args:
            force_rebuild: If True, rebuild index even if cache exists
        """
        logger.info("Initializing RAG system")
        
        # Try to load from cache first
        if not force_rebuild and self._load_cache():
            logger.info("RAG system initialized from cache")
            return
        
        # Build new index
        logger.info("Building new index")
        documents = self._load_documents()
        
        if not documents:
            logger.warning("No documents loaded, RAG system may not function properly")
            return
        
        document_chunks = self._split_documents(documents)
        
        if not document_chunks:
            logger.warning("No document chunks created")
            return
        
        self._build_index(document_chunks)
        self._save_cache()
        
        logger.info("RAG system initialized successfully")
    
    def search_docs(self, query: str, top_k: int = TOP_K_RESULTS) -> List[Dict[str, str]]:
        """
        Search for relevant passages in the document store
        
        Args:
            query: Search query string
            top_k: Number of top results to return (default: 3)
        
        Returns:
            List of dictionaries containing:
                - content: The relevant passage text
                - source: Source document filename
                - score: Relevance score
        """
        if self.vectorizer is None or self.tfidf_matrix is None:
            logger.warning("Index not initialized. Call initialize() first.")
            return []
        
        try:
            logger.info(f"Searching for query: '{query[:50]}...'")
            
            # Transform query using the same vectorizer
            query_vector = self.vectorizer.transform([query])
            
            # Calculate cosine similarity
            similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]
            
            # Get top k indices
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            # Format results
            formatted_results = []
            for idx in top_indices:
                score = float(similarities[idx])
                if score > 0:  # Only include results with non-zero similarity
                    doc = self.document_chunks[idx]
                    result = {
                        "content": doc.page_content,
                        "source": os.path.basename(doc.metadata.get("source", "unknown")),
                        "score": score
                    }
                    formatted_results.append(result)
            
            logger.info(f"Found {len(formatted_results)} relevant passages")
            return formatted_results
        
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []


# Global RAG instance
_rag_instance: Optional[RAGSystem] = None


def get_rag_system() -> RAGSystem:
    """
    Get or create the global RAG system instance
    
    Returns:
        RAGSystem instance
    """
    global _rag_instance
    
    if _rag_instance is None:
        _rag_instance = RAGSystem()
        _rag_instance.initialize()
    
    return _rag_instance


def search_docs(query: str, top_k: int = 3) -> List[Dict[str, str]]:
    """
    Convenience function to search documents using the global RAG instance
    
    Args:
        query: Search query string
        top_k: Number of top results to return (default: 3)
    
    Returns:
        List of dictionaries with content, source, and score
    """
    rag = get_rag_system()
    return rag.search_docs(query, top_k=top_k)
