"""
Validation Agents for Campaign AI Platform

This module contains validation agents that ensure output quality and prevent
infinite loops in the agent workflow system.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import re

from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)

class HallucinationGrader:
    """
    Agent that evaluates LLM outputs for hallucinations and factual accuracy.
    Returns binary output: "yes" if hallucination detected, "no" if valid.
    """
    
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.llm = ChatOpenAI(
            model=model,
            temperature=0.1,  # Low temperature for consistent evaluation
            max_tokens=500
        )
        logger.info(f"✅ Initialized Hallucination Grader with model: {model}")
    
    def grade_output(self, 
                    output: str, 
                    context: Optional[str] = None,
                    source_data: Optional[str] = None) -> Dict[str, Any]:
        """
        Grade an LLM output for hallucinations.
        
        Args:
            output: The LLM output to evaluate
            context: Optional context or prompt that generated the output
            source_data: Optional source data that should be referenced
            
        Returns:
            Dict with 'is_hallucination' (bool), 'confidence' (float), 'reason' (str)
        """
        try:
            system_message = """You are a factual accuracy evaluator for marketing campaign analysis outputs. 
            Your job is to detect hallucinations, false claims, or unsupported statements in AI-generated content.
            
            Evaluate the provided output for:
            1. Factual accuracy and consistency
            2. Logical coherence and reasoning
            3. Unsupported claims or made-up statistics
            4. Consistency with provided context/data
            
            Respond with ONLY:
            - "VALID" if the output appears factually sound and well-reasoned
            - "HALLUCINATION" if you detect false claims, inconsistencies, or unsupported statements
            
            Be strict but fair in your evaluation."""
            
            prompt_parts = [f"**Output to Evaluate:**\n{output}"]
            
            if context:
                prompt_parts.append(f"\n**Original Context:**\n{context}")
            
            if source_data:
                prompt_parts.append(f"\n**Source Data:**\n{source_data}")
            
            prompt_parts.append("\n**Evaluation:** Is this output factually accurate and well-reasoned?")
            
            prompt = "\n".join(prompt_parts)
            
            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            evaluation = response.content.strip().upper()
            
            # Parse response
            is_hallucination = "HALLUCINATION" in evaluation
            confidence = 0.9 if "HALLUCINATION" in evaluation or "VALID" in evaluation else 0.5
            
            # Extract reason if provided
            reason = "Detected potential hallucination or unsupported claims" if is_hallucination else "Output appears factually sound"
            
            result = {
                'is_hallucination': is_hallucination,
                'confidence': confidence,
                'reason': reason,
                'raw_evaluation': evaluation
            }
            
            logger.info(f"🔍 Hallucination Grade: {'DETECTED' if is_hallucination else 'VALID'} (confidence: {confidence})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Hallucination grading error: {str(e)}")
            return {
                'is_hallucination': False,  # Default to valid on error
                'confidence': 0.0,
                'reason': f"Grading error: {str(e)}",
                'raw_evaluation': "ERROR"
            }

class EnforcerAgent:
    """
    Agent that prevents infinite loops by tracking iterations and enforcing limits.
    Returns binary output: "continue" or "stop".
    """
    
    def __init__(self, max_iterations: int = 5, max_retries: int = 3):
        self.max_iterations = max_iterations
        self.max_retries = max_retries
        self.iteration_counts = {}  # Track iterations per workflow/session
        self.retry_counts = {}      # Track retries per specific operation
        logger.info(f"✅ Initialized Enforcer Agent (max_iterations: {max_iterations}, max_retries: {max_retries})")
    
    def should_continue(self, 
                       workflow_id: str, 
                       operation: str = "default",
                       reset: bool = False) -> Dict[str, Any]:
        """
        Determine if workflow should continue or stop.
        
        Args:
            workflow_id: Unique identifier for the workflow session
            operation: Specific operation being tracked
            reset: Whether to reset counters for this workflow
            
        Returns:
            Dict with 'should_continue' (bool), 'reason' (str), 'counts' (dict)
        """
        try:
            if reset:
                self.iteration_counts.pop(workflow_id, None)
                self.retry_counts.pop(f"{workflow_id}_{operation}", None)
                logger.info(f"🔄 Reset counters for workflow: {workflow_id}")
            
            # Track iterations
            if workflow_id not in self.iteration_counts:
                self.iteration_counts[workflow_id] = 0
            self.iteration_counts[workflow_id] += 1
            
            # Track retries for specific operations
            retry_key = f"{workflow_id}_{operation}"
            if retry_key not in self.retry_counts:
                self.retry_counts[retry_key] = 0
            self.retry_counts[retry_key] += 1
            
            current_iterations = self.iteration_counts[workflow_id]
            current_retries = self.retry_counts[retry_key]
            
            # Check limits
            if current_iterations > self.max_iterations:
                reason = f"Maximum iterations exceeded ({current_iterations}/{self.max_iterations})"
                should_continue = False
            elif current_retries > self.max_retries:
                reason = f"Maximum retries exceeded for {operation} ({current_retries}/{self.max_retries})"
                should_continue = False
            else:
                reason = f"Within limits (iterations: {current_iterations}/{self.max_iterations}, retries: {current_retries}/{self.max_retries})"
                should_continue = True
            
            result = {
                'should_continue': should_continue,
                'reason': reason,
                'counts': {
                    'iterations': current_iterations,
                    'retries': current_retries,
                    'max_iterations': self.max_iterations,
                    'max_retries': self.max_retries
                }
            }
            
            status = "CONTINUE" if should_continue else "STOP"
            logger.info(f"🛡️ Enforcer Decision: {status} - {reason}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Enforcer error: {str(e)}")
            return {
                'should_continue': False,  # Default to stop on error
                'reason': f"Enforcer error: {str(e)}",
                'counts': {}
            }
    
    def get_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get current status for a workflow."""
        return {
            'iterations': self.iteration_counts.get(workflow_id, 0),
            'retry_operations': {k.split('_', 1)[1]: v for k, v in self.retry_counts.items() 
                               if k.startswith(f"{workflow_id}_")}
        }

