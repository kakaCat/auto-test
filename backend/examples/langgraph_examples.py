"""LangGraph examples demonstrating the usage of graphs and workflows."""

import asyncio
import os
from typing import List, Dict, Any, TypedDict

# Set up the path to import from src
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from langchain_langgraph_project.graphs import WorkflowGraph, AgentGraph
from langchain_langgraph_project.agents import ResearchAgent, ChatAgent
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


class SimpleWorkflowState(TypedDict):
    """State for simple workflow example."""
    input_text: str
    processed_text: str
    analysis_result: str
    final_output: str
    step_count: int


class DataProcessingState(TypedDict):
    """State for data processing workflow."""
    raw_data: List[str]
    cleaned_data: List[str]
    analyzed_data: Dict[str, Any]
    summary: str
    metadata: Dict[str, Any]


class MultiAgentState(TypedDict):
    """State for multi-agent collaboration."""
    task: str
    research_results: str
    chat_responses: List[str]
    final_report: str
    agent_logs: List[Dict[str, Any]]


async def simple_workflow_example():
    """Example demonstrating a simple workflow graph."""
    print("\n=== Simple Workflow Graph Example ===")
    
    try:
        # Create a workflow graph
        workflow = WorkflowGraph[SimpleWorkflowState]()
        
        # Define workflow steps
        def preprocess_step(state: SimpleWorkflowState) -> SimpleWorkflowState:
            """First step: preprocess the input text."""
            processed = state['input_text'].strip().lower()
            state['processed_text'] = processed
            state['step_count'] = state.get('step_count', 0) + 1
            print(f"Step 1: Preprocessed text: '{processed}'")
            return state
        
        def analyze_step(state: SimpleWorkflowState) -> SimpleWorkflowState:
            """Second step: analyze the processed text."""
            text = state['processed_text']
            word_count = len(text.split())
            char_count = len(text)
            analysis = f"Words: {word_count}, Characters: {char_count}"
            state['analysis_result'] = analysis
            state['step_count'] = state.get('step_count', 0) + 1
            print(f"Step 2: Analysis: {analysis}")
            return state
        
        def finalize_step(state: SimpleWorkflowState) -> SimpleWorkflowState:
            """Final step: create the final output."""
            final_output = f"Processed: {state['processed_text']} | Analysis: {state['analysis_result']}"
            state['final_output'] = final_output
            state['step_count'] = state.get('step_count', 0) + 1
            print(f"Step 3: Final output created")
            return state
        
        # Add steps to workflow
        workflow.add_step("preprocess", preprocess_step)
        workflow.add_step("analyze", analyze_step)
        workflow.add_step("finalize", finalize_step)
        
        # Create and compile the graph
        graph = workflow.create_graph()
        compiled_graph = workflow.compile_graph()
        
        # Run the workflow
        initial_state: SimpleWorkflowState = {
            'input_text': '  Hello World! This is a TEST message.  ',
            'processed_text': '',
            'analysis_result': '',
            'final_output': '',
            'step_count': 0
        }
        
        print(f"\nInput: '{initial_state['input_text']}'")
        print("Running workflow...")
        
        result = await workflow.run(initial_state)
        
        print(f"\nWorkflow completed in {result['step_count']} steps")
        print(f"Final output: {result['final_output']}")
        
        # Show workflow structure
        workflow_info = workflow.get_info()
        print(f"\nWorkflow Info:")
        for key, value in workflow_info.items():
            print(f"  {key}: {value}")
        
    except Exception as e:
        logger.error(f"Error in simple workflow example: {e}")
        print(f"Error: {e}")


