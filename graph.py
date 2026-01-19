"""
LangGraph Orchestration for Multi-Agent Teaching Assistant
Coordinates agent execution using state graph.
"""

import logging
from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from agents.query_agent import QueryAgent
from agents.retrieval_agent import RetrievalAgent
from agents.teaching_agent import TeachingAgent
from agents.quiz_agent import QuizAgent
from agents.evaluation_agent import EvaluationAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Define the state structure
class AgentState(TypedDict):
    """State object shared across all agents."""
    query: str                          # User's question/request
    intent: str                         # Classified intent (concept/practice/quiz/doubt)
    topic: str                          # Extracted topic
    difficulty: str                     # Difficulty level (easy/medium/hard)
    context: str                        # Retrieved content from vector DB
    explanation: str                    # Generated explanation
    quiz: List[Dict[str, Any]]         # Generated quiz questions
    student_answers: Dict[int, str]    # Student's answers to quiz
    evaluation: Dict[str, Any]         # Evaluation results
    messages: Annotated[list, add_messages]  # Conversation history


class TeachingAssistantGraph:
    """
    Multi-agent orchestration using LangGraph.
    Manages workflow and agent interactions.
    """
    
    def __init__(self):
        """Initialize all agents and build the graph."""
        logger.info("=" * 70)
        logger.info("Initializing Teaching Assistant Multi-Agent System")
        logger.info("=" * 70)
        
        # Initialize agents
        self.query_agent = QueryAgent()
        self.retrieval_agent = RetrievalAgent()
        self.teaching_agent = TeachingAgent()
        self.quiz_agent = QuizAgent()
        self.evaluation_agent = EvaluationAgent()
        
        # Build the state graph
        self.graph = self._build_graph()
        
        logger.info("Multi-Agent System Ready")
        logger.info("=" * 70)
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state graph defining agent workflow.
        
        Workflow:
        1. Query Agent: Understand intent and extract topic
        2. Retrieval Agent: Get relevant content from vector DB
        3. Teaching Agent: Generate explanation (if needed)
        4. Quiz Agent: Generate quiz (if intent is quiz/practice)
        5. Evaluation Agent: Evaluate answers (if student provided answers)
        """
        logger.info("Building LangGraph workflow...")
        
        # Create state graph
        workflow = StateGraph(AgentState)
        
        # Add nodes for each agent
        workflow.add_node("query_understanding", self._query_node)
        workflow.add_node("retrieval", self._retrieval_node)
        workflow.add_node("teaching", self._teaching_node)
        workflow.add_node("quiz_generation", self._quiz_node)
        workflow.add_node("evaluate", self._evaluation_node)
        
        # Define the workflow edges
        workflow.set_entry_point("query_understanding")
        
        # After query understanding, always retrieve context
        workflow.add_edge("query_understanding", "retrieval")
        
        # After retrieval, decide based on intent
        workflow.add_conditional_edges(
            "retrieval",
            self._route_after_retrieval,
            {
                "teaching": "teaching",
                "quiz": "quiz_generation",
                "end": END
            }
        )
        
        # After teaching, check if quiz needed
        workflow.add_conditional_edges(
            "teaching",
            self._route_after_teaching,
            {
                "quiz": "quiz_generation",
                "end": END
            }
        )
        
        # After quiz, check if evaluation needed
        workflow.add_conditional_edges(
            "quiz_generation",
            self._route_after_quiz,
            {
                "evaluate": "evaluate",
                "end": END
            }
        )
        
        # After evaluation, end
        workflow.add_edge("evaluate", END)
        
        logger.info("LangGraph workflow built successfully")
        
        return workflow.compile()
    
    def _query_node(self, state: AgentState) -> AgentState:
        """Execute query understanding agent."""
        logger.info("\n" + "=" * 70)
        logger.info("STEP 1: Query Understanding Agent")
        logger.info("=" * 70)
        return self.query_agent.execute(state)
    
    def _retrieval_node(self, state: AgentState) -> AgentState:
        """Execute retrieval agent."""
        logger.info("\n" + "=" * 70)
        logger.info("STEP 2: Retrieval Agent (RAG)")
        logger.info("=" * 70)
        return self.retrieval_agent.execute(state)
    
    def _teaching_node(self, state: AgentState) -> AgentState:
        """Execute teaching agent."""
        logger.info("\n" + "=" * 70)
        logger.info("STEP 3: Teaching Agent")
        logger.info("=" * 70)
        return self.teaching_agent.execute(state)
    
    def _quiz_node(self, state: AgentState) -> AgentState:
        """Execute quiz generation agent."""
        logger.info("\n" + "=" * 70)
        logger.info("STEP 4: Quiz Generation Agent")
        logger.info("=" * 70)
        return self.quiz_agent.execute(state)
    
    def _evaluation_node(self, state: AgentState) -> AgentState:
        """Execute evaluation agent."""
        logger.info("\n" + "=" * 70)
        logger.info("STEP 5: Evaluation Agent")
        logger.info("=" * 70)
        return self.evaluation_agent.execute(state)
    
    def _route_after_retrieval(self, state: AgentState) -> str:
        """
        Decide next step after retrieval based on intent.
        
        Returns:
            Next node to execute
        """
        intent = state.get("intent", "concept")
        
        logger.info(f"\n[ROUTER] Intent: {intent}")
        
        if intent == "quiz":
            logger.info("[ROUTER] → Routing directly to quiz generation")
            return "quiz"
        elif intent in ["concept", "doubt", "practice"]:
            logger.info("[ROUTER] → Routing to teaching agent")
            return "teaching"
        else:
            logger.info("[ROUTER] → Ending workflow")
            return "end"
    
    def _route_after_teaching(self, state: AgentState) -> str:
        """
        Decide if quiz should be generated after teaching.
        
        Returns:
            Next node to execute
        """
        intent = state.get("intent", "concept")
        
        logger.info(f"\n[ROUTER] After teaching - Intent: {intent}")
        
        if intent == "practice":
            logger.info("[ROUTER] → Routing to quiz generation")
            return "quiz"
        else:
            logger.info("[ROUTER] → Ending workflow")
            return "end"
    
    def _route_after_quiz(self, state: AgentState) -> str:
        """
        Decide if evaluation should run after quiz.
        
        Returns:
            Next node to execute
        """
        student_answers = state.get("student_answers", {})
        
        logger.info(f"\n[ROUTER] After quiz - Has answers: {bool(student_answers)}")
        
        if student_answers:
            logger.info("[ROUTER] → Routing to evaluation")
            return "evaluate"
        else:
            logger.info("[ROUTER] → Ending workflow (no answers to evaluate)")
            return "end"
    
    def process_query(
        self, 
        query: str,
        student_answers: Dict[int, str] = None
    ) -> AgentState:
        """
        Process a student query through the multi-agent system.
        
        Args:
            query: Student's question or request
            student_answers: Optional answers to quiz questions
            
        Returns:
            Final state with all results
        """
        logger.info("\n" + "#" * 70)
        logger.info("PROCESSING NEW QUERY")
        logger.info("#" * 70)
        logger.info(f"Query: {query}")
        
        # Initialize state
        initial_state: AgentState = {
            "query": query,
            "intent": "",
            "topic": "",
            "difficulty": "medium",
            "context": "",
            "explanation": "",
            "quiz": [],
            "student_answers": student_answers or {},
            "evaluation": None,
            "messages": []
        }
        
        # Execute the graph
        final_state = self.graph.invoke(initial_state)
        
        logger.info("\n" + "#" * 70)
        logger.info("WORKFLOW COMPLETED")
        logger.info("#" * 70)
        
        return final_state


def create_teaching_assistant() -> TeachingAssistantGraph:
    """
    Factory function to create teaching assistant instance.
    
    Returns:
        Initialized TeachingAssistantGraph
    """
    return TeachingAssistantGraph()


# Example usage
if __name__ == "__main__":
    """
    Test the multi-agent system.
    """
    import os
    
    logger.info("🚀 Using 100% LOCAL Ollama model - no API keys needed!")
    
    # Create teaching assistant
    assistant = create_teaching_assistant()
    
    # Test queries
    test_queries = [
        "What is machine learning?",
        "I want to practice linear regression",
        "Give me a quiz on decision trees",
    ]
    
    for query in test_queries:
        logger.info(f"\n\n{'='*70}")
        logger.info(f"Testing: {query}")
        logger.info('='*70)
        
        result = assistant.process_query(query)
        
        logger.info("\n--- RESULTS ---")
        logger.info(f"Intent: {result['intent']}")
        logger.info(f"Topic: {result['topic']}")
        
        if result.get('explanation'):
            logger.info(f"\nExplanation: {result['explanation'][:200]}...")
        
        if result.get('quiz'):
            logger.info(f"\nQuiz: {len(result['quiz'])} questions generated")
        
        logger.info("\n")
