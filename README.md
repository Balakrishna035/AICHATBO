# 🏛️ Constitutional Law AI Agent (LangGraph & Gemini Edition)

An **Agentic AI** chatbot specialized in Constitutional Law and Indian Jurisprudence, powered by **LangGraph**, **Google Gemini**, and a verified local legal knowledge base.

---

## 🌟 Key Features

1. **LangGraph StateGraph Workflow**:
   - `analyze_intent` ➔ `search_knowledge_base` ➔ `fetch_legal_data` ➔ `analyze_results` ➔ `generate_response`
   - Complete visibility into agent activities: reasoning, searching, executing tools, and synthesizing judicial doctrines.

2. **Real-Time Streaming & ChatGPT-Style Thinking**:
   - Streams both the agent's step-by-step thinking/activities **AND** token-by-token responses via Server-Sent Events (SSE).
   - Dynamic progress indicators show what the agent is doing at each stage (e.g. searching knowledge base, fetching statutory provisions, analyzing landmark case rulings).

3. **Expandable Execution Steps (UI)**:
   - Displays a brief, non-intrusive progress summary by default (`✓ Thought for 1.4s · 5 execution steps`).
   - Click to expand and view the detailed timeline of tools invoked, parameters passed, and observations retrieved.

4. **Conversational Memory**:
   - Powered by LangGraph checkpointer (`thread_id`) to retain context across multi-turn discussions.

5. **Authoritative Legal Knowledge Base & Tools**:
   - `lookup_article`: Statutory text and judicial significance for key constitutional articles (Arts 12, 13, 14, 15, 19, 21, 21A, 32, 142, 226, 370, etc.).
   - `lookup_landmark_case`: Supreme Court benches, ratios, and doctrines (Kesavananda Bharati, Maneka Gandhi, Puttaswamy, Navtej Johar, Shayara Bano, S.R. Bommai, Minerva Mills).
   - `lookup_legal_term`: All 5 prerogative writs (*Habeas Corpus*, *Mandamus*, *Prohibition*, *Certiorari*, *Quo Warranto*) and constitutional doctrines.
   - `lookup_amendment`: 42nd Mini-Constitution, 44th, 86th, 101st GST.
   - `get_preamble`: Complete text, philosophy, and sovereign values.

---

## 🚀 How to Run the Web Application

1. Open **Command Prompt** or **PowerShell**:
   ```cmd
   cd c:\Users\BalaKrishnaa\Desktop\AICHATBOT
   ```

2. Start the Flask application:
   ```cmd
   python app.py
   ```

3. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

---

## 💻 Optional: Running in Command-Line (CMD)

If you prefer using the terminal directly without a browser:
```cmd
python constitution_cli.py
```
