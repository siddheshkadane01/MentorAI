"""
Retrieval Agent
Performs RAG (Retrieval-Augmented Generation) using vector database.
"""

import logging
from typing import Dict, Any, List
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import os

# Configure logging
logger = logging.getLogger(__name__)


class RetrievalAgent:
    """
    Agent responsible for retrieving relevant content from vector database.
    Uses RAG to prevent hallucination.
    Uses LOCAL embeddings (no API needed).
    """
    
    def __init__(self, vector_db_path: str = "vectorstore/faiss_index"):
        """
        Initialize the Retrieval Agent.
        
        Args:
            vector_db_path: Path to the FAISS vector database
        """
        self.vector_db_path = vector_db_path
        # Use local embeddings (no API key needed!)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        self.vectorstore = None
        
        # Load vector database if it exists
        if os.path.exists(vector_db_path):
            try:
                self.vectorstore = FAISS.load_local(
                    vector_db_path, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info(f"[RETRIEVAL AGENT] Vector database loaded from {vector_db_path}")
            except Exception as e:
                logger.error(f"[RETRIEVAL AGENT] Failed to load vector database: {e}")
        else:
            logger.warning(f"[RETRIEVAL AGENT] Vector database not found at {vector_db_path}")
    
    def retrieve_context(self, query: str, k: int = 3) -> List[str]:
        """
        Retrieve top-k relevant documents for a query.
        
        Args:
            query: Search query
            k: Number of documents to retrieve
            
        Returns:
            List of relevant text chunks
        """
        if not self.vectorstore:
            logger.warning("[RETRIEVAL AGENT] No vectorstore available, returning empty context")
            return []
        
        logger.info(f"[RETRIEVAL AGENT] Retrieving top-{k} documents for: {query[:50]}...")
        
        try:
            docs = self.vectorstore.similarity_search(query, k=k)
            contexts = [doc.page_content for doc in docs]
            logger.info(f"[RETRIEVAL AGENT] Retrieved {len(contexts)} relevant chunks")
            
            for i, ctx in enumerate(contexts, 1):
                logger.debug(f"[RETRIEVAL AGENT] Chunk {i}: {ctx[:100]}...")
            
            return contexts
        except Exception as e:
            logger.error(f"[RETRIEVAL AGENT] Retrieval failed: {e}")
            return []
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute retrieval as part of agent workflow.
        
        Args:
            state: Current state containing 'query' and 'topic'
            
        Returns:
            Updated state with 'context' field
        """
        topic = state.get("topic", state.get("query", ""))
        contexts = self.retrieve_context(topic, k=3)
        
        # Combine contexts into a single string
        combined_context = "\n\n---\n\n".join(contexts) if contexts else "No relevant context found."
        
        state["context"] = combined_context
        logger.info(f"[RETRIEVAL AGENT] Context added to state ({len(combined_context)} chars)")
        
        return state
