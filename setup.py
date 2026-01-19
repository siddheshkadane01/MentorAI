#!/usr/bin/env python3
"""
Simple setup wizard for MentorAI Teaching Assistant
Configures the Google Gemini API key
"""

import os
import sys

def main():
    print("\n" + "="*70)
    print("🤖 MentorAI: AI Teaching Assistant - Setup Wizard")
    print("="*70 + "\n")
    
    # Check current .env file
    env_path = ".env"
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            content = f.read()
            if 'GOOGLE_API_KEY=' in content and 'your_google_api_key_here' not in content:
                # Extract the key
                for line in content.split('\n'):
                    if line.startswith('GOOGLE_API_KEY=') and not line.endswith('your_google_api_key_here'):
                        print("✅ API key already configured!\n")
                        print("To start the application, run:")
                        print("   streamlit run app.py\n")
                        return
    
    print("📋 SETUP STEPS:\n")
    print("1. Get your FREE Google Gemini API key:")
    print("   👉 Visit: https://aistudio.google.com/app/apikey")
    print("   👉 Sign in with your Google account")
    print("   👉 Click 'Create API Key'")
    print("   👉 Copy the key (starts with 'AIza...')\n")
    
    print("2. Paste your API key below:\n")
    
    api_key = input("Enter your Google API Key: ").strip()
    
    if not api_key:
        print("\n❌ No API key entered. Run setup again when you have your key.\n")
        sys.exit(1)
    
    if api_key == "your_google_api_key_here":
        print("\n❌ Please enter your actual API key, not the placeholder.\n")
        sys.exit(1)
    
    # Validate format
    if not api_key.startswith('AIza'):
        print("\n⚠️  Warning: API key doesn't start with 'AIza'. Make sure it's correct.")
        confirm = input("Continue anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            print("\n❌ Setup cancelled.\n")
            sys.exit(1)
    
    # Write to .env
    with open(env_path, 'w') as f:
        f.write("# Google Gemini API Key (FREE TIER)\n")
        f.write("# Get your key from: https://aistudio.google.com/app/apikey\n\n")
        f.write(f"GOOGLE_API_KEY={api_key}\n")
    
    print("\n" + "="*70)
    print("✅ Setup Complete!")
    print("="*70 + "\n")
    print("Your API key has been saved to .env\n")
    print("Next steps:")
    print("1. Start the application:")
    print("   streamlit run app.py\n")
    print("2. Open in browser: http://localhost:8501\n")
    print("3. Try asking:")
    print("   • 'Explain supervised learning'")
    print("   • 'Give me a quiz on machine learning'\n")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled.\n")
        sys.exit(1)
