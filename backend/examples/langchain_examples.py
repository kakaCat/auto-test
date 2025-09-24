"""LangChain examples demonstrating the usage of chains and agents."""

import asyncio
import os
from typing import List, Dict, Any

# Set up the path to import from src
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from langchain_langgraph_project.agents import ResearchAgent, ChatAgent
from langchain_langgraph_project.chains import QAChain, SummarizationChain
from langchain_langgraph_project.utils import setup_logger

# Set up logging
logger = setup_logger(__name__)


def setup_environment():
    """Set up environment variables for the examples."""
    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("Warning: OPENAI_API_KEY environment variable not set.")
        print("Please set it before running the examples:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return False
    return True


async def research_agent_example():
    """Example demonstrating the ResearchAgent."""
    print("\n=== Research Agent Example ===")
    
    try:
        # Create a research agent
        research_agent = ResearchAgent(
            model_name="gpt-3.5-turbo",
            temperature=0.1
        )
        
        # Research a topic
        query = "What are the latest developments in artificial intelligence in 2024?"
        print(f"Research Query: {query}")
        
        result = await research_agent.run({"query": query})
        
        print(f"\nResearch Results:")
        print(f"Answer: {result.get('answer', 'No answer provided')}")
        
        if 'intermediate_steps' in result:
            print(f"\nSources used: {len(result['intermediate_steps'])} tools")
        
        # Synchronous research example
        print("\n--- Synchronous Research ---")
        sync_result = research_agent.research_topic("Machine Learning trends")
        print(f"Topic: {sync_result.get('topic')}")
        print(f"Results: {sync_result.get('research_results', '')[:200]}...")
        
    except Exception as e:
        logger.error(f"Error in research agent example: {e}")
        print(f"Error: {e}")


async def chat_agent_example():
    """Example demonstrating the ChatAgent."""
    print("\n=== Chat Agent Example ===")
    
    try:
        # Create a chat agent
        chat_agent = ChatAgent(
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            memory_window=5
        )
        
        # Have a conversation
        messages = [
            "Hello! I'm interested in learning about Python programming.",
            "Can you explain what object-oriented programming is?",
            "How does inheritance work in Python?",
            "Can you give me a simple example?"
        ]
        
        print("Starting conversation...")
        
        for i, message in enumerate(messages, 1):
            print(f"\nUser ({i}): {message}")
            
            result = await chat_agent.run({"message": message})
            response = result.get('agent_response', 'No response')
            
            print(f"Agent: {response[:200]}{'...' if len(response) > 200 else ''}")
        
        # Show conversation history
        history = chat_agent.get_conversation_history()
        print(f"\nConversation length: {len(history)} messages")
        
        # Clear memory and start fresh
        chat_agent.clear_memory()
        print("\nMemory cleared. Starting fresh conversation...")
        
        fresh_response = chat_agent.chat("What's the weather like?")
        print(f"Fresh conversation: {fresh_response[:100]}...")
        
    except Exception as e:
        logger.error(f"Error in chat agent example: {e}")
        print(f"Error: {e}")


async def qa_chain_example():
    """Example demonstrating the QAChain."""
    print("\n=== QA Chain Example ===")
    
    try:
        # Create a simple QA chain
        qa_chain = QAChain(
            model_name="gpt-3.5-turbo",
            temperature=0.1,
            use_retrieval=False
        )
        
        # Ask questions
        questions = [
            "What is the capital of France?",
            "Explain the concept of machine learning in simple terms.",
            "What are the benefits of using Python for data science?"
        ]
        
        for question in questions:
            print(f"\nQuestion: {question}")
            
            result = await qa_chain.run({"question": question})
            answer = result.get('answer', 'No answer provided')
            
            print(f"Answer: {answer}")
        
        # Example with retrieval (requires documents)
        print("\n--- QA with Retrieval Example ---")
        
        # Create QA chain with retrieval
        retrieval_qa = QAChain(
            model_name="gpt-3.5-turbo",
            use_retrieval=True
        )
        
        # Add some sample documents
        sample_docs = [
            "Python is a high-level programming language known for its simplicity and readability. It was created by Guido van Rossum and first released in 1991.",
            "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed.",
            "Data science combines statistics, programming, and domain expertise to extract insights from data."
        ]
        
        retrieval_qa.add_documents(sample_docs, ["Python Info", "ML Info", "Data Science Info"])
        
        # Ask a question that should use the documents
        retrieval_question = "Who created Python and when was it released?"
        print(f"\nRetrieval Question: {retrieval_question}")
        
        retrieval_result = await retrieval_qa.run({"question": retrieval_question})
        print(f"Answer: {retrieval_result.get('answer', 'No answer')}")
        
        # Show relevant documents
        relevant_docs = retrieval_qa.get_relevant_documents(retrieval_question)
        print(f"\nRelevant documents found: {len(relevant_docs)}")
        
    except Exception as e:
        logger.error(f"Error in QA chain example: {e}")
        print(f"Error: {e}")


async def summarization_chain_example():
    """Example demonstrating the SummarizationChain."""
    print("\n=== Summarization Chain Example ===")
    
    try:
        # Create a summarization chain
        summarization_chain = SummarizationChain(
            model_name="gpt-3.5-turbo",
            temperature=0.3
        )
        
        # Sample text to summarize
        long_text = """
        Artificial Intelligence (AI) has become one of the most transformative technologies of the 21st century. 
        From its early beginnings in the 1950s with pioneers like Alan Turing and John McCarthy, AI has evolved 
        from simple rule-based systems to sophisticated machine learning algorithms capable of complex reasoning 
        and decision-making.
        
        Today, AI applications are ubiquitous in our daily lives. We interact with AI through virtual assistants 
        like Siri and Alexa, recommendation systems on Netflix and Amazon, and autonomous vehicles that are 
        beginning to navigate our roads. In healthcare, AI is revolutionizing diagnosis and treatment, with 
        algorithms that can detect diseases in medical images with accuracy that sometimes surpasses human experts.
        
        The field of machine learning, a subset of AI, has seen remarkable progress with the development of 
        deep learning neural networks. These systems can process vast amounts of data and identify patterns 
        that would be impossible for humans to detect. Large language models like GPT have demonstrated 
        unprecedented capabilities in natural language understanding and generation.
        
        However, the rapid advancement of AI also brings challenges. Concerns about job displacement, privacy, 
        bias in algorithms, and the potential for misuse have sparked important discussions about AI ethics and 
        governance. As we continue to integrate AI into society, it's crucial to develop frameworks that ensure 
        these technologies benefit humanity while minimizing potential risks.
        
        Looking forward, the future of AI holds immense promise. Researchers are working on artificial general 
        intelligence (AGI), quantum computing applications, and AI systems that can reason and learn more like 
        humans. The next decade will likely see even more dramatic advances that will reshape industries and 
        transform how we live and work.
        """
        
        print(f"Original text length: {len(long_text)} characters")
        
        # Test different summary lengths
        summary_lengths = ['short', 'medium', 'long']
        
        for length in summary_lengths:
            print(f"\n--- {length.title()} Summary ---")
            
            result = await summarization_chain.run({
                'text': long_text,
                'length': length
            })
            
            summary = result.get('summary', 'No summary generated')
            compression_ratio = result.get('compression_ratio', 0)
            
            print(f"Summary ({len(summary)} chars, {compression_ratio:.1%} compression):")
            print(summary)
        
        # Synchronous summarization example
        print("\n--- Synchronous Summarization ---")
        sync_summary = summarization_chain.summarize_text(long_text, 'medium')
        print(f"Sync Summary: {sync_summary[:200]}...")
        
    except Exception as e:
        logger.error(f"Error in summarization chain example: {e}")
        print(f"Error: {e}")


def chain_info_example():
    """Example showing how to get information about chains and agents."""
    print("\n=== Chain and Agent Information Example ===")
    
    try:
        # Create instances
        research_agent = ResearchAgent()
        chat_agent = ChatAgent()
        qa_chain = QAChain()
        summarization_chain = SummarizationChain()
        
        # Get information
        components = [
            ("Research Agent", research_agent),
            ("Chat Agent", chat_agent),
            ("QA Chain", qa_chain),
            ("Summarization Chain", summarization_chain)
        ]
        
        for name, component in components:
            print(f"\n{name} Info:")
            info = component.get_info()
            for key, value in info.items():
                print(f"  {key}: {value}")
    
    except Exception as e:
        logger.error(f"Error in info example: {e}")
        print(f"Error: {e}")


async def main():
    """Main function to run all examples."""
    print("LangChain Examples - Demonstrating Agents and Chains")
    print("=" * 60)
    
    # Check environment setup
    if not setup_environment():
        print("\nSkipping examples due to missing environment setup.")
        print("Set OPENAI_API_KEY and run again to see the examples in action.")
        return
    
    try:
        # Run all examples
        await research_agent_example()
        await chat_agent_example()
        await qa_chain_example()
        await summarization_chain_example()
        chain_info_example()
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("\nNext steps:")
        print("1. Check out the LangGraph examples in langgraph_examples.py")
        print("2. Explore the configuration options in config/")
        print("3. Read the README.md for more detailed documentation")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(f"\nAn error occurred: {e}")
        print("Please check your environment setup and try again.")


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())