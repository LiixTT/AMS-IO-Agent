#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Filler Component Generation Module for T28
"""

from typing import List
from ..device_classifier import DeviceClassifier
from ..voltage_domain import VoltageDomainHandler
from ..filler_generator import FillerGenerator
from ..position_calculator import PositionCalculator
from .inner_pad_handler import InnerPadHandler
from ..process_node_config import get_process_node_config


def get_corner_domain(oriented_pads, corner_orientation) -> str:
    """Get corner domain based on the two pads around the corner.
    
    If the two adjacent pads share the same domain, return that domain;
    otherwise, default to "analog". If either pad is missing, also
    default to "analog".
    
    For 180nm, use pad.get("domain") directly if available, otherwise use VoltageDomainHandler.
    """
    pad1 = None
    pad2 = None
    if corner_orientation == "R180":  # Top edge
        left_pads = oriented_pads.get("R270", [])
        top_pads = oriented_pads.get("R180", [])
        pad1 = left_pads[-1] if left_pads else None
        pad2 = top_pads[0] if top_pads else None
    elif corner_orientation == "R90":  # Right edge
        top_pads = oriented_pads.get("R180", [])
        right_pads = oriented_pads.get("R90", [])
        pad1 = top_pads[-1] if top_pads else None
        pad2 = right_pads[0] if right_pads else None
    elif corner_orientation == "R0":  # Bottom edge
        right_pads = oriented_pads.get("R90", [])
        bottom_pads = oriented_pads.get("R0", [])
        pad1 = right_pads[-1] if right_pads else None
        pad2 = bottom_pads[0] if bottom_pads else None
    elif corner_orientation == "R270":  # Left edge
        bottom_pads = oriented_pads.get("R0", [])
        left_pads = oriented_pads.get("R270", [])
        pad1 = bottom_pads[-1] if bottom_pads else None
        pad2 = left_pads[0] if left_pads else None
    
    if pad1 and pad2:
        # For 180nm, prefer pad.get("domain") if available
        domain1 = pad1.get("domain") or VoltageDomainHandler.get_voltage_domain(pad1)
        domain2 = pad2.get("domain") or VoltageDomainHandler.get_voltage_domain(pad2)
        # Normalize "null" to None for comparison
        if domain1 == "null":
            domain1 = None
        if domain2 == "null":
            domain2 = None
        if domain1 and domain2 and domain1 == domain2:
            return domain1
    
    # Default to analog if pads don't match or are missing
    return "analog"


class AutoFillerGeneratorT28:
    """Auto Filler Component Generator for T28 process node"""
    
    def __init__(self, config: dict):
        self.config = config
        self.position_calculator = PositionCalculator(config)
        self.inner_pad_handler = InnerPadHandler(config)
    
    def auto_insert_fillers_with_inner_pads(self, layout_components: List[dict], inner_pads: List[dict]) -> List[dict]:
        """Auto-insert filler components for 28nm, supporting inner pad space reservation, compatible with clockwise and counterclockwise placement"""
        process_node = self.config.get("process_node", "T28")
        
        # Check if filler components are already included
        existing_fillers = [comp for comp in layout_components if comp.get("type") == "filler" or DeviceClassifier.is_filler_device(comp.get("device", ""), process_node)]
        existing_separators = [comp for comp in layout_components if comp.get("type") == "separator" or DeviceClassifier.is_separator_device(comp.get("device", ""), process_node)]
        
        if existing_fillers or existing_separators:
            print(f"🔍 Detected filler components in intent graph: {len(existing_fillers)} fillers, {len(existing_separators)} separators")
            print("📝 Skipping auto-filler generation, using components defined in intent graph")
            return layout_components
        
        # Get placement order
        placement_order = self.config.get("placement_order", "counterclockwise")
        
        # Sort components by position
        sorted_components = self.position_calculator.sort_components_by_position(layout_components, placement_order)
        
        # Separate pads and corners
        pads = [comp for comp in sorted_components if comp.get("type") == "pad"]
        corners = [comp for comp in sorted_components if comp.get("type") == "corner"]
        
        # Group pads by orientation
        oriented_pads = {"R0": [], "R90": [], "R180": [], "R270": []}
        for pad in pads:
            orientation = pad.get("orientation", "")
            if orientation in oriented_pads:
                oriented_pads[orientation].append(pad)
        
        # Sort pads by orientation (adjust based on placement order)
        for orientation in oriented_pads:
            if placement_order == "clockwise":
                # Clockwise sorting
                if orientation == "R180":  # Top edge, left to right
                    oriented_pads[orientation].sort(key=lambda x: x["position"][0])
                elif orientation == "R90":  # Right edge, top to bottom
                    oriented_pads[orientation].sort(key=lambda x: x["position"][1], reverse=True)
                elif orientation == "R0":  # Bottom edge, right to left
                    oriented_pads[orientation].sort(key=lambda x: x["position"][0], reverse=True)
                elif orientation == "R270":  # Left edge, bottom to top
                    oriented_pads[orientation].sort(key=lambda x: x["position"][1])
            else:
                # Counterclockwise sorting
                if orientation == "R270":  # Left edge, bottom to top
                    oriented_pads[orientation].sort(key=lambda x: x["position"][1])
                elif orientation == "R0":  # Bottom edge, right to left
                    oriented_pads[orientation].sort(key=lambda x: x["position"][0], reverse=True)
                elif orientation == "R90":  # Right edge, top to bottom
                    oriented_pads[orientation].sort(key=lambda x: x["position"][1], reverse=True)
                elif orientation == "R180":  # Top edge, left to right
                    oriented_pads[orientation].sort(key=lambda x: x["position"][0])
        
        # Get configuration parameters
        pad_width = 20
        pad_height = 110
        corner_size = 110
        # Get chip dimensions from config (matching merge_source - uses ring_config values)
        chip_width = self.config.get("chip_width")
        chip_height = self.config.get("chip_height")
        # Fallback to calculation if not in config
        if chip_width is None or chip_height is None:
            chip_width, chip_height = self.position_calculator.calculate_chip_size(sorted_components)
        
        fillers = []
        
        # Get pad information on both sides of corner to determine filler type
        def get_adjacent_pads_for_corner(corner_orientation, is_first_corner):
            """Get pads on both sides of corner"""
            if corner_orientation == "R180":  # Top edge
                if is_first_corner:  # Top-left corner
                    left_pads = oriented_pads.get("R270", [])
                    top_pads = oriented_pads.get("R180", [])
                    return (left_pads[-1] if left_pads else None, top_pads[0] if top_pads else None)
                else:  # Top-right corner
                    top_pads = oriented_pads.get("R180", [])
                    right_pads = oriented_pads.get("R90", [])
                    return (top_pads[-1] if top_pads else None, right_pads[0] if right_pads else None)
            elif corner_orientation == "R90":  # Right edge
                if is_first_corner:  # Top-right corner
                    top_pads = oriented_pads.get("R180", [])
                    right_pads = oriented_pads.get("R90", [])
                    return (top_pads[-1] if top_pads else None, right_pads[0] if right_pads else None)
                else:  # Bottom-right corner
                    right_pads = oriented_pads.get("R90", [])
                    bottom_pads = oriented_pads.get("R0", [])
                    return (right_pads[-1] if right_pads else None, bottom_pads[0] if bottom_pads else None)
            elif corner_orientation == "R0":  # Bottom edge
                if is_first_corner:  # Bottom-right corner
                    right_pads = oriented_pads.get("R90", [])
                    bottom_pads = oriented_pads.get("R0", [])
                    return (right_pads[-1] if right_pads else None, bottom_pads[0] if bottom_pads else None)
                else:  # Bottom-left corner
                    bottom_pads = oriented_pads.get("R0", [])
                    left_pads = oriented_pads.get("R270", [])
                    return (bottom_pads[-1] if bottom_pads else None, left_pads[0] if left_pads else None)
            elif corner_orientation == "R270":  # Left edge
                if is_first_corner:  # Bottom-left corner
                    bottom_pads = oriented_pads.get("R0", [])
                    left_pads = oriented_pads.get("R270", [])
                    return (bottom_pads[-1] if bottom_pads else None, left_pads[0] if left_pads else None)
                else:  # Top-left corner
                    left_pads = oriented_pads.get("R270", [])
                    top_pads = oriented_pads.get("R180", [])
                    return (left_pads[-1] if left_pads else None, top_pads[0] if top_pads else None)
            return (None, None)
        
        # Process each orientation's pads
        for orientation, pad_list in oriented_pads.items():
            if not pad_list:
                continue
            
            # 1. Filler between corner and first pad (28nm only)
            if orientation == "R180":  # Top edge
                # Between top-left corner and first pad
                first_pad = pad_list[0]
                x = first_pad["position"][0] - pad_width
                y = chip_height  # 28nm: filler on top edge, not chip_height - pad_height
                pad1, pad2 = get_adjacent_pads_for_corner("R180", True)
                filler_type = FillerGenerator.get_filler_type_for_corner_and_pad("PCORNERA_G", pad1, pad2, process_node)
                fillers.append({
                    "type": "filler",
                    "name": "sep_top_left_corner",
                    "device": filler_type,
                    "position": [x, y],
                    "orientation": "R180"
                })
                
                # Between last pad and top-right corner
                last_pad = pad_list[-1]
                x = last_pad["position"][0] + pad_width
                y = chip_height  # 28nm: filler on top edge, not chip_height - pad_height
                pad1, pad2 = get_adjacent_pads_for_corner("R180", False)
                filler_type = FillerGenerator.get_filler_type_for_corner_and_pad("PCORNERA_G", pad1, pad2, process_node)
                fillers.append({
                    "type": "filler",
                    "name": "filler_top_right_corner",
                    "device": filler_type,
                    "position": [x, y],
                    "orientation": "R180"
                })
                
            elif orientation == "R90":  # Right edge
                # Between top-right corner and first pad
                first_pad = pad_list[0]
                x = chip_width  # 28nm: filler on right edge, not chip_width - pad_height
                y = first_pad["position"][1] + pad_width
                pad1, pad2 = get_adjacent_pads_for_corner("R90", True)
                filler_type = FillerGenerator.get_filler_type_for_corner_and_pad("PCORNERA_G", pad1, pad2, process_node)
                fillers.append({
                    "type": "filler",
                    "name": "filler_right_top_corner",
                    "device": filler_type,
                    "position": [x, y],
                    "orientation": "R90"
                })
                
                # Between last pad and bottom-right corner
                last_pad = pad_list[-1]
                x = chip_width  # 28nm: filler on right edge, not chip_width - pad_height
                y = last_pad["position"][1] - pad_width
                pad1, pad2 = get_adjacent_pads_for_corner("R90", False)
                filler_type = FillerGenerator.get_filler_type_for_corner_and_pad("PCORNERA_G", pad1, pad2, process_node)
                fillers.append({
                    "type": "filler",
                    "name": "filler_right_bottom_corner",
                    "device": filler_type,
                    "position": [x, y],
                    "orientation": "R90"
                })
                
            elif orientation == "R0":  # Bottom edge
                # Between bottom-right corner and first pad
                first_pad = pad_list[0]
                x = first_pad["position"][0] + pad_width
                y = 0
                pad1, pad2 = get_adjacent_pads_for_corner("R0", True)
                filler_type = FillerGenerator.get_filler_type_for_corner_and_pad("PCORNERA_G", pad1, pad2, process_node)
                fillers.append({
                    "type": "filler",
                    "name": "sep_bottom_right_corner",
                    "device": filler_type,
                    "position": [x, y],
                    "orientation": "R0"
                })
                
                # Between last pad and bottom-left corner
                last_pad = pad_list[-1]
                x = last_pad["position"][0] - pad_width
                y = 0
                pad1, pad2 = get_adjacent_pads_for_corner("R0", False)
                filler_type = FillerGenerator.get_filler_type_for_corner_and_pad("PCORNER_G", pad1, pad2, process_node)
                fillers.append({
                    "type": "filler",
                    "name": "filler_bottom_left_corner",
                    "device": filler_type,
                    "position": [x, y],
                    "orientation": "R0"
                })
                
            elif orientation == "R270":  # Left edge
                # Between bottom-left corner and first pad
                first_pad = pad_list[0]
                x = 0
                y = first_pad["position"][1] - pad_width
                pad1, pad2 = get_adjacent_pads_for_corner("R270", True)
                filler_type = FillerGenerator.get_filler_type_for_corner_and_pad("PCORNER_G", pad1, pad2, process_node)
                fillers.append({
                    "type": "filler",
                    "name": "filler_left_bottom_corner",
                    "device": filler_type,
                    "position": [x, y],
                    "orientation": "R270"
                })
                
                # Between last pad and top-left corner
                last_pad = pad_list[-1]
                x = 0
                y = last_pad["position"][1] + pad_width
                pad1, pad2 = get_adjacent_pads_for_corner("R270", False)
                filler_type = FillerGenerator.get_filler_type_for_corner_and_pad("PCORNERA_G", pad1, pad2, process_node)
                fillers.append({
                    "type": "filler",
                    "name": "sep_left_top_corner",
                    "device": filler_type,
                    "position": [x, y],
                    "orientation": "R270"
                })
            
            # 2. Filler between pads
            for i in range(len(pad_list) - 1):
                curr_pad = pad_list[i]
                next_pad = pad_list[i + 1]
                
                # Calculate filler position (28nm logic - fillers on edges, not offset by pad_height)
                if orientation == "R0":  # Bottom edge
                    x = curr_pad["position"][0] - pad_width
                    y = 0
                elif orientation == "R90":  # Right edge
                    x = chip_width  # 28nm: filler on right edge, not chip_width - pad_height
                    y = curr_pad["position"][1] - pad_width
                elif orientation == "R180":  # Top edge
                    x = curr_pad["position"][0] + pad_width
                    y = chip_height  # 28nm: filler on top edge, not chip_height - pad_height
                elif orientation == "R270":  # Left edge
                    x = 0
                    y = curr_pad["position"][1] + pad_width
                
                # 28nm: Use original logic with 2 fillers
                curr_index = sorted_components.index(curr_pad)
                next_index = sorted_components.index(next_pad)
                
                if self.inner_pad_handler.is_inner_pad_gap_by_index(curr_index, next_index, inner_pads, sorted_components):
                    # Reserve space for inner pad, use 10 unit filler
                    filler_type = FillerGenerator.get_filler_type(curr_pad, next_pad, process_node)
                    
                    # If in the same voltage domain, use 10 unit filler
                    if VoltageDomainHandler.get_voltage_domain(curr_pad) == VoltageDomainHandler.get_voltage_domain(next_pad):
                        if "PFILLER" in filler_type:
                            # Replace 20 unit filler with 10 unit
                            filler_type = filler_type.replace("PFILLER20", "PFILLER10")
                    
                    # Position of the first filler (move 10 units in counterclockwise direction)
                    if orientation == "R0":  # Bottom edge
                        x1 = x + 10
                        y1 = y
                    elif orientation == "R90":  # Right edge
                        x1 = x
                        y1 = y + 10
                    elif orientation == "R180":  # Top edge
                        x1 = x - 10
                        y1 = y
                    elif orientation == "R270":  # Left edge
                        x1 = x
                        y1 = y - 10

                    fillers.append({
                        "type": "filler",
                        "name": f"filler_{orientation}_{i+1}_1",
                        "device": filler_type,
                        "position": [x1, y1],
                        "orientation": orientation
                    })
                    
                    # Position of the second filler
                    if orientation == "R0":  # Bottom edge
                        x2 = x - 20
                        y2 = y
                    elif orientation == "R90":  # Right edge
                        x2 = x
                        y2 = y - 20
                    elif orientation == "R180":  # Top edge
                        x2 = x + 20
                        y2 = y
                    elif orientation == "R270":  # Left edge
                        x2 = x
                        y2 = y + 20
                    
                    fillers.append({
                        "type": "filler",
                        "name": f"filler_{orientation}_{i+1}_2",
                        "device": filler_type,
                        "position": [x2, y2],
                        "orientation": orientation
                    })
                else:
                    # Normal spacing, use 20 unit filler
                    filler_type = FillerGenerator.get_filler_type(curr_pad, next_pad, process_node)
                    
                    # Insert two 20 unit fillers
                    fillers.append({
                        "type": "filler",
                        "name": f"filler_{orientation}_{i+1}_1",
                        "device": filler_type,
                        "position": [x, y],
                        "orientation": orientation
                    })
                    
                    # Position of the second filler
                    if orientation == "R0":  # Bottom edge
                        x2 = x - 20
                        y2 = y
                    elif orientation == "R90":  # Right edge
                        x2 = x
                        y2 = y - 20
                    elif orientation == "R180":  # Top edge
                        x2 = x + 20
                        y2 = y
                    elif orientation == "R270":  # Left edge
                        x2 = x
                        y2 = y + 20
                    
                    fillers.append({
                        "type": "filler",
                        "name": f"filler_{orientation}_{i+1}_2",
                        "device": filler_type,
                        "position": [x2, y2],
                        "orientation": orientation
                    })
        
        return layout_components + fillers

