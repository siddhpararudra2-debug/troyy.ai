"""
Session Manager - Handles user sessions and tokens
"""
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class SessionManager:
    """In-memory session manager (can be extended to Redis)"""

    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._user_sessions: Dict[str, list] = {}

    def create_session(
        self,
        user_id: str,
        user_data: Dict[str, Any],
        ttl_hours: int = 24,
    ) -> Dict[str, Any]:
        """Create a new user session"""
        session_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "user_data": user_data,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expires_at.isoformat(),
        }
        self._sessions[session_id] = session
        if user_id not in self._user_sessions:
            self._user_sessions[user_id] = []
        self._user_sessions[user_id].append(session_id)
        logger.info(f"Created session for user {user_id}")
        return session

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a session by ID"""
        session = self._sessions.get(session_id)
        if session:
            # Check expiry
            expires = datetime.fromisoformat(session["expires_at"])
            if expires > datetime.utcnow():
                return session
            # Expired - clean up
            self.delete_session(session_id)
        return None

    def delete_session(self, session_id: str) -> None:
        """Delete a session"""
        session = self._sessions.pop(session_id, None)
        if session:
            user_sessions = self._user_sessions.get(session["user_id"], [])
            if session_id in user_sessions:
                user_sessions.remove(session_id)
            logger.info(f"Deleted session {session_id}")
