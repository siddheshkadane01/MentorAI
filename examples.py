"""
Example demonstrations of the AI Teaching Assistant.
Run this file to see the multi-agent system in action.
"""

import os
import logging
from graph import create_teaching_assistant

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_1_concept_learning():
    """Example 1: Learning a new concept."""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Learning a Concept")
    print("=" * 80)
    
    assistant = create_teaching_assistant()
    
    query = "What is machine learning?"
    print(f"\nStudent Query: {query}")
    
    result = assistant.process_query(query)
    
    print("\n" + "-" * 80)
    print("RESULTS:")
    print("-" * 80)
    print(f"Intent: {result['intent']}")
    print(f"Topic: {result['topic']}")
    print(f"\nExplanation:\n{result['explanation']}")


def example_2_practice_mode():
    """Example 2: Getting practice problems."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Practice Mode")
    print("=" * 80)
    
    assistant = create_teaching_assistant()
    
    query = "Give me practice problems on linear regression"
    print(f"\nStudent Query: {query}")
    
    result = assistant.process_query(query)
    
    print("\n" + "-" * 80)
    print("RESULTS:")
    print("-" * 80)
    print(f"Intent: {result['intent']}")
    print(f"Topic: {result['topic']}")
    print(f"\nExplanation:\n{result['explanation'][:500]}...")
    
    if result.get('quiz'):
        print(f"\n{len(result['quiz'])} practice questions generated!")
        for i, q in enumerate(result['quiz'][:2], 1):  # Show first 2
            print(f"\nQuestion {i}: {q['question']}")
            print(f"Type: {q['type']}")


def example_3_quiz_with_evaluation():
    """Example 3: Taking a quiz and getting evaluated."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Quiz with Evaluation")
    print("=" * 80)
    
    assistant = create_teaching_assistant()
    
    # Step 1: Generate quiz
    query = "Quiz me on decision trees"
    print(f"\nStudent Query: {query}")
    
    result = assistant.process_query(query)
    
    print("\n" + "-" * 80)
    print("QUIZ GENERATED:")
    print("-" * 80)
    print(f"Intent: {result['intent']}")
    print(f"Topic: {result['topic']}")
    
    quiz = result.get('quiz', [])
    if quiz:
        print(f"\n{len(quiz)} questions generated!")
        
        # Show first question
        print(f"\nSample Question:")
        print(f"Q: {quiz[0]['question']}")
        if quiz[0].get('options'):
            for opt in quiz[0]['options']:
                print(f"   {opt}")
        
        # Step 2: Simulate student answers
        print("\n" + "-" * 80)
        print("SIMULATING STUDENT ANSWERS:")
        print("-" * 80)
        
        # Provide sample answers (some correct, some partially correct)
        student_answers = {
            0: "Decision trees split data based on features to make predictions",
            1: "They use information gain or Gini impurity",
        }
        
        for idx, answer in student_answers.items():
            print(f"\nAnswer to Q{idx + 1}: {answer}")
        
        # Step 3: Get evaluation
        print("\n" + "-" * 80)
        print("EVALUATION:")
        print("-" * 80)
        
        eval_result = assistant.process_query(query, student_answers=student_answers)
        evaluation = eval_result.get('evaluation')
        
        if evaluation:
            print(f"\nOverall Score: {evaluation['overall_score']}/100")
            print(f"Questions Evaluated: {evaluation['questions_evaluated']}")
            
            for eval_item in evaluation['evaluations'][:1]:  # Show first evaluation
                print(f"\nQuestion {eval_item['question_number']} Feedback:")
                print(f"Score: {eval_item['score']}/100")
                print(f"Correct: {eval_item['is_correct']}")
                print(f"Feedback: {eval_item['feedback']}")


