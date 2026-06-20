"""
Embedded Systems & Firmware API Routes
"""
from fastapi import APIRouter
from app.embedded.schemas.schemas import (
    FirmwareArchitectureRequest, FirmwareArchitectureResponse,
    RTOSRequest, RTOSResponse,
    TaskSchedulingRequest, TaskSchedulingResponse,
    DriverGenerationRequest, DriverGenerationResponse,
    CommunicationStackRequest, CommunicationStackResponse,
    StateMachineRequest, StateMachineResponse,
    SensorIntegrationRequest, SensorIntegrationResponse,
    MotorControlRequest, MotorControlResponse,
    FlightControllerRequest, FlightControllerResponse,
    RoboticsControllerRequest, RoboticsControllerResponse,
    CodeGenerationRequest, CodeGenerationResponse
)
from app.embedded.services.firmware_architecture_service import FirmwareArchitectureService
from app.embedded.services.rtos_service import RTOSService
from app.embedded.services.task_scheduler_service import TaskSchedulerService
from app.embedded.services.driver_generation_service import DriverGenerationService
from app.embedded.services.communication_stack_service import CommunicationStackService
from app.embedded.services.state_machine_service import StateMachineService
from app.embedded.services.sensor_integration_service import SensorIntegrationService
from app.embedded.services.motor_control_service import MotorControlService
from app.embedded.services.flight_controller_service import FlightControllerService
from app.embedded.services.robotics_controller_service import RoboticsControllerService
from app.embedded.services.code_generation_service import CodeGenerationService


router = APIRouter(prefix="/embedded", tags=["Embedded Systems"])


@router.post("/architecture", response_model=FirmwareArchitectureResponse)
async def generate_firmware_architecture(request: FirmwareArchitectureRequest):
    return FirmwareArchitectureService.generate(request)


@router.post("/rtos", response_model=RTOSResponse)
async def generate_rtos_configuration(request: RTOSRequest):
    return RTOSService.generate(request)


@router.post("/tasks", response_model=TaskSchedulingResponse)
async def generate_task_schedule(request: TaskSchedulingRequest):
    return TaskSchedulerService.generate(request)


@router.post("/drivers", response_model=DriverGenerationResponse)
async def generate_drivers(request: DriverGenerationRequest):
    return DriverGenerationService.generate(request)


@router.post("/communications", response_model=CommunicationStackResponse)
async def generate_communication_stack(request: CommunicationStackRequest):
    return CommunicationStackService.generate(request)


@router.post("/state-machines", response_model=StateMachineResponse)
async def generate_state_machine(request: StateMachineRequest):
    return StateMachineService.generate(request)


@router.post("/sensors", response_model=SensorIntegrationResponse)
async def generate_sensor_integration(request: SensorIntegrationRequest):
    return SensorIntegrationService.generate(request)


@router.post("/motor-control", response_model=MotorControlResponse)
async def generate_motor_control(request: MotorControlRequest):
    return MotorControlService.generate(request)


@router.post("/flight-controller", response_model=FlightControllerResponse)
async def generate_flight_controller(request: FlightControllerRequest):
    return FlightControllerService.generate(request)


@router.post("/robotics-controller", response_model=RoboticsControllerResponse)
async def generate_robotics_controller(request: RoboticsControllerRequest):
    return RoboticsControllerService.generate(request)


@router.post("/generate-code", response_model=CodeGenerationResponse)
async def generate_code(request: CodeGenerationRequest):
    return CodeGenerationService.generate(request)
