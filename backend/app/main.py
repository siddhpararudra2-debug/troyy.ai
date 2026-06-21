"""
Troy — FastAPI Application Entry Point
Main application with lifespan management, router registration, and middleware.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine, async_session_factory
from app.core.logging import setup_logging, get_logger

logger = get_logger("main")

# ── SQL Schema ───────────────────────────────────────────────────
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    domain TEXT NOT NULL CHECK(domain IN ('aerospace', 'drones', 'robotics', 'electronics', 'multi')),
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'archived')),
    metadata_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS calculations (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    domain TEXT NOT NULL,
    formula_id TEXT NOT NULL,
    title TEXT NOT NULL,
    inputs_json TEXT NOT NULL DEFAULT '{}',
    outputs_json TEXT NOT NULL DEFAULT '{}',
    units_json TEXT DEFAULT '{}',
    execution_time_ms REAL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('completed', 'error', 'pending')),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS calculation_steps (
    id TEXT PRIMARY KEY,
    calculation_id TEXT NOT NULL,
    step_order INTEGER NOT NULL,
    step_type TEXT NOT NULL CHECK(step_type IN ('symbolic', 'substitution', 'simplification', 'result', 'unit_conversion')),
    description TEXT NOT NULL,
    latex_expression TEXT NOT NULL,
    expression_json TEXT DEFAULT '{}',
    variables_json TEXT DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    calculation_id TEXT,
    title TEXT NOT NULL,
    doc_type TEXT NOT NULL CHECK(doc_type IN ('calculation_report', 'project_summary', 'custom')),
    format TEXT NOT NULL DEFAULT 'markdown' CHECK(format IN ('markdown', 'html')),
    content TEXT NOT NULL DEFAULT '',
    file_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS memory_entries (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    entry_type TEXT NOT NULL CHECK(entry_type IN ('decision', 'assumption', 'constraint', 'note', 'reference')),
    content TEXT NOT NULL,
    context TEXT DEFAULT '',
    tags_json TEXT DEFAULT '[]',
    relevance_score REAL DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_sessions (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    title TEXT DEFAULT 'New Chat',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    metadata_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_calculations_project ON calculations(project_id);
CREATE INDEX IF NOT EXISTS idx_calculations_domain ON calculations(domain);
CREATE INDEX IF NOT EXISTS idx_calc_steps_calc ON calculation_steps(calculation_id);
CREATE INDEX IF NOT EXISTS idx_documents_project ON documents(project_id);
CREATE INDEX IF NOT EXISTS idx_memory_project ON memory_entries(project_id);
CREATE INDEX IF NOT EXISTS idx_memory_type ON memory_entries(entry_type);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_project ON chat_sessions(project_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages(session_id);

CREATE TABLE IF NOT EXISTS solver_sessions (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    user_query TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS solver_runs (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    domain TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    execution_time_ms REAL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(session_id) REFERENCES solver_sessions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS solver_requirements (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    project_type TEXT,
    mission_type TEXT,
    payload TEXT,
    flight_time TEXT,
    missing_requirements TEXT,
    raw_extracted TEXT,
    FOREIGN KEY(run_id) REFERENCES solver_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS solver_assumptions (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    missing_information TEXT NOT NULL,
    assumption TEXT NOT NULL,
    reasoning TEXT NOT NULL,
    confidence_score TEXT NOT NULL,
    editable INTEGER NOT NULL DEFAULT 1,
    user_override TEXT,
    FOREIGN KEY(run_id) REFERENCES solver_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS solver_constraints (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    category TEXT NOT NULL,
    limit_value TEXT NOT NULL,
    source TEXT NOT NULL,
    FOREIGN KEY(run_id) REFERENCES solver_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS solver_variables (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    name TEXT NOT NULL,
    value REAL,
    unit TEXT,
    description TEXT,
    var_type TEXT NOT NULL,
    FOREIGN KEY(run_id) REFERENCES solver_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS solver_recommendations (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    reasoning TEXT NOT NULL,
    expected_benefits TEXT,
    potential_risks TEXT,
    FOREIGN KEY(run_id) REFERENCES solver_runs(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_solver_runs_session ON solver_runs(session_id);
CREATE INDEX IF NOT EXISTS idx_solver_req_run ON solver_requirements(run_id);
CREATE INDEX IF NOT EXISTS idx_solver_assume_run ON solver_assumptions(run_id);
CREATE INDEX IF NOT EXISTS idx_solver_const_run ON solver_constraints(run_id);
CREATE INDEX IF NOT EXISTS idx_solver_var_run ON solver_variables(run_id);
CREATE INDEX IF NOT EXISTS idx_solver_rec_run ON solver_recommendations(run_id);

CREATE TABLE IF NOT EXISTS solver_selected_formulas (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    formula_id TEXT NOT NULL,
    name TEXT NOT NULL,
    relevance_score REAL,
    reasoning TEXT,
    required_inputs TEXT NOT NULL DEFAULT '[]',
    expected_outputs TEXT NOT NULL DEFAULT '[]',
    dependencies TEXT NOT NULL DEFAULT '[]',
    FOREIGN KEY(run_id) REFERENCES solver_runs(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_solver_selected_formulas_run ON solver_selected_formulas(run_id);

CREATE TABLE IF NOT EXISTS validation_runs (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    solver_run_id TEXT,
    domain TEXT NOT NULL,
    total_errors INTEGER NOT NULL DEFAULT 0,
    total_warnings INTEGER NOT NULL DEFAULT 0,
    is_approved INTEGER NOT NULL DEFAULT 1 CHECK(is_approved IN (0, 1)),
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY(solver_run_id) REFERENCES solver_runs(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS validation_issues (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    severity TEXT NOT NULL CHECK(severity IN ('error', 'warning', 'info')),
    category TEXT NOT NULL,
    message TEXT NOT NULL,
    validator_name TEXT NOT NULL,
    engineering_reasoning TEXT,
    recommendation TEXT,
    FOREIGN KEY(run_id) REFERENCES validation_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS engineering_reviews (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    design_decisions_check TEXT NOT NULL,
    component_choices_check TEXT NOT NULL,
    structural_choices_check TEXT NOT NULL,
    electrical_choices_check TEXT NOT NULL,
    weight_budgets_check TEXT NOT NULL,
    power_budgets_check TEXT NOT NULL,
    thermal_assumptions_check TEXT NOT NULL,
    overall_assessment TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(run_id) REFERENCES validation_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS risk_assessments (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    overall_risk_level TEXT NOT NULL CHECK(overall_risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    risks_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(run_id) REFERENCES validation_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS approval_decisions (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('APPROVED', 'APPROVED WITH CONCERNS', 'REQUIRES REVISION', 'REJECTED')),
    engineering_reasoning TEXT NOT NULL,
    risk_summary TEXT NOT NULL,
    validation_summary TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(run_id) REFERENCES validation_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS audit_reports (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    report_type TEXT NOT NULL,
    format TEXT NOT NULL CHECK(format IN ('markdown', 'html', 'json', 'pdf')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(run_id) REFERENCES validation_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    action TEXT NOT NULL,
    user_id TEXT,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_validation_runs_project ON validation_runs(project_id);
CREATE INDEX IF NOT EXISTS idx_validation_issues_run ON validation_issues(run_id);
CREATE INDEX IF NOT EXISTS idx_reviews_run ON engineering_reviews(run_id);
CREATE INDEX IF NOT EXISTS idx_risks_run ON risk_assessments(run_id);
CREATE INDEX IF NOT EXISTS idx_approvals_run ON approval_decisions(run_id);
CREATE INDEX IF NOT EXISTS idx_audit_reports_run ON audit_reports(run_id);

CREATE TABLE IF NOT EXISTS component_library (
    id TEXT PRIMARY KEY,
    component_type TEXT NOT NULL,
    manufacturer TEXT NOT NULL,
    part_number TEXT NOT NULL UNIQUE,
    description TEXT,
    specifications_json TEXT NOT NULL DEFAULT '{}',
    package TEXT,
    operating_voltage_min REAL,
    operating_voltage_max REAL,
    operating_current_max REAL,
    operating_temp_min REAL,
    operating_temp_max REAL,
    interfaces_json TEXT DEFAULT '[]',
    cost_usd REAL,
    availability_score REAL DEFAULT 1.0,
    datasheet_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS component_recommendations (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    component_type TEXT NOT NULL,
    requirements_json TEXT NOT NULL DEFAULT '{}',
    constraints_json TEXT NOT NULL DEFAULT '{}',
    selected_component_id TEXT,
    alternatives_json TEXT NOT NULL DEFAULT '[]',
    engineering_justification_json TEXT NOT NULL DEFAULT '{}',
    tradeoffs_json TEXT NOT NULL DEFAULT '[]',
    performance_analysis_json TEXT NOT NULL DEFAULT '{}',
    cost_analysis_json TEXT NOT NULL DEFAULT '{}',
    availability_analysis_json TEXT NOT NULL DEFAULT '{}',
    validation_results_json TEXT NOT NULL DEFAULT '{}',
    documentation_json TEXT NOT NULL DEFAULT '{}',
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(selected_component_id) REFERENCES component_library(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS microcontroller_recommendations (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    requirements_json TEXT NOT NULL DEFAULT '{}',
    selected_mcu_id TEXT,
    alternatives_json TEXT NOT NULL DEFAULT '[]',
    gpio_analysis_json TEXT NOT NULL DEFAULT '{}',
    adc_analysis_json TEXT NOT NULL DEFAULT '{}',
    pwm_analysis_json TEXT NOT NULL DEFAULT '{}',
    memory_analysis_json TEXT NOT NULL DEFAULT '{}',
    communication_analysis_json TEXT NOT NULL DEFAULT '{}',
    justification_json TEXT NOT NULL DEFAULT '{}',
    tradeoffs_json TEXT NOT NULL DEFAULT '[]',
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(selected_mcu_id) REFERENCES component_library(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS sensor_recommendations (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    sensor_type TEXT NOT NULL,
    requirements_json TEXT NOT NULL DEFAULT '{}',
    selected_sensor_id TEXT,
    alternatives_json TEXT NOT NULL DEFAULT '[]',
    justification_json TEXT NOT NULL DEFAULT '{}',
    tradeoffs_json TEXT NOT NULL DEFAULT '[]',
    performance_analysis_json TEXT NOT NULL DEFAULT '{}',
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(selected_sensor_id) REFERENCES component_library(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS regulator_recommendations (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    regulator_type TEXT NOT NULL,
    requirements_json TEXT NOT NULL DEFAULT '{}',
    selected_regulator_id TEXT,
    alternatives_json TEXT NOT NULL DEFAULT '[]',
    power_dissipation_analysis_json TEXT NOT NULL DEFAULT '{}',
    efficiency_analysis_json TEXT NOT NULL DEFAULT '{}',
    thermal_analysis_json TEXT NOT NULL DEFAULT '{}',
    justification_json TEXT NOT NULL DEFAULT '{}',
    tradeoffs_json TEXT NOT NULL DEFAULT '[]',
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(selected_regulator_id) REFERENCES component_library(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS mosfet_recommendations (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    requirements_json TEXT NOT NULL DEFAULT '{}',
    selected_mosfet_id TEXT,
    alternatives_json TEXT NOT NULL DEFAULT '[]',
    voltage_analysis_json TEXT NOT NULL DEFAULT '{}',
    current_analysis_json TEXT NOT NULL DEFAULT '{}',
    switching_analysis_json TEXT NOT NULL DEFAULT '{}',
    thermal_analysis_json TEXT NOT NULL DEFAULT '{}',
    justification_json TEXT NOT NULL DEFAULT '{}',
    tradeoffs_json TEXT NOT NULL DEFAULT '[]',
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(selected_mosfet_id) REFERENCES component_library(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS communication_recommendations (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    requirements_json TEXT NOT NULL DEFAULT '{}',
    selected_protocol TEXT NOT NULL,
    alternatives_json TEXT NOT NULL DEFAULT '[]',
    justification_json TEXT NOT NULL DEFAULT '{}',
    tradeoffs_json TEXT NOT NULL DEFAULT '[]',
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS compatibility_analyses (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    components_json TEXT NOT NULL DEFAULT '[]',
    voltage_compatibility_json TEXT NOT NULL DEFAULT '{}',
    current_compatibility_json TEXT NOT NULL DEFAULT '{}',
    logic_level_compatibility_json TEXT NOT NULL DEFAULT '{}',
    communication_compatibility_json TEXT NOT NULL DEFAULT '{}',
    thermal_compatibility_json TEXT NOT NULL DEFAULT '{}',
    overall_compatibility_score REAL NOT NULL,
    issues_json TEXT NOT NULL DEFAULT '[]',
    recommendations_json TEXT NOT NULL DEFAULT '[]',
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS electronics_architectures (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    requirements_json TEXT NOT NULL DEFAULT '{}',
    power_tree_json TEXT NOT NULL DEFAULT '{}',
    signal_architecture_json TEXT NOT NULL DEFAULT '{}',
    communication_architecture_json TEXT NOT NULL DEFAULT '{}',
    subsystem_architecture_json TEXT NOT NULL DEFAULT '{}',
    components_json TEXT NOT NULL DEFAULT '[]',
    documentation_json TEXT NOT NULL DEFAULT '{}',
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS schematics (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    title TEXT NOT NULL,
    author TEXT,
    sheets_json TEXT NOT NULL DEFAULT '[]',
    components_json TEXT NOT NULL DEFAULT '[]',
    nets_json TEXT NOT NULL DEFAULT '[]',
    netlist TEXT,
    bom_json TEXT DEFAULT '{}',
    svg TEXT,
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pcb_projects (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    schematic_id TEXT,
    name TEXT NOT NULL,
    board_width_mm REAL DEFAULT 100.0,
    board_height_mm REAL DEFAULT 80.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pcb_architectures (
    id TEXT PRIMARY KEY,
    pcb_project_id TEXT,
    subsystem_regions_json TEXT NOT NULL DEFAULT '[]',
    power_domains_json TEXT NOT NULL DEFAULT '[]',
    signal_domains_json TEXT NOT NULL DEFAULT '[]',
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pcb_stackups (
    id TEXT PRIMARY KEY,
    pcb_project_id TEXT,
    layer_count INTEGER NOT NULL,
    layers_json TEXT NOT NULL DEFAULT '[]',
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS placement_plans (
    id TEXT PRIMARY KEY,
    pcb_project_id TEXT,
    components_json TEXT NOT NULL DEFAULT '[]',
    placement_regions_json TEXT NOT NULL DEFAULT '[]',
    optimization_score REAL,
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS routing_plans (
    id TEXT PRIMARY KEY,
    pcb_project_id TEXT,
    routing_rules_json TEXT NOT NULL DEFAULT '[]',
    routing_priorities_json TEXT NOT NULL DEFAULT '[]',
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS power_distributions (
    id TEXT PRIMARY KEY,
    pcb_project_id TEXT,
    power_domains_json TEXT NOT NULL DEFAULT '[]',
    power_planes_json TEXT NOT NULL DEFAULT '[]',
    regulator_placement_json TEXT NOT NULL DEFAULT '[]',
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ground_strategies (
    id TEXT PRIMARY KEY,
    pcb_project_id TEXT,
    strategy_type TEXT NOT NULL,
    ground_strategy_json TEXT NOT NULL DEFAULT '{}',
    return_current_analysis_json TEXT NOT NULL DEFAULT '{}',
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS thermal_analyses (
    id TEXT PRIMARY KEY,
    pcb_project_id TEXT,
    power_dissipation_w REAL,
    hot_spots_json TEXT NOT NULL DEFAULT '[]',
    thermal_density_map_json TEXT NOT NULL DEFAULT '{}',
    cooling_recommendations_json TEXT NOT NULL DEFAULT '[]',
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS emi_analyses (
    id TEXT PRIMARY KEY,
    pcb_project_id TEXT,
    emi_risks_json TEXT NOT NULL DEFAULT '[]',
    emc_recommendations_json TEXT NOT NULL DEFAULT '[]',
    loop_area_analysis_json TEXT NOT NULL DEFAULT '{}',
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS drc_results (
    id TEXT PRIMARY KEY,
    pcb_project_id TEXT,
    violations_json TEXT NOT NULL DEFAULT '[]',
    total_errors INTEGER DEFAULT 0,
    total_warnings INTEGER DEFAULT 0,
    is_drc_passed INTEGER DEFAULT 1,
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS manufacturing_reviews (
    id TEXT PRIMARY KEY,
    pcb_project_id TEXT,
    fabrication_constraints_json TEXT NOT NULL DEFAULT '[]',
    assembly_constraints_json TEXT NOT NULL DEFAULT '[]',
    dfm_review_json TEXT NOT NULL DEFAULT '[]',
    dfa_review_json TEXT NOT NULL DEFAULT '[]',
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pcb_review_results (
    id TEXT PRIMARY KEY,
    pcb_project_id TEXT,
    placement_review_json TEXT NOT NULL DEFAULT '[]',
    routing_review_json TEXT NOT NULL DEFAULT '[]',
    power_review_json TEXT NOT NULL DEFAULT '[]',
    grounding_review_json TEXT NOT NULL DEFAULT '[]',
    thermal_review_json TEXT NOT NULL DEFAULT '[]',
    emi_review_json TEXT NOT NULL DEFAULT '[]',
    manufacturability_review_json TEXT NOT NULL DEFAULT '[]',
    approval_status TEXT DEFAULT 'pending',
    overall_score REAL,
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS simulation_projects (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS simulation_runs (
    id TEXT PRIMARY KEY,
    simulation_project_id TEXT,
    simulation_type TEXT NOT NULL,
    parameters_json TEXT NOT NULL DEFAULT '{}',
    status TEXT DEFAULT 'pending',
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS circuit_simulations (
    id TEXT PRIMARY KEY,
    simulation_run_id TEXT,
    voltages_json TEXT NOT NULL DEFAULT '{}',
    currents_json TEXT NOT NULL DEFAULT '{}',
    power_json TEXT NOT NULL DEFAULT '{}',
    waveforms_json TEXT NOT NULL DEFAULT '{}',
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS power_simulations (
    id TEXT PRIMARY KEY,
    simulation_run_id TEXT,
    efficiency REAL,
    power_losses_json TEXT NOT NULL DEFAULT '{}',
    current_flow_json TEXT NOT NULL DEFAULT '{}',
    thermal_loads_json TEXT NOT NULL DEFAULT '{}',
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS thermal_simulations (
    id TEXT PRIMARY KEY,
    simulation_run_id TEXT,
    temperature_rise_json TEXT NOT NULL DEFAULT '{}',
    hotspots_json TEXT NOT NULL DEFAULT '[]',
    cooling_requirements_json TEXT NOT NULL DEFAULT '[]',
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mechanical_simulations (
    id TEXT PRIMARY KEY,
    simulation_run_id TEXT,
    loads_json TEXT NOT NULL DEFAULT '{}',
    forces_json TEXT NOT NULL DEFAULT '{}',
    deflections_json TEXT NOT NULL DEFAULT '{}',
    stress_estimates_json TEXT NOT NULL DEFAULT '{}',
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS robotics_simulations (
    id TEXT PRIMARY KEY,
    simulation_run_id TEXT,
    motion_results_json TEXT NOT NULL DEFAULT '{}',
    joint_stress_json TEXT NOT NULL DEFAULT '{}',
    actuator_utilization_json TEXT NOT NULL DEFAULT '{}',
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS aerospace_simulations (
    id TEXT PRIMARY KEY,
    simulation_run_id TEXT,
    lift REAL,
    drag REAL,
    stability_json TEXT NOT NULL DEFAULT '{}',
    performance_json TEXT NOT NULL DEFAULT '{}',
    risk_factors_json TEXT NOT NULL DEFAULT '[]',
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS drone_simulations (
    id TEXT PRIMARY KEY,
    simulation_run_id TEXT,
    flight_time REAL,
    power_usage_json TEXT NOT NULL DEFAULT '{}',
    payload_impact_json TEXT NOT NULL DEFAULT '{}',
    motor_loading_json TEXT NOT NULL DEFAULT '{}',
    mission_results_json TEXT NOT NULL DEFAULT '{}',
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS optimization_results (
    id TEXT PRIMARY KEY,
    simulation_run_id TEXT,
    alternative_designs_json TEXT NOT NULL DEFAULT '[]',
    improved_parameters_json TEXT NOT NULL DEFAULT '{}',
    efficiency_improvements_json TEXT NOT NULL DEFAULT '{}',
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS firmware_projects (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS firmware_architectures (
    id TEXT PRIMARY KEY,
    firmware_project_id TEXT,
    folder_structure_json TEXT NOT NULL DEFAULT '[]',
    module_architecture_json TEXT NOT NULL DEFAULT '{}',
    subsystem_design_json TEXT NOT NULL DEFAULT '{}',
    dependency_map_json TEXT NOT NULL DEFAULT '{}',
    boot_process_json TEXT NOT NULL DEFAULT '[]',
    initialization_flow_json TEXT NOT NULL DEFAULT '[]',
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rtos_configurations (
    id TEXT PRIMARY KEY,
    firmware_project_id TEXT,
    rtos_type TEXT NOT NULL,
    tasks_json TEXT NOT NULL DEFAULT '[]',
    queues_json TEXT NOT NULL DEFAULT '[]',
    semaphores_json TEXT NOT NULL DEFAULT '[]',
    mutexes_json TEXT NOT NULL DEFAULT '[]',
    timers_json TEXT NOT NULL DEFAULT '[]',
    watchdogs_json TEXT NOT NULL DEFAULT '[]',
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS task_definitions (
    id TEXT PRIMARY KEY,
    rtos_config_id TEXT,
    name TEXT NOT NULL,
    priority INTEGER NOT NULL,
    stack_size INTEGER NOT NULL,
    period_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS driver_definitions (
    id TEXT PRIMARY KEY,
    firmware_project_id TEXT,
    driver_type TEXT NOT NULL,
    hal_layer_json TEXT NOT NULL DEFAULT '{}',
    driver_layer_json TEXT NOT NULL DEFAULT '{}',
    abstraction_layer_json TEXT NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS communication_stacks (
    id TEXT PRIMARY KEY,
    firmware_project_id TEXT,
    protocol_layers_json TEXT NOT NULL DEFAULT '{}',
    packet_definitions_json TEXT NOT NULL DEFAULT '{}',
    communication_frameworks_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS state_machines (
    id TEXT PRIMARY KEY,
    firmware_project_id TEXT,
    type TEXT NOT NULL,
    states_json TEXT NOT NULL DEFAULT '[]',
    transitions_json TEXT NOT NULL DEFAULT '[]',
    conditions_json TEXT NOT NULL DEFAULT '[]',
    actions_json TEXT NOT NULL DEFAULT '[]',
    recovery_logic_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS flight_controller_architectures (
    id TEXT PRIMARY KEY,
    firmware_project_id TEXT,
    vehicle_type TEXT NOT NULL,
    flight_tasks_json TEXT NOT NULL DEFAULT '[]',
    navigation_tasks_json TEXT NOT NULL DEFAULT '[]',
    mission_tasks_json TEXT NOT NULL DEFAULT '[]',
    control_tasks_json TEXT NOT NULL DEFAULT '[]',
    sensor_fusion_tasks_json TEXT NOT NULL DEFAULT '[]',
    failsafe_systems_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS robotics_controller_architectures (
    id TEXT PRIMARY KEY,
    firmware_project_id TEXT,
    kinematics_tasks_json TEXT NOT NULL DEFAULT '[]',
    motion_planning_tasks_json TEXT NOT NULL DEFAULT '[]',
    actuator_tasks_json TEXT NOT NULL DEFAULT '[]',
    safety_tasks_json TEXT NOT NULL DEFAULT '[]',
    trajectory_controllers_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS generated_code_projects (
    id TEXT PRIMARY KEY,
    firmware_project_id TEXT,
    language TEXT NOT NULL,
    project_structure_json TEXT NOT NULL DEFAULT '[]',
    modules_json TEXT NOT NULL DEFAULT '[]',
    interfaces_json TEXT NOT NULL DEFAULT '[]',
    configuration_files_json TEXT NOT NULL DEFAULT '[]',
    build_files_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS system_projects (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS requirements (
    id TEXT PRIMARY KEY,
    system_project_id TEXT,
    description TEXT NOT NULL,
    status TEXT DEFAULT 'draft',
    parent_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS traceability_records (
    id TEXT PRIMARY KEY,
    system_project_id TEXT,
    requirement_id TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS subsystems (
    id TEXT PRIMARY KEY,
    system_project_id TEXT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    subcomponents_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS interface_definitions (
    id TEXT PRIMARY KEY,
    system_project_id TEXT,
    type TEXT NOT NULL,
    source TEXT NOT NULL,
    target TEXT NOT NULL,
    properties_json TEXT NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dependencies (
    id TEXT PRIMARY KEY,
    system_project_id TEXT,
    source TEXT NOT NULL,
    target TEXT NOT NULL,
    type TEXT NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS configuration_baselines (
    id TEXT PRIMARY KEY,
    system_project_id TEXT,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    artifacts_json TEXT NOT NULL DEFAULT '[]',
    approvals_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS system_validation_results (
    id TEXT PRIMARY KEY,
    system_project_id TEXT,
    validation_results_json TEXT NOT NULL DEFAULT '[]',
    engineering_findings_json TEXT NOT NULL DEFAULT '[]',
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS review_board_decisions (
    id TEXT PRIMARY KEY,
    system_project_id TEXT,
    critical_findings_json TEXT NOT NULL DEFAULT '[]',
    risks_json TEXT NOT NULL DEFAULT '[]',
    recommendations_json TEXT NOT NULL DEFAULT '[]',
    approval_status TEXT DEFAULT 'pending',
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS digital_thread_records (
    id TEXT PRIMARY KEY,
    system_project_id TEXT,
    artifact_type TEXT NOT NULL,
    artifact_id TEXT NOT NULL,
    parent_ids_json TEXT NOT NULL DEFAULT '[]',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cad_projects (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cad_parts (
    id TEXT PRIMARY KEY,
    cad_project_id TEXT,
    name TEXT NOT NULL,
    part_type TEXT NOT NULL,
    features_json TEXT NOT NULL DEFAULT '[]',
    constraints_json TEXT NOT NULL DEFAULT '[]',
    parametric_dimensions_json TEXT NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cad_assemblies (
    id TEXT PRIMARY KEY,
    cad_project_id TEXT,
    name TEXT NOT NULL,
    parts_json TEXT NOT NULL DEFAULT '[]',
    mates_json TEXT NOT NULL DEFAULT '[]',
    joints_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cad_drawings (
    id TEXT PRIMARY KEY,
    cad_project_id TEXT,
    name TEXT NOT NULL,
    part_id TEXT,
    assembly_id TEXT,
    views_json TEXT NOT NULL DEFAULT '[]',
    dimensions_json TEXT NOT NULL DEFAULT '[]',
    notes_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mass_properties (
    id TEXT PRIMARY KEY,
    part_id TEXT,
    assembly_id TEXT,
    mass_kg REAL,
    cog_x REAL,
    cog_y REAL,
    cog_z REAL,
    volume_m3 REAL,
    surface_area_m2 REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tolerance_analyses (
    id TEXT PRIMARY KEY,
    part_id TEXT,
    tolerances_json TEXT NOT NULL DEFAULT '[]',
    gdt_json TEXT NOT NULL DEFAULT '[]',
    stackups_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS manufacturing_reviews (
    id TEXT PRIMARY KEY,
    part_id TEXT,
    constraints_json TEXT NOT NULL DEFAULT '[]',
    dfm_json TEXT NOT NULL DEFAULT '[]',
    recommendations_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cad_revisions (
    id TEXT PRIMARY KEY,
    cad_project_id TEXT,
    version TEXT NOT NULL,
    changes_json TEXT NOT NULL DEFAULT '[]',
    approvals_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bill_of_materials (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    items_json TEXT NOT NULL DEFAULT '[]',
    total_items INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS suppliers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    part_number TEXT NOT NULL,
    lead_time_days INTEGER DEFAULT 7,
    price REAL DEFAULT 0.0,
    availability TEXT DEFAULT 'in_stock',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS procurement_plans (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    purchase_orders_json TEXT NOT NULL DEFAULT '[]',
    supplier_list_json TEXT NOT NULL DEFAULT '[]',
    lead_times_json TEXT NOT NULL DEFAULT '{}',
    critical_components_json TEXT NOT NULL DEFAULT '[]',
    procurement_risks_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cost_estimates (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    materials REAL DEFAULT 0.0,
    machining REAL DEFAULT 0.0,
    printing REAL DEFAULT 0.0,
    electronics REAL DEFAULT 0.0,
    pcb REAL DEFAULT 0.0,
    labor REAL DEFAULT 0.0,
    testing REAL DEFAULT 0.0,
    logistics REAL DEFAULT 0.0,
    total REAL DEFAULT 0.0,
    unit_cost REAL DEFAULT 0.0,
    batch_size INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS manufacturing_plans (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    production_level TEXT DEFAULT 'prototype',
    fabrication_steps_json TEXT NOT NULL DEFAULT '[]',
    assembly_steps_json TEXT NOT NULL DEFAULT '[]',
    testing_steps_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cnc_routes (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    operations_json TEXT NOT NULL DEFAULT '[]',
    tool_selection_json TEXT NOT NULL DEFAULT '[]',
    cycle_time_min REAL DEFAULT 0.0,
    dfm_recommendations_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS print_plans (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    technology TEXT DEFAULT 'FDM',
    orientation TEXT NOT NULL,
    support_strategy TEXT NOT NULL,
    material TEXT NOT NULL,
    print_time_hours REAL DEFAULT 0.0,
    recommendations_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS risk_assessments (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    risks_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS build_packages (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    cad_files_json TEXT NOT NULL DEFAULT '[]',
    drawings_json TEXT NOT NULL DEFAULT '[]',
    bom_id TEXT,
    assembly_instructions TEXT,
    manufacturing_plans_json TEXT NOT NULL DEFAULT '[]',
    testing_plans_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# ── Day 28: Optimization & Engineering Intelligence Platform ──────────────────
OPTIMIZATION_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS optimization_projects (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    domain TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    config_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS optimization_runs (
    id TEXT PRIMARY KEY,
    opt_project_id TEXT NOT NULL,
    algorithm TEXT NOT NULL,
    generation INTEGER DEFAULT 0,
    population_size INTEGER DEFAULT 50,
    status TEXT NOT NULL DEFAULT 'pending',
    best_score REAL,
    elapsed_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(opt_project_id) REFERENCES optimization_projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS optimization_objectives (
    id TEXT PRIMARY KEY,
    opt_project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    direction TEXT NOT NULL,
    weight REAL DEFAULT 1.0,
    unit TEXT,
    FOREIGN KEY(opt_project_id) REFERENCES optimization_projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS optimization_constraints (
    id TEXT PRIMARY KEY,
    opt_project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    constraint_type TEXT NOT NULL,
    operator TEXT NOT NULL,
    value REAL NOT NULL,
    value_max REAL,
    unit TEXT,
    is_hard INTEGER DEFAULT 1,
    FOREIGN KEY(opt_project_id) REFERENCES optimization_projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS trade_studies (
    id TEXT PRIMARY KEY,
    opt_project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    options_json TEXT NOT NULL DEFAULT '[]',
    decision_matrix_json TEXT NOT NULL DEFAULT '{}',
    winner TEXT,
    ahp_weights_json TEXT DEFAULT '{}',
    risk_json TEXT DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(opt_project_id) REFERENCES optimization_projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS design_alternatives (
    id TEXT PRIMARY KEY,
    opt_run_id TEXT NOT NULL,
    name TEXT NOT NULL,
    parameters_json TEXT NOT NULL DEFAULT '{}',
    objectives_json TEXT NOT NULL DEFAULT '{}',
    constraints_satisfied INTEGER DEFAULT 1,
    rank INTEGER,
    crowding_distance REAL,
    generation INTEGER DEFAULT 0,
    FOREIGN KEY(opt_run_id) REFERENCES optimization_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS recommendations (
    id TEXT PRIMARY KEY,
    opt_project_id TEXT NOT NULL,
    rank INTEGER NOT NULL,
    title TEXT NOT NULL,
    design_alternative_id TEXT,
    justification TEXT NOT NULL,
    tradeoff_summary TEXT NOT NULL,
    risk_summary TEXT NOT NULL,
    improvement_potential TEXT,
    confidence_score REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(opt_project_id) REFERENCES optimization_projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS pareto_solutions (
    id TEXT PRIMARY KEY,
    opt_run_id TEXT NOT NULL,
    design_alternative_id TEXT NOT NULL,
    front_rank INTEGER NOT NULL DEFAULT 1,
    hypervolume_contribution REAL,
    objectives_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(opt_run_id) REFERENCES optimization_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS iteration_history (
    id TEXT PRIMARY KEY,
    opt_run_id TEXT NOT NULL,
    iteration INTEGER NOT NULL,
    best_objectives_json TEXT NOT NULL DEFAULT '{}',
    population_stats_json TEXT NOT NULL DEFAULT '{}',
    constraint_violations INTEGER DEFAULT 0,
    improvement_delta REAL DEFAULT 0.0,
    elapsed_ms REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(opt_run_id) REFERENCES optimization_runs(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_opt_projects_project ON optimization_projects(project_id);
CREATE INDEX IF NOT EXISTS idx_opt_runs_project ON optimization_runs(opt_project_id);
CREATE INDEX IF NOT EXISTS idx_opt_objectives_project ON optimization_objectives(opt_project_id);
CREATE INDEX IF NOT EXISTS idx_opt_constraints_project ON optimization_constraints(opt_project_id);
CREATE INDEX IF NOT EXISTS idx_trade_studies_project ON trade_studies(opt_project_id);
CREATE INDEX IF NOT EXISTS idx_design_alternatives_run ON design_alternatives(opt_run_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_project ON recommendations(opt_project_id);
CREATE INDEX IF NOT EXISTS idx_pareto_solutions_run ON pareto_solutions(opt_run_id);
CREATE INDEX IF NOT EXISTS idx_iteration_history_run ON iteration_history(opt_run_id);
"""