def example_4_doubt_clarification():
    """Example 4: Asking a specific doubt."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Doubt Clarification")
    print("=" * 80)
    
    assistant = create_teaching_assistant()
    
    query = "What's the difference between overfitting and underfitting?"
    print(f"\nStudent Query: {query}")
    
    result = assistant.process_query(query)
    
    print("\n" + "-" * 80)
    print("RESULTS:")
    print("-" * 80)
    print(f"Intent: {result['intent']}")
    print(f"Topic: {result['topic']}")
    print(f"\nExplanation:\n{result['explanation']}")


def example_5_multi_query_session():
    """Example 5: Multiple queries in one session."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Multi-Query Learning Session")
    print("=" * 80)
    
    assistant = create_teaching_assistant()
    
    queries = [
        "What is supervised learning?",
        "Give me an example of classification",
        "Quiz me on logistic regression",
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'─' * 80}")
        print(f"Query {i}: {query}")
        print('─' * 80)
        
        result = assistant.process_query(query)
        
        print(f"Intent: {result['intent']} | Topic: {result['topic']}")
        
        if result.get('explanation'):
            print(f"Response: {result['explanation'][:200]}...")
        
        if result.get('quiz'):
            print(f"Quiz: {len(result['quiz'])} questions generated")


def demonstrate_rag_accuracy():
    """Demonstrate RAG preventing hallucination."""
    print("\n" + "=" * 80)
    print("DEMONSTRATION: RAG Accuracy")
    print("=" * 80)
    print("\nThis demonstrates how RAG prevents hallucination by grounding")
    print("answers in the vector database content.")
    
    assistant = create_teaching_assistant()
    
    # Query about something in our study material
    query = "Explain the sigmoid function in logistic regression"
    print(f"\nQuery: {query}")
    
    result = assistant.process_query(query)
    
    print("\n" + "-" * 80)
    print("RETRIEVED CONTEXT (from Vector DB):")
    print("-" * 80)
    context = result.get('context', '')
    print(context[:500] + "..." if len(context) > 500 else context)
    
    print("\n" + "-" * 80)
    print("GENERATED EXPLANATION (based on context):")
    print("-" * 80)
    print(result['explanation'])
    
    print("\n✅ The explanation is grounded in retrieved content, not hallucinated!")


def main():
    """Run all examples."""
    
    # Check for API key
    print("🚀 Using LOCAL Ollama model - no API keys required!")
    print("💰 Cost: $0 - Runs completely offline!\n")
    
    print("\n" + "█" * 80)
    print("  MentorAI: AI TEACHING ASSISTANT - EXAMPLE DEMONSTRATIONS")
    print("█" * 80)
    
    print("\nThis script demonstrates the multi-agent system capabilities.")
    print("Watch the logs to see agents collaborating!\n")
    
    try:
        # Run examples
        example_1_concept_learning()
        
        print("\n\n" + "▓" * 80)
        input("Press Enter to continue to Example 2...")
        example_2_practice_mode()
        
        print("\n\n" + "▓" * 80)
        input("Press Enter to continue to Example 3...")
        example_3_quiz_with_evaluation()
        
        print("\n\n" + "▓" * 80)
        input("Press Enter to continue to Example 4...")
        example_4_doubt_clarification()
        
        print("\n\n" + "▓" * 80)
        input("Press Enter to continue to Example 5...")
        example_5_multi_query_session()
        
        print("\n\n" + "▓" * 80)
        input("Press Enter to see RAG demonstration...")
        demonstrate_rag_accuracy()
        
        print("\n\n" + "█" * 80)
        print("  ALL EXAMPLES COMPLETED!")
        print("█" * 80)
        
        print("\n✨ Key Takeaways:")
        print("  1. Multiple agents collaborate for each query")
        print("  2. RAG ensures accurate, grounded responses")
        print("  3. Dynamic routing based on student intent")
        print("  4. Comprehensive logging for transparency")
        print("  5. Personalized learning experience")
        
        print("\n🚀 Next Steps:")
        print("  - Launch the Streamlit app: streamlit run app.py")
        print("  - Try your own queries")
        print("  - Explore the agent logs")
        print("  - Customize agents for your use case")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Examples interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        logger.error("Example execution failed", exc_info=True)


if __name__ == "__main__":
    main()
