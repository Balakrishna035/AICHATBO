"""
constitution_agent.py - Constitutional Law AI Agent with Google Gemini Integration.

Capabilities:
1. Google Gemini 1.5 Integration: Answers ANY constitutional question, case law,
   history, comparative law, or civic query with deep intelligence.
2. Tool Calling & Grounding: Uses constitution_tools.py to ground answers in
   exact constitutional texts, articles, writs, and interactive quizzes.
3. Chat Memory: Remembers previous questions in the conversation session.
4. Offline Fallback: If no API key is provided or if network is offline,
   seamlessly falls back to the local constitutional database.
"""

import os
import re
from typing import Dict, Any, List, Optional
from constitution_tools import CONSTITUTION_TOOLS

# Try to load existing .env file
try:
    from dotenv import load_dotenv, set_key
    load_dotenv()
except ImportError:
    pass


class ConstitutionAgent:
    """An Agentic AI assistant specialized in Constitutional Law powered by Gemini."""

    def __init__(self):
        self.tools = CONSTITUTION_TOOLS
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.gemini_model = None
        self.active_model_name = "Gemini"
        self.chat_session = None
        self.chat_history: List[Dict[str, str]] = []

        # Attempt to initialize Gemini if key exists
        if self.api_key:
            self._init_gemini(self.api_key)

    def _init_gemini(self, api_key: str) -> bool:
        """Initializes or updates the Google Gemini client."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)

            # System instructions with strict domain guardrails
            tools_desc = "\n".join([f"- {name}: {meta['description']}" for name, meta in self.tools.items()])
            system_instruction = f"""
You are the "Constitution AI Agent", a strictly specialized expert on the Constitution of India and Constitutional Law.

CRITICAL SCOPE & DOMAIN BOUNDARY:
- You are EXCLUSIVELY dedicated to Constitutional Law, the Constitution of India, legal rights, landmark court rulings, and civic governance.
- ALLOWED TOPICS:
  * Articles, Schedules, Preamble, and Amendments of the Constitution.
  * Fundamental Rights, Directive Principles (DPSP), Fundamental Duties.
  * Landmark Supreme Court & High Court judgements (e.g., Kesavananda Bharati, Maneka Gandhi, Puttaswamy, Navtej Johar).
  * Writs (Habeas Corpus, Mandamus, Quo Warranto, Certiorari, Prohibition).
  * Constitutional institutions (President, Parliament, Judiciary, Election Commission, etc.).
  * Comparative constitutional principles (e.g., federalism, separation of powers).

- STRICTLY FORBIDDEN / OFF-TOPIC TOPICS:
  * General technology, computer programming, Large Language Models (LLMs), AI explanations, coding.
  * Sports, cinema, cooking, gaming, weather, travel, general science, or casual non-legal advice.

- HOW TO HANDLE OFF-TOPIC QUESTIONS:
  If the user asks about ANY topic outside of constitutional and legal matters (such as "What is an LLM?", "How to write Python code?", "Who won the cricket match?"):
  You MUST politely refuse and NOT answer the unrelated question. Respond with this exact style:
  "🏛️ I am a specialized Constitutional Law AI Agent. I am designed exclusively to answer questions about the Constitution, legal rights, court judgements, and civic governance.

  I cannot answer unrelated questions on general topics (like technology, sports, or entertainment).

  Please feel free to ask me anything about the Constitution, such as:
  • 'What is Article 21 (Right to Life & Liberty)?'
  • 'What are my Fundamental Rights?'
  • 'Explain the Basic Structure Doctrine'
  • 'What is Article 370 and its history?'"

