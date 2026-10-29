"""
constitution_cli.py - Interactive Command-Line (CMD) Interface for Constitution AI Agent.

Run this directly in your terminal:
    python constitution_cli.py
"""

import sys
import os

# Ensure UTF-8 output encoding on Windows Command Prompt / PowerShell
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from constitution_agent import constitution_agent
from constitution_tools import get_random_quiz, ARTICLES_DB, TERMS_DB

# ANSI color codes for rich CMD output
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_banner():
    if constitution_agent.is_gemini_active:
        model_name = getattr(constitution_agent, "active_model_name", "Gemini")
        engine_status = f"{GREEN}🌟 Google {model_name} (Live AI - Answers ALL Questions){RESET}"
    else:
        engine_status = f"{YELLOW}⚡ Built-in Local Engine (Offline Mode - Type 'key' to connect Gemini){RESET}"

    banner = f"""
{CYAN}========================================================================{RESET}
{BOLD}🏛️  CONSTITUTIONAL LAW AI AGENT (CMD TERMINAL EDITION) 🇮🇳{RESET}
{CYAN}========================================================================{RESET}
{YELLOW}• Active Engine:{RESET}  {engine_status}
{YELLOW}• Specialization:{RESET} Indian Constitution, Articles, Landmark Cases & Writs
{YELLOW}• Commands:{RESET}       Type {GREEN}'quiz'{RESET} to test your knowledge,
                    Type {GREEN}'articles'{RESET} to see key articles index,
                    Type {GREEN}'writs'{RESET} to see the 5 constitutional writs,
                    Type {GREEN}'key'{RESET} to enter or update your Gemini API key,
                    Type {GREEN}'clear'{RESET} to clean the screen,
                    Type {RED}'exit'{RESET} or {RED}'quit'{RESET} to close.
{CYAN}========================================================================{RESET}
"""
    print(banner)


def handle_quiz():
    """Interactive quiz mode right inside CMD."""
    quiz_data = get_random_quiz()
    print(f"\n{YELLOW}📝 --- CONSTITUTIONAL QUIZ ---{RESET}")
    print(f"{BOLD}{quiz_data['question']}{RESET}\n")
    for opt in quiz_data["options"]:
        print(f"   {opt}")

    print()
    user_choice = input(f"{CYAN}Your choice (A/B/C/D): {RESET}").strip().upper()

    if user_choice == quiz_data["answer"]:
        print(f"\n{GREEN}✅ CORRECT!{RESET}")
    else:
        print(f"\n{RED}❌ INCORRECT. Correct answer is {quiz_data['answer']}.{RESET}")

    print(f"💡 {quiz_data['explanation']}\n")


def show_articles_index():
    """Prints a quick reference index of key articles in the database."""
    print(f"\n{YELLOW}📖 Key Constitutional Articles Reference:{RESET}")
    print("-" * 65)
    for num, art in ARTICLES_DB.items():
        print(f" {BOLD}Article {num.upper():<4}{RESET} : {art['title']}")
    print("-" * 65)
    print("Tip: Ask the agent 'What is Article 21?' or 'What is Article 370?'\n")


def show_writs_index():
    """Prints quick explanation of the 5 constitutional writs under Article 32/226."""
    print(f"\n{MAGENTA}⚖️ The 5 Constitutional Writs (Articles 32 & 226):{RESET}")
    print("-" * 65)
    for term, exp in TERMS_DB.items():
        if term in ["habeas corpus", "mandamus", "prohibition", "certiorari", "quo warranto"]:
            first_line = exp.split("\n")[0]
            print(f" • {BOLD}{term.upper():<14}{RESET} : {first_line}")
    print("-" * 65)
    print("Tip: Ask the agent 'Explain Habeas Corpus in detail'\n")


