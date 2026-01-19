#!/usr/bin/env python3
"""
Simple setup wizard for MentorAI Teaching Assistant
Checks Ollama installation and downloads required model
"""

import os
import sys
import subprocess

def check_ollama():
    """Check if Ollama is installed."""
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def check_model():
    """Check if llama3.2:3b model is available."""
    try:
        result = subprocess.run(['ollama', 'list'], 
                              capture_output=True, text=True, timeout=5)
        return 'llama3.2:3b' in result.stdout
    except:
        return False

def pull_model():
    """Download the llama3.2:3b model."""
    print("\n📥 Downloading llama3.2:3b model (2GB)...")
    print("This may take a few minutes...\n")
    try:
        subprocess.run(['ollama', 'pull', 'llama3.2:3b'], check=True)
        return True
    except:
        return False

def main():
    print("\n" + "="*70)
    print("🤖 MentorAI: AI Teaching Assistant - Setup Wizard")
    print("="*70 + "\n")
    
    print("✅ 100% LOCAL SETUP - No API keys needed!\n")
    
    # Check Ollama installation
    print("Checking Ollama installation...")
    if not check_ollama():
        print("\n❌ Ollama not found!")
        print("\n📋 Installation Instructions:")
        print("   macOS:   brew install ollama")
        print("   Linux:   curl -fsSL https://ollama.ai/install.sh | sh")
        print("   Windows: Visit https://ollama.ai/download\n")
        sys.exit(1)
    
    print("✅ Ollama is installed!\n")
    
    # Check model
    print("Checking for llama3.2:3b model...")
    if not check_model():
        print("❌ Model not found!")
        response = input("\nDownload llama3.2:3b model (2GB)? (y/n): ").strip().lower()
        if response == 'y':
            if pull_model():
                print("\n✅ Model downloaded successfully!")
            else:
                print("\n❌ Failed to download model.")
                sys.exit(1)
        else:
            print("\n❌ Model is required. Setup cancelled.\n")
            sys.exit(1)
    else:
        print("✅ llama3.2:3b model is ready!\n")
    
    print("\n" + "="*70)
    print("✅ Setup Complete!")
    print("="*70 + "\n")
    print("💰 100% Local - No API costs!")
    print("🔒 Complete privacy - Everything runs offline\n")
    print("Next steps:")
    print("1. Create vector database:")
    print("   python vectorstore/create_db.py\n")
    print("2. Start the application:")
    print("   streamlit run app.py\n")
    print("3. Open in browser: http://localhost:8501\n")
    print("4. Try asking:")
    print("   • 'Explain supervised learning'")
    print("   • 'Give me a quiz on machine learning'\n")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled.\n")
        sys.exit(1)
