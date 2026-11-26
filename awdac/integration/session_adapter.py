from typing import Protocol

class ExistingSession(Protocol):
    """Host bridge invoked inside an existing DSH turn."""
    def append_context(self, session_id: str, context: str) -> None: ...

def attach(session: ExistingSession, session_id: str, context: str):
    if context.strip():
        session.append_context(session_id, context)