def handle_api_key_setup():
    """Allows user to paste or enter their Gemini API key directly in CMD."""
    print(f"\n{CYAN}🔑 --- GOOGLE GEMINI API SETUP ---{RESET}")
    print("Get your free Gemini API key from: https://aistudio.google.com/app/apikey")
    key_input = input(f"{YELLOW}Paste your Gemini API Key here (or press Enter to cancel): {RESET}").strip()

    if not key_input:
        print(f"{YELLOW}Key entry cancelled. Continuing in current mode.{RESET}\n")
        return

    print(f"{CYAN}Validating and connecting to Gemini...{RESET}")
    success = constitution_agent.set_api_key(key_input, save_to_env=True)

    if success:
        print(f"\n{GREEN}✅ SUCCESS! Google Gemini 1.5 Flash is now connected and saved to .env!{RESET}")
        print(f"{GREEN}The agent can now answer ANY question about constitutional law, history, or cases.{RESET}\n")
    else:
        print(f"\n{RED}❌ Could not connect to Gemini. Please verify that your API key is correct.{RESET}\n")


def main():
    # Enable ANSI escape sequences on Windows Command Prompt
    os.system("")

    print_banner()

    # If Gemini is not configured, inform the user they can enable it anytime
    if not constitution_agent.is_gemini_active:
        print(f"{YELLOW}💡 Tip: To enable the AI to answer ANY constitutional question using Google Gemini,{RESET}")
        print(f"{YELLOW}   type {GREEN}'key'{YELLOW} and paste your free key, or continue with offline queries.{RESET}\n")

    while True:
        try:
            # Prompt the user for input
            prompt = input(f"{BOLD}User >> {RESET}").strip()

            # Ignore empty lines
            if not prompt:
                continue

            # Command shortcuts
            cmd_lower = prompt.lower()
            if cmd_lower in ["exit", "quit", "q"]:
                print(f"\n{GREEN}Thank you for exploring the Constitution! Goodbye.{RESET}\n")
                break

            elif cmd_lower in ["clear", "cls"]:
                os.system("cls" if os.name == "nt" else "clear")
                print_banner()
                continue

            elif cmd_lower in ["quiz", "test"]:
                handle_quiz()
                continue

            elif cmd_lower in ["articles", "list articles"]:
                show_articles_index()
                continue

            elif cmd_lower in ["writs", "list writs"]:
                show_writs_index()
                continue

            elif cmd_lower in ["key", "api", "gemini"]:
                handle_api_key_setup()
                continue

            elif cmd_lower in ["new", "reset"]:
                constitution_agent.reset_chat()
                print(f"\n{GREEN}🔄 Chat context has been reset for a fresh conversation.{RESET}\n")
                continue

            elif cmd_lower in ["help", "?"]:
                print_banner()
                continue

            # Delegate to Agentic AI Reasoning Loop
            print(f"\n{CYAN}⚡ [Agent is thinking...]{RESET}")
            result = constitution_agent.process(prompt)

            # Display the internal Agent ReAct steps (Agentic transparency)
            print(f"{YELLOW}💭 [THOUGHT]:{RESET} {result.get('thought', 'Reasoning...')}")
            print(f"{GREEN}⚡ [ACTION]:{RESET}  {result.get('action', 'Direct Reply')}")
            if result.get("observation") and result.get("observation") != "N/A":
                print(f"{MAGENTA}🔍 [OBSERVATION]:{RESET} {result.get('observation')}")

            # Display final synthesized answer
            print(f"\n{BOLD}🏛️  CONSTITUTION AGENT:{RESET}\n")
            print(result.get("answer", "No response generated."))
            print(f"\n{'-' * 65}\n")

        except KeyboardInterrupt:
            # User pressed Ctrl+C
            print(f"\n\n{YELLOW}Session interrupted. Goodbye!{RESET}\n")
            sys.exit(0)
        except Exception as e:
            print(f"\n{RED}An error occurred: {str(e)}{RESET}\n")


if __name__ == "__main__":
    main()
