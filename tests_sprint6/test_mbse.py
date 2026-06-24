"""
Tests for MBSE and Architecture Modules.
"""
from mbse.system_model import SystemModel, ModelElementType, ModelRelationType
from mbse.architecture_builder import ArchitectureBuilder
from mbse.behavior_model import BehaviorModel, BehaviorType, ActivityModel
from mbse.interface_model import InterfaceModel, InterfaceType


class TestSystemModel:
    def setup_method(self):
        self.model = SystemModel("Test System")

    def test_create_element(self):
        el = self.model.create_element("Flight Controller", ModelElementType.SUBSYSTEM)
        assert el.id is not None
        assert el.name == "Flight Controller"

    def test_create_relation(self):
        s1 = self.model.create_element("Source", ModelElementType.COMPONENT)
        s2 = self.model.create_element("Target", ModelElementType.COMPONENT)
        rel = self.model.create_relation(s1.id, s2.id, ModelRelationType.ASSOCIATION)
        assert rel is not None
        assert rel.source_id == s1.id

    def test_create_port(self):
        el = self.model.create_element("Sensor", ModelElementType.COMPONENT)
        port = self.model.create_port(el.id, "Data Out", "output")
        assert port is not None
        assert port.direction == "output"

    def test_get_element_tree(self):
        root = self.model.create_element("System", ModelElementType.SYSTEM)
        sub = self.model.create_element("Sub1", ModelElementType.SUBSYSTEM, parent_id=root.id)
        tree = self.model.get_element_tree()
        assert len(tree["trees"]) >= 1

    def test_export_model(self):
        self.model.create_element("Test", ModelElementType.COMPONENT)
        exported = self.model.export_model()
        assert "elements" in exported
        assert len(exported["elements"]) >= 1

    def test_link_requirement(self):
        el = self.model.create_element("Component", ModelElementType.COMPONENT)
        result = self.model.link_requirement(el.id, "req-123")
        assert result is True
        assert "req-123" in el.requirement_ids

    def test_delete_element(self):
        el = self.model.create_element("ToDelete", ModelElementType.COMPONENT)
        assert self.model.delete_element(el.id) is True


class TestArchitectureBuilder:
    def setup_method(self):
        self.builder = ArchitectureBuilder()

    def test_create_view(self):
        view = self.builder.create_view("Structural View", "structural")
        assert view.id is not None
        assert view.view_type == "structural"

    def test_generate_block_definition_diagram(self):
        self.builder.model.create_element("System", ModelElementType.SYSTEM)
        bdd = self.builder.generate_block_definition_diagram()
        assert bdd["type"] == "BlockDefinitionDiagram"
        assert len(bdd["blocks"]) >= 1

    def test_generate_internal_block_diagram(self):
        root = self.builder.model.create_element("System", ModelElementType.SYSTEM)
        self.builder.model.create_element("Sub", ModelElementType.SUBSYSTEM, parent_id=root.id)
        ibd = self.builder.generate_internal_block_diagram()
        assert ibd["type"] == "InternalBlockDiagram"

    def test_analyze_architecture(self):
        analysis = self.builder.analyze_architecture()
        assert "total_elements" in analysis
        assert "total_relations" in analysis


class TestBehaviorModel:
    def setup_method(self):
        self.model = BehaviorModel()

    def test_create_behavior(self):
        b = self.model.create_behavior("Takeoff", BehaviorType.ACTIVITY)
        assert b.name == "Takeoff"
        assert b.behavior_type == BehaviorType.ACTIVITY

    def test_get_functional_flow(self):
        parent = self.model.create_behavior("Mission", BehaviorType.FUNCTION)
        self.model.create_behavior("SubFunction", BehaviorType.FUNCTION, parent_id=parent.id)
        flow = self.model.get_functional_flow()
        assert len(flow) >= 1

    def test_allocate_to_element(self):
        b = self.model.create_behavior("Fly", BehaviorType.FUNCTION)
        assert self.model.allocate_to_element(b.id, "element-1") is True


class TestActivityModel:
    def setup_method(self):
        self.model = ActivityModel()

    def test_add_activity(self):
        aid = self.model.add_activity("Start")
        assert aid is not None

    def test_add_control_flow(self):
        a1 = self.model.add_activity("A")
        a2 = self.model.add_activity("B")
        assert self.model.add_control_flow(a1, a2) is True

    def test_get_activity_diagram(self):
        self.model.add_activity("Activity")
        diagram = self.model.get_activity_diagram()
        assert diagram["type"] == "ActivityDiagram"


class TestInterfaceModel:
    def setup_method(self):
        self.model = InterfaceModel()

    def test_create_interface(self):
        iface = self.model.create_interface("CAN Bus", InterfaceType.DATA)
        assert iface.name == "CAN Bus"

    def test_add_signal(self):
        iface = self.model.create_interface("UART")
        iface.add_signal("TX", "digital", "output")
        assert len(iface.signals) == 1

    def test_map_port(self):
        iface = self.model.create_interface("I2C")
        assert self.model.map_port_to_interface("port-1", iface.id) is True

    def test_generate_icd(self):
        self.model.create_interface("Ethernet", InterfaceType.DATA)
        icd = self.model.generate_interface_control_document()
        assert len(icd["interfaces"]) >= 1