async def data_processing_workflow_example():
    """Example demonstrating a data processing workflow."""
    print("\n=== Data Processing Workflow Example ===")
    
    try:
        # Create a data processing workflow
        workflow = WorkflowGraph[DataProcessingState]()
        
        # Define data processing steps
        def clean_data_step(state: DataProcessingState) -> DataProcessingState:
            """Clean the raw data."""
            raw_data = state['raw_data']
            cleaned = [item.strip().lower() for item in raw_data if item.strip()]
            state['cleaned_data'] = cleaned
            print(f"Cleaned {len(raw_data)} items -> {len(cleaned)} clean items")
            return state
        
        def analyze_data_step(state: DataProcessingState) -> DataProcessingState:
            """Analyze the cleaned data."""
            cleaned_data = state['cleaned_data']
            
            analysis = {
                'total_items': len(cleaned_data),
                'unique_items': len(set(cleaned_data)),
                'avg_length': sum(len(item) for item in cleaned_data) / len(cleaned_data) if cleaned_data else 0,
                'word_count': sum(len(item.split()) for item in cleaned_data)
            }
            
            state['analyzed_data'] = analysis
            print(f"Analysis completed: {analysis['total_items']} items, {analysis['unique_items']} unique")
            return state
        
        def summarize_step(state: DataProcessingState) -> DataProcessingState:
            """Create a summary of the analysis."""
            analysis = state['analyzed_data']
            
            summary = f"""Data Processing Summary:
            - Total items processed: {analysis['total_items']}
            - Unique items: {analysis['unique_items']}
            - Average item length: {analysis['avg_length']:.1f} characters
            - Total word count: {analysis['word_count']}
            """
            
            state['summary'] = summary
            state['metadata'] = {
                'processing_date': 'today',
                'version': '1.0',
                'status': 'completed'
            }
            
            print("Summary generated")
            return state
        
        # Add steps to workflow
        workflow.add_step("clean", clean_data_step)
        workflow.add_step("analyze", analyze_data_step)
        workflow.add_step("summarize", summarize_step)
        
        # Compile the graph
        compiled_graph = workflow.compile_graph()
        
        # Sample data to process
        sample_data = [
            "  Python Programming  ",
            "Machine Learning",
            "  ",  # Empty item
            "Data Science and Analytics",
            "ARTIFICIAL INTELLIGENCE",
            "python programming",  # Duplicate
            "Web Development",
            "  Cloud Computing  "
        ]
        
        # Run the workflow
        initial_state: DataProcessingState = {
            'raw_data': sample_data,
            'cleaned_data': [],
            'analyzed_data': {},
            'summary': '',
            'metadata': {}
        }
        
        print(f"\nProcessing {len(sample_data)} data items...")
        
        result = await workflow.run(initial_state)
        
        print(f"\n{result['summary']}")
        print(f"\nMetadata: {result['metadata']}")
        
    except Exception as e:
        logger.error(f"Error in data processing workflow example: {e}")
        print(f"Error: {e}")


async def multi_agent_collaboration_example():
    """Example demonstrating multi-agent collaboration using AgentGraph."""
    print("\n=== Multi-Agent Collaboration Example ===")
    
    try:
        # Create agents
        research_agent = ResearchAgent(
            model_name="gpt-3.5-turbo",
            temperature=0.1
        )
        
        chat_agent = ChatAgent(
            model_name="gpt-3.5-turbo",
            temperature=0.7
        )
        
        # Create agent graph
        agent_graph = AgentGraph[MultiAgentState]()
        
        # Add agents to the graph
        agent_graph.add_agent("researcher", research_agent)
        agent_graph.add_agent("chat_assistant", chat_agent)
        
        # Define coordination functions
        def research_coordinator(state: MultiAgentState) -> MultiAgentState:
            """Coordinate research task."""
            task = state['task']
            print(f"Research Coordinator: Processing task '{task}'")
            
            # This would typically call the research agent
            # For demo purposes, we'll simulate the result
            research_results = f"Research completed for: {task}. Found relevant information about current trends and developments."
            
            state['research_results'] = research_results
            state['agent_logs'].append({
                'agent': 'researcher',
                'action': 'research_completed',
                'timestamp': 'now'
            })
            
            print(f"Research completed: {research_results[:100]}...")
            return state
        
        def chat_coordinator(state: MultiAgentState) -> MultiAgentState:
            """Coordinate chat responses."""
            research_results = state['research_results']
            
            # Generate multiple chat responses based on research
            chat_responses = [
                f"Based on the research: {research_results[:50]}...",
                "Here are the key insights from the analysis...",
                "The findings suggest several important trends..."
            ]
            
            state['chat_responses'] = chat_responses
            state['agent_logs'].append({
                'agent': 'chat_assistant',
                'action': 'responses_generated',
                'timestamp': 'now'
            })
            
            print(f"Generated {len(chat_responses)} chat responses")
            return state
        
        def report_generator(state: MultiAgentState) -> MultiAgentState:
            """Generate final report combining all agent outputs."""
            task = state['task']
            research = state['research_results']
            responses = state['chat_responses']
            
            final_report = f"""Multi-Agent Collaboration Report
            
            Task: {task}
            
            Research Findings:
            {research}
            
            Generated Responses:
            {chr(10).join(f'- {response}' for response in responses)}
            
            Collaboration Summary:
            The research agent successfully gathered information, and the chat assistant 
            generated multiple response variations. Total agents involved: 2
            """
            
            state['final_report'] = final_report
            state['agent_logs'].append({
                'agent': 'coordinator',
                'action': 'report_generated',
                'timestamp': 'now'
            })
            
            print("Final report generated")
            return state
        
        # Add coordination steps
        agent_graph.add_step("research", research_coordinator)
        agent_graph.add_step("chat", chat_coordinator)
        agent_graph.add_step("report", report_generator)
        
        # Compile the graph
        compiled_graph = agent_graph.compile_graph()
        
        # Run the multi-agent workflow
        initial_state: MultiAgentState = {
            'task': 'Analyze the impact of AI on modern software development',
            'research_results': '',
            'chat_responses': [],
            'final_report': '',
            'agent_logs': []
        }
        
        print(f"\nStarting multi-agent collaboration...")
        print(f"Task: {initial_state['task']}")
        
        result = await agent_graph.run(initial_state)
        
        print(f"\n{result['final_report']}")
        
        print(f"\nAgent Activity Log:")
        for log_entry in result['agent_logs']:
            print(f"  {log_entry['agent']}: {log_entry['action']} at {log_entry['timestamp']}")
        
        # Show graph info
        graph_info = agent_graph.get_info()
        print(f"\nAgent Graph Info:")
        for key, value in graph_info.items():
            print(f"  {key}: {value}")
        
    except Exception as e:
        logger.error(f"Error in multi-agent collaboration example: {e}")
        print(f"Error: {e}")


