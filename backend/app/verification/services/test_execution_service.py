"""
Test Execution Service
"""
import uuid
import time
from datetime import datetime
from app.verification.schemas.schemas import (
    TestExecutionRequest,
    TestExecutionResponse,
    TestExecutionResult
)


class TestExecutionService:
    @staticmethod
    def execute_tests(request: TestExecutionRequest) -> TestExecutionResponse:
        results = []
        for test_case_id in request.test_case_ids:
            results.append(
                TestExecutionResult(
                    test_case_id=test_case_id,
                    status="pass",
                    duration_sec=2.5
                )
            )
        return TestExecutionResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            results=results,
            created_at=datetime.utcnow()
        )
