from datetime import datetime, timezone
from typing import Dict, List

# In-memory session store (replace with Redis in production).
_MEMORY: Dict[str, Dict] = {}


def get_user_state(user_id: str) -> Dict:
    key = str(user_id)
    return _MEMORY.setdefault(
        key,
        {
            "last_products": [],
            "pending_checkout": False,
            "history": [],
        },
    )


def set_last_products(user_id: str, products: List[Dict]):
    state = get_user_state(user_id)
    state["last_products"] = products


def mark_checkout_pending(user_id: str, pending: bool):
    state = get_user_state(user_id)
    state["pending_checkout"] = pending


def append_history(user_id: str, role: str, content: str, metadata: Dict | None = None):
    state = get_user_state(user_id)
    state["history"].append(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "role": role,
            "content": content,
            "metadata": metadata or {},
        }
    )


def get_user_history(user_id: str) -> List[Dict]:
    state = get_user_state(user_id)
    return state.get("history", [])


def list_histories() -> List[Dict]:
    sessions: List[Dict] = []
    for user_id, state in _MEMORY.items():
        history = state.get("history", [])
        sessions.append(
            {
                "user_id": user_id,
                "message_count": len(history),
                "last_message": history[-1] if history else None,
                "history": history,
            }
        )

    sessions.sort(
        key=lambda x: (x.get("last_message") or {}).get("timestamp", ""),
        reverse=True,
    )
    return sessions
