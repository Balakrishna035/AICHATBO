"""
app.py - The Flask Web Server for the Constitutional Law AI Agent.

Features:
1. Real-Time Streaming Endpoint (/chat/stream) using Server-Sent Events (SSE).
   Streams LangGraph execution steps (reasoning, tool calls, analysis)
   and token-by-token response text.
2. Synchronous Chat API (/chat) for non-streaming clients.
3. Conversational Memory Management (/reset).
4. Tools and Capabilities Inspection (/tools).
5. Modern, responsive web interface serving templates/index.html.
"""

import os
import json
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from law_langgraph_agent import (
    stream_law_agent_execution,
    execute_law_agent_sync,
    clear_session_memory,
    _active_model_name,
    _gemini_client
)
from constitution_tools import (
    CONSTITUTION_TOOLS,
    ARTICLES_DB,
    CASES_DB,
    TERMS_DB,
    AMENDMENTS_DB
)

# Initialize Flask application
app = Flask(__name__)


@app.route("/")
def index():
    """Renders the Constitutional Law Chatbot web interface."""
    return render_template("index.html")


@app.route("/chat/stream", methods=["POST"])
def chat_stream():
    """
    Real-Time SSE Streaming Endpoint:
    Receives JSON: { "message": "...", "thread_id": "session_xxx" }
    Streams:
      - 'status' events (current agent activity: searching, fetching data, etc.)
      - 'step' events (detailed completed execution step for expandable UI)
      - 'token' events (progressive text generation)
      - 'done' event (completion with total steps and execution time)
    """
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Invalid request: 'message' is required."}), 400

        user_message = data.get("message", "").strip()
        thread_id = data.get("thread_id", "default_session").strip() or "default_session"

        if not user_message:
            return jsonify({"error": "Message cannot be empty."}), 400

        def generate_sse():
            try:
                for event in stream_law_agent_execution(user_message, thread_id):
                    yield f"data: {json.dumps(event)}\n\n"
            except Exception as e:
                err_event = {
                    "type": "error",
                    "message": f"Agent error during execution: {str(e)}"
                }
                yield f"data: {json.dumps(err_event)}\n\n"

        return Response(
            stream_with_context(generate_sse()),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive"
            }
        )

    except Exception as e:
        return jsonify({"error": f"Failed to initiate stream: {str(e)}"}), 500


@app.route("/chat", methods=["POST"])
def chat():
    """Synchronous chat endpoint (JSON fallback)."""
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Invalid request: 'message' is required."}), 400

        user_message = data.get("message", "").strip()
        thread_id = data.get("thread_id", "default_session").strip() or "default_session"

        result = execute_law_agent_sync(user_message, thread_id)
        return jsonify({
            "status": "success",
            "reply": result["reply"],
            "steps": result["steps"],
            "duration": result["duration"],
            "mode": result["mode"]
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": f"Server encountered an error: {str(e)}"
        }), 500


@app.route("/reset", methods=["POST"])
def reset():
    """Resets conversational memory for a given thread_id."""
    data = request.get_json() or {}
    thread_id = data.get("thread_id", "default_session")
    clear_session_memory(thread_id)
    return jsonify({"status": "success", "message": f"Memory cleared for {thread_id}."})


# --- CHAT SESSIONS & HISTORY PERSISTENCE ENDPOINTS ---

import chat_store

@app.route("/api/chats", methods=["GET"])
def get_all_chats():
    """Returns list of all saved chat sessions."""
    chats = chat_store.list_chats()
    return jsonify({"status": "success", "chats": chats})


@app.route("/api/chats/<chat_id>", methods=["GET"])
def get_chat_detail(chat_id):
    """Retrieves full conversation with messages and thinking steps for a session."""
    chat = chat_store.get_chat(chat_id)
    if not chat:
        return jsonify({"status": "error", "error": "Chat session not found."}), 404
    return jsonify({"status": "success", "chat": chat})


@app.route("/api/chats/<chat_id>", methods=["DELETE"])
def delete_chat_session(chat_id):
    """Deletes a specific chat session."""
    success = chat_store.delete_chat(chat_id)
    clear_session_memory(chat_id)
    return jsonify({"status": "success" if success else "error"})


@app.route("/api/chats", methods=["DELETE"])
def clear_all_chat_sessions():
    """Clears all stored chat history."""
    chat_store.clear_all_chats()
    return jsonify({"status": "success", "message": "All chat history cleared."})



@app.route("/tools", methods=["GET"])
def get_tools():
    """Returns agent capabilities, legal tools, and active engine configuration."""
    tools_info = [
        {"name": name, "description": details["description"]}
        for name, details in CONSTITUTION_TOOLS.items()
    ]
    return jsonify({
        "mode": "LangGraph Legal AI Agent",
        "is_active": True,
        "model": "Legal AI Agent",
        "tools": tools_info
    })


if __name__ == "__main__":
    print("\n=======================================================")
    print("🏛️ Constitutional Law AI Agent (LangGraph Edition)")
    print("🌐 Web UI: http://127.0.0.1:5000")
    print("⚙️ Engine: LangGraph Legal AI Agent")
    print("⚡ Real-Time Streaming: Enabled via SSE (/chat/stream)")
    print("🧠 Conversational Memory: Enabled via LangGraph checkpointer")
    print("=======================================================\n")

    app.run(host="127.0.0.1", port=5000, debug=True)
