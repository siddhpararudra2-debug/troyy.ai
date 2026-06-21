from typing import Dict, List
from datetime import datetime
from collaboration.schemas.collab_models import Notification
from collaboration.schemas.enums import NotificationType

class NotificationService:
    def __init__(self):
        self.notifications: Dict[str, List[Notification]] = {}  # user_id -> [notifications]
        
    def send(self, user_id: str, notification_type: NotificationType,
            title: str, message: str, link: str = None) -> Notification:
        notif = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link
        )
        self.notifications.setdefault(user_id, []).append(notif)
        return notif
        
    def get_unread(self, user_id: str) -> List[Notification]:
        return [n for n in self.notifications.get(user_id, []) if not n.read]
        
    def mark_read(self, user_id: str, notification_id: str):
        for n in self.notifications.get(user_id, []):
            if n.id == notification_id:
                n.read = True
                return
                
    def get_all(self, user_id: str) -> List[Notification]:
        return self.notifications.get(user_id, [])
