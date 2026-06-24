"""
Role Manager for Security Module
Manages roles (Admin, Engineering Lead, etc.).
"""
import uuid
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Default roles as specified in the requirements
DEFAULT_ROLES = [
    {"name": "Admin", "description": "Full system access"},
    {"name": "Engineering Lead", "description": "Engineering team lead"},
    {"name": "Mechanical Engineer", "description": "Mechanical engineering work"},
    {"name": "Electronics Engineer", "description": "Electronics engineering work"},
    {"name": "Manufacturing Engineer", "description": "Manufacturing engineering work"},
    {"name": "Reviewer", "description": "Design and document reviews"},
    {"name": "Program Manager", "description": "Program management"},
    {"name": "Viewer", "description": "Read-only access"},
]


class RoleManager:
    """
    Manages roles and their definitions.
    """

    def __init__(self):
        self._roles: Dict[str, Dict[str, Any]] = {}
        self._role_users: Dict[str, List[str]] = {}  # key: role_name, value: user_ids
        # Initialize with default roles
        self._init_default_roles()

    def _init_default_roles(self):
        """
        Initialize the system with default engineering roles.
        """
        for role in DEFAULT_ROLES:
            self._roles[role["name"]] = {
                "id": str(uuid.uuid4()),
                "name": role["name"],
                "description": role["description"],
                "is_system": True,
            }

    async def create_custom_role(
        self,
        name: str,
        description: str,
        permissions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a custom role.
        """
        if name in self._roles:
            raise ValueError(f"Role {name} already exists")
        role = {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "is_system": False,
            "permissions": permissions or [],
        }
        self._roles[name] = role
        logger.info(f"Created custom role: {name}")
        return role

    async def get_role(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a role by name.
        """
        return self._roles.get(name)

    async def list_roles(self) -> List[Dict[str, Any]]:
        """
        List all roles.
        """
        return list(self._roles.values())

    async def assign_role_to_user(
        self,
        user_id: str,
        role_name: str,
    ) -> Dict[str, Any]:
        """
        Assign a role to a user.
        """
        if role_name not in self._roles:
            raise ValueError(f"Role {role_name} does not exist")
        if role_name not in self._role_users:
            self._role_users[role_name] = []
        if user_id not in self._role_users[role_name]:
            self._role_users[role_name].append(user_id)
        logger.info(f"Assigned role {role_name} to user {user_id}")
        return {
            "user_id": user_id,
            "role": role_name,
            "status": "assigned",
        }

    async def get_user_roles(self, user_id: str) -> List[str]:
        """
        Get all roles assigned to a user.
        """
        return [
            role_name
            for role_name, users in self._role_users.items()
            if user_id in users
        ]
