"""
Evaluation Agent
Evaluates student answers and provides feedback.
"""

import logging
import os
from typing import Dict, Any, List
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import json

# Configure logging
logger = logging.getLogger(__name__)


class EvaluationAgent:
    """
    Agent responsible for evaluating student answers.
    Provides scores, identifies weaknesses, and suggests improvements.
    """
    
    def __init__(self, model_name: str = "llama3.2:3b", temperature: float = 0.3):
        """Initialize the Evaluation Agent."""
        self.llm = ChatOllama(
            model=model_name,
            temperature=temperature
        )
        logger.info(f"EvaluationAgent initialized with LOCAL model: {model_name}")
    
    def evaluate_mcq_answer(
        self,
        question: str,
        student_answer: str,
        correct_answer: str,
        explanation: str = ""
    ) -> Dict[str, Any]:
        """
        Evaluate an MCQ answer with exact matching.
        
        Args:
            question: The question asked
            student_answer: Student's selected option
            correct_answer: Correct option
            explanation: Explanation for the correct answer
            
        Returns:
            Dictionary with score and feedback
        """
        # Normalize answers for comparison
        student_clean = student_answer.strip()
        correct_clean = correct_answer.strip()
        
        is_correct = student_clean == correct_clean
        score = 100 if is_correct else 0
        
        logger.info(f"[EVALUATION AGENT] MCQ - Student: '{student_clean}' | Correct: '{correct_clean}' | Match: {is_correct}")
        
        if is_correct:
            return {
                "score": score,
                "is_correct": True,
                "strengths": ["Correct answer selected", "Good understanding of the concept"],
                "weaknesses": [],
                "feedback": f"✅ Excellent! Your answer is correct. {explanation}",
                "improvement_tips": []
            }
        else:
            return {
                "score": score,
                "is_correct": False,
                "strengths": ["Attempted the question"],
                "weaknesses": ["Incorrect option selected", "Review the concept"],
                "feedback": f"❌ Incorrect. The correct answer is: {correct_answer}. {explanation}",
                "improvement_tips": [
                    "Review the relevant study material",
                    "Focus on understanding key concepts",
                    "Try similar practice questions"
                ]
            }
    
    def evaluate_answer(
        self, 
        question: str,
        student_answer: str,
        correct_answer: str,
        question_type: str = "multiple_choice",
        explanation: str = "",
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Evaluate a student's answer against the correct answer.
        
        Args:
            question: The question asked
            student_answer: Student's response
            correct_answer: Expected correct answer
            question_type: Type of question (multiple_choice or short_answer)
            explanation: Explanation for correct answer
            context: Additional context for evaluation
            
        Returns:
            Dictionary with score, feedback, and suggestions
        """
        logger.info(f"[EVALUATION AGENT] Evaluating {question_type} answer for question: {question[:50]}...")
        
        # For MCQ, use exact matching
        if question_type == "multiple_choice":
            return self.evaluate_mcq_answer(question, student_answer, correct_answer, explanation)
        
        # For short answer, use LLM evaluation
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert educational evaluator.

Evaluate the student's answer and provide constructive feedback.

Question: {question}
Correct Answer: {correct_answer}
Student Answer: {student_answer}
Context: {context}

Provide evaluation in this JSON format:
{{
  "score": <0-100>,
  "is_correct": <true/false>,
  "strengths": ["strength 1", "strength 2"],
  "weaknesses": ["weakness 1", "weakness 2"],
  "feedback": "Detailed constructive feedback",
  "improvement_tips": ["tip 1", "tip 2"]
}}

Be encouraging but honest. Focus on understanding, not exact wording."""),
            ("user", "Evaluate now.")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "question": question,
            "student_answer": student_answer,
            "correct_answer": correct_answer,
            "context": context
        })
        
        try:
            evaluation = json.loads(response.content)
            logger.info(f"[EVALUATION AGENT] Score: {evaluation['score']}/100, Correct: {evaluation['is_correct']}")
            return evaluation
        except json.JSONDecodeError:
            logger.error("[EVALUATION AGENT] Failed to parse evaluation JSON")
            return {
                "score": 50,
                "is_correct": False,
                "strengths": ["Attempted the question"],
                "weaknesses": ["Unable to fully evaluate"],
                "feedback": "Please try again with more detail.",
                "improvement_tips": ["Review the material", "Practice more examples"]
            }
    
    def evaluate_quiz(
        self,
        quiz: list,
        student_answers: Dict[int, str],
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Evaluate multiple quiz answers.
        
        Args:
            quiz: List of question dictionaries
            student_answers: Dictionary mapping question index to student answer
            context: Additional context
            
        Returns:
            Overall evaluation with per-question breakdown
        """
        logger.info(f"[EVALUATION AGENT] Evaluating quiz with {len(student_answers)} answers")
        
        evaluations = []
        total_score = 0
        
        for idx, answer_text in student_answers.items():
            if idx < len(quiz):
                question_data = quiz[idx]
                eval_result = self.evaluate_answer(
                    question=question_data["question"],
                    student_answer=answer_text,
                    correct_answer=question_data["correct_answer"],
                    question_type=question_data.get("type", "multiple_choice"),
                    explanation=question_data.get("explanation", ""),
                    context=context
                )
                eval_result["question_number"] = idx + 1
                evaluations.append(eval_result)
                total_score += eval_result["score"]
        
        avg_score = total_score / len(student_answers) if student_answers else 0
        
        # Calculate additional stats
        correct_count = sum(1 for e in evaluations if e.get("is_correct", False))
        
        return {
            "overall_score": round(avg_score, 2),
            "questions_evaluated": len(evaluations),
            "correct_answers": correct_count,
            "incorrect_answers": len(evaluations) - correct_count,
            "evaluations": evaluations
        }
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute evaluation as part of agent workflow.
        
        Args:
            state: Current state with quiz and student_answers
            
        Returns:
            Updated state with 'evaluation' field
        """
        # Check if there's anything to evaluate
        student_answers = state.get("student_answers", {})
        
        if not student_answers:
            logger.info("[EVALUATION AGENT] No student answers to evaluate")
            state["evaluation"] = None
            return state
        
        quiz = state.get("quiz", [])
        context = state.get("context", "")
        
        evaluation = self.evaluate_quiz(quiz, student_answers, context)
        state["evaluation"] = evaluation
        
        logger.info(f"[EVALUATION AGENT] Overall score: {evaluation['overall_score']}/100")
        
        return state
    
    def evaluate_quiz_directly(self, quiz_questions: List[Dict[str, Any]], student_answers: Dict[int, str], context: str = "") -> Dict[str, Any]:
        """
        Directly evaluate a quiz without going through the state graph.
        Used for MCQ mode where we already have the quiz questions.
        
        Args:
            quiz_questions: List of quiz questions with correct answers
            student_answers: Dict mapping question index to student's answer
            context: Optional context for evaluation
            
        Returns:
            Evaluation results dictionary
        """
        logger.info(f"[EVALUATION AGENT] Direct evaluation of {len(student_answers)} answers...")
        return self.evaluate_quiz(quiz_questions, student_answers, context)
