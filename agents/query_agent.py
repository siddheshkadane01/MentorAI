"""
Query Understanding Agent
Classifies student intent and extracts topics from queries.
"""

import logging
import os
from typing import Dict, Any
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

# Configure logging
logger = logging.getLogger(__name__)


class QueryAgent:
    """
    Agent responsible for understanding student queries.
    Extracts intent and topic information.
    """
    
    def __init__(self, model_name: str = "llama3.2:3b", temperature: float = 0.0):
        """Initialize the Query Understanding Agent."""
        self.llm = ChatOllama(
            model=model_name,
            temperature=temperature
        )
        logger.info(f"QueryAgent initialized with LOCAL model: {model_name}")
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze student query and extract intent and topic.
        
        Args:
            query: Student's question or request
            
        Returns:
            Dictionary with intent, topic, and difficulty level
        """
        logger.info(f"[QUERY AGENT] Analyzing query: {query[:50]}...")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a query analysis expert for an educational system.
Analyze the student's query and extract:
1. Intent: Choose ONE from [concept, practice, quiz, doubt]
   - concept: student wants to learn a new topic
   - practice: student wants examples or practice problems
   - quiz: student wants to test their knowledge
   - doubt: student has a specific question about a topic
2. Topic: Main subject/concept mentioned
3. Difficulty: Infer from query context [easy, medium, hard] or default to 'medium'

Respond ONLY in this JSON format:
{{"intent": "...", "topic": "...", "difficulty": "..."}}"""),
            ("user", "{query}")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"query": query})
        
        # Parse response
        import json
        try:
            result = json.loads(response.content)
            logger.info(f"[QUERY AGENT] Detected - Intent: {result['intent']}, Topic: {result['topic']}, Difficulty: {result['difficulty']}")
            return result
        except json.JSONDecodeError:
            logger.warning("[QUERY AGENT] Failed to parse JSON, using defaults")
            return {
                "intent": "concept",
                "topic": query,
                "difficulty": "medium"
            }
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute query analysis as part of agent workflow.
        
        Args:
            state: Current state containing 'query'
            
        Returns:
            Updated state with intent, topic, and difficulty
        """
        query = state.get("query", "")
        analysis = self.analyze_query(query)
        
        state.update({
            "intent": analysis["intent"],
            "topic": analysis["topic"],
            "difficulty": analysis.get("difficulty", "medium")
        })
        
        return state
