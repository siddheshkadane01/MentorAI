"""
Configuration settings for the AI Teaching Assistant.
Centralized configuration management.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration."""
    
    # Model Configuration (LOCAL - No API needed!)
    DEFAULT_MODEL: str = "llama3.2:3b"  # Local Ollama model
    TEMPERATURE_QUERY: float = 0.0      # Deterministic for classification
    TEMPERATURE_TEACHING: float = 0.7   # Creative for explanations
    TEMPERATURE_QUIZ: float = 0.7       # Creative for questions
    TEMPERATURE_EVAL: float = 0.3       # Consistent for evaluation
    
    # Vector Database Configuration
    VECTOR_DB_PATH: str = "vectorstore/faiss_index"
    DATA_PATH: str = "data/sample_notes.txt"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RETRIEVAL: int = 3
    
    # Quiz Configuration
    DEFAULT_NUM_QUESTIONS: int = 5
    DEFAULT_DIFFICULTY: str = "medium"
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # UI Configuration
    APP_TITLE: str = "MentorAI: AI Teaching Assistant"
    APP_ICON: str = "🤖"
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate configuration.
        
        Returns:
            True if configuration is valid
        """
        # No API keys needed for 100% local operation
        return True


# Export config instance
config = Config()
