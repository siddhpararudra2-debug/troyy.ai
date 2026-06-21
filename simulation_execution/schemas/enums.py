from enum import Enum

class SolverType(str, Enum):
    OPENFOAM = "OPENFOAM"
    CALCULIX = "CALCULIX"
    CODE_ASTER = "CODE_ASTER"
    ELMER = "ELMER"
    MBDYN = "MBDYN"
    NGSPICE = "NGSPICE"

class SimulationDomain(str, Enum):
    STRUCTURAL = "STRUCTURAL"
    THERMAL = "THERMAL"
    CFD = "CFD"
    ELECTROMAGNETIC = "ELECTROMAGNETIC"
    MULTIBODY = "MULTIBODY"
    CIRCUIT = "CIRCUIT"
    MULTI_PHYSICS = "MULTI_PHYSICS"

class JobStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    TIMEOUT = "TIMEOUT"

class MeshType(str, Enum):
    TETRA = "TETRA"
    HEXA = "HEXA"
    POLY = "POLY"
    HYBRID = "HYBRID"

class TurbulenceModel(str, Enum):
    LAMINAR = "LAMINAR"
    K_EPSILON = "K_EPSILON"
    K_OMEGA_SST = "K_OMEGA_SST"
    SPALART_ALLMARAS = "SPALART_ALLMARAS"
    LES = "LES"
    DES = "DES"
