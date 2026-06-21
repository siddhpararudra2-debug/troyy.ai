import uuid
from typing import Dict, List, Optional
from datetime import datetime
from collaboration.schemas.collab_models import Workspace, Team, User, ActivityEvent
from collaboration.schemas.enums import Role

class WorkspaceService:
    def __init__(self):
        self.workspaces: Dict[str, Workspace] = {}
        self.teams: Dict[str, Team] = {}
        self.users: Dict[str, User] = {}
        self.activity_log: List[ActivityEvent] = []
        
    def create_workspace(self, name: str, project_id: str, creator_id: str) -> Workspace:
        ws = Workspace(name=name, project_id=project_id)
        self.workspaces[ws.id] = ws
        self._log_activity(ws.id, creator_id, "WORKSPACE_CREATED", "WORKSPACE", ws.id)
        return ws
        
    def add_team_to_workspace(self, workspace_id: str, team_id: str):
        ws = self.workspaces.get(workspace_id)
        if not ws:
            raise ValueError(f"Workspace {workspace_id} not found")
        if team_id not in ws.team_ids:
            ws.team_ids.append(team_id)
            
    def create_team(self, name: str, lead_id: str, member_ids: List[str]) -> Team:
        team = Team(name=name, lead_id=lead_id, members=[lead_id] + member_ids)
        self.teams[team.id] = team
        return team
        
    def register_user(self, username: str, email: str, role: Role) -> User:
        user = User(username=username, email=email, role=role)
        self.users[user.id] = user
        return user
        
    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        return self.workspaces.get(workspace_id)
        
    def list_workspaces(self, project_id: Optional[str] = None) -> List[Workspace]:
        if project_id:
            return [w for w in self.workspaces.values() if w.project_id == project_id]
        return list(self.workspaces.values())
        
    def _log_activity(self, workspace_id: str, user_id: str, event_type: str,
                     entity_type: str, entity_id: str, metadata: Dict = None):
        event = ActivityEvent(
            workspace_id=workspace_id,
            user_id=user_id,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata=metadata or {}
        )
        self.activity_log.append(event)