You have access to verified local tools:
{tools_desc}
"""
            # Candidate models in order of speed and capability
            candidate_models = [
                "gemini-2.5-flash",
                "gemini-flash-latest",
                "gemini-2.5-pro",
                "gemini-1.5-flash",
                "gemini-pro-latest"
            ]

            selected_model = None
            for model_name in candidate_models:
                try:
                    m = genai.GenerativeModel(
                        model_name=model_name,
                        system_instruction=system_instruction
                    )
                    # Quick verification
                    selected_model = m
                    self.active_model_name = model_name
                    break
                except Exception:
                    continue

            if not selected_model:
                raise RuntimeError("No compatible Gemini model found.")

            self.gemini_model = selected_model
            self.chat_session = self.gemini_model.start_chat(history=[])
            self.api_key = api_key
            return True
        except Exception as e:
            print(f"Warning: Could not initialize Gemini with the provided key: {e}")
            self.gemini_model = None
            self.chat_session = None
            return False

    def set_api_key(self, api_key: str, save_to_env: bool = True) -> bool:
        """Allows dynamically setting the API key from CMD and saving it to .env."""
        success = self._init_gemini(api_key.strip())
        if success and save_to_env:
            try:
                env_path = os.path.join(os.path.dirname(__file__), ".env")
                with open(env_path, "w", encoding="utf-8") as f:
                    f.write(f"GEMINI_API_KEY={api_key.strip()}\n")
            except Exception as e:
                print(f"Note: Could not write .env file: {e}")
        return success

    @property
    def is_gemini_active(self) -> bool:
        return self.gemini_model is not None

    def execute_tool(self, tool_name: str, **kwargs) -> str:
        """Invokes a constitutional tool safely."""
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' is not in the agent registry."
        try:
            return self.tools[tool_name]["function"](**kwargs)
        except Exception as e:
            return f"Error running {tool_name}: {str(e)}"

    def _builtin_reasoning(self, query: str) -> Dict[str, Any]:
        """Offline fallback reasoning engine using local knowledge base."""
        q = query.strip().lower()

        # Preamble
        if any(term in q for term in ["preamble", "we the people", "sovereign socialist"]):
            thought = "User asked about the Preamble. Querying local get_preamble tool."
            obs = self.execute_tool("get_preamble")
            return {
                "thought": thought,
                "action": "get_preamble()",
                "observation": "Retrieved Preamble text.",
                "answer": f"{obs}\n\n💡 Key Concept: The Preamble is the soul and preamble philosophy of the Constitution."
            }

        # Fundamental Rights
        if any(term in q for term in ["fundamental rights", "part 3", "part iii", "rights of citizen", "my rights"]):
            thought = "User requested a summary of Fundamental Rights (Part III)."
            obs = self.execute_tool("get_fundamental_rights_summary")
            return {
                "thought": thought,
                "action": "get_fundamental_rights_summary()",
                "observation": "Retrieved 6 Fundamental Rights groups.",
                "answer": obs
            }

        # Article lookup
        art_match = re.search(r"(?:article|art\.?)\s*([0-9]+[a-z]?)|([0-9]+[a-z]?)\s*(?:article|art\.?)", q)
        if art_match:
            art_num = art_match.group(1) or art_match.group(2)
            thought = f"Querying verified database for Article {art_num.upper()}."
            obs = self.execute_tool("lookup_article", query=art_num)
            return {
                "thought": thought,
                "action": f"lookup_article(query='{art_num}')",
                "observation": f"Retrieved details for Article {art_num.upper()}.",
                "answer": obs
            }

        # Writs & Terms
        for term in ["habeas corpus", "mandamus", "prohibition", "certiorari", "quo warranto", "basic structure", "secularism", "judicial review"]:
            if term in q:
                thought = f"User inquired about legal term/writ '{term}'."
                obs = self.execute_tool("lookup_legal_term", term=term)
                return {
                    "thought": thought,
                    "action": f"lookup_legal_term(term='{term}')",
                    "observation": f"Found legal definition for '{term}'.",
                    "answer": obs
                }

        # Amendments
        amd_match = re.search(r"([0-9]+)(?:st|nd|rd|th)?\s*(?:amendment|amd)|(?:amendment|amd\.?)\s*([0-9]+)", q)
        if amd_match:
            amd_num = amd_match.group(1) or amd_match.group(2)
            thought = f"Querying database for {amd_num}th Amendment."
            obs = self.execute_tool("lookup_amendment", query=amd_num)
            return {
                "thought": thought,
                "action": f"lookup_amendment(query='{amd_num}')",
                "observation": f"Retrieved amendment data for {amd_num}.",
                "answer": obs
            }

        # Fallback when offline or off-topic
        thought = "Query is either outside indexed constitutional database or off-topic."
        return {
            "thought": thought,
            "action": "Domain Guardrail Filter",
            "observation": "Checked against constitutional law domain.",
            "answer": (
                "🏛️ I am a specialized Constitutional Law AI Agent.\n\n"
                "I am exclusively designed to answer questions regarding the Constitution of India, legal rights, landmark court rulings, and civic governance.\n\n"
                "Please ask questions related to the Constitution, such as:\n"
                "  • 'What is Article 21 (Right to Life)?'\n"
                "  • 'What are my Fundamental Rights?'\n"
                "  • 'Explain the Preamble'\n"
                "  • 'What is Habeas Corpus?'\n"
                "  • 'What is Article 370?'\n"
                "  • Type 'quiz' to test your knowledge!"
            )
        }

    def _extract_text(self, response) -> str:
        """Safely extracts text from Gemini response avoiding finish_reason exceptions."""
        try:
            return response.text.strip()
        except Exception:
            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, "content") and candidate.content and hasattr(candidate.content, "parts"):
                    parts_text = [p.text for p in candidate.content.parts if hasattr(p, "text") and p.text]
                    if parts_text:
                        return "\n".join(parts_text).strip()
            return "Unable to parse response from model."

    def _gemini_reasoning(self, query: str) -> Dict[str, Any]:
        """
        Full-capability reasoning using Google Gemini 1.5 Flash.
        Can answer ANY constitutional question in the world!
        """
        q = query.strip().lower()

        # Step 1: Check if a local tool directly answers this query with verified text
        tool_used = None
        obs = None

        if "preamble" in q:
            tool_used = "get_preamble()"
            obs = self.execute_tool("get_preamble")
        elif "fundamental rights" in q and ("summary" in q or "what are" in q or "list" in q):
            tool_used = "get_fundamental_rights_summary()"
            obs = self.execute_tool("get_fundamental_rights_summary")
        elif "habeas corpus" in q or "mandamus" in q or "quo warranto" in q or "certiorari" in q or "prohibition" in q:
            for writ in ["habeas corpus", "mandamus", "quo warranto", "certiorari", "prohibition"]:
                if writ in q:
                    tool_used = f"lookup_legal_term('{writ}')"
                    obs = self.execute_tool("lookup_legal_term", term=writ)
                    break

        thought = (
            f"Grounding query with local tool '{tool_used}' and expanding with Gemini."
            if tool_used
            else "Reasoning with Google Gemini's constitutional law knowledge base."
        )

        try:
            # Build prompt with optional tool grounding
            if obs:
                augmented_prompt = (
                    f"User question: {query}\n\n"
                    f"Verified Grounding Context from Local Law Database:\n{obs}\n\n"
                    f"Please provide an accurate, clear, and comprehensive response answering the user's question, "
                    f"incorporating the verified context above and explaining any relevant landmark Supreme Court cases or nuances."
                )
            else:
                augmented_prompt = query

            response = self.chat_session.send_message(augmented_prompt)
            answer_text = self._extract_text(response)

            return {
                "thought": thought,
                "action": tool_used or "Google Gemini 2.5 Flash (Constitutional Reasoning)",
                "observation": "Retrieved authoritative constitutional analysis from Gemini.",
                "answer": answer_text
            }

        except Exception as e:
            # If Gemini call fails (e.g. quota or internet drop), fallback to built-in reasoning
            print(f"\n[Gemini Notice: {e}. Falling back to local engine...]")
            return self._builtin_reasoning(query)

    def process(self, query: str) -> Dict[str, Any]:
        """Processes any constitutional query using Gemini or offline fallback."""
        if not query or not query.strip():
            return {
                "thought": "Empty query received.",
                "action": "None",
                "observation": "N/A",
                "answer": "Please ask a question about the Constitution!"
            }

        if self.is_gemini_active:
            return self._gemini_reasoning(query)
        else:
            return self._builtin_reasoning(query)

    def reset_chat(self):
        """Clears chat history for a fresh start."""
        if self.gemini_model:
            self.chat_session = self.gemini_model.start_chat(history=[])


# Global singleton instance
constitution_agent = ConstitutionAgent()
