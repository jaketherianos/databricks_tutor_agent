"""
Small Tutor Agent Module

This module provides a clean interface to the tutor agent.
It wraps the implementation in agent.py with a simple function signature.
"""

from agent import tutor_agent


def run_tutor_agent(topic: str) -> dict:
    """
    Run the Small Tutor Agent to explain a topic at 3 difficulty levels.
    
    Args:
        topic: The topic to explain (e.g., "Delta Lake time travel")
    
    Returns:
        Dictionary with keys 'beginner', 'intermediate', and 'expert',
        each containing a string explanation at that difficulty level.
    
    Example:
        >>> result = run_tutor_agent("transformers")
        >>> print(result["beginner"])
        >>> print(result["intermediate"])
        >>> print(result["expert"])
    """
    return tutor_agent(topic)

