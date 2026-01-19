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

# Check for Google API key
echo "Checking Google API key..."
if [ -z "$GOOGLE_API_KEY" ]; then
    echo -e "${YELLOW}⚠ GOOGLE_API_KEY not set${NC}"
    echo ""
    echo "🆓 Google Gemini is FREE with generous limits!"
    echo "Get your API key at: https://makersuite.google.com/app/apikey"
    echo ""
    read -p "Enter your Google API key: " api_key
    export GOOGLE_API_KEY="$api_key"
    echo "export GOOGLE_API_KEY='$api_key'" >> ~/.zshrc
    echo -e "${GREEN}✓ API key configured${NC}"
else
    echo -e "${GREEN}✓ GOOGLE_API_KEY already set${NC}"
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
from langchain_google_genai import ChatGoogleGenerativeAI
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
