"""
Streamlit Frontend for AI Teaching Assistant
Interactive UI for student-agent interaction.
"""

import streamlit as st
import os
import sys
import logging
import time
from typing import Dict, Any, Optional

import requests
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from graph import create_teaching_assistant
from config import config

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
        st.session_state.assistant = None
    
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

    if 'access_token' not in st.session_state:
        st.session_state.access_token = None

    if 'user_role' not in st.session_state:
        st.session_state.user_role = None

    if 'username' not in st.session_state:
        st.session_state.username = None

    if 'user_id' not in st.session_state:
        st.session_state.user_id = None

    if 'latest_interaction_latency_ms' not in st.session_state:
        st.session_state.latest_interaction_latency_ms = 0.0

    if 'latest_hallucination_score' not in st.session_state:
        st.session_state.latest_hallucination_score = 0.0

    if 'latest_query_meta' not in st.session_state:
        st.session_state.latest_query_meta = {}


def get_assistant():
    """Initialize and return the assistant only when needed."""
    if st.session_state.assistant is None:
        with st.spinner("🤖 Initializing AI Teaching Assistant..."):
            st.session_state.assistant = create_teaching_assistant()
    return st.session_state.assistant


def get_auth_headers() -> Dict[str, str]:
    """Build auth headers from current session token."""
    token = st.session_state.get('access_token')
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def api_post(endpoint: str, payload: Dict[str, Any], use_auth: bool = False) -> Optional[Dict[str, Any]]:
    """POST helper for backend API."""
    url = f"{config.BACKEND_BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if use_auth:
        headers.update(get_auth_headers())

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=20)
        if resp.status_code >= 400:
            detail = resp.json().get("detail", resp.text) if resp.text else "Request failed"
            st.error(f"API error: {detail}")
            return None
        return resp.json() if resp.text else {}
    except requests.RequestException:
        st.error("Backend service is unreachable. Start FastAPI server first.")
        return None


def api_get(endpoint: str, use_auth: bool = False) -> Optional[Dict[str, Any]]:
    """GET helper for backend API."""
    url = f"{config.BACKEND_BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if use_auth:
        headers.update(get_auth_headers())

    try:
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code >= 400:
            detail = resp.json().get("detail", resp.text) if resp.text else "Request failed"
            st.error(f"API error: {detail}")
            return None
        return resp.json() if resp.text else {}
    except requests.RequestException:
        st.error("Backend service is unreachable. Start FastAPI server first.")
        return None


def logout_user():
    """Clear auth state and reset role-scoped session values."""
    st.session_state.access_token = None
    st.session_state.user_role = None
    st.session_state.username = None
    st.session_state.user_id = None
    st.session_state.mcq_quiz = None
    st.session_state.mcq_answers = {}
    st.session_state.mcq_results = None
    st.session_state.current_quiz = None
    st.session_state.quiz_results = None
    st.rerun()


def estimate_hallucination_score(response_text: str, context: str) -> float:
    """A lightweight proxy based on lexical overlap with retrieved context."""
    response_terms = {w.lower() for w in response_text.split() if len(w) > 3}
    context_terms = {w.lower() for w in context.split() if len(w) > 3}
    if not response_terms:
        return 0.0

    overlap = len(response_terms.intersection(context_terms)) / max(1, len(response_terms))
    score = max(0.0, min(1.0, 1.0 - overlap))
    return round(score, 3)


def classify_topic(topic: str, fallback_query: str) -> str:
    """Choose a topic string for telemetry."""
    if topic:
        return topic
    return fallback_query[:80]


def render_auth_screen() -> bool:
    """Render login/signup UI. Returns True when authenticated."""
    if st.session_state.get('access_token'):
        return True

    st.title("MentorAI Access")
    st.markdown("Use student signup/login or admin login to continue.")

    tab_login, tab_signup = st.tabs(["Login", "Student Signup"])

    with tab_login:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", type="primary", key="login_button"):
            payload = {"username": username, "password": password}
            response = api_post("/auth/login", payload)
            if response:
                st.session_state.access_token = response.get("access_token")
                st.session_state.user_role = response.get("role")
                st.session_state.username = response.get("username")
                st.session_state.user_id = response.get("user_id")
                st.success("Login successful")
                st.rerun()

    with tab_signup:
        full_name = st.text_input("Full Name", key="signup_name")
        username = st.text_input("Choose Username", key="signup_username")
        password = st.text_input("Choose Password", type="password", key="signup_password")
        if st.button("Create Student Account", key="signup_button"):
            payload = {
                "full_name": full_name,
                "username": username,
                "password": password,
            }
            response = api_post("/auth/signup", payload)
            if response:
                st.success("Signup complete. Please log in using your student credentials.")

    st.info("Default admin credentials are set using ADMIN_USERNAME and ADMIN_PASSWORD environment variables.")
    return False


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


