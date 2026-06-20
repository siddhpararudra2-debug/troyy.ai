import pytest
from app.schematic_engine.services.pin_mapping_service import PinMappingService
from app.schematic_engine.services.erc_service import ERCService

def test_pin_mapping_success():
    svc = PinMappingService()
    mcu = {
        "PA0": ["ADC1", "TIM1"],
        "PA9": ["USART1_TX"],
        "PA10": ["USART1_RX"],
        "PB6": ["I2C1_SCL"],
        "PB7": ["I2C1_SDA"]
    }
    reqs = {"USART1_TX": 1, "USART1_RX": 1, "I2C1_SCL": 1, "I2C1_SDA": 1}
    
    report = svc.assign_pins(mcu, reqs)
    assert report.final_results['pin_mapping']['USART1_TX'] == "PA9"
    assert len(report.final_results['unassigned_pins']) == 1 # PA0 is unused

def test_pin_mapping_failure():
    svc = PinMappingService()
    mcu = {"PA0": ["ADC1"]}
    reqs = {"USART1_TX": 1} # Impossible
    
    with pytest.raises(ValueError, match="Insufficient pins"):
        svc.assign_pins(mcu, reqs)

def test_erc_detects_short():
    svc = ERCService()
    netlist = {
        "nets": [
            {
                "name": "NET_SHORT",
                "net_type": "SIGNAL",
                "connections": [
                    {"comp_ref": "U1", "pin_name": "OUT1", "direction": "OUTPUT"},
                    {"comp_ref": "U2", "pin_name": "OUT2", "direction": "OUTPUT"}
                ]
            }
        ]
    }
    report = svc.run_erc(netlist)
    assert report.final_results['status'] == "FAIL"
    assert any("Short circuit" in err for err in report.final_results['errors']) 
