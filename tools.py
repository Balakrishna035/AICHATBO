"""
tools.py - The "Hands and Senses" of our AI Agent.

In Agentic AI:
- An LLM by itself can only generate text based on its past training data.
- It CANNOT browse the current time, do exact math reliably, or access external systems.
- "Tools" are Python functions that we give to the Agent so it can take ACTIONS in the real world.
"""

from datetime import datetime
import math

# A simple in-memory storage for the agent to remember user notes
_agent_memory = {}

# A built-in knowledge base for quick offline answers
_KNOWLEDGE_BASE = {
    "agentic ai": (
        "Agentic AI refers to AI systems that can proactively pursue goals, "
        "break tasks into steps, make decisions, use external tools, and learn from "
        "feedback without requiring continuous human guidance at every micro-step."
    ),
    "react pattern": (
        "ReAct stands for 'Reasoning + Acting'. It is a prompting and control paradigm where "
        "the agent generates a Thought (reasoning), decides on an Action (tool call), "
        "reads the Observation (tool result), and repeats until it reaches the Final Answer."
    ),
    "flask": (
        "Flask is a lightweight and beginner-friendly web framework for Python. "
        "It provides tools and libraries to build web apps and REST APIs quickly."
    ),
    "python": (
        "Python is a high-level, interpreted programming language known for its readable syntax "
        "and extensive ecosystem for AI, data science, and web development."
    )
}


def calculate(expression: str) -> str:
    """
    Safely evaluates a basic mathematical expression.
    Example input: "25 * 40 + 10" or "sqrt(144)"
    """
    try:
        # Provide a restricted math namespace for safe evaluation
        allowed_names = {
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "pi": math.pi,
            "pow": pow,
            "abs": abs,
            "round": round
        }
        # Disallow dangerous builtins
        result = eval(expression, {"__builtins__": None}, allowed_names)
        return f"Calculation Result: {result}"
    except Exception as e:
        return f"Error evaluating expression '{expression}': {str(e)}"


def get_current_time(location: str = "local") -> str:
    """
    Returns the current local date and time.
    """
    now = datetime.now()
    formatted_time = now.strftime("%A, %B %d, %Y - %I:%M:%S %p")
    return f"Current time ({location}): {formatted_time}"


def search_knowledge_base(query: str) -> str:
    """
    Searches the internal knowledge base for known concepts.
    """
    query_clean = query.strip().lower()
    for topic, info in _KNOWLEDGE_BASE.items():
        if topic in query_clean or query_clean in topic:
            return f"Knowledge Base [{topic.title()}]: {info}"
    
    return f"No direct entry found in knowledge base for '{query}'. Try searching for: agentic ai, react pattern, flask, or python."


def manage_notes(action: str, note: str = "") -> str:
    """
    Saves or retrieves simple notes for the user.
    action: 'save', 'get', or 'clear'
    """
    action = action.lower().strip()
    if action == "save":
        if not note:
            return "Please provide content to save."
        note_id = len(_agent_memory) + 1
        _agent_memory[note_id] = note
        return f"Saved note #{note_id}: '{note}'"
    elif action == "get":
        if not _agent_memory:
            return "No notes currently saved in memory."
        notes_list = "\n".join([f"#{k}: {v}" for k, v in _agent_memory.items()])
        return f"Current Saved Notes:\n{notes_list}"
    elif action == "clear":
        _agent_memory.clear()
        return "All notes have been cleared."
    else:
        return f"Unknown note action '{action}'. Use 'save', 'get', or 'clear'."


# Tool Registry: Maps tool names to actual functions and descriptions for the agent
TOOL_REGISTRY = {
    "calculate": {
        "function": calculate,
        "description": "Performs exact math calculations. Input should be a math expression (e.g. '125 * 8')."
    },
    "get_current_time": {
        "function": get_current_time,
        "description": "Gets the current system date and time. Useful when user asks what time or day it is."
    },
    "search_knowledge_base": {
        "function": search_knowledge_base,
        "description": "Looks up definitions for Agentic AI, ReAct pattern, Flask, Python, etc."
    },
    "manage_notes": {
        "function": manage_notes,
        "description": "Saves or reads user notes. Inputs: action ('save', 'get', or 'clear'), note (text)."
    }
}
