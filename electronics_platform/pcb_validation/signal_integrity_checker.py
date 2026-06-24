"""
Signal Integrity Checker — validates PCB for SI issues.
"""
from typing import List, Dict
from electronics_platform.schemas.electronics_models import PCBBoard, SignalIntegrityReport
from electronics_platform.electronics.signal_analysis import SignalAnalysis
import numpy as np

class SignalIntegrityChecker:
    """Checks PCB for signal integrity issues."""
    
    # Thresholds
    HIGH_SPEED_THRESHOLD_MHZ = 50  # Above this, treat as high-speed
    IMPEDANCE_TOLERANCE_PCT = 10
    MAX_CROSSTALK_V = 0.1  # 100mV
    
    def __init__(self):
        self.signal_analysis = SignalAnalysis()
        
    def check(self, board: PCBBoard, net_metadata: Dict = None) -> SignalIntegrityReport:
        """Run SI checks on a PCB."""
        net_metadata = net_metadata or {}
        
        high_speed_nets = []
        impedance_violations = []
        crosstalk_risks = []
        length_mismatches = []
        recommendations = []
        
        # Identify high-speed nets
        for net in board.nets if hasattr(board, 'nets') else []:
            metadata = net_metadata.get(net.name, {})
            frequency = metadata.get("frequency_mhz", 0)
            rise_time = metadata.get("rise_time_ns", 2.0)
            
            if frequency > self.HIGH_SPEED_THRESHOLD_MHZ or rise_time < 1.0:
                high_speed_nets.append({
                    "net_name": net.name,
                    "frequency_mhz": frequency,
                    "rise_time_ns": rise_time,
                    "is_differential": metadata.get("differential", False)
                })
                
        # Check impedance for high-speed traces
        for trace in board.traces:
            net_name = trace.get("net", "")
            metadata = net_metadata.get(net_name, {})
            
            if metadata.get("frequency_mhz", 0) > self.HIGH_SPEED_THRESHOLD_MHZ:
                width = trace.get("width", 0.2)
                layer = trace.get("layer", "F.Cu")
                
                # Estimate dielectric height based on layer
                h_mm = 0.2 if "F.Cu" in layer or "B.Cu" in layer else 0.1
                
                z0 = self.signal_analysis.microstrip_impedance(width, h_mm)
                target = metadata.get("target_impedance", 50.0)
                error_pct = abs(z0 - target) / target * 100
                
                if error_pct > self.IMPEDANCE_TOLERANCE_PCT:
                    impedance_violations.append({
                        "net": net_name,
                        "layer": layer,
                        "trace_width_mm": width,
                        "calculated_impedance": z0,
                        "target_impedance": target,
                        "error_pct": error_pct
                    })
                    
        # Check differential pair length matching
        diff_pairs = self._identify_diff_pairs(board)
        for pair_name, traces in diff_pairs.items():
            if len(traces) >= 2:
                lengths = [self._estimate_trace_length(t) for t in traces]
                mismatch = max(lengths) - min(lengths)
                if mismatch > 0.5:  # 0.5mm mismatch threshold
                    length_mismatches.append({
                        "pair": pair_name,
                        "max_length_mm": max(lengths),
                        "min_length_mm": min(lengths),
                        "mismatch_mm": mismatch
                    })

        # Combine everything into SignalIntegrityReport
        if impedance_violations:
            recommendations.append("Adjust trace widths to meet target impedance (e.g. increase width for lower impedance).")
        if length_mismatches:
            recommendations.append("Tune differential trace lengths to match within 0.15mm (6 mils).")
        if crosstalk_risks:
            recommendations.append("Increase spacing between high-speed signal traces or route with a ground plane reference.")
            
        status = "PASS"
        if impedance_violations or length_mismatches:
            status = "FAIL"
            
        return SignalIntegrityReport(
            pcb_id=board.id,
            high_speed_nets=high_speed_nets,
            impedance_violations=impedance_violations,
            crosstalk_risks=crosstalk_risks,
            length_mismatches=length_mismatches,
            recommendations=recommendations,
            status=status
        )

    def _identify_diff_pairs(self, board: PCBBoard) -> Dict[str, List[Dict]]:
        """Identify differential pairs from trace names (e.g. TX_P and TX_N)."""
        pairs = {}
        for trace in board.traces:
            net_name = trace.get("net", "")
            if net_name.endswith("_P") or net_name.endswith("_N"):
                base = net_name[:-2]
                pairs.setdefault(base, []).append(trace)
            elif net_name.endswith("+") or net_name.endswith("-"):
                base = net_name[:-1]
                pairs.setdefault(base, []).append(trace)
        return pairs

    def _estimate_trace_length(self, trace: Dict) -> float:
        """Estimate trace length from coordinates in the trace dict."""
        points = trace.get("points", [])
        if not points:
            return 0.0
        length = 0.0
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i+1]
            length += np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return length
