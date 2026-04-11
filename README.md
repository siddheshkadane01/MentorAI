# MentorAI: Autonomous AI Teaching Assistant

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-green)](https://github.com/langchain-ai/langgraph)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.39-red)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**A production-ready multi-agent AI teaching assistant using LangGraph, LangChain, and RAG (Retrieval-Augmented Generation). Features 5 specialized agents orchestrated for personalized learning experiences.**

## ✨ Key Features

- 🤖 **Multi-Agent Architecture** - 5 specialized agents working collaboratively
- 🔄 **LangGraph Orchestration** - Dynamic workflow routing based on student intent
- 📚 **RAG Implementation** - Vector database for accurate, context-aware responses
- 🎓 **Adaptive Learning** - Personalized explanations, quizzes, and feedback
- 📊 **Real-time Logging** - Complete visibility into agent decisions
- 💻 **Interactive UI** - Clean Streamlit interface
- 💰 **100% Local & Free** - Runs completely offline with Ollama (no API costs)
- 🔌 **No Internet Required** - All processing happens on your machine
- 🔐 **Role-Based Access** - Student signup/login and admin login
- 📈 **Admin Analytics Dashboard** - Accuracy, score, topic trends, question-fit, latency, and hallucination indicators
- 🗄️ **Persistent Metrics** - Quiz attempts and interaction telemetry stored in SQLite/PostgreSQL-compatible schema

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Ollama installed ([ollama.ai](https://ollama.ai))
- 8GB RAM minimum (16GB recommended)

### Installation

```bash
# Clone repository
git clone https://github.com/siddheshkadane01/MentorAI.git
cd MentorAI

# Install Ollama (if not installed)
brew install ollama  # macOS
# or visit https://ollama.ai for other platforms

# Download LLM model
ollama pull llama3.2:3b

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: configure backend env vars
export JWT_SECRET="replace-with-strong-secret"
export ADMIN_USERNAME="admin"
export ADMIN_PASSWORD="admin123"

# Create vector database
python vectorstore/create_db.py

# Start backend API (in terminal 1)
uvicorn backend.main:app --reload --port 8000

# Run Streamlit application (in terminal 2)
streamlit run app.py
```

Open **http://localhost:8501** and try:
- "Explain supervised learning"
- "Give me a quiz on machine learning"
- "What's gradient descent?"

### Role-Based Access

- Student: Sign up from the Streamlit login screen, then use Ask mode and MCQ quiz mode.
- Admin: Log in using seeded admin credentials to view dashboard analytics.

### Admin Dashboard Metrics

- Quiz accuracy and overall score
- Precision, recall, and F1 (attempt-level proxy)
- Topic-wise performance
- Question-fit by difficulty vs success rate
- Per-student trend summary
- Average latency and hallucination indicators

## 🏗️ Architecture

### Agent Workflow

```
Student Query → Query Agent (intent classification)
                     ↓
              Retrieval Agent (RAG search)
                     ↓
        ┌────────────┴────────────┐
        ↓                         ↓
  Teaching Agent            Quiz Agent
  (explanations)           (questions)
        ↓                         ↓
        └────────────┬────────────┘
                     ↓
            Evaluation Agent
            (feedback & scoring)
```

### Agent Responsibilities

| Agent | Purpose | Model |
|-------|---------|-------|
| **Query Agent** | Classifies intent (concept/practice/quiz/doubt) | Ollama (llama3.2:3b) |
| **Retrieval Agent** | Semantic search using FAISS + local embeddings | Sentence Transformers |
| **Teaching Agent** | Generates explanations with examples | Ollama (llama3.2:3b) |
| **Quiz Agent** | Creates adaptive practice questions | Ollama (llama3.2:3b) |
| **Evaluation Agent** | Scores answers and provides feedback | Ollama (llama3.2:3b) |

## 📂 Project Structure

```
agent1-teaching-assistant/
├── agents/                  # Specialized AI agents
│   ├── query_agent.py      # Intent classification
│   ├── retrieval_agent.py  # RAG implementation
│   ├── teaching_agent.py   # Explanation generation
│   ├── quiz_agent.py       # Quiz creation
│   └── evaluation_agent.py # Answer evaluation
├── vectorstore/            # Vector database
│   ├── create_db.py       # Database creation script
│   └── faiss_index/       # FAISS vector store (generated)
├── data/                   # Study materials
│   └── sample_notes.txt   # Sample ML notes
├── app.py                  # Streamlit frontend
├── graph.py                # LangGraph orchestration
├── config.py               # Configuration settings
├── requirements.txt        # Dependencies
├── .env.example           # Environment template
└── README.md              # This file
```

## 💡 Usage Examples

### Concept Learning
```
User: "Explain supervised learning"
→ Query Agent: Detects "concept" intent
→ Retrieval Agent: Fetches relevant content
→ Teaching Agent: Generates clear explanation with examples
```

### Quiz Practice
```
User: "Give me a quiz on neural networks"
→ Query Agent: Detects "quiz" intent  
→ Retrieval Agent: Gets context
→ Quiz Agent: Creates 5 questions
→ Evaluation Agent: Scores answers and provides feedback
```

### Doubt Clarification
```
User: "What's the difference between bagging and boosting?"
→ Query Agent: Detects "doubt" intent
→ Retrieval Agent: Searches knowledge base
→ Teaching Agent: Explains the differences
```

## 🔧 Configuration

Edit `config.py` to customize:
- Model selection (default: `llama3.2:3b`)
- Temperature settings for each agent
- Chunk size for RAG
- Number of quiz questions
- Retrieval K value

## 📊 Tech Stack

- **Orchestration**: LangGraph 0.2.45
- **Framework**: LangChain 0.3.7
- **Chat Model**: Ollama (llama3.2:3b) - 100% Local
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2) - Local
- **Vector DB**: FAISS 1.8.0 - Local Storage
- **Frontend**: Streamlit 1.39.0
- **Backend API**: FastAPI + Uvicorn
- **Database**: SQLAlchemy ORM (SQLite default)
- **Auth**: JWT + bcrypt password hashing
- **Python**: 3.8+
- **Cost**: $0 - Everything runs locally!

## 🎯 Why Multi-Agent?

| Aspect | Single LLM | Multi-Agent System |
|--------|-----------|-------------------|
| **Specialization** | General purpose | Each agent optimized for specific tasks |
| **Accuracy** | Prone to hallucination | RAG ensures factual responses |
| **Workflow** | Monolithic | Dynamic routing based on intent |
| **Debugging** | Black box | Clear agent-level logging |
| **Scalability** | Limited | Easy to add/modify agents |
| **Scalability** | Hard to extend | Easy to add/modify agents |
| **Context Management** | Limited context window | Shared state across specialized agents |

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph) for multi-agent orchestration
- Powered by [Ollama](https://ollama.ai/) for local LLM execution
- Uses [Sentence Transformers](https://www.sbert.net/) for local embeddings
- UI built with [Streamlit](https://streamlit.io/)

## 📬 Contact

For questions or feedback, please open an issue on GitHub.

---

**Made with ❤️ using LangGraph, LangChain, Ollama, and Streamlit | 100% Local & Free**


### Step 1: Clone and Navigate

```bash
cd agent1-teaching-assistant
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install and Setup Ollama

```bash
# Install Ollama (macOS)
brew install ollama

# For other platforms, visit: https://ollama.ai

# Download the LLM model
ollama pull llama3.2:3b
```

### Step 5: Create Vector Database

```bash
python vectorstore/create_db.py
```

Expected output:
```
============================================================
Starting Vector Database Creation
============================================================
Loading documents from: data/sample_notes.txt
Loaded 1 document(s)
Splitting documents (chunk_size=1000, overlap=200)
Created 45 text chunks
✅ LOCAL EMBEDDINGS: Using Sentence Transformers (no API needed!)
Creating FAISS vector store...
Saving vector store to: vectorstore/faiss_index
============================================================
Vector Database Created Successfully!
Location: vectorstore/faiss_index
Total chunks indexed: 45
============================================================
```

### Step 6: Launch Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 💡 Usage Examples

### Example 1: Learning a Concept

**Query:** "What is machine learning?"

**Agent Flow:**
1. ✅ Query Agent → Detects intent: `concept`, topic: `machine learning`
2. ✅ Retrieval Agent → Searches vector DB, retrieves relevant chunks
3. ✅ Teaching Agent → Generates comprehensive explanation with examples

**Output:** Detailed explanation of machine learning with types and applications

---

### Example 2: Practice Mode

**Query:** "Give me practice problems on linear regression"

**Agent Flow:**
1. ✅ Query Agent → Detects intent: `practice`, topic: `linear regression`
2. ✅ Retrieval Agent → Retrieves linear regression content
3. ✅ Teaching Agent → Provides worked examples
4. ✅ Quiz Agent → Generates practice questions

**Output:** Practice problems with step-by-step solutions

---

### Example 3: Quiz Mode

**Query:** "Quiz me on decision trees"

**Agent Flow:**
1. ✅ Query Agent → Detects intent: `quiz`, topic: `decision trees`
2. ✅ Retrieval Agent → Retrieves decision tree content
3. ✅ Quiz Agent → Generates 5 questions (multiple choice + short answer)
4. ✅ Evaluation Agent → (After student submits) Scores answers and provides feedback

**Output:** 
- 5 adaptive questions
- Detailed evaluation with scores
- Strengths and improvement suggestions

---

### Example 4: Asking Doubts

**Query:** "What's the difference between overfitting and underfitting?"

**Agent Flow:**
1. ✅ Query Agent → Detects intent: `doubt`, topic: `overfitting vs underfitting`
2. ✅ Retrieval Agent → Retrieves relevant explanations
3. ✅ Teaching Agent → Provides focused comparison

**Output:** Clear comparison with examples and solutions

## 🔍 Agent Collaboration Example

**Query:** "I want to practice gradient descent"

### Detailed Agent Log:

```
======================================================================
STEP 1: Query Understanding Agent
======================================================================
[QUERY AGENT] Analyzing query: I want to practice gradient descent...
[QUERY AGENT] Detected - Intent: practice, Topic: gradient descent, Difficulty: medium

======================================================================
STEP 2: Retrieval Agent (RAG)
======================================================================
[RETRIEVAL AGENT] Retrieving top-3 documents for: gradient descent...
[RETRIEVAL AGENT] Retrieved 3 relevant chunks

======================================================================
STEP 3: Teaching Agent
======================================================================
[TEACHING AGENT] Generating explanation for intent: practice, difficulty: medium
[TEACHING AGENT] Generated explanation (1247 chars)

======================================================================
STEP 4: Quiz Generation Agent
======================================================================
[QUIZ AGENT] Generating 5 medium questions on: gradient descent
[QUIZ AGENT] Successfully generated 5 questions

======================================================================
WORKFLOW COMPLETED
======================================================================
```

### Why This is Better Than Single LLM:

1. **No Hallucination**: Retrieval Agent ensures facts come from vector DB
2. **Intent-Driven**: Query Agent routes to appropriate workflow
3. **Optimized Prompts**: Each agent has specialized prompts
4. **Transparency**: Complete visibility into decision-making
5. **Modularity**: Easy to improve individual agents

## 🛠️ Customization

### Adding Your Own Study Material

1. Add `.txt` files to `data/` directory
2. Rebuild vector database:
   ```bash
   python vectorstore/create_db.py
   ```

### Adjusting Agent Behavior

Edit agent files in `agents/` directory:
- **Temperature**: Control creativity (0.0 = deterministic, 1.0 = creative)
- **Prompts**: Customize system messages
- **Models**: Switch between GPT-4, GPT-3.5, etc.

### Modifying Workflow

Edit `graph.py` to change:
- Agent execution order
- Conditional routing logic
- State management

## 📊 Performance Optimization

### Vector Database

- **Chunk Size**: Adjust `chunk_size` in `create_db.py` (default: 1000)
- **Overlap**: Modify `chunk_overlap` for better context (default: 200)
- **Top-k**: Change number of retrieved documents in `retrieval_agent.py`

### Cost Optimization

```python
# Use faster, cheaper models for less critical agents:
QueryAgent(model_name="gpt-3.5-turbo")  # Query understanding
TeachingAgent(model_name="gpt-4o-mini")  # Explanations
```

## 🐛 Troubleshooting

### Vector Database Not Found

**Error:** `Vector database not found at vectorstore/faiss_index`

**Solution:**
```bash
python vectorstore/create_db.py
```

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'langgraph'`

**Solution:**
```bash
pip install -r requirements.txt
```

## 🧪 Testing

### Test Individual Agents

```bash
# Test query agent
python -c "from agents.query_agent import QueryAgent; agent = QueryAgent(); print(agent.analyze_query('What is ML?'))"

# Test vector database
python vectorstore/create_db.py
```

### Test Complete Workflow

```bash
python graph.py
```

## 📈 Future Enhancements

- [ ] Memory across conversations
- [ ] Multi-modal support (images, diagrams)
- [ ] Progress tracking dashboard
- [ ] Personalized learning paths
- [ ] Support for multiple students
- [ ] Integration with educational platforms
- [ ] Voice interaction
- [ ] Mobile app

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

1. Additional agent types (summarization, translation, etc.)
2. Support for more vector databases (Pinecone, Weaviate)
3. Advanced evaluation metrics
4. Gamification features
5. Multi-language support

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **LangGraph**: For powerful agent orchestration
- **LangChain**: For LLM application framework
- **Ollama**: For local LLM execution
- **FAISS**: For efficient vector similarity search
- **Streamlit**: For rapid UI development

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ using Multi-Agent Agentic Workflows**

*Demonstrating the power of specialized AI agents working in harmony*
