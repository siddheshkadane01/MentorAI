#!/bin/bash

# MentorAI Setup Script
# Automates the setup process for the AI Teaching Assistant

set -e  # Exit on error

echo "=========================================="
echo "MentorAI: AI Teaching Assistant Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '(?<=Python )\d+\.\d+')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}Error: Python 3.8 or higher is required${NC}"
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi
echo -e "${GREEN}✓ Python version OK: $PYTHON_VERSION${NC}"
echo ""

# Check for Ollama installation
echo "Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓ Ollama is installed${NC}"
    
    # Check if model is downloaded
    if ollama list | grep -q "llama3.2:3b"; then
        echo -e "${GREEN}✓ llama3.2:3b model is already downloaded${NC}"
    else
        echo -e "${YELLOW}⚠ llama3.2:3b model not found${NC}"
        echo "Downloading model (this may take a few minutes)..."
        ollama pull llama3.2:3b
        echo -e "${GREEN}✓ Model downloaded${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Ollama not installed${NC}"
    echo ""
    echo "💻 Ollama is required for 100% local operation"
    echo "Install it with: brew install ollama"
    echo "Or visit: https://ollama.ai"
    echo ""
    read -p "Do you want to continue without Ollama? (y/n): " continue_setup
    if [ "$continue_setup" != "y" ]; then
        echo "Setup cancelled. Please install Ollama first."
        exit 1
    fi
fi
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Create vector database
echo "Creating vector database..."
if [ ! -d "vectorstore/faiss_index" ]; then
    python vectorstore/create_db.py
    echo -e "${GREEN}✓ Vector database created${NC}"
else
    echo -e "${YELLOW}Vector database already exists${NC}"
    read -p "Rebuild vector database? (y/n): " rebuild
    if [ "$rebuild" = "y" ]; then
        python vectorstore/create_db.py
        echo -e "${GREEN}✓ Vector database rebuilt${NC}"
    fi
fi
echo ""

# Test import
echo "Testing installation..."
python -c "
import streamlit
import langchain
import langgraph
from langchain_ollama import ChatOllama
print('All imports successful!')
" 2>&1 && echo -e "${GREEN}✓ Installation test passed${NC}" || echo -e "${RED}✗ Installation test failed${NC}"
echo ""

echo "=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "To start the application:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run: streamlit run app.py"
echo ""
echo "The app will open at: http://localhost:8501"
echo ""
