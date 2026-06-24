"""
Autonomous Design Engine for Engineering OS
Orchestrates design generation, evaluation, and refinement.
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.autonomous_design.design_generator import DesignGenerator
from app.autonomous_design.design_evaluator import DesignEvaluator
from app.autonomous_design.design_refiner import DesignRefiner

logger = logging.getLogger(__name__)


class DesignEngine:
    """
    Core autonomous design engine that orchestrates the complete design process:
    generate → evaluate → refine → repeat until optimal design is found.
    """

    def __init__(
        self,
        generator: Optional[DesignGenerator] = None,
        evaluator: Optional[DesignEvaluator] = None,
        refiner: Optional[DesignRefiner] = None,
    ):
        self.generator = generator or DesignGenerator()
        self.evaluator = evaluator or DesignEvaluator()
        self.refiner = refiner or DesignRefiner()
        self._designs: Dict[str, Dict] = {}

    async def run_design_process(
        self,
        requirements: str,
        project_id: Optional[str] = None,
        max_iterations: int = 5,
    ) -> Dict[str, Any]:
        """
        Run the complete autonomous design process.
        """
        design_process_id = str(uuid.uuid4())
        logger.info(f"Starting design process {design_process_id}")

        best_design = None
        best_score = -1.0
        design_history = []

        for iteration in range(max_iterations):
            # Step 1: Generate design
            design = await self.generator.generate_design(
                requirements=requirements,
                iteration=iteration,
                project_id=project_id,
            )
            design_history.append(design)
            self._designs[design["design_id"]] = design

            # Step 2: Evaluate design
            evaluation = await self.evaluator.evaluate_design(design, requirements)
            design["evaluation"] = evaluation
            score = evaluation.get("overall_score", 0)
            logger.info(f"Iteration {iteration+1}: design score = {score}")

            # Step 3: Check if current design is best
            if score > best_score:
                best_score = score
                best_design = design

            # Step 4: Check if we're done (pass threshold)
            if score >= 0.95:  # 95% or higher = done
                logger.info("Design meets quality threshold; stopping early")
                break

            # Step 5: Refine design for next iteration
            if iteration < max_iterations - 1:
                design = await self.refiner.refine_design(
                    design=design,
                    evaluation=evaluation,
                    requirements=requirements,
                )

        logger.info(f"Design process complete; best score: {best_score}")
        return {
            "design_process_id": design_process_id,
            "project_id": project_id,
            "best_design": best_design,
            "design_history": design_history,
            "iterations": len(design_history),
            "status": "completed",
            "started_at": datetime.utcnow().isoformat(),
        }
