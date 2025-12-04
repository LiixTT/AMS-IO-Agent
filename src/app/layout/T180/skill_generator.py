#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SKILL Script Generation Module for T180
Includes _generate_config_io_wires() method and 180nm-specific digital IO features
"""

from typing import List, Dict, Tuple
from ..T28.inner_pad_handler import InnerPadHandler
from ..position_calculator import PositionCalculator
from ..voltage_domain import VoltageDomainHandler


class SkillGeneratorT180:
    """SKILL Script Generator for T180 process node"""
    
    def __init__(self, config: dict):
        self.config = config
        self.inner_pad_handler = InnerPadHandler(config)
        self.position_calculator = PositionCalculator(config)

    def _generate_config_io_wires(self, oriented_pads: dict, ring_config: dict) -> Tuple[List[str], dict]:
        """Generate METAL1 configuration lines and corner connections for 180nm.

        Returns (commands, side_endpoints)."""
        skill_commands: List[str] = []

        # Record which sides have configuration lines
        sides_with_lines: dict = {}

        # Configuration offsets for digital IO wires (GND_wire or VDD_wire relative to pad edges)
        vdd_wire_offset = 5
        gnd_wire_offset = 7

        # Cache configuration line endpoints for each side in one pass
        side_endpoints: dict = {}

        # Generate configuration lines for each orientation and fill side_endpoints
        for orient, pad_positions in oriented_pads.items():
            if not pad_positions:
                continue

            sides_with_lines[orient] = True
            x_coords = [pos[0] for pos in pad_positions]
            y_coords = [pos[1] for pos in pad_positions]

            if orient == "R0":  # Bottom edge
                line_y_high = max(y_coords) + ring_config["pad_height"] + vdd_wire_offset
                line_y_low = max(y_coords) + ring_config["pad_height"] + gnd_wire_offset
                high_points = f'list(list({min(x_coords)} {line_y_high}) list({max(x_coords) + ring_config["pad_width"]} {line_y_high}))'
                low_points = f'list(list({min(x_coords)} {line_y_low}) list({max(x_coords) + ring_config["pad_width"]} {line_y_low}))'
                side_endpoints["R0"] = {
                    "high": {"x_range": [min(x_coords), max(x_coords) + ring_config["pad_width"]], "y": line_y_high},
                    "low": {"x_range": [min(x_coords), max(x_coords) + ring_config["pad_width"]], "y": line_y_low}
                }
            elif orient == "R90":  # Right edge
                line_x_high = min(x_coords) - ring_config["pad_height"] - vdd_wire_offset
                line_x_low = min(x_coords) - ring_config["pad_height"] - gnd_wire_offset
                high_points = f'list(list({line_x_high} {min(y_coords)}) list({line_x_high} {max(y_coords) + ring_config["pad_width"]}))'
                low_points = f'list(list({line_x_low} {min(y_coords)}) list({line_x_low} {max(y_coords) + ring_config["pad_width"]}))'
                side_endpoints["R90"] = {
                    "high": {"x": line_x_high, "y_range": [min(y_coords), max(y_coords) + ring_config["pad_width"]]},
                    "low": {"x": line_x_low, "y_range": [min(y_coords), max(y_coords) + ring_config["pad_width"]]}
                }
            elif orient == "R180":  # Top edge
                line_y_high = min(y_coords) - ring_config["pad_height"] - vdd_wire_offset
                line_y_low = min(y_coords) - ring_config["pad_height"] - gnd_wire_offset
                high_points = f'list(list({min(x_coords) - ring_config["pad_width"]} {line_y_high}) list({max(x_coords)} {line_y_high}))'
                low_points = f'list(list({min(x_coords) - ring_config["pad_width"]} {line_y_low}) list({max(x_coords)} {line_y_low}))'
                side_endpoints["R180"] = {
                    "high": {"x_range": [min(x_coords) - ring_config["pad_width"], max(x_coords)], "y": line_y_high},
                    "low": {"x_range": [min(x_coords) - ring_config["pad_width"], max(x_coords)], "y": line_y_low}
                }
            elif orient == "R270":  # Left edge
                line_x_high = max(x_coords) + ring_config["pad_height"] + vdd_wire_offset
                line_x_low = max(x_coords) + ring_config["pad_height"] + gnd_wire_offset
                high_points = f'list(list({line_x_high} {min(y_coords) - ring_config["pad_width"]}) list({line_x_high} {max(y_coords)}))'
                low_points = f'list(list({line_x_low} {min(y_coords) - ring_config["pad_width"]}) list({line_x_low} {max(y_coords)}))'
                side_endpoints["R270"] = {
                    "high": {"x": line_x_high, "y_range": [min(y_coords) - ring_config["pad_width"], max(y_coords)]},
                    "low": {"x": line_x_low, "y_range": [min(y_coords) - ring_config["pad_width"], max(y_coords)]}
                }

            # Create configuration lines
            skill_commands.append(f'dbCreatePath(cv list("METAL1" "drawing") {high_points} 1)')
            skill_commands.append(f'dbCreatePath(cv list("METAL1" "drawing") {low_points} 1)')

        # Connect configuration lines at corners (reuse side_endpoints)
        if len(sides_with_lines) > 1:
            corner_connections = {
                "top_left": ["R180", "R270"],
                "top_right": ["R180", "R90"],
                "bottom_left": ["R0", "R270"],
                "bottom_right": ["R0", "R90"]
            }
            for corner_name, adjacent_sides in corner_connections.items():
                if adjacent_sides[0] in side_endpoints and adjacent_sides[1] in side_endpoints:
                    # High voltage line
                    if corner_name == "top_left":
                        x1 = side_endpoints["R180"]["high"]["x_range"][0]
                        y1 = side_endpoints["R180"]["high"]["y"]
                        x2 = side_endpoints["R270"]["high"]["x"]
                        y2 = side_endpoints["R270"]["high"]["y_range"][1]
                        skill_commands.append(f'dbCreatePath(cv list("METAL1" "drawing") list(list({x1} {y1}) list({x2} {y1})) 1 "extendExtend")')
                        skill_commands.append(f'dbCreatePath(cv list("METAL1" "drawing") list(list({x2} {y1}) list({x2} {y2})) 1 "extendExtend")')
                        # Low voltage line
                        x1l = side_endpoints["R180"]["low"]["x_range"][0]
                        y1l = side_endpoints["R180"]["low"]["y"]
                        x2l = side_endpoints["R270"]["low"]["x"]
                        y2l = side_endpoints["R270"]["low"]["y_range"][1]
                        skill_commands.append(f'dbCreatePath(cv list("METAL1" "drawing") list(list({x1l} {y1l}) list({x2l} {y1l})) 1 "extendExtend")')
                        skill_commands.append(f'dbCreatePath(cv list("METAL1" "drawing") list(list({x2l} {y1l}) list({x2l} {y2l})) 1 "extendExtend")')
                    elif corner_name == "top_right":
                        x1 = side_endpoints["R180"]["high"]["x_range"][1]
                        y1 = side_endpoints["R180"]["high"]["y"]
                        x2 = side_endpoints["R90"]["high"]["x"]
                        y2 = side_endpoints["R90"]["high"]["y_range"][1]
                        skill_commands.append(f'dbCreatePath(cv list("METAL1" "drawing") list(list({x1} {y1}) list({x2} {y1})) 1 "extendExtend")')
                        skill_commands.append(f'dbCreatePath(cv list("METAL1" "drawing") list(list({x2} {y1}) list({x2} {y2})) 1 "extendExtend")')
                        x1l = side_endpoints["R180"]["low"]["x_range"][1]
                        y1l = side_endpoints["R180"]["low"]["y"]
                        x2l = side_endpoints["R90"]["low"]["x"]
                        y2l = side_endpoints["R90"]["low"]["y_range"][1]
                        skill_commands.append(f'dbCreatePath(cv list("METAL1" "drawing") list(list({x1l} {y1l}) list({x2l} {y1l})) 1 "extendExtend")')
                        skill_commands.append(f'dbCreatePath(cv list("METAL1" "drawing") list(list({x2l} {y1l}) list({x2l} {y2l})) 1 "extendExtend")')
                    elif corner_name == "bottom_left":
                        x1 = side_endpoints["R0"]["high"]["x_range"][0]
                        y1 = side_endpoints["R0"]["high"]["y"]
                        x2 = side_endpoints["R270"]["high"]["x"]
                        y2 = side_endpoints["R270"]["high"]["y_range"][0]
                        skill_commands.append(f'dbCreatePath(cv list("METAL1" "drawing") list(list({x1} {y1}) list({x2} {y1})) 1 "extendExtend")')
                        skill_commands.append(f'dbCreatePath(cv list("METAL1" "drawing") list(list({x2} {y1}) list({x2} {y2})) 1 "extendExtend")')
                        x1l = side_endpoints["R0"]["low"]["x_range"][0]
                        y1l = side_endpoints["R0"]["low"]["y"]
                        x2l = side_endpoints["R270"]["low"]["x"]
                        y2l = side_endpoints["R270"]["low"]["y_range"][0]
                        skill_commands.append(f'dbCreatePath(cv list("METAL1" "drawing") list(list({x1l} {y1l}) list({x2l} {y1l})) 1 "extendExtend")')
                        skill_commands.append(f'dbCreatePath(cv list("METAL1" "drawing") list(list({x2l} {y1l}) list({x2l} {y2l})) 1 "extendExtend")')
                    elif corner_name == "bottom_right":
                        x1 = side_endpoints["R0"]["high"]["x_range"][1]
                        y1 = side_endpoints["R0"]["high"]["y"]
                        x2 = side_endpoints["R90"]["high"]["x"]
                        y2 = side_endpoints["R90"]["high"]["y_range"][0]
                        skill_commands.append(f'dbCreatePath(cv list("METAL1" "drawing") list(list({x1} {y1}) list({x2} {y1})) 1 "extendExtend")')
                        skill_commands.append(f'dbCreatePath(cv list("METAL1" "drawing") list(list({x2} {y1}) list({x2} {y2})) 1 "extendExtend")')
                        x1l = side_endpoints["R0"]["low"]["x_range"][1]
                        y1l = side_endpoints["R0"]["low"]["y"]
                        x2l = side_endpoints["R90"]["low"]["x"]
                        y2l = side_endpoints["R90"]["low"]["y_range"][0]
                        skill_commands.append(f'dbCreatePath(cv list("METAL1" "drawing") list(list({x1l} {y1l}) list({x2l} {y1l})) 1 "extendExtend")')
                        skill_commands.append(f'dbCreatePath(cv list("METAL1" "drawing") list(list({x2l} {y1l}) list({x2l} {y2l})) 1 "extendExtend")')

        return skill_commands, side_endpoints

    def generate_digital_io_features_with_inner(self, outer_pads: List[dict], inner_pads: List[dict], ring_config: dict) -> List[str]:
        """Generate digital IO features for 180nm (configuration lines + secondary lines + pin labels), supporting inner pads."""
        skill_commands = []
        # Get all digital pads (not distinguishing IO)
        all_digital_pads = self.inner_pad_handler.get_all_digital_pads_with_inner_any(outer_pads, inner_pads, ring_config)
        # Get all digital IO pads
        digital_io_pads = self.inner_pad_handler.get_all_digital_pads_with_inner(outer_pads, inner_pads, ring_config)
        if not all_digital_pads:
            return skill_commands
        
        # Generate configuration lines (grouped by orientation)
        oriented_pads = {"R0": [], "R90": [], "R180": [], "R270": []}
        for pad in all_digital_pads:
            oriented_pads[pad["orientation"]].append(pad["position"])

        # Use helper to create config lines and corner connections, and get endpoints
        config_cmds, side_endpoints = self._generate_config_io_wires(oriented_pads, ring_config)
        skill_commands.extend(config_cmds)
        
        # Secondary lines and pin labels only for digital IO pads
        # Configuration offsets for digital IO wires (relative to pad edges)
        pin_offsets = {"OEN": 5.64, "I": 26.74, "DS": 40.61, "IE": 44.78, "C": 56.395, "PE": 67.73}
        vdd_wire_offset = 5
        gnd_wire_offset = 7
        # Common wire geometry parameters
        wire_width = 1
        secondary_wire_width = 1.2

        # Place vias and connect to configuration lines for digital power pads
        pad_height = ring_config.get("pad_height", 120)
        for pad in all_digital_pads:
            device_type = pad.get("device") or pad.get("device_type", "")
            if device_type in ["PVDD1CDG", "PVSS1CDG"]:  # Digital power pads
                x, y = pad["position"]
                orient = pad["orientation"]
                # the wire offset from the pad edge
                horizontal_offset = 20    
                vertical_offset = 2
                
                is_vdd = device_type == "PVDD1CDG"

                # Calculate via position (based on orientation)
                if orient == "R0":  # Bottom edge
                    config_x = x + horizontal_offset
                    config_y = y + pad_height - vertical_offset
                    # Configuration line y-coordinate
                    via_y = y + pad_height + (vdd_wire_offset if is_vdd else gnd_wire_offset)
                    via_x = config_x
                    # Draw line connecting via and configuration line
                    via_orientation = "R0"
                    skill_commands.append(f'dbCreatePath(cv list("METAL2" "drawing") list(list({via_x} {via_y + wire_width/2}) list({config_x} {config_y})) {wire_width})')
                elif orient == "R90":  # Right edge
                    config_x = x - pad_height + vertical_offset
                    config_y = y + horizontal_offset
                    via_x = x - pad_height - (vdd_wire_offset if is_vdd else gnd_wire_offset)
                    via_y = config_y
                    via_orientation = "R90"
                    skill_commands.append(f'dbCreatePath(cv list("METAL2" "drawing") list(list({via_x - wire_width/2} {via_y}) list({config_x} {config_y})) {wire_width})')
                elif orient == "R180":  # Top edge
                    config_x = x - horizontal_offset
                    config_y = y - pad_height + vertical_offset
                    via_y = y - pad_height - (vdd_wire_offset if is_vdd else gnd_wire_offset)
                    via_x = config_x
                    via_orientation = "R180"
                    skill_commands.append(f'dbCreatePath(cv list("METAL2" "drawing") list(list({via_x} {via_y - wire_width/2}) list({config_x} {config_y})) {wire_width})')
                elif orient == "R270":  # Left edge
                    config_x = x + pad_height - vertical_offset
                    config_y = y - horizontal_offset
                    via_x = x + pad_height + (vdd_wire_offset if is_vdd else gnd_wire_offset)
                    via_y = config_y
                    via_orientation = "R270"
                    skill_commands.append(f'dbCreatePath(cv list("METAL2" "drawing") list(list({via_x + wire_width/2} {via_y}) list({config_x} {config_y})) {wire_width})')
                else:
                    continue
                
                # Place via
                skill_commands.append("tech = techGetTechFile(cv)")
                skill_commands.append('viaParams = list(list("cutRows" 2) list("cutColumns" 2))')
                skill_commands.append('viaDefId = techFindViaDefByName(tech "M2_M1")')
                skill_commands.append(f'newVia = dbCreateVia(cv viaDefId list({via_x} {via_y}) "{via_orientation}" viaParams)')
        
        for pad in digital_io_pads:
            x, y = pad["position"]
            orient = pad["orientation"]
            is_input = pad["io_direction"] == "input"

            # Step 1: orientation-specific geometric preprocessing
            def get_wire_endpoint_geometry(orientation: str, end_config: str, pin_offset: float):
                if orientation == "R0":  # Bottom edge pad
                    basex_coord = x + pin_offset
                    basey_coord = y + ring_config["pad_height"] - wire_width
                    end_x_coord = x + pin_offset
                    end_y_coord = y + ring_config["pad_height"] + (vdd_wire_offset if end_config == "vdd" else gnd_wire_offset) + wire_width / 2
                    via_x = x + pin_offset
                    via_y = y + ring_config["pad_height"] + (vdd_wire_offset if end_config == "vdd" else gnd_wire_offset)
                    pin_just, pin_orient = "centerLeft", "R90"
                elif orientation == "R90":  # Right edge pad
                    basex_coord = x - ring_config["pad_height"] + wire_width
                    basey_coord = y + pin_offset
                    end_x_coord = x - ring_config["pad_height"] - (vdd_wire_offset if end_config == "vdd" else gnd_wire_offset) - wire_width / 2
                    end_y_coord = y + pin_offset
                    via_x = x - ring_config["pad_height"] - (vdd_wire_offset if end_config == "vdd" else gnd_wire_offset)
                    via_y = y + pin_offset
                    pin_just, pin_orient = "centerRight", "R0"
                elif orientation == "R180":  # Top edge pad
                    basex_coord = x - pin_offset
                    basey_coord = y - ring_config["pad_height"] + wire_width
                    end_x_coord = x - pin_offset
                    end_y_coord = y - ring_config["pad_height"] - (vdd_wire_offset if end_config == "vdd" else gnd_wire_offset) - wire_width / 2
                    via_x = x - pin_offset
                    via_y = y - ring_config["pad_height"] - (vdd_wire_offset if end_config == "vdd" else gnd_wire_offset)
                    pin_just, pin_orient = "centerRight", "R90"
                elif orientation == "R270":  # Left edge pad
                    basex_coord = x + ring_config["pad_height"] - wire_width
                    basey_coord = y - pin_offset
                    end_x_coord = x + ring_config["pad_height"] + (vdd_wire_offset if end_config == "vdd" else gnd_wire_offset) + wire_width / 2
                    end_y_coord = y - pin_offset
                    via_x = x + ring_config["pad_height"] + (vdd_wire_offset if end_config == "vdd" else gnd_wire_offset)
                    via_y = y - pin_offset
                    pin_just, pin_orient = "centerLeft", "R0"
                else:
                    return None

                if end_config == "null":
                    return basex_coord, basey_coord, 0, 0, 0, 0, pin_just, pin_orient
                return basex_coord, basey_coord, end_x_coord, end_y_coord, via_x, via_y, pin_just, pin_orient

            # Step 2: draw secondary lines and vias
            if is_input:
                end_configs = {"OEN": "vdd", "I": "gnd", "C": "null", "DS": "vdd", "PE": "gnd", "IE": "vdd"}
            else:
                end_configs = {"OEN": "gnd", "I": "null", "DS": "vdd", "PE": "gnd", "IE": "gnd"}

            for signal, end_config in end_configs.items():
                pin_offset = pin_offsets[signal]
                result = get_wire_endpoint_geometry(orient, end_config, pin_offset)
                if result is None:
                    continue
                basex_coord, basey_coord, end_x_coord, end_y_coord, via_x, via_y, pin_just, pin_orient = result
                if end_config != "null":
                    # Draw secondary line
                    skill_commands.append(
                        f'dbCreatePath(cv list("METAL2" "drawing") list(list({basex_coord} {basey_coord}) list({end_x_coord} {end_y_coord})) {secondary_wire_width})'
                    )
                    # Place via
                    skill_commands.append("tech = techGetTechFile(cv)")
                    skill_commands.append('viaParams = list(list("cutRows" 2) list("cutColumns" 2))')
                    skill_commands.append('viaDefId = techFindViaDefByName(tech "M2_M1")')
                    skill_commands.append(
                        f'newVia = dbCreateVia(cv viaDefId list({via_x} {via_y}) "{orient}" viaParams)'
                    )
                else:
                    # Create pin label (always at base)
                    skill_commands.append(
                        f'dbCreateLabel(cv list("METAL1" "pin") list({basex_coord} {basey_coord}) "{pad["name"]}_CORE" "{pin_just}" "{pin_orient}" "roman" 2)'
                    )
        return skill_commands
    
    def generate_pin_labels_with_inner(self, outer_pads: List[dict], inner_pads: List[dict], ring_config: dict) -> List[str]:
        """Generate main pin labels for 180nm, supporting inner pads"""
        skill_commands = []
        
        # Main pin labels for outer pads
        for pad in outer_pads:
            x, y = pad["position"]
            orient = pad["orientation"]
            name = pad["name"]
            
            # Calculate pin label position (matching merge_source for 180nm)
            if orient == "R0":  # bottom edge pad
                pin_pos = f'list({x + 40} {y - 70})'
                justification, pin_orient = "centerRight", "R90"
            elif orient == "R90":  # right edge pad
                pin_pos = f'list({x + 70} {y + 40})'
                justification, pin_orient = "centerLeft", "R0"
            elif orient == "R180":  # top edge pad
                pin_pos = f'list({x - 40} {y + 70})'
                justification, pin_orient = "centerLeft", "R90"
            elif orient == "R270":  # left edge pad
                pin_pos = f'list({x - 70} {y - 40})'
                justification, pin_orient = "centerRight", "R0"
            
            skill_commands.append(f'dbCreateLabel(cv list("METAL6" "pin") {pin_pos} "{name}" "{justification}" "{pin_orient}" "roman" 10)')
            
            # Create core label for voltage domain components
            if VoltageDomainHandler.is_voltage_domain_provider(pad):
                # Calculate core label position (within the pad)
                if orient == "R0":
                    core_pos = f'list({x + 10} {y + ring_config["pad_height"] - 0.1})'
                    core_just, core_orient = "centerLeft", "R90"
                elif orient == "R90":
                    core_pos = f'list({x - ring_config["pad_height"] + 0.1} {y + 10})'
                    core_just, core_orient = "centerRight", "R0"
                elif orient == "R180":
                    core_pos = f'list({x - 10} {y - ring_config["pad_height"] + 0.1})'
                    core_just, core_orient = "centerRight", "R90"
                elif orient == "R270":
                    core_pos = f'list({x + ring_config["pad_height"] - 0.1} {y - 10})'
                    core_just, core_orient = "centerLeft", "R0"
                
                skill_commands.append(f'dbCreateLabel(cv list("M2" "pin") {core_pos} "{name}_CORE" "{core_just}" "{core_orient}" "roman" 2)')
        
        # Main pin labels for inner pads (move 152 units inward, opposite direction)
        for inner_pad in inner_pads:
            # If position is already absolute coordinates, use directly
            if isinstance(inner_pad["position"], list):
                position = inner_pad["position"]
                orient = inner_pad["orientation"]
            else:
                # Otherwise, recalculate position
                position, orient = self.inner_pad_handler.calculate_inner_pad_position(inner_pad["position"], outer_pads, ring_config)
            
            x, y = position
            name = inner_pad["name"]
            
            # Calculate pin label position for inner pads (move inward) and direction (opposite to outer)
            if orient == "R0":  # Bottom edge inner pad
                pin_pos = f'list({x + 10} {y + 152})'  # Move inward (up)
                justification, pin_orient = "centerLeft", "R90"  # Opposite direction
            elif orient == "R90":  # Right edge inner pad
                pin_pos = f'list({x - 152} {y + 10})'  # Move inward (left)
                justification, pin_orient = "centerRight", "R0"  # Opposite direction
            elif orient == "R180":  # Top edge inner pad
                pin_pos = f'list({x - 10} {y - 152})'  # Move inward (down)
                justification, pin_orient = "centerRight", "R90"  # Opposite direction
            elif orient == "R270":  # Left edge inner pad
                pin_pos = f'list({x + 152} {y - 10})'  # Move inward (right)
                justification, pin_orient = "centerLeft", "R0"  # Opposite direction
            
            skill_commands.append(f'dbCreateLabel(cv list("AP" "pin") {pin_pos} "{name}" "{justification}" "{pin_orient}" "roman" 10)')
            
            # Create core label for inner pad voltage domain components
            if VoltageDomainHandler.is_voltage_domain_provider(inner_pad):
                # Calculate core label position for inner pads (within the pad, opposite to outer)
                if orient == "R0":  # Bottom edge inner pad
                    core_pos = f'list({x + 10} {y + ring_config["pad_height"] - 0.1})'
                    core_just, core_orient = "centerLeft", "R90"
                elif orient == "R90":  # Right edge inner pad
                    core_pos = f'list({x - ring_config["pad_height"] + 0.1} {y + 10})'
                    core_just, core_orient = "centerRight", "R0"
                elif orient == "R180":  # Top edge inner pad
                    core_pos = f'list({x - 10} {y - ring_config["pad_height"] + 0.1})'
                    core_just, core_orient = "centerRight", "R90"
                elif orient == "R270":  # Left edge inner pad
                    core_pos = f'list({x + ring_config["pad_height"] - 0.1} {y - 10})'
                    core_just, core_orient = "centerLeft", "R0"
                
                skill_commands.append(f'dbCreateLabel(cv list("M2" "pin") {core_pos} "{name}_CORE" "{core_just}" "{core_orient}" "roman" 2)')
        
        return skill_commands

    def generate_psub2(self, outer_pads: List[dict], corners: List[dict], ring_config: dict) -> List[str]:
        """Generate PSUB2 layer for 180nm process"""
        chip_width = ring_config.get("chip_width", 0)
        chip_height = ring_config.get("chip_height", 0)
        pad_width = ring_config.get("pad_width", 80)
        pad_height = ring_config.get("pad_height", 120)
        skill_commands = []
        if not outer_pads:
            return skill_commands
        skill_commands.append('; --- PSUB2 edge rectangles and corner polygons')
        pad_w = ring_config.get("pad_width", 80)
        pad_h = ring_config.get("pad_height", 120)

        for pads in outer_pads:
            # Skip certain device types for PSUB2
            device = pads.get("device", pads.get("device_type", ""))
            if device == "PVSS1CDG" or device == "PDDW0412SCDG":
                continue
            xs = pads["position"][0]
            ys = pads["position"][1]
            orient = pads["orientation"]
            h_offset = 1.5
            vl_offset = 82.5
            vh_offset = 115
            # pads PSUB2
            if orient == "R0":
                # bottom edge pads
                x1 = xs + h_offset
                y1 = ys + vl_offset
                x2 = xs + pad_w - h_offset
                y2 = ys + vh_offset
            elif orient == "R90":
                # right edge pads
                x1 = xs - vl_offset
                y1 = ys + h_offset
                x2 = xs - vh_offset
                y2 = ys + pad_w - h_offset
            elif orient == "R180":
                # top edge pads
                x1 = xs - h_offset
                y1 = ys - vl_offset
                x2 = xs - pad_w + h_offset
                y2 = ys - vh_offset
            elif orient == "R270":
                # left edge pads
                x1 = xs + vl_offset
                y1 = ys - h_offset
                x2 = xs + vh_offset
                y2 = ys - pad_w + h_offset
            skill_commands.append(f'dbCreateRect(cv list("PSUB2" "drawing") list(list({x1} {y1}) list({x2} {y2})))')
        
        # Corner PSUB2 polygons
        for corner in corners:
            x, y = corner["position"]
            orient = corner["orientation"]
            corner_size = ring_config.get("corner_size", 130)
            
            if orient == "R0":  # Bottom-left corner
                pts = f'list(list({x} {y + 94.5}) list({x + 127} {y + 94.5}) list({x + 127} {y + 120}) list({x + 120} {y + 120}) list({x + 120} {y + 127}) list({x + 94.5} {y + 127}) list({x + 94.5} {y + corner_size}) list({x} {y + corner_size}))'
            elif orient == "R90":  # Bottom-right corner
                pts = f'list(list({x - 94.5} {y}) list({x - 127} {y}) list({x - 127} {y + 94.5}) list({x - 120} {y + 94.5}) list({x - 120} {y + 127}) list({x - 94.5} {y + 127}) list({x - 94.5} {y + corner_size}) list({x} {y + corner_size}))'
            elif orient == "R180":  # Top-right corner
                pts = f'list(list({x} {y - 94.5}) list({x - 127} {y - 94.5}) list({x - 127} {y - 120}) list({x - 120} {y - 120}) list({x - 120} {y - 127}) list({x - 94.5} {y - 127}) list({x - 94.5} {y - corner_size}) list({x} {y - corner_size}))'
            elif orient == "R270":  # Top-left corner
                pts = f'list(list({x + 94.5} {y}) list({x + 127} {y}) list({x + 127} {y - 94.5}) list({x + 120} {y - 94.5}) list({x + 120} {y - 127}) list({x + 94.5} {y - 127}) list({x + 94.5} {y - corner_size}) list({x} {y - corner_size}))'
            else:
                continue
            
            skill_commands.append(f'dbCreatePolygon(cv list("PSUB2" "drawing") {pts})')
        
        # Edge rectangles (with cut support)
        cut_orient_index = {"R0": [], "R90": [], "R180": [], "R270": []}
        for pads in outer_pads:
            device = pads.get("device", pads.get("device_type", ""))
            if device == "PFILLER10":  # Cut device
                orient = pads["orientation"]
                if orient == "R0":
                    cut_orient_index["R0"].append(pads["position"][0])
                elif orient == "R90":
                    cut_orient_index["R90"].append(pads["position"][1])
                elif orient == "R180":
                    cut_orient_index["R180"].append(pads["position"][0])
                elif orient == "R270":
                    cut_orient_index["R270"].append(pads["position"][1])
        
        # Generate edge rectangles with cut support
        if cut_orient_index["R0"]:
            skill_commands.append(f'dbCreateRect(cv list("PSUB2" "drawing") list(list(127 94.5) list({cut_orient_index["R0"][0] - 2.5} 120)))')  # bottom edge part before cut
            skill_commands.append(f'dbCreateRect(cv list("PSUB2" "drawing") list(list({cut_orient_index["R0"][0] + 2.5} 94.5) list({chip_width - 127} 120) ))') # bottom edge part after cut
        else:
            skill_commands.append(f'dbCreateRect(cv list("PSUB2" "drawing") list(list(127 94.5) list({chip_width - 127} 120)))') 
        
        if cut_orient_index["R90"]:
            skill_commands.append(f'dbCreateRect(cv list("PSUB2" "drawing") list(list({chip_width - 94.5} 127) list({chip_width - 120} {cut_orient_index["R90"][0] - 2.5})))')  # right edge part before cut
            skill_commands.append(f'dbCreateRect(cv list("PSUB2" "drawing") list(list({chip_width - 94.5} {cut_orient_index["R90"][0] + 2.5}) list({chip_width - 120} {chip_height - 127})))')  # right edge part after cut
        else:
            skill_commands.append(f'dbCreateRect(cv list("PSUB2" "drawing") list(list({chip_width - 94.5} 127) list({chip_width - 120} {chip_height - 127})))')
        
        if cut_orient_index["R180"]:
            skill_commands.append(f'dbCreateRect(cv list("PSUB2" "drawing") list(list(127 {chip_height - 94.5}) list({cut_orient_index["R180"][0] - 2.5} {chip_height - 120})))')  # top edge part before cut
            skill_commands.append(f'dbCreateRect(cv list("PSUB2" "drawing") list(list({cut_orient_index["R180"][0] + 2.5} {chip_height - 120}) list({chip_width - 127} {chip_height - 94.5})))')  # top edge part after cut
        else:
            skill_commands.append(f'dbCreateRect(cv list("PSUB2" "drawing") list(list({chip_width - 127} {chip_height - 120}) list(127 {chip_height - 94.5})))')  # top edge
        
        if cut_orient_index["R270"]:
            skill_commands.append(f'dbCreateRect(cv list("PSUB2" "drawing") list(list(94.5 127) list(120 {cut_orient_index["R270"][0] - 2.5})))')  # left edge part before cut
            skill_commands.append(f'dbCreateRect(cv list("PSUB2" "drawing") list(list(94.5 {cut_orient_index["R270"][0] + 2.5}) list(120 {chip_height - 127})))')  # left edge part after cut
        else:
            skill_commands.append(f'dbCreateRect(cv list("PSUB2" "drawing") list(list(94.5 127) list(120 {chip_height - 127})))')  # left edge

        return skill_commands

