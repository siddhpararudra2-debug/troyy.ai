from typing import Dict, Set
from collaboration.schemas.enums import Role, Permission

# Role → Permission matrix
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.CHIEF_ENGINEER: {Permission.READ, Permission.WRITE, Permission.REVIEW, Permission.APPROVE, Permission.ADMIN},
    Role.PROGRAM_MANAGER: {Permission.READ, Permission.WRITE, Permission.REVIEW, Permission.APPROVE},
    Role.MECHANICAL_ENGINEER: {Permission.READ, Permission.WRITE, Permission.REVIEW},
    Role.ELECTRONICS_ENGINEER: {Permission.READ, Permission.WRITE, Permission.REVIEW},
    Role.FIRMWARE_ENGINEER: {Permission.READ, Permission.WRITE, Permission.REVIEW},
    Role.SIMULATION_ENGINEER: {Permission.READ, Permission.WRITE, Permission.REVIEW},
    Role.MANUFACTURING_ENGINEER: {Permission.READ, Permission.WRITE, Permission.REVIEW},
    Role.COMPLIANCE_ENGINEER: {Permission.READ, Permission.REVIEW, Permission.APPROVE},
    Role.VIEWER: {Permission.READ},
}

class PermissionsService:
    def has_permission(self, role: Role, permission: Permission) -> bool:
        return permission in ROLE_PERMISSIONS.get(role, set())
        
    def require_permission(self, role: Role, permission: Permission) -> bool:
        if not self.has_permission(role, permission):
            role_val = role.value if hasattr(role, "value") else role
            perm_val = permission.value if hasattr(permission, "value") else permission
            raise PermissionError(f"Role {role_val} lacks permission {perm_val}")
        return True
        
    def get_role_permissions(self, role: Role) -> Set[Permission]:
        return ROLE_PERMISSIONS.get(role, set())
