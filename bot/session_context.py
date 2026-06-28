"""
Active session context for correlating TMDB, LLM, and service API logs within a bot interaction.

Uses a ContextVar so clients can attach session_id to outbound requests without
threading it through every method signature.
"""

from contextvars import ContextVar
from typing import Optional

session_id_var: ContextVar[Optional[str]] = ContextVar('session_id', default=None)


def get_session_id() -> Optional[str]:
    """Return the current session ID, if any."""
    return session_id_var.get()


def set_session_id(session_id: str):
    """Set the active session ID; returns a token for reset()."""
    return session_id_var.set(session_id)


def reset_session_id(token) -> None:
    """Restore the previous session ID context."""
    session_id_var.reset(token)
