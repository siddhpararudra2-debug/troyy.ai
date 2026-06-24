"""
Requirement Parser - Parses and classifies engineering requirements.

Capabilities:
- Natural language requirement parsing
- Requirement classification by type
- Structured requirement extraction
- Requirement template support
"""

import re
import uuid
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from enum import Enum

from requirements.requirement_manager import (
    RequirementType,
    RequirementPriority,
    Requirement,
    RequirementManager,
)


class ParsedRequirement:
    """Result of parsing a requirement statement."""

    def __init__(
        self,
        original_text: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        req_type: Optional[RequirementType] = None,
        priority: Optional[RequirementPriority] = None,
        confidence: float = 0.0,
        keywords: Optional[List[str]] = None,
        extracted_entities: Optional[Dict[str, Any]] = None,
        is_valid: bool = True,
        validation_errors: Optional[List[str]] = None,
    ):
        self.original_text = original_text
        self.title = title
        self.description = description
        self.req_type = req_type
        self.priority = priority
        self.confidence = confidence
        self.keywords = keywords or []
        self.extracted_entities = extracted_entities or {}
        self.is_valid = is_valid
        self.validation_errors = validation_errors or []


class RequirementParser:
    """
    Parses natural language requirement statements into structured requirements.
    Classifies requirements by type and extracts key parameters.
    """

    # Patterns for identifying requirement types
    TYPE_PATTERNS: Dict[RequirementType, List[str]] = {
        RequirementType.FUNCTIONAL: [
            r"\bshall\b", r"\bmust\b", r"\bwill\b", r"\bsystem\s+shall\b",
            r"\bprovide\b", r"\bsupport\b", r"\bcapable\s+of\b",
            r"\benable\b", r"\bperform\b", r"\bexecute\b",
        ],
        RequirementType.PERFORMANCE: [
            r"\bwithin\s+\d+\.?\d*\s*%", r"\baccuracy\b", r"\bresolution\b",
            r"\blatency\b", r"\bthroughput\b", r"\bbandwidth\b",
            r"\bresponse\s+time\b", r"\buptime\b", r"\bcapacity\b",
            r"\befficiency\b", r"\bspeed\b", r"\bmaximum\b", r"\bminimum\b",
            r"\b\:?\d+\s*(?:ms|s|Hz|MHz|GHz|MB|GB|TB|kbps|Mbps|Gbps)\b",
        ],
        RequirementType.SAFETY: [
            r"\bsafety\b", r"\bhazard\b", r"\brisk\b", r"\bfail-safe\b",
            r"\bredundancy\b", r"\bprotection\b", r"\bshutdown\b",
            r"\bemergency\b", r"\bcontainment\b", r"\bisolation\b",
            r"\bsafe\s+state\b", r"\bSIL\b", r"\bintegrity\s+level\b",
            r"\bfailure\s+mode\b", r"\bmitigation\b",
        ],
        RequirementType.MANUFACTURING: [
            r"\bmanufactur\w+\b", r"\bfabricat\w+\b", r"\bassembly\b",
            r"\btolerance\b", r"\bproduction\b", r"\bprocess\b",
            r"\bmaterial\b", r"\bcoating\b", r"\bfinish\b",
            r"\bquality\s+control\b", r"\binspection\b", r"\btest\w+\b",
            r"\bISO\s+\d+\b", r"\bstandard\b",
        ],
        RequirementType.MISSION: [
            r"\bmission\b", r"\bobjective\b", r"\bgoal\b", r"\btarget\b",
            r"\bdeploy\w+\b", r"\boperation\b", r"\boperational\b",
            r"\bscenario\b", r"\benvironment\b", r"\bduration\b",
            r"\brange\b", r"\borbit\b", r"\btrajectory\b", r"\bpayload\b",
            r"\bendurance\b",
        ],
        RequirementType.INTERFACE: [
            r"\binterface\b", r"\bconnector\b", r"\bprotocol\b",
            r"\bcompatible\b", r"\bport\b", r"\bbus\b", r"\bcommunication\b",
            r"\bAPI\b", r"\bsignal\b", r"\bpin\b", r"\bwiring\b",
            r"\bdata\s+link\b",
        ],
        RequirementType.RELIABILITY: [
            r"\breliab\w+\b", r"\bMTBF\b", r"\bMTTR\b", r"\blifetime\b",
            r"\bdurability\b", r"\bwarranty\b", r"\bavailability\b",
            r"\bredundancy\b", r"\bfault\s+tolerance\b",
        ],
    }

    # Priority indicators
    PRIORITY_PATTERNS: Dict[RequirementPriority, List[str]] = {
        RequirementPriority.CRITICAL: [
            r"\bcritical\b", r"\bmandatory\b", r"\bshall\b",
            r"\bmust\b", r"\brequired\b", r"\bessential\b",
        ],
        RequirementPriority.HIGH: [
            r"\bhigh\s+priority\b", r"\bimportant\b", r"\bsignificant\b",
            r"\bmajor\b", r"\bkey\b", r"\bprimary\b",
        ],
        RequirementPriority.MEDIUM: [
            r"\bshould\b", r"\bdesirable\b", r"\bpreferable\b",
            r"\brecommended\b",
        ],
        RequirementPriority.LOW: [
            r"\bnice.to.have\b", r"\boptional\b", r"\bwould\s+be\s+nice\b",
            r"\bminor\b", r"\blow\s+priority\b",
        ],
    }

    def __init__(self):
        self._compiled_patterns: Dict[RequirementType, List[re.Pattern]] = {}
        self._compiled_priorities: Dict[RequirementPriority, List[re.Pattern]] = {}
        self._compile_patterns()

    def _compile_patterns(self):
        """Pre-compile regex patterns for performance."""
        for req_type, patterns in self.TYPE_PATTERNS.items():
            self._compiled_patterns[req_type] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]
        for priority, patterns in self.PRIORITY_PATTERNS.items():
            self._compiled_priorities[priority] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]

    def parse(self, text: str) -> ParsedRequirement:
        """
        Parse a natural language requirement statement.
        
        Args:
            text: Natural language requirement text
            
        Returns:
            Parsed requirement with classified type and extracted parameters
        """
        if not text or not text.strip():
            return ParsedRequirement(
                original_text=text,
                is_valid=False,
                validation_errors=["Empty requirement text"],
            )

        # Extract title (first sentence or line)
        title = self._extract_title(text)
        description = text

        # Classify requirement type
        req_type, type_confidence = self._classify_type(text)

        # Determine priority
        priority, priority_confidence = self._determine_priority(text)

        # Extract keywords
        keywords = self._extract_keywords(text)

        # Extract entities (numbers, units, parameters)
        entities = self._extract_entities(text)

        # Calculate overall confidence
        confidence = (type_confidence + priority_confidence) / 2.0

        # Validate
        errors = self._validate(text)

        return ParsedRequirement(
            original_text=text,
            title=title,
            description=description,
            req_type=req_type,
            priority=priority,
            confidence=confidence,
            keywords=keywords,
            extracted_entities=entities,
            is_valid=len(errors) == 0,
            validation_errors=errors,
        )

    def _extract_title(self, text: str) -> str:
        """Extract requirement title from text."""
        # Use first sentence or first line
        sentences = re.split(r'[.!?\n]', text)
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 10:
                if len(sentence) > 100:
                    return sentence[:97] + "..."
                return sentence
        return text[:100] if text else "Untitled Requirement"

    def _classify_type(self, text: str) -> Tuple[Optional[RequirementType], float]:
        """Classify requirement type based on content patterns."""
        scores: Dict[RequirementType, int] = {}
        
        for req_type, patterns in self._compiled_patterns.items():
            score = 0
            for pattern in patterns:
                matches = pattern.findall(text)
                score += len(matches)
            if score > 0:
                scores[req_type] = score

        if not scores:
            return RequirementType.FUNCTIONAL, 0.3

        # Find the best match
        best_type = max(scores, key=scores.get)
        total = sum(scores.values())
        confidence = min(scores[best_type] / max(total / len(scores), 1) * 0.3, 0.95)
        
        return best_type, confidence

    def _determine_priority(self, text: str) -> Tuple[RequirementPriority, float]:
        """Determine requirement priority."""
        scores: Dict[RequirementPriority, int] = {}
        
        for priority, patterns in self._compiled_priorities.items():
            score = 0
            for pattern in patterns:
                matches = pattern.findall(text)
                score += len(matches)
            if score > 0:
                scores[priority] = score

        if not scores:
            return RequirementPriority.MEDIUM, 0.4

        best = max(scores, key=scores.get)
        total = sum(scores.values())
        confidence = min(scores[best] / max(total / len(scores), 1) * 0.3, 0.9)
        
        return best, confidence

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract key terms from requirement text."""
        # Technical keywords
        tech_terms = re.findall(r'\b[A-Z]{2,}\b', text)
        # Units and measurements
        measurements = re.findall(r'\b\w+(?:[-/]\w+)*\s*(?::|of|with|at)\b', text)
        
        keywords = tech_terms
        for m in measurements:
            keywords.extend(m.split())
        
        # Add capitalized terms
        capitalized = re.findall(r'\b[A-Z][a-z]+\b', text)
        keywords.extend([k for k in capitalized if k.lower() not in 
                        ['The', 'This', 'That', 'These', 'Those', 'Each', 'Every']])
        
        return list(set(keywords))[:20]

    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract numerical entities and parameters."""
        entities = {
            "numbers": [],
            "ranges": [],
            "units": [],
            "parameters": [],
        }

        # Extract numbers with units
        number_unit_pattern = r'(\d+\.?\d*)\s*([a-zA-Z°/µ%]+)'
        for match in re.finditer(number_unit_pattern, text):
            entities["numbers"].append({
                "value": float(match.group(1)),
                "unit": match.group(2),
            })

        # Extract ranges (e.g., 10-20, 10 to 20)
        range_pattern = r'(\d+\.?\d*)\s*(?:to|-|–)\s*(\d+\.?\d*)\s*([a-zA-Z%]+)?'
        for match in re.finditer(range_pattern, text):
            entities["ranges"].append({
                "min": float(match.group(1)),
                "max": float(match.group(2)),
                "unit": match.group(3) or "",
            })

        # Extract parameter assignments (e.g., weight < 10kg)
        param_pattern = r'(\w+)\s*(?:=|<=|<|>=|>|:)\s*(\d+\.?\d*)\s*([a-zA-Z%]+)?'
        for match in re.finditer(param_pattern, text):
            entities["parameters"].append({
                "name": match.group(1),
                "value": float(match.group(2)),
                "unit": match.group(3) or "",
            })

        return entities

    def _validate(self, text: str) -> List[str]:
        """Validate requirement text quality."""
        errors = []
        
        if len(text.strip().split()) < 3:
            errors.append("Requirement too short (minimum 3 words)")

        # Check for weak/ambiguous terms
        weak_terms = [
            r'\bappropriate\b', r'\badéquate\b', r'\bsufficient\b',
            r'\befficient\b', r'\buser-friendly\b', r'\betc\b',
            r'\band/or\b', r'\bsupport\b', r'\bminimize\b',
            r'\bmaximize\b', r'\boptimize\b',
        ]
        for pattern in weak_terms:
            if re.search(pattern, text, re.IGNORECASE):
                errors.append(f"Ambiguous term detected: '{pattern}'")
                break

        # Check for testability
        if not re.search(r'\b\d+\b', text):
            if not re.search(r'\bshall\b|\bmust\b|\bwill\b', text, re.IGNORECASE):
                errors.append("Requirement lacks testable criteria or imperative verb")

        return errors

    def parse_batch(self, texts: List[str]) -> List[ParsedRequirement]:
        """Parse multiple requirement statements."""
        return [self.parse(text) for text in texts]

    def create_requirement_from_text(
        self,
        text: str,
        manager: RequirementManager,
        parent_id: Optional[str] = None,
    ) -> Optional[Requirement]:
        """Parse text and create a structured requirement."""
        parsed = self.parse(text)
        if not parsed.is_valid:
            return None

        return manager.create_requirement(
            title=parsed.title or "Untitled",
            description=parsed.description,
            req_type=parsed.req_type or RequirementType.FUNCTIONAL,
            priority=parsed.priority or RequirementPriority.MEDIUM,
            parent_id=parent_id,
            parsed_confidence=parsed.confidence,
            extracted_keywords=parsed.keywords,
            extracted_entities=parsed.extracted_entities,
        )

    def export_to_standard_format(self, requirements: List[Requirement]) -> List[Dict[str, Any]]:
        """Export requirements to a standardized format."""
        return [
            {
                "id": r.id,
                "title": r.title,
                "description": r.description,
                "type": r.req_type.value,
                "priority": r.priority.value,
                "status": r.status.value,
                "source": r.source,
                "owner": r.owner,
                "verification_method": r.verification_method,
            }
            for r in requirements
        ]