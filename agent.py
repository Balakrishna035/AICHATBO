"""
agent.py - The "Brain" and Orchestrator of our Agentic Chatbot.

What makes an AI "Agentic"?
1. Perception: Receives the user message.
2. Reasoning: Decides if it needs to use an external tool or if it can answer directly.
3. Action: Calls the chosen tool with parameters.
4. Observation: Inspects the result returned by the tool.
5. Reflection & Response: Generates the final answer using the observation.

This file supports:
- Built-in Agent Engine (Works immediately offline, no API key needed!)
- Google Gemini API (Optional, if GEMINI_API_KEY is placed in .env)
"""

import os
import re
from typing import Dict, Any, List
from tools import TOOL_REGISTRY

# Optional dotenv loader (graceful fallback if not yet installed)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Try setting up Gemini if key is provided
_gemini_model = None
if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        _gemini_model = genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        print(f"Warning: Could not initialize Gemini API: {e}")
        _gemini_model = None


class AgenticChatbot:
    """
    Demonstrates the ReAct (Reasoning + Acting) Agent pattern.
    """

    def __init__(self):
        self.tools = TOOL_REGISTRY
        self.is_llm_enabled = _gemini_model is not None

    def execute_tool(self, tool_name: str, **kwargs) -> str:
        """Executes a registered tool by name safely."""
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' does not exist."
        try:
            tool_fn = self.tools[tool_name]["function"]
            return tool_fn(**kwargs)
        except Exception as e:
            return f"Error executing tool '{tool_name}': {str(e)}"

    def _builtin_reasoning_engine(self, user_prompt: str) -> Dict[str, Any]:
        """
        A rule-based ReAct engine that showcases Agentic workflows
        without requiring external cloud API keys.
        """
        steps: List[Dict[str, str]] = []
        prompt_lower = user_prompt.lower().strip()

        # Case 1: Math calculation intent
        # Check if user asks to calculate or if there are math symbols
        math_match = re.search(r"calculate\s+(.+)|what is\s+([0-9\.\s\+\-\*\/\^\(\)]+)|([0-9\.\s\+\-\*\/\(\)]{3,})", prompt_lower)
        if ("calculate" in prompt_lower or any(op in prompt_lower for op in ["+", "-", "*", "/", "sqrt", "power"])) and any(char.isdigit() for char in prompt_lower):
            raw_expr = prompt_lower.replace("calculate", "").replace("what is", "").replace("?", "").strip()
            # Clean expression
            raw_expr = re.sub(r"[^\d\+\-\*\/\.\(\)\s]", "", raw_expr)
            if raw_expr:
                steps.append({
                    "thought": f"The user wants to evaluate a mathematical expression. Standard LLMs can make arithmetic mistakes, so I will delegate this to the 'calculate' tool.",
                    "action": f"calculate(expression='{raw_expr}')"
                })
                observation = self.execute_tool("calculate", expression=raw_expr)
                steps[-1]["observation"] = observation

                final_answer = f"According to the calculation tool, the result of `{raw_expr}` is: **{observation.replace('Calculation Result: ', '')}**."
                return {"response": final_answer, "steps": steps, "mode": "Built-in ReAct Engine"}

        # Case 2: Time / Date intent
        if any(word in prompt_lower for word in ["time", "date", "day", "today", "clock"]):
            steps.append({
                "thought": "The user is asking for the current date or time. As an AI without real-time perception, I need to fetch the system clock using the 'get_current_time' tool.",
                "action": "get_current_time(location='local')"
            })
            observation = self.execute_tool("get_current_time", location="local")
            steps[-1]["observation"] = observation

            final_answer = f"I checked the system time for you: **{observation}**."
            return {"response": final_answer, "steps": steps, "mode": "Built-in ReAct Engine"}

        # Case 3: Note taking / Memory intent
        if "note" in prompt_lower or "remember" in prompt_lower:
            if "remember" in prompt_lower or "save note" in prompt_lower or "take a note" in prompt_lower:
                # Extract content
                content = re.sub(r"^(remember that|remember|save note|take a note:?)\s*", "", user_prompt, flags=re.I).strip()
                steps.append({
                    "thought": "The user wants to store information in working memory. Calling 'manage_notes' with action='save'.",
                    "action": f"manage_notes(action='save', note='{content}')"
                })
                observation = self.execute_tool("manage_notes", action="save", note=content)
                steps[-1]["observation"] = observation
                final_answer = f"I have saved that to my memory: *\"{content}\"*.\nYou can ask me 'show notes' at any time!"
                return {"response": final_answer, "steps": steps, "mode": "Built-in ReAct Engine"}

            elif any(w in prompt_lower for w in ["show", "get", "list", "view", "what are my notes"]):
                steps.append({
                    "thought": "The user wants to recall saved notes. Calling 'manage_notes' with action='get'.",
                    "action": "manage_notes(action='get')"
                })
                observation = self.execute_tool("manage_notes", action="get")
                steps[-1]["observation"] = observation
                return {"response": observation, "steps": steps, "mode": "Built-in ReAct Engine"}

        # Case 4: Concept lookup in Knowledge Base
        for topic in ["agentic ai", "react", "flask", "python"]:
            if topic in prompt_lower:
                steps.append({
                    "thought": f"The user is asking about the concept '{topic}'. I will retrieve verified information from the 'search_knowledge_base' tool.",
                    "action": f"search_knowledge_base(query='{topic}')"
                })
                observation = self.execute_tool("search_knowledge_base", query=topic)
                steps[-1]["observation"] = observation

                final_answer = f"Here is what I found in the knowledge base:\n\n{observation}"
                return {"response": final_answer, "steps": steps, "mode": "Built-in ReAct Engine"}

        # Default: General conversational reply with agent explanation
        steps.append({
            "thought": "This is a general conversational message that does not require external tools. I can answer directly.",
            "action": "None (Direct conversational response)",
            "observation": "N/A"
        })
        greeting_text = (
            f"Hello! I am your **Agentic AI Chatbot**.\n\n"
            f"Unlike a basic chatbot, I can **reason** about your request and **use tools**! "
            f"Here are some things you can ask me to do:\n"
            f"• **Math**: *'Calculate 35 * 18 + 140'*\n"
            f"• **Real-time info**: *'What is the current time and date?'*\n"
            f"• **Learning concepts**: *'What is Agentic AI?'* or *'Explain ReAct pattern'*\n"
            f"• **Memory & Notes**: *'Remember I need to study Flask tomorrow'* then *'Show my notes'*"
        )
        return {"response": greeting_text, "steps": steps, "mode": "Built-in ReAct Engine"}

    def _llm_reasoning_engine(self, user_prompt: str) -> Dict[str, Any]:
        """
        Uses Gemini LLM to decide on actions and generate answers.
        """
        # Build prompt describing available tools
        tool_descriptions = "\n".join([
            f"- {name}: {info['description']}" for name, info in self.tools.items()
        ])

        system_instruction = f"""
You are an Agentic AI assistant. You have access to the following tools:
{tool_descriptions}

When you receive a user message, you MUST respond in this exact ReAct format:
Thought: <Explain what the user wants and if a tool is needed>
Action: <Tool name: calculate, get_current_time, search_knowledge_base, manage_notes, or None>
Action Input: <Arguments in json or key=value format, or None>
Final Answer: <Your final conversational answer to the user if no tool is needed>
"""
        try:
            prompt = f"{system_instruction}\n\nUser Question: {user_prompt}\n"
            response = _gemini_model.generate_content(prompt)
            raw_text = response.text

            # Parse out Thought, Action, Action Input, Final Answer
            thought_match = re.search(r"Thought:\s*(.*?)(?=Action:|$)", raw_text, re.DOTALL)
            action_match = re.search(r"Action:\s*(.*?)(?=Action Input:|$)", raw_text, re.DOTALL)
            input_match = re.search(r"Action Input:\s*(.*?)(?=Final Answer:|$)", raw_text, re.DOTALL)
            final_match = re.search(r"Final Answer:\s*(.*)", raw_text, re.DOTALL)

            thought = thought_match.group(1).strip() if thought_match else "Reasoning about user request."
            action = action_match.group(1).strip() if action_match else "None"
            action_input = input_match.group(1).strip() if input_match else ""

            steps = [{
                "thought": thought,
                "action": f"{action}({action_input})",
                "observation": ""
            }]

            if action and action != "None" and action in self.tools:
                # Execute the tool
                if action == "calculate":
                    obs = self.execute_tool("calculate", expression=action_input)
                elif action == "get_current_time":
                    obs = self.execute_tool("get_current_time", location=action_input or "local")
                elif action == "search_knowledge_base":
                    obs = self.execute_tool("search_knowledge_base", query=action_input)
                elif action == "manage_notes":
                    obs = self.execute_tool("manage_notes", action="save" if "save" in action_input else "get", note=action_input)
                else:
                    obs = "Executed."

                steps[0]["observation"] = obs

                # Follow-up generation with observation
                follow_up = f"{prompt}\nThought: {thought}\nAction: {action}\nObservation: {obs}\nFinal Answer:"
                final_res = _gemini_model.generate_content(follow_up)
                final_answer = final_res.text.strip()
            else:
                final_answer = final_match.group(1).strip() if final_match else raw_text

            return {"response": final_answer, "steps": steps, "mode": "Gemini LLM (Live ReAct Loop)"}

        except Exception as e:
            # Graceful fallback to built-in engine if API error occurs
            result = self._builtin_reasoning_engine(user_prompt)
            result["mode"] = f"Fallback Built-in Engine (LLM Error: {str(e)})"
            return result

    def process_message(self, user_message: str) -> Dict[str, Any]:
        """
        Main entry point for processing chat messages.
        """
        if not user_message or not user_message.strip():
            return {
                "response": "Please type a message so I can assist you!",
                "steps": [],
                "mode": "Idle"
            }

        if self.is_llm_enabled:
            return self._llm_reasoning_engine(user_message)
        else:
            return self._builtin_reasoning_engine(user_message)


# Global singleton instance
agent = AgenticChatbot()
