"""
Quiz Generation Agent
Creates practice questions based on topic and difficulty.
"""

import logging
import os
from typing import Dict, Any, List
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import json

# Configure logging
logger = logging.getLogger(__name__)


class QuizAgent:
    """
    Agent responsible for generating quiz questions.
    Creates questions with appropriate difficulty and includes answers.
    """
    
    def __init__(self, model_name: str = "llama3.2:3b", temperature: float = 0.7):
        """Initialize the Quiz Agent."""
        self.llm = ChatOllama(
            model=model_name,
            temperature=temperature
        )
        logger.info(f"QuizAgent initialized with LOCAL model: {model_name}")
    
    def generate_quiz(
        self, 
        topic: str, 
        context: str,
        difficulty: str = "medium",
        num_questions: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generate quiz questions on a topic.
        
        Args:
            topic: Subject to quiz on
            context: Retrieved relevant content
            difficulty: Question difficulty level
            num_questions: Number of questions to generate
            
        Returns:
            List of question dictionaries
        """
        logger.info(f"[QUIZ AGENT] Generating {num_questions} {difficulty} questions on: {topic}")
        
        system_prompt = f"""You are an expert quiz creator for educational purposes.

IMPORTANT: Generate EXACTLY {num_questions} questions. No more, no less.

Topic: {topic}
Difficulty: {difficulty}
Number of Questions Required: {num_questions}

Use the provided context to ensure questions are relevant and accurate.

Context:
{{{{context}}}}

Requirements:
1. Generate EXACTLY {num_questions} questions
2. Questions should test understanding, not just memorization
3. Include a mix of question types (multiple choice preferred)
4. Provide correct answers clearly
5. Make questions appropriate for {difficulty} difficulty

Respond ONLY in this JSON format (no additional text):
{{{{
  "questions": [
    {{{{
      "question": "Question text here?",
      "type": "multiple_choice",
      "options": ["A) First option", "B) Second option", "C) Third option", "D) Fourth option"],
      "correct_answer": "A) First option",
      "explanation": "Why this is the correct answer"
    }}}}
  ]
}}}}

For short_answer type, use empty options list [].
IMPORTANT: The 'correct_answer' must EXACTLY match one of the options (including the letter prefix)."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "Generate the quiz now.")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "context": context,
            "topic": topic
        })
        
        try:
            quiz_data = json.loads(response.content)
            questions = quiz_data.get("questions", [])
            logger.info(f"[QUIZ AGENT] Successfully generated {len(questions)} questions")
            return questions
        except json.JSONDecodeError:
            logger.error("[QUIZ AGENT] Failed to parse quiz JSON")
            return [{
                "question": f"What are the key concepts in {topic}?",
                "type": "short_answer",
                "options": [],
                "correct_answer": "Based on the study material...",
                "explanation": "This tests overall understanding."
            }]
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute quiz generation as part of agent workflow.
        
        Args:
            state: Current state with topic, context, difficulty
            
        Returns:
            Updated state with 'quiz' field
        """
        intent = state.get("intent", "concept")
        
        # Only generate quiz if intent is quiz or practice
        if intent not in ["quiz", "practice"]:
            logger.info("[QUIZ AGENT] Skipping quiz generation (intent not quiz/practice)")
            state["quiz"] = None
            return state
        
        topic = state.get("topic", "")
        context = state.get("context", "")
        difficulty = state.get("difficulty", "medium")
        query = state.get("query", "")
        
        # Try to extract number of questions from query
        num_questions = 5  # default
        import re
        match = re.search(r'(\d+)-question', query.lower())
        if match:
            num_questions = int(match.group(1))
            logger.info(f"[QUIZ AGENT] Detected {num_questions} questions requested in query")
        
        quiz = self.generate_quiz(topic, context, difficulty, num_questions)
        state["quiz"] = quiz
        
        return state
