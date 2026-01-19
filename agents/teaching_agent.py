"""
Teaching Agent
Generates educational explanations using retrieved context.
"""

import logging
import os
from typing import Dict, Any
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

# Configure logging
logger = logging.getLogger(__name__)


class TeachingAgent:
    """
    Agent responsible for generating clear, educational explanations.
    Uses retrieved context to provide accurate information.
    """
    
    def __init__(self, model_name: str = "llama3.2:3b", temperature: float = 0.7):
        """Initialize the Teaching Agent."""
        self.llm = ChatOllama(
            model=model_name,
            temperature=temperature
        )
        logger.info(f"TeachingAgent initialized with LOCAL model: {model_name}")
    
    def generate_explanation(
        self, 
        query: str, 
        context: str, 
        intent: str = "concept",
        difficulty: str = "medium"
    ) -> str:
        """
        Generate educational explanation based on context and intent.
        
        Args:
            query: Student's question
            context: Retrieved relevant content
            intent: Type of request (concept, practice, doubt)
            difficulty: Difficulty level
            
        Returns:
            Educational explanation
        """
        logger.info(f"[TEACHING AGENT] Generating explanation for intent: {intent}, difficulty: {difficulty}")
        
        # Customize prompt based on intent
        intent_instructions = {
            "concept": "Provide a comprehensive explanation of the concept with examples.",
            "practice": "Provide practice examples and walk through the solution steps.",
            "doubt": "Address the specific question clearly and concisely.",
            "quiz": "This will be handled by the quiz agent, provide brief overview only."
        }
        
        instruction = intent_instructions.get(intent, intent_instructions["concept"])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are an expert tutor helping students learn.

Your task: {instruction}

Guidelines:
- Use the provided context as your primary source of truth
- Adjust explanation complexity to {difficulty} level
- Use clear examples and analogies
- Break down complex concepts into steps
- Be encouraging and supportive
- If context is insufficient, acknowledge it and provide general guidance

Context:
{{context}}

Remember: Base your answer on the context provided to ensure accuracy."""),
            ("user", "{query}")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "query": query,
            "context": context
        })
        
        explanation = response.content
        logger.info(f"[TEACHING AGENT] Generated explanation ({len(explanation)} chars)")
        
        return explanation
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute teaching as part of agent workflow.
        
        Args:
            state: Current state with query, context, intent, difficulty
            
        Returns:
            Updated state with 'explanation' field
        """
        query = state.get("query", "")
        context = state.get("context", "")
        intent = state.get("intent", "concept")
        difficulty = state.get("difficulty", "medium")
        
        # Skip if intent is quiz (handled by quiz agent)
        if intent == "quiz":
            state["explanation"] = "Quiz mode activated. Proceeding to quiz generation..."
            logger.info("[TEACHING AGENT] Skipping explanation for quiz intent")
            return state
        
        explanation = self.generate_explanation(query, context, intent, difficulty)
        state["explanation"] = explanation
        
        return state
