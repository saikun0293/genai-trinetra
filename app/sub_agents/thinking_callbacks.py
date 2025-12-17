"""Callbacks for emitting thinking/analysis messages during agent execution."""

import logging
from typing import Optional
from google.adk.agents.callback_context import CallbackContext
from google.genai import types as genai_types

logger = logging.getLogger(__name__)


def create_thinking_callback(agent_name: str, thinking_message: str):
    """
    Factory function to create before_agent callbacks that log thinking messages.
    Note: This returns None to avoid interfering with agent execution.
    
    Args:
        agent_name: The name of the agent (e.g., "Payer Agent", "Geopolitics Agent")
        thinking_message: The message to display (e.g., "Analyzing payer behavior patterns...")
        
    Returns:
        A callback function that logs a thinking message before the agent runs
    """
    def callback(callback_context: CallbackContext) -> Optional[genai_types.Content]:
        """Log a thinking message before the agent starts processing."""
        try:
            # Check if we have a transaction_id (only emit thinking after transaction_id is obtained)
            transaction_id = callback_context.session.state.get("transaction_id")
            
            if transaction_id:
                logger.info(f"🧠 {agent_name} is thinking: {thinking_message}")
                
                # Store thinking message in session for potential later use
                # but return None to not interfere with agent execution
                thinking_key = f"_thinking_{agent_name}"
                callback_context.session.state[thinking_key] = {
                    "agent": agent_name,
                    "message": thinking_message
                }
            
        except Exception as e:
            logger.error(f"✗ Error in thinking callback for {agent_name}: {e}", exc_info=True)
        
        # IMPORTANT: Return None to allow agent to execute normally
        return None
    
    return callback

