"""
Requirement Parser for Design Synthesis
"""
import uuid
import time
from typing import Dict, Any, List
import re


class RequirementParser:
    """
    Parses natural language requirements into structured parameters
    """

    @staticmethod
    def parse(requirement_text: str) -> Dict[str, Any]:
        """
        Parse requirements from natural language
        """
        start_time = time.time()
        
        requirements = {
            "raw_text": requirement_text,
            "extracted_parameters": {},
            "domain": "mechanical",
            "part_types": [],
            "constraints": [],
            "assumptions": []
        }
        
        # Extract payload
        text_lower = requirement_text.lower()
        
        # Detect domain detection
        if "drone" in text_lower:
            requirements["domain"] = "aerospace"
            requirements["part_types"].append("drone_arm")
        elif "robot" in text_lower:
            requirements["domain"] = "robotics"
        
        # Extract payload
        payload_match = re.search(r'(\d+(?:\.\d+)?)\s*(kg|g|lb)', text_lower)
        if payload_match:
            value = float(payload_match.group(1))
            unit = payload_match.group(2)
            if unit == 'g':
                value /= 1000
            elif unit == 'lb':
                value *= 0.453592
            requirements["extracted_parameters"]["payload_kg"] = value
        
        # Extract dimensions
        length_match = re.search(r'length\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(mm|cm|m)', text_lower)
        if length_match:
            value = float(length_match.group(1))
            unit = length_match.group(2)
            if unit == 'cm':
                value *= 10
            elif unit == 'm':
                value *= 1000
            requirements["extracted_parameters"]["length_mm"] = value
        
        return requirements
