"""
RBAC Engine for Security Module
Provides comprehensive role-based access control.
"""
import logging
from typing import Dict, Any, Optional
from app.security.role_manager import RoleManager
from app.security.permissions_manager import PermissionsManager

logger = logging.getLogger(__name__)


class RBACEngine:
    """
    Central RBAC engine that combines role and permissions management.
    """

    def __init__(
        self,
        role_manager: Optional[RoleManager] = None,
        permissions_manager: Optional[PermissionsManager] = None,
    ):
        self.role_manager = role_manager or RoleManager()
        self.permissions_manager = permissions_manager or PermissionsManager()

    async def has_permission(
        self,
        user_id: str,
        required_permission: str,
        resource_id: Optional[str] = None,
    ) -> bool:
        """
        Check if a user has a specific permission (optionally for a resource).
        """
        user_roles = await self.role_manager.get_user_roles(user_id)
        return await self.permissions_manager.check_permission(
            user_id, user_roles, required_permission
        )

    async def get_user_effective_permissions(self, user_id: str) -> Dict[str, Any]:
        """
        Get all effective permissions for a user.
        """
        user_roles = await self.role_manager.get_user_roles(user_id)
        perms = await self.permissions_manager.get_permissions_for_user(user_id, user_roles)
        return {
            "user_id": user_id,
            "roles": user_roles,
            "permissions": perms,
        }
