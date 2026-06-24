"""
Program Manager for Portfolio Module
Manages programs.
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ProgramManager:
    """
    Manages programs (groups of projects).
    """

    def __init__(self):
        self._programs: Dict[str, Dict[str, Any]] = {}

    async def create_program(
        self,
        name: str,
        portfolio_id: str,
        description: str = "",
    ) -> Dict[str, Any]:
        program = {
            "id": str(uuid.uuid4()),
            "name": name,
            "portfolio_id": portfolio_id,
            "description": description,
            "projects": [],
            "created_at": datetime.utcnow().isoformat(),
        }
        self._programs[program["id"]] = program
        return program