def display_sidebar(role: str):
    """Display sidebar with information and controls."""
    with st.sidebar:
        st.success(f"Signed in as: {st.session_state.get('username')} ({role})")
        if st.button("Logout"):
            logout_user()

        st.divider()
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
        
        difficulty = "medium"
        if role == "student":
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
                        eval_start = time.perf_counter()
                        # Create new state with answers
                        eval_result = get_assistant().process_query(
                            result['query'],
                            student_answers=student_answers
                        )
                        st.session_state.quiz_results = eval_result.get('evaluation')

                        evaluation_latency_ms = (time.perf_counter() - eval_start) * 1000.0
                        meta = st.session_state.get("latest_query_meta", {})
                        quiz_questions = st.session_state.get("current_quiz") or []
                        if st.session_state.quiz_results and quiz_questions:
                            payload = build_attempt_payload(
                                topic=meta.get("topic") or "General",
                                difficulty=meta.get("difficulty") or "medium",
                                query_text=meta.get("query") or result.get("query") or "",
                                evaluation=st.session_state.quiz_results,
                                quiz_questions=quiz_questions,
                                student_answers=student_answers,
                                generation_latency_ms=float(meta.get("generation_latency_ms", 0.0)),
                                evaluation_latency_ms=evaluation_latency_ms,
                                hallucination_score=float(st.session_state.get("latest_hallucination_score", 0.0)),
                            )
                            persist_quiz_attempt(payload)
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


def build_attempt_payload(
    topic: str,
    difficulty: str,
    query_text: str,
    evaluation: Dict[str, Any],
    quiz_questions: list,
    student_answers: Dict[int, str],
    generation_latency_ms: float,
    evaluation_latency_ms: float,
    hallucination_score: float,
) -> Dict[str, Any]:
    """Convert local quiz result to backend payload schema."""
    correct = int(evaluation.get("correct_answers", 0))
    incorrect = int(evaluation.get("incorrect_answers", 0))
    total = max(1, int(evaluation.get("questions_evaluated", correct + incorrect)))

    accuracy = round((correct / total) * 100.0, 2)
    precision = round(correct / max(1, correct + incorrect), 4)
    recall = precision
    f1_score = precision

    question_rows = []
    for idx, eval_item in enumerate(evaluation.get("evaluations", [])):
        q_idx = int(eval_item.get("question_number", idx + 1)) - 1
        question = quiz_questions[q_idx] if 0 <= q_idx < len(quiz_questions) else {}
        question_rows.append(
            {
                "question_number": int(eval_item.get("question_number", idx + 1)),
                "question_text": question.get("question"),
                "question_type": question.get("type", "multiple_choice"),
                "difficulty": difficulty,
                "student_answer": student_answers.get(q_idx),
                "correct_answer": question.get("correct_answer"),
                "is_correct": bool(eval_item.get("is_correct", False)),
                "score": float(eval_item.get("score", 0.0)),
                "feedback": eval_item.get("feedback"),
            }
        )

    total_latency = round(generation_latency_ms + evaluation_latency_ms, 2)
    return {
        "topic": topic,
        "difficulty": difficulty,
        "query_text": query_text,
        "overall_score": float(evaluation.get("overall_score", 0.0)),
        "correct_answers": correct,
        "incorrect_answers": incorrect,
        "total_questions": total,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "latency_ms": total_latency,
        "generation_latency_ms": round(generation_latency_ms, 2),
        "evaluation_latency_ms": round(evaluation_latency_ms, 2),
        "hallucination_score": hallucination_score,
        "hallucination_flag": hallucination_score > 0.6,
        "evaluations": question_rows,
    }


def persist_interaction(topic: str, query_text: str, response_text: str, context_text: str, latency_ms: float):
    """Push query-level telemetry for student analytics."""
    if st.session_state.get("user_role") != "student" or not st.session_state.get("access_token"):
        return

    hall_score = estimate_hallucination_score(response_text or "", context_text or "")
    st.session_state.latest_hallucination_score = hall_score
    st.session_state.latest_interaction_latency_ms = latency_ms

    api_post(
        "/student/interactions",
        {
            "interaction_type": "query",
            "topic": topic,
            "query_text": query_text,
            "response_text": (response_text or "")[:2000],
            "response_latency_ms": round(latency_ms, 2),
            "retrieval_context_length": len(context_text or ""),
            "hallucination_score": hall_score,
        },
        use_auth=True,
    )