# ── Day 29: Engineering Knowledge Graph & Memory Platform ──────────────────
KNOWLEDGE_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS knowledge_nodes (
    id TEXT PRIMARY KEY,
    node_type TEXT NOT NULL,
    name TEXT NOT NULL,
    project_id TEXT,
    properties_json TEXT NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS knowledge_relationships (
    id TEXT PRIMARY KEY,
    source_node_id TEXT NOT NULL,
    target_node_id TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    properties_json TEXT NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS engineering_memories (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    memory_type TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tags_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS component_profiles (
    id TEXT PRIMARY KEY,
    component_type TEXT NOT NULL,
    name TEXT NOT NULL,
    part_number TEXT,
    properties_json TEXT NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS material_profiles (
    id TEXT PRIMARY KEY,
    material_type TEXT NOT NULL,
    name TEXT NOT NULL,
    properties_json TEXT NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS failure_records (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    failure_type TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    root_cause TEXT,
    symptoms_json TEXT NOT NULL DEFAULT '[]',
    mitigations_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lessons_learned (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    impact TEXT NOT NULL,
    tags_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS knowledge_embeddings (
    id TEXT PRIMARY KEY,
    node_id TEXT,
    memory_id TEXT,
    embedding_vector_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS engineering_insights (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    insight_type TEXT NOT NULL,
    content TEXT NOT NULL,
    source_ids_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recommendation_history (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    recommendation_type TEXT NOT NULL,
    content_json TEXT NOT NULL DEFAULT '[]',
    outcome TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_knowledge_nodes_project ON knowledge_nodes(project_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_nodes_type ON knowledge_nodes(node_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_relationships_source ON knowledge_relationships(source_node_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_relationships_target ON knowledge_relationships(target_node_id);
CREATE INDEX IF NOT EXISTS idx_engineering_memories_project ON engineering_memories(project_id);
CREATE INDEX IF NOT EXISTS idx_failure_records_project ON failure_records(project_id);
CREATE INDEX IF NOT EXISTS idx_lessons_learned_project ON lessons_learned(project_id);
"""

# ── Day 30: Standards, Regulations & Compliance Platform ──────────────────
COMPLIANCE_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS standards (
    id TEXT PRIMARY KEY,
    standard_type TEXT NOT NULL,
    name TEXT NOT NULL,
    code TEXT NOT NULL,
    description TEXT,
    requirements_json TEXT NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS regulations (
    id TEXT PRIMARY KEY,
    regulation_type TEXT NOT NULL,
    name TEXT NOT NULL,
    jurisdiction TEXT NOT NULL,
    description TEXT,
    requirements_json TEXT NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS compliance_requirements (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    requirement_id TEXT NOT NULL,
    standard_id TEXT,
    regulation_id TEXT,
    verification_method TEXT,
    evidence_id TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS certification_plans (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    certification_type TEXT NOT NULL,
    tasks_json TEXT NOT NULL DEFAULT '[]',
    timeline_json TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS safety_analyses (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    analysis_type TEXT NOT NULL,
    hazards_json TEXT NOT NULL DEFAULT '[]',
    risk_register_json TEXT NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS risk_assessments (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    risk_type TEXT NOT NULL,
    risks_json TEXT NOT NULL DEFAULT '[]',
    mitigations_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_records (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    audit_type TEXT NOT NULL,
    auditor TEXT,
    findings_json TEXT NOT NULL DEFAULT '[]',
    overall_result TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS evidence_records (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    requirement_id TEXT NOT NULL,
    evidence_type TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS compliance_reports (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    report_type TEXT NOT NULL,
    content TEXT NOT NULL,
    sections_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS verification_activities (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    requirement_id TEXT NOT NULL,
    activity_type TEXT NOT NULL,
    description TEXT NOT NULL,
    result TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_standards_type ON standards(standard_type);
CREATE INDEX IF NOT EXISTS idx_regulations_jurisdiction ON regulations(jurisdiction);
CREATE INDEX IF NOT EXISTS idx_compliance_requirements_project ON compliance_requirements(project_id);
CREATE INDEX IF NOT EXISTS idx_certification_plans_project ON certification_plans(project_id);
CREATE INDEX IF NOT EXISTS idx_safety_analyses_project ON safety_analyses(project_id);
CREATE INDEX IF NOT EXISTS idx_audit_records_project ON audit_records(project_id);
CREATE INDEX IF NOT EXISTS idx_evidence_records_project ON evidence_records(project_id);
"""

# ── Day 31: Testing, Verification & Hardware-In-The-Loop Platform ──────────────────
VERIFICATION_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS verification_plans (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    verification_type TEXT NOT NULL,
    activities_json TEXT NOT NULL DEFAULT '[]',
    schedule_json TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS validation_plans (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    validation_type TEXT NOT NULL,
    scenarios_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS test_cases (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    test_type TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    steps_json TEXT NOT NULL DEFAULT '[]',
    expected_results TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS test_executions (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    test_case_ids_json TEXT NOT NULL DEFAULT '[]',
    results_json TEXT NOT NULL DEFAULT '[]',
    status TEXT NOT NULL DEFAULT 'in_progress',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS acceptance_criteria (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    system_type TEXT NOT NULL,
    criteria_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS hil_sessions (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    hardware_id TEXT NOT NULL,
    simulation_model_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    results_json TEXT NOT NULL DEFAULT '{}',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sil_sessions (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    firmware_id TEXT NOT NULL,
    simulation_model_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    results_json TEXT NOT NULL DEFAULT '{}',
    coverage_json TEXT NOT NULL DEFAULT '{}',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS coverage_metrics (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    coverage_type TEXT NOT NULL,
    metrics_json TEXT NOT NULL DEFAULT '{}',
    gaps_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS verification_matrices (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    rows_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS verification_reports (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    report_type TEXT NOT NULL,
    content TEXT NOT NULL,
    sections_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_verification_plans_project ON verification_plans(project_id);
CREATE INDEX IF NOT EXISTS idx_test_cases_project ON test_cases(project_id);
CREATE INDEX IF NOT EXISTS idx_test_executions_project ON test_executions(project_id);
CREATE INDEX IF NOT EXISTS idx_hil_sessions_project ON hil_sessions(project_id);
CREATE INDEX IF NOT EXISTS idx_sil_sessions_project ON sil_sessions(project_id);
"""


# ── Lifespan ─────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown handlers."""
    # ── Startup ──────────────────────────────────────────────
    setup_logging()
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Ensure directories exist
    settings.ensure_dirs()

    # Create database tables
    async with engine.begin() as conn:
        for sql_block in (SCHEMA_SQL, OPTIMIZATION_SCHEMA_SQL, KNOWLEDGE_SCHEMA_SQL, COMPLIANCE_SCHEMA_SQL, VERIFICATION_SCHEMA_SQL):
            for statement in sql_block.strip().split(";"):
                stmt = statement.strip()
                if stmt:
                    await conn.execute(text(stmt))
    logger.info("Database tables initialized (including Day 28 optimization, Day 29 knowledge, Day 30 compliance, and Day 31 verification tables)")

    # Import domain formulas to trigger registration
    _register_all_formulas()

    from app.calculations.registry import registry
    logger.info(f"Formula registry loaded: {registry.count} formulas across {registry.get_domains()}")

    # Create default project if none exists
    async with async_session_factory() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM projects"))
        count = result.scalar()
        if count == 0:
            await session.execute(
                text("""
                    INSERT INTO projects (id, name, description, domain, status)
                    VALUES ('default', 'Default Project', 'Default engineering workspace', 'multi', 'active')
                """)
            )
            await session.commit()
            logger.info("Created default project")

    logger.info(f"✓ {settings.APP_NAME} ready — API at http://localhost:8000{settings.API_V1_PREFIX}")

    yield

    # ── Shutdown ─────────────────────────────────────────────
    logger.info("Shutting down...")
    await engine.dispose()
    logger.info("Database engine disposed")


def _register_all_formulas():
    """Import all domain formula modules to trigger @register_formula decorators."""
    # Aerospace
    import app.domains.aerospace.formulas.aerodynamics  # noqa: F401
    import app.domains.aerospace.formulas.propulsion    # noqa: F401

    # Drones
    import app.domains.drones.formulas.flight_dynamics  # noqa: F401
    import app.domains.drones.formulas.battery          # noqa: F401

    # Robotics
    import app.domains.robotics.formulas.kinematics     # noqa: F401

    # Electronics
    import app.domains.electronics.formulas.circuit_analysis  # noqa: F401


# ── Application Factory ──────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered engineering copilot for Aerospace, Drones, Robotics & Electronics",
    lifespan=lifespan,
)

# ── CORS Middleware ──────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ─────────────────────────────────────────────
from app.calculations.router import router as calc_router
from app.projects.router import router as projects_router
from app.memory.router import router as memory_router
from app.memory.chat_router import router as chat_router
from app.documents.router import router as documents_router
from app.solver.router import router as solver_router
from app.validation.routes.validation_routes import router as validation_router
from documentation.routes.api import router as documentation_router
from app.electronics_intelligence.routes.electronics_routes import router as electronics_router
from app.schematic_engine.routes.schematic_routes import router as schematic_router
from app.pcb.routes.pcb_routes import router as pcb_router
from app.simulation.routes.simulation_routes import router as simulation_router
from app.embedded.routes.embedded_routes import router as embedded_router
from app.system_integration.routes.system_integration_routes import router as system_integration_router
from app.cad.routes.cad_routes import router as cad_router
from app.optimization.routes.optimization_routes import router as optimization_router
from app.manufacturing.routes.manufacturing_routes import router as manufacturing_router
from app.knowledge.routes.knowledge_routes import router as knowledge_router
from app.compliance.routes.compliance_routes import router as compliance_router
from app.verification.routes.verification_routes import router as verification_router
from app.cad_execution.routes.cad_execution_routes import router as cad_execution_router
from app.design_synthesis.routes.design_synthesis_routes import router as design_synthesis_router
from app.pcb_execution.routes.pcb_execution_routes import router as pcb_execution_router
from app.electronics_execution.routes.electronics_execution_routes import router as electronics_execution_router
from app.engineering_os.routes.engineering_os_routes import router as engineering_os_router
from app.engineering_os_v2.routes.engineering_os_v2_routes import router as engineering_os_v2_router
from app.marketplace.routes.marketplace_routes import router as marketplace_router
from app.engineering_cloud.routes.engineering_cloud_routes import router as engineering_cloud_router
from app.business_operations.routes.business_operations_routes import router as business_operations_router
from app.technology_discovery.routes.technology_discovery_routes import router as technology_discovery_router
from app.engineering_os_v3.routes.engineering_os_v3_routes import router as engineering_os_v3_router
from app.mbse.routes.mbse_routes import router as mbse_router
from app.safety_engineering.routes.safety_engineering_routes import router as safety_engineering_router
from app.hardware_integration.routes.hardware_integration_routes import router as hardware_integration_router
from app.factory_platform.routes.factory_platform_routes import router as factory_platform_router
from app.autonomy.routes.autonomy_routes import router as autonomy_router

app.include_router(calc_router, prefix=settings.API_V1_PREFIX)
app.include_router(projects_router, prefix=settings.API_V1_PREFIX)
app.include_router(memory_router, prefix=settings.API_V1_PREFIX)
app.include_router(chat_router, prefix=settings.API_V1_PREFIX)
app.include_router(documents_router, prefix=settings.API_V1_PREFIX)
app.include_router(solver_router, prefix=settings.API_V1_PREFIX)
app.include_router(validation_router, prefix=settings.API_V1_PREFIX)
app.include_router(documentation_router, prefix=settings.API_V1_PREFIX)
app.include_router(electronics_router, prefix=settings.API_V1_PREFIX)
app.include_router(schematic_router, prefix=settings.API_V1_PREFIX)
app.include_router(pcb_router, prefix=settings.API_V1_PREFIX)
app.include_router(simulation_router, prefix=settings.API_V1_PREFIX)
app.include_router(embedded_router, prefix=settings.API_V1_PREFIX)
app.include_router(system_integration_router, prefix=settings.API_V1_PREFIX)
app.include_router(cad_router, prefix=settings.API_V1_PREFIX)
app.include_router(optimization_router, prefix=settings.API_V1_PREFIX)
app.include_router(manufacturing_router, prefix=settings.API_V1_PREFIX)
app.include_router(knowledge_router, prefix=settings.API_V1_PREFIX)
app.include_router(compliance_router, prefix=settings.API_V1_PREFIX)
app.include_router(verification_router, prefix=settings.API_V1_PREFIX)
app.include_router(cad_execution_router, prefix=settings.API_V1_PREFIX)
app.include_router(design_synthesis_router, prefix=settings.API_V1_PREFIX)
app.include_router(pcb_execution_router, prefix=settings.API_V1_PREFIX)
app.include_router(electronics_execution_router, prefix=settings.API_V1_PREFIX)
app.include_router(engineering_os_router, prefix=settings.API_V1_PREFIX)        
app.include_router(engineering_os_v2_router, prefix=settings.API_V1_PREFIX)
app.include_router(marketplace_router, prefix=settings.API_V1_PREFIX)
app.include_router(engineering_cloud_router, prefix=settings.API_V1_PREFIX)
app.include_router(business_operations_router, prefix=settings.API_V1_PREFIX)
app.include_router(technology_discovery_router, prefix=settings.API_V1_PREFIX)
app.include_router(engineering_os_v3_router, prefix=settings.API_V1_PREFIX)
app.include_router(mbse_router, prefix=settings.API_V1_PREFIX)
app.include_router(safety_engineering_router, prefix=settings.API_V1_PREFIX)
app.include_router(hardware_integration_router, prefix=settings.API_V1_PREFIX)
app.include_router(factory_platform_router, prefix=settings.API_V1_PREFIX)
app.include_router(autonomy_router, prefix=settings.API_V1_PREFIX)



# ── Health Check ─────────────────────────────────────────────────
@app.get("/health")
async def health_check():
    """Application health check endpoint."""
    from app.calculations.registry import registry
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "formulas_loaded": registry.count,
        "domains": registry.get_domains(),
    }
