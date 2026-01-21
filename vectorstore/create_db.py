"""
Create Vector Database from Study Materials
Builds FAISS vector store from text documents for RAG.
"""

import os
import logging
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_vector_database(
    data_path: str = "data/sample_notes.txt",
    output_path: str = "vectorstore/faiss_index",
    chunk_size: int = 1000,
    chunk_overlap: int = 200
):
    """
    Create FAISS vector database from text documents.
    
    Args:
        data_path: Path to input text file(s)
        output_path: Path to save FAISS index
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
    """
    logger.info("=" * 60)
    logger.info("Starting Vector Database Creation")
    logger.info("=" * 60)
    
    # Check if data file exists
    if not os.path.exists(data_path):
        logger.error(f"Data file not found: {data_path}")
        logger.info("Please create sample_notes.txt in the data/ directory first.")
        return
    
    # Load documents
    logger.info(f"Loading documents from: {data_path}")
    loader = TextLoader(data_path, encoding="utf-8")
    documents = loader.load()
    logger.info(f"Loaded {len(documents)} document(s)")
    
    # Split documents into chunks
    logger.info(f"Splitting documents (chunk_size={chunk_size}, overlap={chunk_overlap})")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Created {len(chunks)} text chunks")
    
    # Create embeddings (LOCAL - No API needed!)
    logger.info("Initializing local Sentence Transformers embeddings...")
    logger.info("Using model: all-MiniLM-L6-v2 (runs on your machine)")
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    # Create vector store
    logger.info("Creating FAISS vector store...")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    # Save to disk
    logger.info(f"Saving vector store to: {output_path}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    vectorstore.save_local(output_path)
    
    logger.info("=" * 60)
    logger.info("Vector Database Created Successfully!")
    logger.info(f"Location: {output_path}")
    logger.info(f"Total chunks indexed: {len(chunks)}")
    logger.info("=" * 60)
    
    # Test retrieval
    logger.info("\nTesting retrieval...")
    test_query = "What is machine learning?"
    results = vectorstore.similarity_search(test_query, k=2)
    logger.info(f"Test query: '{test_query}'")
    logger.info(f"Retrieved {len(results)} results")
    for i, doc in enumerate(results, 1):
        logger.info(f"\nResult {i}:")
        logger.info(doc.page_content[:200] + "...")


def load_multiple_files(directory: str = "data") -> list:
    """
    Load multiple text files from a directory.
    
    Args:
        directory: Directory containing text files
        
    Returns:
        List of loaded documents
    """
    documents = []
    data_dir = Path(directory)
    
    if not data_dir.exists():
        logger.error(f"Directory not found: {directory}")
        return documents
    
    for file_path in data_dir.glob("*.txt"):
        logger.info(f"Loading: {file_path}")
        loader = TextLoader(str(file_path), encoding="utf-8")
        documents.extend(loader.load())
    
    return documents


if __name__ == "__main__":
    """
    Run this script to create the vector database:
    python vectorstore/create_db.py
    """
    import sys
    
    logger.info("100% LOCAL: Using Sentence Transformers for embeddings (no API needed!)")
    logger.info("100% LOCAL: Using Ollama for chat (no API needed!)")
    
    # Create vector database
    try:
        create_vector_database()
    except Exception as e:
        logger.error(f"Failed to create vector database: {e}")
        sys.exit(1)
