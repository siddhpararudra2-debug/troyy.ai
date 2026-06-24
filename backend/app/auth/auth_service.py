"""
Auth Service - Orchestrates authentication flows
"""
import uuid
import logging
from typing import Dict, Any, Optional
from app.auth.session_manager import SessionManager
from app.auth.identity_provider import IdentityProvider

logger = logging.getLogger(__name__)


class AuthService:
    """Core authentication service"""

    def __init__(
        self,
        session_manager: Optional[SessionManager] = None,
        identity_provider: Optional[IdentityProvider] = None,
    ):
        self.session_manager = session_manager or SessionManager()
        self.identity_provider = identity_provider or IdentityProvider()

    async def login_with_provider(
        self,
        provider_name: str,
        code: str,
        state: str,
    ) -> Dict[str, Any]:
        """Login with OAuth/OIDC provider"""
        # Exchange code for token
        tokens = await self.identity_provider.exchange_code_for_tokens(
            provider_name, code, state
        )
        # Get user info
        user_info = await self.identity_provider.get_user_info(
            provider_name, tokens["access_token"]
        )
        # Create session
        session = self.session_manager.create_session(
            user_id=user_info["id"],
            user_data=user_info,
        )
        return {
            "session": session,
            "user": user_info,
        }

    def logout(self, session_id: str) -> None:
        """Logout a user"""
        self.session_manager.delete_session(session_id)
        logger.info(f"User logged out of session {session_id}")

    def verify_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Verify a session is valid"""
        return self.session_manager.get_session(session_id)
