"""
Permissions Manager for Security Module
Manages fine-grained permissions.
"""
import logging
from typing import Dict, Any, List, Set

logger = logging.getLogger(__name__)

# Define default permissions
DEFAULT_PERMISSIONS = [
    "design.create", "design.read", "design.update", "design.delete",
    "simulation.run", "simulation.read",
    "manufacturing.execute", "manufacturing.read",
    "project.create", "project.read", "project.update",
    "review.start", "review.approve",
    "document.read", "document.write",
]

# Default role-to-permissions mapping
ROLE_PERMISSIONS = {
    "Admin": DEFAULT_PERMISSIONS,
    "Engineering Lead": [
        "design.create", "design.read", "design.update",
        "simulation.run", "simulation.read",
        "project.read", "project.update",
        "review.start", "review.approve",
        "document.read", "document.write",
    ],
    "Mechanical Engineer": [
        "design.create", "design.read", "design.update",
        "simulation.run", "simulation.read",
        "project.read",
        "review.start",
        "document.read", "document.write",
    ],
    "Electronics Engineer": [
        "design.create", "design.read", "design.update",
        "simulation.run", "simulation.read",
        "project.read",
        "review.start",
        "document.read", "document.write",
    ],
    "Manufacturing Engineer": [
        "manufacturing.execute", "manufacturing.read",
        "project.read",
        "document.read",
    ],
    "Reviewer": [
        "review.start", "review.approve",
        "design.read", "simulation.read",
        "project.read", "document.read",
    ],
    "Program Manager": [
        "project.create", "project.read", "project.update",
        "document.read", "simulation.read",
    ],
    "Viewer": ["project.read", "document.read"],
}


class PermissionsManager:
    """
    Manages permissions and assignment to roles.
    """

    def __init__(self):
        self._permissions: Set[str] = set(DEFAULT_PERMISSIONS)
        self._role_permissions: Dict[str, Set[str]] = {
            role: set(perms) for role, perms in ROLE_PERMISSIONS.items()
        }
        self._user_permissions: Dict[str, Set[str]] = {}  # key: user_id, value: permissions

    async def get_permissions_for_role(self, role_name: str) -> List[str]:
        """
        Get all permissions assigned to a role.
        """
        return list(self._role_permissions.get(role_name, []))

    async def get_permissions_for_user(
        self,
        user_id: str,
        user_roles: List[str],
    ) -> List[str]:
        """
        Get all effective permissions for a user (based on roles and direct permissions).
        """
        perms = set()
        # Add permissions from roles
        for role in user_roles:
            perms.update(self._role_permissions.get(role, []))
        # Add direct user permissions
        perms.update(self._user_permissions.get(user_id, []))
        return list(perms)

    async def check_permission(
        self,
        user_id: str,
        user_roles: List[str],
        required_permission: str,
    ) -> bool:
        """
        Check if a user has a specific permission.
        """
        user_perms = await self.get_permissions_for_user(user_id, user_roles)
        return required_permission in user_perms
