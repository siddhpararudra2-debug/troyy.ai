# Engineering OS — Sprint 2: Engineering Intelligence Core

## Architecture Overview

```
┌────────────────────────────────────────────────────────────────┐
│              Engineering Intelligence Core                      │
├────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Math Engine      │  │  Physics      │  │  Units       │    │
│  │  Symbolic Math    │  │  Mechanics    │  │  Converter   │    │
│  │  Equation Solver  │  │  Fluid/Aero   │  │  Dimensional │    │
│  │  Matrix/Linear    │  │  Thermo/Heat  │  │  Uncertainty │    │
│  │  Numerical        │  │  EMag/Circuits│  │  Propagate   │    │
│  │  Optimization     │  │  Control      │  │              │    │
│  └──────────────────┘  └──────────────┘  └──────────────┘    │
│                                                               │
│  ┌──────────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Calculation      │  │  Reasoning   │  │  Validation  │    │
│  │  Engine           │  │  Engine      │  │  Engine      │    │
│  │  Formula Library  │  │  Trade-offs  │  │  Equation    │    │
│  │  Step-by-step     │  │  Constraints │  │  Physics     │    │
│  │  Full Trace       │  │  Alternatives│  │  Safety      │    │
│  └──────────────────┘  └──────────────┘  └──────────────┘    │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              Report Generator                            │  │
│  │  Engineering Reports · Calculation Reports · HTML/MD    │  │
│  └─────────────────────────────────────────────────────────┘  │
├────────────────────────────────────────────────────────────────┤
│  API: /calculate · /formulas · /validate · /reason · /report  │
│  + Sprint 1: /chat · /memory · /knowledge · /agents           │
└────────────────────────────────────────────────────────────────┘
```

## Components Created

### 1. Engineering Mathematics Engine (`math_engine/` — 5 files)
| File | Capabilities |
|---|---|
| `symbolic_math.py` | SymPy algebra, calculus, series, limits, partial fractions — step-by-step |
| `equation_solver.py` | Linear, quadratic, polynomial, systems, ODE solving |
| `numerical_solver.py` | Bisection, Newton-Raphson, Simpson's rule, Euler/RK4 ODE |
| `matrix_engine.py` | Determinants, inverses, eigenvalues/vectors, linear systems, Gram-Schmidt |
| `optimization_math.py` | Gradient descent, golden section, QP, least squares |

### 2. Physics Engine (`physics/` — 5 files)
| File | Domains Covered |
|---|---|
| `mechanics_engine.py` | Statics, dynamics, beam bending (σ=Mc/I), shear (τ=VQ/Ib), torsion, buckling (Pcr=π²EI/(KL)²), von Mises stress, safety factor |
| `fluid_engine.py` | Reynolds number, lift (L=½ρv²SCl), drag, Bernoulli, Darcy-Weisbach, Mach number |
| `thermodynamics_engine.py` | Ideal gas law, Fourier conduction, Newton cooling, thermal expansion, LMTD heat exchangers |
| `electromagnetics_engine.py` | Ohm's law, power, RC time constant, LC resonance, Coulomb force, filter cutoff, transformer ratio |
| `control_theory_engine.py` | Transfer function gain, 2nd order damping, Ziegler-Nichols PID tuning |

### 3. Units & Dimensional Analysis (`units/` — 3 files)
| File | Capabilities |
|---|---|
| `unit_converter.py` | 60+ engineering units across 17 dimensions (length, force, pressure, energy, power, temperature, etc.) with SI conversion |
| `dimensional_checker.py` | Dimensional consistency checking, Buckingham Pi theorem, formula unit validation |
| `uncertainty_engine.py` | Gaussian uncertainty propagation for add, multiply, divide, power, log |

### 4. Engineering Calculation Engine (`calculations/` — 3 files)
| File | Capabilities |
|---|---|
| `formula_library.py` | 13 formulas across mechanical, aerospace, electrical, thermal with search |
| `calculation_engine.py` | Central orchestrator: formula lookup → parameter validation → symbolic/numeric execution → step tracking → assumptions → LaTeX summary |

### 5. Engineering Reasoning Engine (`reasoning/` — 1 file)
| File | Capabilities |
|---|---|
| `engineering_reasoner.py` | Design option evaluation with weighted criteria, constraint checking, alternative suggestions |

### 6. Validation Engine (`validation_engine/` — 1 file)
| File | Capabilities |
|---|---|
| `equation_validator.py` | Parameter completeness, value reasonableness, safety factor adequacy by application domain |

### 7. Report Generation (`reports/` — 1 file)
| File | Capabilities |
|---|---|
| `report_generator.py` | Auto-generates engineering reports with formula, steps, results tables, assumptions, warnings; exports to Markdown and HTML |

### 8. API (`api/routes_sprint2.py` — 9 endpoints)
| Endpoint | Description |
|---|---|
| `POST /api/v1/calculate` | Execute formula with full step-by-step trace |
| `GET /api/v1/formulas` | List/search Formulas by domain & category |
| `GET /api/v1/formulas/{id}` | Formula details |
| `POST /api/v1/validate` | Validate calculation completeness & reasonableness |
| `POST /api/v1/reason` | Trade-off analysis with weighted criteria |
| `POST /api/v1/report` | Generate engineering report (markdown export) |
| `GET /api/v1/units/convert` | Unit conversion (60+ units) |
| `GET /api/v1/units/systems` | Unit system listing by dimension |
| `GET /api/v1/calculation/{id}` | Get stored calculation |
| `GET /api/v1/report/{id}` | Get stored report |

### 9. Tests (2 files — 35+ test cases)
- `test_math.py`: Symbolic math, equations, matrices, numerical methods, optimization
- `test_physics.py`: Mechanics, fluid dynamics, thermodynamics, electromagnetics, units, dimensional analysis, uncertainty propagation, validation, reports

## Quick Start

```bash
# Install dependencies
pip install -r requirements_sprint1.txt

# Run tests
pytest tests_sprint2/ -v

# Start backend
uvicorn backend.app.main:app --reload --port 8000

# API Docs
# http://localhost:8000/docs
```

## Integration with Sprint 1
Sprint 2 components integrate naturally:
- **Calculation Engine** ← uses **Symbolic Math** + **Physics Engines**
- **Validation** ← uses **Dimensional Checker** + **Unit Converter**
- **Reports** ← uses **Calculation Results** for auto-documentation
- **Agent Framework** ← can invoke `/calculate` and `/reason`
- **Memory System** ← stores calculation results as engineering decisions
- **RAG System** ← indexes formulas as searchable knowledge

## Foundation for Future Modules
This Sprint 2 provides the mathematical and physical foundation for:
- **CAD Generation** (mechanics, matrices, optimization)
- **PCB Generation** (electromagnetics, control theory)
- **FEA** (numerical solvers, matrix methods)
- **CFD** (fluid dynamics, numerical integration)
- **Drone Design** (mechanics, aerodynamics, control)
- **Aerospace Design** (compressible flow, orbital mechanics)
- **Robotics Design** (kinematics, dynamics, control)
- **Optimization Engine** (QP, gradient methods, least squares)
- **Digital Twin System** (physics validation, uncertainty)