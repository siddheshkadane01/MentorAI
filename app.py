"""
Streamlit Frontend for AI Teaching Assistant
Interactive UI for student-agent interaction.
"""

import streamlit as st
import os
import sys
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from graph import create_teaching_assistant

# Configure logging to capture agent activities
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="MentorAI: AI Teaching Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    .agent-status {
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        font-weight: bold;
    }
    .agent-active {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .quiz-box {
        background-color: #f5f5f5;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 2px solid #e0e0e0;
    }
    .feedback-good {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #4caf50;
    }
    .feedback-poor {
        background-color: #ffebee;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #f44336;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'assistant' not in st.session_state:
        with st.spinner("🤖 Initializing AI Teaching Assistant..."):
            st.session_state.assistant = create_teaching_assistant()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'current_quiz' not in st.session_state:
        st.session_state.current_quiz = None
    
    if 'quiz_results' not in st.session_state:
        st.session_state.quiz_results = None
    
    if 'mcq_quiz' not in st.session_state:
        st.session_state.mcq_quiz = None
    
    if 'mcq_answers' not in st.session_state:
        st.session_state.mcq_answers = {}
    
    if 'mcq_results' not in st.session_state:
        st.session_state.mcq_results = None


def display_header():
    """Display application header."""
    st.markdown('<h1 class="main-header">🤖 MentorAI: Autonomous AI Teaching Assistant</h1>', 
                unsafe_allow_html=True)
    st.markdown("""
    <p style='text-align: center; color: #666; font-size: 1.1rem;'>
    Multi-Agent System powered by LangGraph | Learn, Practice, and Master Concepts
    </p>
    """, unsafe_allow_html=True)
    st.divider()


def display_sidebar():
    """Display sidebar with information and controls."""
    with st.sidebar:
        st.header("📚 About")
        st.markdown("""
        **MentorAI** is an autonomous teaching assistant that uses multiple AI agents 
        working together to help you learn effectively.
        
        ### 🤖 Active Agents:
        1. **Query Agent** - Understands your intent
        2. **Retrieval Agent** - Finds relevant content (RAG)
        3. **Teaching Agent** - Explains concepts
        4. **Quiz Agent** - Generates practice questions
        5. **Evaluation Agent** - Provides feedback
        
        ### 💡 How to Use:
        - **Learn a concept**: "Explain linear regression"
        - **Get practice**: "Give me practice problems on decision trees"
        - **Take a quiz**: "Quiz me on machine learning basics"
        - **Ask doubts**: "What's the difference between bias and variance?"
        """)
        
        st.divider()
        
        st.header("⚙️ Settings")
        difficulty = st.selectbox(
            "Preferred Difficulty",
            ["easy", "medium", "hard"],
            index=1
        )
        
        st.divider()
        
        # Display vector DB status
        vector_db_path = "vectorstore/faiss_index"
        if os.path.exists(vector_db_path):
            st.success("✅ Vector Database: Loaded")
        else:
            st.error("❌ Vector Database: Not Found")
            st.info("Run: `python vectorstore/create_db.py`")
        
        # Model status
        st.success("✅ Ollama (llama3.2:3b): Local - No API needed")
        st.info("💰 Cost: $0 - Runs completely offline!")
        
        st.divider()
        
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.session_state.current_quiz = None
            st.session_state.quiz_results = None
            st.rerun()
        
        return difficulty


def display_explanation(result: Dict[str, Any]):
    """Display the teaching explanation."""
    if result.get('explanation') and result['explanation'] != "Quiz mode activated. Proceeding to quiz generation...":
        st.subheader("📖 Explanation")
        with st.container():
            st.markdown(result['explanation'])
        
        # Display retrieved context in expander
        if result.get('context'):
            with st.expander("📚 View Retrieved Context (RAG)"):
                st.text(result['context'][:1000] + "..." if len(result['context']) > 1000 else result['context'])


def display_quiz(result: Dict[str, Any]):
    """Display generated quiz questions."""
    quiz = result.get('quiz')
    
    if quiz and len(quiz) > 0:
        st.subheader("📝 Practice Quiz")
        st.markdown("Test your understanding with these questions:")
        
        # Store quiz in session state
        st.session_state.current_quiz = quiz
        
        # Display each question
        student_answers = {}
        
        for idx, q in enumerate(quiz):
            with st.container():
                st.markdown(f"### Question {idx + 1}")
                st.markdown(f"**{q['question']}**")
                
                if q['type'] == 'multiple_choice' and q.get('options'):
                    answer = st.radio(
                        "Select your answer:",
                        q['options'],
                        key=f"q_{idx}",
                        index=None
                    )
                    if answer:
                        student_answers[idx] = answer
                else:
                    answer = st.text_area(
                        "Your answer:",
                        key=f"q_{idx}",
                        height=100
                    )
                    if answer:
                        student_answers[idx] = answer
                
                st.divider()
        
        # Submit button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("✅ Submit Answers", type="primary"):
                if student_answers:
                    with st.spinner("🤖 Evaluating your answers..."):
                        # Create new state with answers
                        eval_result = st.session_state.assistant.process_query(
                            result['query'],
                            student_answers=student_answers
                        )
                        st.session_state.quiz_results = eval_result.get('evaluation')
                    st.rerun()
                else:
                    st.warning("⚠️ Please answer at least one question before submitting.")


def display_evaluation(evaluation: Dict[str, Any]):
    """Display quiz evaluation results."""
    if not evaluation:
        return
    
    st.subheader("📊 Evaluation Results")
    
    # Overall score
    score = evaluation.get('overall_score', 0)
    correct = evaluation.get('correct_answers', 0)
    incorrect = evaluation.get('incorrect_answers', 0)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Overall Score", f"{score}%")
    with col2:
        st.metric("✅ Correct", correct)
    with col3:
        st.metric("❌ Incorrect", incorrect)
    with col4:
        if score >= 70:
            st.success("🎉 Excellent!")
        elif score >= 50:
            st.warning("👍 Good!")
        else:
            st.error("📚 Keep Practicing!")
    
    # Individual question feedback
    st.markdown("---")
    st.markdown("### Detailed Feedback")
    
    for eval_item in evaluation.get('evaluations', []):
        q_num = eval_item.get('question_number', 0)
        q_score = eval_item.get('score', 0)
        is_correct = eval_item.get('is_correct', False)
        
        # Color-coded feedback box
        if is_correct:
            icon = "✅"
            color = "green"
        else:
            icon = "❌"
            color = "red"
        
        with st.container():
            st.markdown(f"### {icon} Question {q_num} - Score: {q_score}/100")
            
            st.markdown(f"**{eval_item.get('feedback', '')}**")
            
            if eval_item.get('strengths'):
                with st.expander("💪 Strengths"):
                    for strength in eval_item.get('strengths', []):
                        st.markdown(f"- {strength}")
            
            if eval_item.get('weaknesses'):
                with st.expander("⚠️ Areas to Improve"):
                    for weakness in eval_item.get('weaknesses', []):
                        st.markdown(f"- {weakness}")
            
            if eval_item.get('improvement_tips'):
                with st.expander("💡 Improvement Tips"):
                    for tip in eval_item['improvement_tips']:
                        st.markdown(f"- {tip}")
            
            st.divider()


def display_mcq_quiz_mode():
    """Display dedicated MCQ quiz mode interface."""
    st.header("📝 MCQ Quiz Mode")
    st.markdown("Generate and take multiple-choice quizzes on any topic!")
    
    # Topic selection
    col1, col2 = st.columns([3, 1])
    with col1:
        topic = st.text_input(
            "Enter topic for quiz:",
            placeholder="e.g., Machine Learning, Neural Networks, Linear Regression",
            key="mcq_topic_input"
        )
    
    with col2:
        num_questions = st.selectbox(
            "Questions:",
            [5, 10, 15, 20],
            index=0,
            key="num_mcq_questions"
        )
    
    difficulty = st.select_slider(
        "Difficulty Level:",
        options=["easy", "medium", "hard"],
        value="medium",
        key="mcq_difficulty"
    )
    
    # Generate quiz button
    if st.button("🎯 Generate MCQ Quiz", type="primary", use_container_width=True):
        if topic:
            with st.spinner(f"🤖 Generating {num_questions} MCQ questions on {topic}..."):
                try:
                    # Generate quiz using the assistant with explicit number
                    query = f"Generate a {num_questions}-question multiple choice quiz on {topic} at {difficulty} difficulty level. Generate EXACTLY {num_questions} questions."
                    
                    # Log the request
                    st.info(f"📋 Requesting {num_questions} questions on '{topic}' ({difficulty} level)")
                    
                    result = st.session_state.assistant.process_query(query)
                    
                    # Filter only MCQ questions
                    all_questions = result.get('quiz', [])
                    mcq_questions = [q for q in all_questions if q.get('type') == 'multiple_choice' and q.get('options')]
                    
                    if mcq_questions:
                        # Warning if fewer questions than requested
                        if len(mcq_questions) < num_questions:
                            st.warning(f"⚠️ Generated {len(mcq_questions)} MCQ questions (requested {num_questions}). The AI model may need more context.")
                        
                        st.session_state.mcq_quiz = {
                            'topic': topic,
                            'difficulty': difficulty,
                            'questions': mcq_questions,
                            'query': query,
                            'requested_count': num_questions
                        }
                        st.session_state.mcq_answers = {}
                        st.session_state.mcq_results = None
                        st.success(f"✅ Generated {len(mcq_questions)} MCQ questions!")
                        st.rerun()
                    else:
                        st.warning("⚠️ No MCQ questions were generated. Try a different topic or rephrase.")
                except Exception as e:
                    st.error(f"❌ Error generating quiz: {str(e)}")
                    st.exception(e)
        else:
            st.warning("⚠️ Please enter a topic for the quiz.")
    
    # Display quiz if generated
    if st.session_state.mcq_quiz and not st.session_state.mcq_results:
        st.divider()
        quiz_data = st.session_state.mcq_quiz
        
        st.subheader(f"📚 Quiz: {quiz_data['topic']}")
        st.caption(f"Difficulty: {quiz_data['difficulty'].title()} | Questions: {len(quiz_data['questions'])}")
        
        # Display questions
        for idx, q in enumerate(quiz_data['questions']):
            with st.container():
                st.markdown(f"### Question {idx + 1}")
                st.markdown(f"**{q['question']}**")
                
                # Radio buttons for MCQ
                answer = st.radio(
                    "Select your answer:",
                    q['options'],
                    key=f"mcq_q_{idx}",
                    index=None
                )
                
                if answer:
                    st.session_state.mcq_answers[idx] = answer
                
                st.divider()
        
        # Submit button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            answered_count = len(st.session_state.mcq_answers)
            total_count = len(quiz_data['questions'])
            
            st.info(f"Answered: {answered_count}/{total_count} questions")
            
            if st.button("✅ Submit Quiz", type="primary", use_container_width=True):
                if st.session_state.mcq_answers:
                    with st.spinner("🤖 Evaluating your answers..."):
                        try:
                            # Evaluate directly using the original quiz questions
                            # Don't regenerate the quiz!
                            from agents.evaluation_agent import EvaluationAgent
                            evaluator = EvaluationAgent()
                            
                            st.session_state.mcq_results = evaluator.evaluate_quiz_directly(
                                quiz_data['questions'],
                                st.session_state.mcq_answers
                            )
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error evaluating quiz: {str(e)}")
                            logger.error(f"Evaluation error: {e}", exc_info=True)
                else:
                    st.warning("⚠️ Please answer at least one question before submitting.")
    
    # Display results if available
    if st.session_state.mcq_results:
        st.divider()
        display_evaluation(st.session_state.mcq_results)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Take Another Quiz", use_container_width=True):
                st.session_state.mcq_quiz = None
                st.session_state.mcq_answers = {}
                st.session_state.mcq_results = None
                st.rerun()
        
        with col2:
            if st.button("📊 View Correct Answers", use_container_width=True):
                st.session_state.show_answers = True
                st.rerun()
        
        # Show correct answers if requested
        if st.session_state.get('show_answers', False):
            st.markdown("---")
            st.subheader("✅ Correct Answers")
            quiz_data = st.session_state.mcq_quiz
            
            for idx, q in enumerate(quiz_data['questions']):
                with st.expander(f"Question {idx + 1}: {q['question'][:50]}..."):
                    st.markdown(f"**Question:** {q['question']}")
                    st.markdown(f"**Your Answer:** {st.session_state.mcq_answers.get(idx, 'Not answered')}")
                    st.markdown(f"**Correct Answer:** {q.get('correct_answer', 'N/A')}")
                    if q.get('explanation'):
                        st.markdown(f"**Explanation:** {q['explanation']}")


def main():
    """Main application function."""
    # Initialize
    initialize_session_state()
    
    # Check for Ollama
    logger.info("🚀 Using LOCAL Ollama model - no API keys required!")
    
    # Display UI
    display_header()
    difficulty = display_sidebar()
    
    # Create tabs for different modes
    tab1, tab2 = st.tabs(["💬 Ask Me Anything", "📝 Take MCQ Quiz"])
    
    with tab1:
        # Main content area
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.header("💬 Ask Me Anything")
            
            # Query input
            query = st.text_input(
                "What would you like to learn?",
                placeholder="e.g., Explain neural networks, Quiz me on clustering, Practice gradient descent",
                label_visibility="collapsed"
            )
            
            # Example queries
            with st.expander("💡 Example Queries"):
                examples = [
                    "What is machine learning?",
                    "Explain linear regression with examples",
                    "Give me practice problems on decision trees",
                    "Quiz me on supervised learning",
                    "What's the difference between overfitting and underfitting?",
                    "How does gradient descent work?",
                ]
                for ex in examples:
                    if st.button(ex, key=ex):
                        query = ex
        
        with col2:
            st.header("🎯 Learning Intent")
            st.markdown("""
            - **concept**: Learn new topics
            - **practice**: Work on examples
            - **quiz**: Test knowledge
            - **doubt**: Ask questions
            """)
        
        # Process query
        if query:
            with st.spinner("🤖 Multi-Agent System Processing..."):
                try:
                    # Show agent activity log
                    with st.expander("🔍 View Agent Activity Log", expanded=False):
                        log_container = st.empty()
                        
                        # Capture logs
                        import io
                        log_stream = io.StringIO()
                        handler = logging.StreamHandler(log_stream)
                        handler.setLevel(logging.INFO)
                        formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
                        handler.setFormatter(formatter)
                        
                        # Add handler
                        root_logger = logging.getLogger()
                        root_logger.addHandler(handler)
                        
                        # Process query
                        result = st.session_state.assistant.process_query(query)
                        
                        # Display logs
                        log_contents = log_stream.getvalue()
                        log_container.code(log_contents, language="log")
                        
                        # Remove handler
                        root_logger.removeHandler(handler)
                    
                    # Display results
                    st.success("✅ Processing Complete!")
                    
                    # Show detected intent and topic
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.info(f"**Intent:** {result['intent']}")
                    with col2:
                        st.info(f"**Topic:** {result['topic']}")
                    with col3:
                        st.info(f"**Difficulty:** {result['difficulty']}")
                    
                    st.divider()
                    
                    # Display explanation
                    display_explanation(result)
                    
                    # Display quiz if generated
                    if not st.session_state.quiz_results:
                        display_quiz(result)
                    
                    # Display evaluation if available
                    if st.session_state.quiz_results:
                        display_evaluation(st.session_state.quiz_results)
                        
                        if st.button("🔄 Start New Query"):
                            st.session_state.current_quiz = None
                            st.session_state.quiz_results = None
                            st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    logger.error(f"Application error: {e}", exc_info=True)
    
    with tab2:
        # MCQ Quiz Mode
        display_mcq_quiz_mode()
    
    # Footer
    st.divider()
    st.markdown("""
    <p style='text-align: center; color: #888; font-size: 0.9rem;'>
    Built with LangGraph, LangChain, Ollama, FAISS, and Streamlit | 
    100% Local Multi-Agent System - Zero API Costs 💰
    </p>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
