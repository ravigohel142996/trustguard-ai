"""
RAG (Retrieval-Augmented Generation) Module using FAISS + LangChain
Handles document loading, vector embeddings, and semantic search
"""

import os
import logging
from typing import List, Dict, Optional
from pathlib import Path

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.embeddings import HuggingFaceEmbeddings
    from langchain.vectorstores import FAISS
    from langchain.docstore.document import Document
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

logger = logging.getLogger(__name__)


class RAGModule:
    """
    RAG Module for semantic search over trusted documents
    Uses FAISS for vector storage and retrieval
    """
    
    def __init__(self, documents_path: Optional[str] = None, index_path: Optional[str] = None):
        """
        Initialize RAG Module
        
        Args:
            documents_path: Path to directory containing trusted documents
            index_path: Path to save/load FAISS index
        """
        if not LANGCHAIN_AVAILABLE:
            logger.warning("LangChain not available. RAG module will operate in limited mode.")
            self.vectorstore = None
            self.embeddings = None
            return
        
        self.documents_path = documents_path or os.path.join(
            os.path.dirname(__file__), '../data/trusted_docs'
        )
        self.index_path = index_path or os.path.join(
            os.path.dirname(__file__), '../data/faiss_index'
        )
        
        # Initialize embeddings model (using a lightweight model)
        logger.info("Initializing embeddings model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        # Initialize or load vector store
        self.vectorstore = None
        self._initialize_vectorstore()
    
    def _initialize_vectorstore(self):
        """Initialize or load FAISS vector store"""
        try:
            # Try to load existing index
            if os.path.exists(self.index_path):
                logger.info(f"Loading existing FAISS index from {self.index_path}")
                self.vectorstore = FAISS.load_local(
                    self.index_path, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info("FAISS index loaded successfully")
            else:
                logger.info("No existing index found. Will create new index when documents are loaded.")
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}")
            self.vectorstore = None
    
    def load_documents(self, documents: Optional[List[str]] = None) -> int:
        """
        Load trusted documents and create vector embeddings
        
        Args:
            documents: List of document texts. If None, loads from documents_path
        
        Returns:
            Number of documents loaded
        """
        if not LANGCHAIN_AVAILABLE:
            logger.warning("LangChain not available. Cannot load documents.")
            return 0
        
        try:
            doc_objects = []
            
            if documents:
                # Use provided documents
                for i, text in enumerate(documents):
                    doc_objects.append(Document(
                        page_content=text,
                        metadata={"source": f"document_{i}"}
                    ))
            else:
                # Load from files
                if os.path.exists(self.documents_path):
                    for file_path in Path(self.documents_path).rglob('*.txt'):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            doc_objects.append(Document(
                                page_content=content,
                                metadata={"source": str(file_path)}
                            ))
            
            if not doc_objects:
                logger.warning("No documents found to load")
                return 0
            
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
                length_function=len,
            )
            splits = text_splitter.split_documents(doc_objects)
            
            # Create or update vector store
            if self.vectorstore is None:
                logger.info(f"Creating new FAISS index with {len(splits)} chunks")
                self.vectorstore = FAISS.from_documents(splits, self.embeddings)
            else:
                logger.info(f"Adding {len(splits)} chunks to existing index")
                self.vectorstore.add_documents(splits)
            
            # Save index
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            self.vectorstore.save_local(self.index_path)
            logger.info(f"FAISS index saved to {self.index_path}")
            
            return len(doc_objects)
        
        except Exception as e:
            logger.error(f"Error loading documents: {e}")
            return 0
    
    def search_relevant_info(self, query: str, k: int = 3) -> List[Dict[str, str]]:
        """
        Search for relevant information from trusted documents
        
        Args:
            query: Search query
            k: Number of top results to return
        
        Returns:
            List of relevant document chunks with scores
        """
        if not LANGCHAIN_AVAILABLE or self.vectorstore is None:
            logger.warning("RAG not available. Returning empty results.")
            return []
        
        try:
            # Perform similarity search
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    'content': doc.page_content,
                    'source': doc.metadata.get('source', 'unknown'),
                    'relevance_score': float(1 / (1 + score))  # Convert distance to similarity
                })
            
            logger.info(f"Found {len(formatted_results)} relevant documents for query")
            return formatted_results
        
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def is_available(self) -> bool:
        """Check if RAG module is available and initialized"""
        return LANGCHAIN_AVAILABLE and self.vectorstore is not None