async def workflow_visualization_example():
    """Example demonstrating workflow visualization."""
    print("\n=== Workflow Visualization Example ===")
    
    try:
        # Create a simple workflow for visualization
        workflow = WorkflowGraph[SimpleWorkflowState]()
        
        # Add some steps
        workflow.add_step("input", lambda state: state)
        workflow.add_step("process", lambda state: state)
        workflow.add_step("output", lambda state: state)
        
        # Create and compile graph
        graph = workflow.create_graph()
        compiled_graph = workflow.compile_graph()
        
        # Try to visualize (this would normally create a visual representation)
        print("Attempting to visualize workflow...")
        
        try:
            # This would normally save a visualization file
            visualization_result = workflow.visualize("workflow_diagram")
            print(f"Visualization saved: {visualization_result}")
        except Exception as viz_error:
            print(f"Visualization not available: {viz_error}")
            print("Note: Install graphviz and related packages for visualization support")
        
        # Show workflow structure as text
        print("\nWorkflow Structure:")
        steps = workflow.get_steps()
        print(f"Steps: {list(steps.keys())}")
        
        workflow_info = workflow.get_info()
        print(f"\nWorkflow Details:")
        for key, value in workflow_info.items():
            print(f"  {key}: {value}")
        
    except Exception as e:
        logger.error(f"Error in visualization example: {e}")
        print(f"Error: {e}")


def graph_management_example():
    """Example showing graph management operations."""
    print("\n=== Graph Management Example ===")
    
    try:
        # Create a workflow
        workflow = WorkflowGraph[SimpleWorkflowState]()
        
        # Add steps
        workflow.add_step("step1", lambda state: state)
        workflow.add_step("step2", lambda state: state)
        workflow.add_step("step3", lambda state: state)
        
        print(f"Initial steps: {list(workflow.get_steps().keys())}")
        
        # Remove a step
        workflow.remove_step("step2")
        print(f"After removing step2: {list(workflow.get_steps().keys())}")
        
        # Add a new step
        workflow.add_step("new_step", lambda state: state)
        print(f"After adding new_step: {list(workflow.get_steps().keys())}")
        
        # Show workflow info
        info = workflow.get_info()
        print(f"\nWorkflow Info:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        # Create agent graph for comparison
        agent_graph = AgentGraph[MultiAgentState]()
        
        # Show agent graph info
        agent_info = agent_graph.get_info()
        print(f"\nAgent Graph Info:")
        for key, value in agent_info.items():
            print(f"  {key}: {value}")
        
    except Exception as e:
        logger.error(f"Error in graph management example: {e}")
        print(f"Error: {e}")


async def main():
    """Main function to run all LangGraph examples."""
    print("LangGraph Examples - Demonstrating Workflows and Multi-Agent Systems")
    print("=" * 70)
    
    # Check environment setup
    if not setup_environment():
        print("\nNote: Some examples may not work without proper environment setup.")
        print("Set OPENAI_API_KEY to see full functionality.")
    
    try:
        # Run all examples
        await simple_workflow_example()
        await data_processing_workflow_example()
        
        # Only run agent collaboration if environment is set up
        if os.getenv('OPENAI_API_KEY'):
            await multi_agent_collaboration_example()
        else:
            print("\n=== Multi-Agent Collaboration Example ===")
            print("Skipped: Requires OPENAI_API_KEY environment variable")
        
        await workflow_visualization_example()
        graph_management_example()
        
        print("\n" + "=" * 70)
        print("All LangGraph examples completed!")
        print("\nNext steps:")
        print("1. Try modifying the workflow steps to see how graphs adapt")
        print("2. Experiment with different state structures")
        print("3. Create your own multi-agent workflows")
        print("4. Explore visualization options with graphviz")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(f"\nAn error occurred: {e}")
        print("Please check your setup and try again.")


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())