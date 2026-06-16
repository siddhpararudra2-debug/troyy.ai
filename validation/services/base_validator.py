from abc import ABC, abstractmethod
from typing import Dict, Any, List
from validation.schemas.validation import ValidationIssueSchema

class BaseValidator(ABC):
    @abstractmethod
    async def validate(self, data: Dict[str, Any]) -> List[ValidationIssueSchema]:
        pass
