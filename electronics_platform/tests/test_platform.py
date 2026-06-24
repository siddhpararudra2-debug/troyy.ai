import pytest
from electronics_platform.schemas.enums import ComponentCategory, ComponentStatus, SimulationType, DesignRuleClass
from electronics_platform.schemas.models import Component, Net, Pin, Schematic
from electronics_platform.electronics.circuit_engine import CircuitEngine
from electronics_platform.electronics.component_selector import ComponentSelector
from electronics_platform.electronics.power_analysis import PowerAnalysis
from electronics_platform.electronics.electronics_orchestrator import ElectronicsOrchestrator
from electronics_platform.components.component_database import ComponentDatabase
from electronics_platform.components.bom_generator import BOMGenerator
from electronics_platform.schematics.schematic_generator import SchematicGenerator

def test_circuit_engine_voltage_divider():
    engine = CircuitEngine()
    divider = engine.voltage_divider(v_in=10.0, r1=10000, r2=10000)
    assert divider["v_out"] == 5.0
    assert divider["ratio"] == 0.5
    assert divider["i_total"] == pytest.approx(0.0005)
    assert divider["p_total"] == pytest.approx(0.005)

def test_circuit_engine_rc_filter():
    engine = CircuitEngine()
    rc = engine.rc_filter_cutoff(r=10000, c=1e-7)  # 10k, 100nF
    assert rc["cutoff_frequency_hz"] == pytest.approx(159.1549, rel=1e-3)
    assert rc["time_constant_s"] == pytest.approx(0.001)

def test_circuit_engine_nodal_analysis():
    engine = CircuitEngine()
    
    components = [
        Component(
            ref="R1", value="10k", footprint="Resistor_SMD:R_0402_1005Metric",
            category=ComponentCategory.RESISTOR,
            pins=[Pin(number="1", name="A", pin_type="PASSIVE"),
                  Pin(number="2", name="B", pin_type="PASSIVE")]
        ),
        Component(
            ref="R2", value="10k", footprint="Resistor_SMD:R_0402_1005Metric",
            category=ComponentCategory.RESISTOR,
            pins=[Pin(number="1", name="A", pin_type="PASSIVE"),
                  Pin(number="2", name="B", pin_type="PASSIVE")]
        )
    ]
    nets = [
        Net(name="VIN", connections=[("R1", "1")]),
        Net(name="VOUT", connections=[("R1", "2"), ("R2", "1")]),
        Net(name="GND", connections=[("R2", "2")], is_ground=True)
    ]
    
    voltages = engine.nodal_analysis(components, nets, {})
    assert isinstance(voltages, dict)

def test_component_database_and_selector():
    db = ComponentDatabase()
    selector = ComponentSelector(db)
    
    resistor = selector.select_resistor(resistance_ohm=10000, package="0402")
    assert resistor is not None
    assert resistor.category == ComponentCategory.RESISTOR
    assert resistor.package == "0402"
    
    capacitor = selector.select_capacitor(capacitance_f=1e-7, voltage_v=10, package="0402")
    assert capacitor is not None
    assert capacitor.category == ComponentCategory.CAPACITOR
    
    regulator = selector.select_regulator(v_in=5.0, v_out=3.3, i_out=0.1, topology="LDO")
    assert regulator is not None
    assert regulator.category == ComponentCategory.REGULATOR

def test_power_analysis():
    analysis = PowerAnalysis()
    thermal = analysis.estimate_thermal_rise(power_w=0.5, thermal_resistance_c_w=50.0, ambient_c=25.0)
    assert thermal["junction_temp_c"] == 50.0
    
    battery = analysis.size_battery(total_power_w=1.0, runtime_hours=10, battery_voltage_v=3.7, efficiency=0.9)
    assert battery["capacity_mah"] == pytest.approx(3003, rel=1e-2)

def test_orchestrator():
    db = ComponentDatabase()
    orch = ElectronicsOrchestrator(db)
    
    divider_schematic = orch.create_voltage_divider(v_in=12.0, v_out=5.0)
    assert divider_schematic.name.startswith("Voltage Divider")
    assert len(divider_schematic.components) == 2
    
    analysis = orch.analyze_schematic(divider_schematic)
    assert "power_budget" in analysis
    assert "erc_findings" in analysis

def test_bom_generator():
    db = ComponentDatabase()
    orch = ElectronicsOrchestrator(db)
    bom_gen = BOMGenerator(db)
    
    divider = orch.create_voltage_divider(v_in=5.0, v_out=2.5)
    bom = bom_gen.generate(divider, project_name="DividerTest")
    assert bom.project_name == "DividerTest"
    assert bom.total_components == 2
    
    markdown = bom_gen.format_markdown(bom)
    assert "Bill of Materials" in markdown
    assert "R1" in markdown
    assert "R2" in markdown

def test_schematic_generator():
    db = ComponentDatabase()
    orch = ElectronicsOrchestrator(db)
    sch_gen = SchematicGenerator()
    
    divider = orch.create_voltage_divider(v_in=5.0, v_out=2.5)
    kicad_sch = sch_gen.generate_kicad_schematic(divider)
    assert "kicad_sch" in kicad_sch
    assert "R1" in kicad_sch
    assert "R2" in kicad_sch
    assert "wire" in kicad_sch
