"""Callbacks for emitting thinking/analysis messages during agent execution."""

import logging
from typing import Optional
from google.adk.agents.callback_context import CallbackContext
from google.genai import types as genai_types

logger = logging.getLogger(__name__)


def create_thinking_callback(agent_name: str, thinking_message: str):
    """
    Factory function to create before_agent callbacks that emit thinking messages.
    
    Args:
        agent_name: The name of the agent (e.g., "Payer Agent", "Geopolitics Agent")
        thinking_message: The message to display (e.g., "Analyzing payer behavior patterns...")
        
    Returns:
        A callback function that emits a thinking message before the agent runs
    """
    def callback(callback_context: CallbackContext) -> Optional[genai_types.Content]:
        """Emit a thinking message before the agent starts processing."""
        try:
            # Check if we have a transaction_id (only emit thinking after transaction_id is obtained)
            transaction_id = callback_context.session.state.get("transaction_id")
            
            if transaction_id:
                logger.info(f"🧠 {agent_name} is thinking: {thinking_message}")
                
                # Return a Content object with metadata to indicate this is a thinking message
                thinking_content = genai_types.Content(
                    role="model",
                    parts=[
                        genai_types.Part(
                            text=f"[THINKING:{agent_name}] {thinking_message}"
                        )
                    ]
                )
                return thinking_content
            
        except Exception as e:
            logger.error(f"✗ Error in thinking callback for {agent_name}: {e}", exc_info=True)
        
        return None
    
    return callback


def create_analysis_output_callback(agent_name: str):
    """
    Factory function to create after_agent callbacks that emit analysis output as thinking messages.
    
    Args:
        agent_name: The name of the agent (e.g., "Payer Agent", "Geopolitics Agent")
        
    Returns:
        A callback function that emits the agent's analysis as a thinking message
    """
    def callback(callback_context: CallbackContext) -> Optional[genai_types.Content]:
        """Emit the agent's analysis output as a thinking message."""
        try:
            # Get the agent's output from the context
            # The output is typically the last content in the turn
            if callback_context.current_turn and callback_context.current_turn.contents:
                last_content = callback_context.current_turn.contents[-1]
                
                if last_content and last_content.parts:
                    analysis_text = ""
                    for part in last_content.parts:
                        if hasattr(part, 'text') and part.text:
                            analysis_text += part.text
                    
                    if analysis_text:
                        logger.info(f"📊 {agent_name} completed analysis")
                        
                        # Return a Content object with the full analysis
                        analysis_content = genai_types.Content(
                            role="model",
                            parts=[
                                genai_types.Part(
                                    text=f"[ANALYSIS:{agent_name}]\n{analysis_text}"
                                )
                            ]
                        )
                        return analysis_content
            
        except Exception as e:
            logger.error(f"✗ Error in analysis output callback for {agent_name}: {e}", exc_info=True)
        
        return None
    
    return callback
