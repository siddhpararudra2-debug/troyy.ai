"""Campaign Manager - Module 10 for Sprint 13."""
import uuid
from typing import Dict, Any, Optional, List


class CampaignManager:
    def __init__(self):
        self.campaigns: Dict[str, Any] = {}

    def create_campaign(
        self,
        name: str,
        description: Optional[str] = None
    ) -> str:
        campaign_id = str(uuid.uuid4())
        campaign = {
            "id": campaign_id,
            "name": name,
            "description": description,
            "missions": [],
            "status": "planning",
        }
        self.campaigns[campaign_id] = campaign
        return campaign_id

    def add_mission_to_campaign(
        self,
        campaign_id: str,
        mission_id: str
    ) -> bool:
        if campaign_id not in self.campaigns:
            return False
        self.campaigns[campaign_id]["missions"].append(mission_id)
        return True

    def get_campaign(self, campaign_id: str) -> Optional[Any]:
        return self.campaigns.get(campaign_id)

    def list_campaigns(self, status: Optional[str] = None) -> List[Any]:
        campaigns = list(self.campaigns.values())
        if status:
            campaigns = [c for c in campaigns if c["status"] == status]
        return campaigns
