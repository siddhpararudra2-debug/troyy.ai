"""
Engineering Review System for Engineering OS.
Comprehensive design reviews and approval workflows.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, List, Any
from datetime import datetime
import uuid


class ReviewStatus(str, Enum):
    """Review status states."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    IN_REVIEW = "in_review"
    CHANGES_REQUESTED = "changes_requested"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class ReviewPriority(str, Enum):
    """Review priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ReviewCategory(str, Enum):
    """Types of engineering reviews."""
    DESIGN_REVIEW = "design_review"
    CALCULATION_REVIEW = "calculation_review"
    SAFETY_REVIEW = "safety_review"
    PERFORMANCE_REVIEW = "performance_review"
    MANUFACTURING_REVIEW = "manufacturing_review"
    COST_REVIEW = "cost_review"
    SUSTAINABILITY_REVIEW = "sustainability_review"


@dataclass
class ReviewComment:
    """A review comment."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    reviewer_id: str = ""
    reviewer_name: str = ""
    text: str = ""
    category: str = "general"  # "concern", "suggestion", "question", "general"
    priority: ReviewPriority = ReviewPriority.MEDIUM
    resolved: bool = False
    response: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ReviewCriteria:
    """Criteria for a design review."""
    name: str
    description: str
    weight: float = 1.0  # 0-1, importance weighting
    pass_threshold: float = 0.7  # 0-1, minimum acceptable score
    metrics: List[str] = field(default_factory=list)


@dataclass
class ReviewResult:
    """Result of a single review criterion."""
    criterion: ReviewCriteria
    score: float  # 0-1
    passed: bool
    evidence: str
    reviewer_notes: Optional[str] = None