def persist_quiz_attempt(payload: Dict[str, Any]):
    """Push quiz attempt metrics to backend."""
    if st.session_state.get("user_role") != "student" or not st.session_state.get("access_token"):
        return
    api_post("/student/attempts", payload, use_auth=True)


def display_admin_dashboard():
    """Render role-gated admin analytics dashboard."""
    st.header("Admin Analytics Dashboard")
    data = api_get("/admin/dashboard", use_auth=True)
    if not data:
        st.warning("No dashboard data available yet.")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Students", data.get("total_students", 0))
    c2.metric("Quiz Attempts", data.get("total_attempts", 0))
    c3.metric("Avg Accuracy", f"{data.get('avg_accuracy', 0)}%")
    c4.metric("Avg Score", f"{data.get('avg_score', 0)}%")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Avg Precision", data.get("avg_precision", 0))
    c6.metric("Avg Recall", data.get("avg_recall", 0))
    c7.metric("Avg F1", data.get("avg_f1_score", 0))
    c8.metric("Avg Latency", f"{data.get('avg_latency_ms', 0)} ms")

    c9, c10 = st.columns(2)
    c9.metric("Hallucination Score", data.get("avg_hallucination_score", 0))
    c10.metric("Hallucination Rate", f"{data.get('hallucination_rate', 0)}%")

    st.subheader("Topic-wise Performance")
    topic_metrics = data.get("topic_metrics", [])
    if topic_metrics:
        st.dataframe(topic_metrics, use_container_width=True)
        chart_data = {row["topic"]: row["avg_accuracy"] for row in topic_metrics}
        st.bar_chart(chart_data)
    else:
        st.info("No topic metrics yet.")

    st.subheader("Question Fit by Difficulty")
    fit_metrics = data.get("question_fit_metrics", [])
    if fit_metrics:
        st.dataframe(fit_metrics, use_container_width=True)
    else:
        st.info("No question-fit data yet.")

    st.subheader("Student Trends")
    student_trends = data.get("student_trends", [])
    if student_trends:
        st.dataframe(student_trends, use_container_width=True)
    else:
        st.info("No student trend data yet.")


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
                    
                    generation_start = time.perf_counter()
                    result = get_assistant().process_query(query)
                    generation_latency_ms = (time.perf_counter() - generation_start) * 1000.0
                    
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
                            'requested_count': num_questions,
                            'generation_latency_ms': generation_latency_ms,
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
                            
                            eval_start = time.perf_counter()
                            st.session_state.mcq_results = evaluator.evaluate_quiz_directly(
                                quiz_data['questions'],
                                st.session_state.mcq_answers
                            )

                            evaluation_latency_ms = (time.perf_counter() - eval_start) * 1000.0
                            hallucination_score = st.session_state.get("latest_hallucination_score", 0.0)
                            payload = build_attempt_payload(
                                topic=quiz_data.get('topic') or 'General',
                                difficulty=quiz_data.get('difficulty') or 'medium',
                                query_text=quiz_data.get('query') or '',
                                evaluation=st.session_state.mcq_results,
                                quiz_questions=quiz_data.get('questions', []),
                                student_answers=st.session_state.mcq_answers,
                                generation_latency_ms=float(quiz_data.get('generation_latency_ms', 0.0)),
                                evaluation_latency_ms=evaluation_latency_ms,
                                hallucination_score=hallucination_score,
                            )
                            persist_quiz_attempt(payload)
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

    if not render_auth_screen():
        return

    role = st.session_state.get("user_role", "student")
    
    # Check for Ollama
    logger.info("🚀 Using LOCAL Ollama model - no API keys required!")
    
    # Display UI
    display_header()
    difficulty = display_sidebar(role)

    if role == "admin":
        display_admin_dashboard()
        st.divider()
        st.caption("Admin view: role-based analytics for student performance and model behavior.")
        return
    
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
                        run_start = time.perf_counter()
                        result = get_assistant().process_query(query)
                        run_latency_ms = (time.perf_counter() - run_start) * 1000.0

                        st.session_state.latest_query_meta = {
                            "query": query,
                            "topic": classify_topic(result.get('topic', ''), query),
                            "difficulty": result.get("difficulty", "medium"),
                            "generation_latency_ms": run_latency_ms,
                        }

                        persist_interaction(
                            topic=classify_topic(result.get('topic', ''), query),
                            query_text=query,
                            response_text=result.get('explanation', ''),
                            context_text=result.get('context', ''),
                            latency_ms=run_latency_ms,
                        )
                        
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
