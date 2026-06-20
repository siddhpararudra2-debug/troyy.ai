"""
Code Generation Service
"""
import uuid
import time
from datetime import datetime
from app.embedded.schemas.schemas import (
    CodeGenerationRequest,
    CodeGenerationResponse,
    GeneratedCodeProject
)


class CodeGenerationService:
    @staticmethod
    def generate(request: CodeGenerationRequest) -> CodeGenerationResponse:
        start_time = time.time()
        project_struct = [
            "src/main.c",
            "inc/main.h",
            "src/drivers/gpio.c",
            "src/rtos/tasks.c",
            "config/config.h",
            "build/Makefile",
        ]
        modules = ["drivers", "rtos", "sensors", "comms"]
        interfaces = ["uart.h", "i2c.h"]
        config_files = ["config.h", "board_config.h"]
        build_files = ["Makefile", "CMakeLists.txt"]
        return CodeGenerationResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            language=request.language,
            code_project=GeneratedCodeProject(
                project_structure=project_struct,
                modules=modules,
                interfaces=interfaces,
                configuration_files=config_files,
                build_files=build_files,
            ),
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow()
        )