@dataclass
class EngineeringReview:
    """Comprehensive engineering review."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    review_id: str = ""  # Human-readable ID
    design_id: str = ""
    category: ReviewCategory = ReviewCategory.DESIGN_REVIEW
    status: ReviewStatus = ReviewStatus.DRAFT
    priority: ReviewPriority = ReviewPriority.MEDIUM
    
    # Metadata
    title: str = ""
    description: str = ""
    design_name: str = ""
    design_version: str = ""
    
    # Reviewers
    primary_reviewer_id: str = ""
    primary_reviewer_name: str = ""
    secondary_reviewers: List[Dict[str, str]] = field(default_factory=list)
    assigned_reviewers: List[str] = field(default_factory=list)
    
    # Review criteria and results
    criteria: List[ReviewCriteria] = field(default_factory=list)
    results: List[ReviewResult] = field(default_factory=list)
    
    # Comments and feedback
    comments: List[ReviewComment] = field(default_factory=list)
    
    # Overall assessment
    overall_score: float = 0.0
    passed: bool = False
    recommendation: str = ""
    risk_assessment: str = ""
    
    # Timeline
    created_at: datetime = field(default_factory=datetime.utcnow)
    submitted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


class EngineeringReviewEngine:
    """Manages engineering design reviews."""

    def __init__(self):
        self.review_count = 0
        self.standard_criteria = self._initialize_criteria()

    def _initialize_criteria(self) -> Dict[ReviewCategory, List[ReviewCriteria]]:
        """Initialize standard review criteria."""
        return {
            ReviewCategory.DESIGN_REVIEW: [
                ReviewCriteria(
                    name="Feasibility",
                    description="Design is technically feasible",
                    weight=1.0,
                    pass_threshold=0.8
                ),
                ReviewCriteria(
                    name="Performance",
                    description="Design meets performance requirements",
                    weight=1.0,
                    pass_threshold=0.8
                ),
                ReviewCriteria(
                    name="Cost Effectiveness",
                    description="Design is cost-effective",
                    weight=0.8,
                    pass_threshold=0.7
                ),
                ReviewCriteria(
                    name="Manufacturability",
                    description="Design is manufacturable",
                    weight=0.9,
                    pass_threshold=0.75
                ),
                ReviewCriteria(
                    name="Maintenance",
                    description="Design is maintainable",
                    weight=0.7,
                    pass_threshold=0.7
                )
            ],
            ReviewCategory.CALCULATION_REVIEW: [
                ReviewCriteria(
                    name="Formula Correctness",
                    description="Formulas are correct",
                    weight=1.0,
                    pass_threshold=1.0
                ),
                ReviewCriteria(
                    name="Unit Consistency",
                    description="Units are consistent throughout",
                    weight=1.0,
                    pass_threshold=1.0
                ),
                ReviewCriteria(
                    name="Assumptions",
                    description="Assumptions are valid and documented",
                    weight=1.0,
                    pass_threshold=0.95
                ),
                ReviewCriteria(
                    name="Numerical Accuracy",
                    description="Calculations are accurate",
                    weight=0.95,
                    pass_threshold=0.9
                )
            ],
            ReviewCategory.SAFETY_REVIEW: [
                ReviewCriteria(
                    name="Safety Factors",
                    description="Appropriate safety factors applied",
                    weight=1.0,
                    pass_threshold=0.95
                ),
                ReviewCriteria(
                    name="Failure Analysis",
                    description="Failure modes identified and mitigated",
                    weight=1.0,
                    pass_threshold=0.9
                ),
                ReviewCriteria(
                    name="Hazard Assessment",
                    description="Hazards identified and controlled",
                    weight=1.0,
                    pass_threshold=0.95
                )
            ]
        }

    async def create_review(
        self,
        design_id: str,
        category: ReviewCategory,
        title: str,
        design_name: str,
        design_version: str = "1.0",
        priority: ReviewPriority = ReviewPriority.MEDIUM
    ) -> EngineeringReview:
        """Create a new engineering review."""
        self.review_count += 1
        
        criteria = self.standard_criteria.get(category, [])
        
        review = EngineeringReview(
            review_id=f"REV-{self.review_count:05d}",
            design_id=design_id,
            category=category,
            title=title,
            design_name=design_name,
            design_version=design_version,
            priority=priority,
            criteria=criteria
        )
        
        return review

    async def add_reviewer(
        self,
        review: EngineeringReview,
        reviewer_id: str,
        reviewer_name: str,
        is_primary: bool = False
    ) -> EngineeringReview:
        """Add a reviewer to the review."""
        if is_primary:
            review.primary_reviewer_id = reviewer_id
            review.primary_reviewer_name = reviewer_name
        else:
            review.secondary_reviewers.append({
                "id": reviewer_id,
                "name": reviewer_name
            })
        
        review.assigned_reviewers.append(reviewer_id)
        return review

    async def submit_review(self, review: EngineeringReview) -> EngineeringReview:
        """Submit review for approval."""
        review.status = ReviewStatus.SUBMITTED
        review.submitted_at = datetime.utcnow()
        return review

    async def add_comment(
        self,
        review: EngineeringReview,
        reviewer_id: str,
        reviewer_name: str,
        comment_text: str,
        category: str = "general",
        priority: ReviewPriority = ReviewPriority.MEDIUM
    ) -> EngineeringReview:
        """Add a comment to the review."""
        comment = ReviewComment(
            reviewer_id=reviewer_id,
            reviewer_name=reviewer_name,
            text=comment_text,
            category=category,
            priority=priority
        )
        review.comments.append(comment)
        review.status = ReviewStatus.IN_REVIEW
        return review

    async def score_criterion(
        self,
        review: EngineeringReview,
        criterion_index: int,
        score: float,
        evidence: str,
        reviewer_notes: Optional[str] = None
    ) -> EngineeringReview:
        """Score a review criterion."""
        if criterion_index >= len(review.criteria):
            return review
        
        criterion = review.criteria[criterion_index]
        passed = score >= criterion.pass_threshold
        
        result = ReviewResult(
            criterion=criterion,
            score=score,
            passed=passed,
            evidence=evidence,
            reviewer_notes=reviewer_notes
        )
        
        review.results.append(result)
        return review

    async def calculate_overall_score(self, review: EngineeringReview) -> EngineeringReview:
        """Calculate overall review score."""
        if not review.results:
            review.overall_score = 0.0
            review.passed = False
            return review
        
        # Weighted average
        total_weight = sum(r.criterion.weight for r in review.results)
        weighted_score = sum(
            r.score * r.criterion.weight 
            for r in review.results
        )
        
        review.overall_score = weighted_score / total_weight if total_weight > 0 else 0.0
        
        # Check if all criteria passed
        review.passed = all(r.passed for r in review.results)
        
        # Generate recommendation
        if review.passed:
            review.recommendation = "APPROVED - Design meets all review criteria"
        elif review.overall_score >= 0.85:
            review.recommendation = "CONDITIONAL APPROVAL - Minor issues to address"
        elif review.overall_score >= 0.70:
            review.recommendation = "CHANGES REQUIRED - Significant issues need resolution"
        else:
            review.recommendation = "REJECTED - Design does not meet requirements"
        
        return review

    async def complete_review(
        self,
        review: EngineeringReview,
        final_comments: Optional[str] = None
    ) -> EngineeringReview:
        """Complete and finalize the review."""
        review = await self.calculate_overall_score(review)
        review.completed_at = datetime.utcnow()
        
        if review.passed:
            review.status = ReviewStatus.APPROVED
        elif review.overall_score >= 0.70:
            review.status = ReviewStatus.CHANGES_REQUESTED
        else:
            review.status = ReviewStatus.REJECTED
        
        if final_comments:
            review.metadata["final_comments"] = final_comments
        
        return review

    async def generate_review_report(self, review: EngineeringReview) -> Dict[str, Any]:
        """Generate a comprehensive review report."""
        return {
            "review_id": review.review_id,
            "design_name": review.design_name,
            "design_version": review.design_version,
            "category": review.category.value,
            "status": review.status.value,
            "priority": review.priority.value,
            "primary_reviewer": review.primary_reviewer_name,
            "secondary_reviewers": [r["name"] for r in review.secondary_reviewers],
            "overall_score": review.overall_score,
            "passed": review.passed,
            "recommendation": review.recommendation,
            "criteria_scores": [
                {
                    "criterion": r.criterion.name,
                    "score": r.score,
                    "passed": r.passed,
                    "evidence": r.evidence
                }
                for r in review.results
            ],
            "comments_count": len(review.comments),
            "open_comments": len([c for c in review.comments if not c.resolved]),
            "created_at": review.created_at.isoformat(),
            "completed_at": review.completed_at.isoformat() if review.completed_at else None,
            "recommendation_text": review.recommendation
        }
