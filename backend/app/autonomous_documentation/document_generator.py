"""
Document Generator for Autonomous Documentation
Generates basic engineering documents.
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


class DocumentGenerator:
    """
    Generates engineering documents in Markdown format.
    """
    def generate_design_document(
        self,
        project_id: str,
        design: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate a design document for a given design.
        """
        doc_id = str(uuid.uuid4())
        markdown = f"""
# Design Document: {design.get("design_id", "Unnamed Design")}
Project ID: {project_id}
Created: {datetime.utcnow().isoformat()}

## Parameters
{self._dict_to_markdown(design.get("parameters", {}))}

## Evaluation
{self._dict_to_markdown(design.get("evaluation", {}))}
        """.strip()

        return {
            "id": doc_id,
            "type": "design_document",
            "format": "markdown",
            "content": markdown,
            "project_id": project_id,
        }

    def _dict_to_markdown(self, data: Dict[str, Any]) -> str:
        """
        Convert a dictionary to Markdown list.
        """
        lines = []
        for key, value in data.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)