# Tool wrappers for LangGraph integration
@tool
def grade_for_hallucination(
    output: str,
    context: Optional[str] = None,
    source_data: Optional[str] = None
) -> str:
    """
    Grade LLM output for hallucinations and factual accuracy.
    
    Args:
        output: The LLM output to evaluate
        context: Optional context that generated the output
        source_data: Optional source data for verification
        
    Returns:
        "yes" if hallucination detected, "no" if output is valid
    """
    grader = HallucinationGrader()
    result = grader.grade_output(output, context, source_data)
    
    # Return binary output for LangGraph conditional edges
    return "yes" if result['is_hallucination'] else "no"

@tool
def enforce_workflow_limits(
    workflow_id: str,
    operation: str = "default",
    reset: bool = False
) -> str:
    """
    Enforce workflow iteration and retry limits to prevent infinite loops.
    
    Args:
        workflow_id: Unique identifier for the workflow session
        operation: Specific operation being tracked
        reset: Whether to reset counters
        
    Returns:
        "continue" if workflow should proceed, "stop" if limits exceeded
    """
    enforcer = EnforcerAgent()
    result = enforcer.should_continue(workflow_id, operation, reset)
    
    # Return binary output for LangGraph conditional edges
    return "continue" if result['should_continue'] else "stop"

# Global instances for reuse
_hallucination_grader = None
_enforcer_agent = None

def get_hallucination_grader() -> HallucinationGrader:
    """Get or create global hallucination grader instance."""
    global _hallucination_grader
    if _hallucination_grader is None:
        _hallucination_grader = HallucinationGrader()
    return _hallucination_grader

def get_enforcer_agent() -> EnforcerAgent:
    """Get or create global enforcer agent instance."""
    global _enforcer_agent
    if _enforcer_agent is None:
        _enforcer_agent = EnforcerAgent()
    return _enforcer_agent 