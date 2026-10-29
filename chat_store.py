"""
chat_store.py - Persistent storage for chat sessions and history.

Features:
- Stores chat conversations in a local JSON file (chat_sessions.json).
- Persists across server restarts, browser refreshes, and multi-tab usage.
- Auto-generates concise, meaningful titles from the first legal query.
- Saves both messages and the full LangGraph execution steps (thinking traces).
"""

import os
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

STORAGE_FILE = os.path.join(os.path.dirname(__file__), "chat_sessions.json")


def _read_data() -> Dict[str, Any]:
    if not os.path.exists(STORAGE_FILE):
        return {"chats": {}}
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict) or "chats" not in data:
                return {"chats": {}}
            return data
    except Exception as e:
        print(f"Warning: Error reading chat_sessions.json: {e}")
        return {"chats": {}}


def _write_data(data: Dict[str, Any]) -> None:
    try:
        temp_file = STORAGE_FILE + ".tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        if os.path.exists(STORAGE_FILE):
            os.replace(temp_file, STORAGE_FILE)
        else:
            os.rename(temp_file, STORAGE_FILE)
    except Exception as e:
        print(f"Error saving chat_sessions.json: {e}")


def _generate_title(first_message: str) -> str:
    """Creates a clean title from the user query."""
    clean = first_message.strip()
    # Remove leading common prefixes
    for prefix in ["what is", "explain", "tell me about", "can you explain", "what does the constitution say about"]:
        if clean.lower().startswith(prefix):
            clean = clean[len(prefix):].strip()
            break
    clean = clean.replace("?", "").replace(".", "").strip()
    if len(clean) > 40:
        clean = clean[:37] + "..."
    return clean.capitalize() or "Constitutional Query"


def list_chats() -> List[Dict[str, Any]]:
    """Returns sorted list of all chat sessions with metadata."""
    data = _read_data()
    chats = data.get("chats", {})
    results = []
    for chat_id, c in chats.items():
        results.append({
            "id": chat_id,
            "title": c.get("title", "New Conversation"),
            "created_at": c.get("created_at", time.time()),
            "updated_at": c.get("updated_at", time.time()),
            "message_count": len(c.get("messages", []))
        })
    # Sort newest updated first
    results.sort(key=lambda x: x["updated_at"], reverse=True)
    return results


def get_chat(chat_id: str) -> Optional[Dict[str, Any]]:
    """Returns the full chat session including all messages and thinking steps."""
    data = _read_data()
    return data.get("chats", {}).get(chat_id)


def save_turn(chat_id: str, user_message: str, bot_message: str, steps: List[Dict[str, Any]], duration: float = 0.0) -> Dict[str, Any]:
    """Appends a user/bot exchange with execution steps to the specified chat session."""
    data = _read_data()
    chats = data.setdefault("chats", {})
    now = time.time()

    if chat_id not in chats:
        title = _generate_title(user_message)
        chats[chat_id] = {
            "id": chat_id,
            "title": title,
            "created_at": now,
            "updated_at": now,
            "messages": []
        }

    chat = chats[chat_id]
    chat["updated_at"] = now

    # Append user message
    chat["messages"].append({
        "role": "user",
        "content": user_message,
        "timestamp": now
    })

    # Append bot message with execution steps
    chat["messages"].append({
        "role": "bot",
        "content": bot_message,
        "steps": steps,
        "duration": duration,
        "timestamp": now
    })

    _write_data(data)
    return chat


def delete_chat(chat_id: str) -> bool:
    """Deletes a single chat session."""
    data = _read_data()
    chats = data.get("chats", {})
    if chat_id in chats:
        del chats[chat_id]
        _write_data(data)
        return True
    return False


def clear_all_chats() -> bool:
    """Clears all stored chat sessions."""
    _write_data({"chats": {}})
    return True
