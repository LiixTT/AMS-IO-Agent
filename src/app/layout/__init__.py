#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layout Generator Package
"""

# Factory functions (recommended way)
from .layout_generator_factory import (
    create_layout_generator,
    generate_layout_from_json,
    validate_layout_config
)

# Process node specific generators
from .T28 import LayoutGeneratorT28, SkillGeneratorT28, AutoFillerGeneratorT28
from .T180 import LayoutGeneratorT180, SkillGeneratorT180, AutoFillerGeneratorT180

# Shared/common modules
from .device_classifier import DeviceClassifier
from .voltage_domain import VoltageDomainHandler
from .position_calculator import PositionCalculator
from .filler_generator import FillerGenerator
from .layout_validator import LayoutValidator
from .process_node_config import get_process_node_config, get_template_file_paths, list_supported_process_nodes

# InnerPadHandler is T28-specific (T180 implementation pending)
from .T28.inner_pad_handler import InnerPadHandler

# Backward compatibility: Export old names
# These imports allow old code to continue working
from .T28.layout_generator import LayoutGeneratorT28 as _LayoutGeneratorT28
from .T28.skill_generator import SkillGeneratorT28 as _SkillGeneratorT28
from .T28.auto_filler import AutoFillerGeneratorT28 as _AutoFillerGeneratorT28
from .T180.layout_generator import LayoutGeneratorT180 as _LayoutGeneratorT180
from .T180.skill_generator import SkillGeneratorT180 as _SkillGeneratorT180
from .T180.auto_filler import AutoFillerGeneratorT180 as _AutoFillerGeneratorT180

# Visualizers
from .T28.layout_visualizer import visualize_layout, visualize_layout_from_components
from .T180.layout_visualizer import visualize_layout_T180, visualize_layout_from_components_T180

__all__ = [
    # Factory functions
    'create_layout_generator',
    'generate_layout_from_json',
    'validate_layout_config',
    # Process node generators
    'LayoutGeneratorT28',
    'LayoutGeneratorT180',
    'SkillGeneratorT28',
    'SkillGeneratorT180',
    'AutoFillerGeneratorT28',
    'AutoFillerGeneratorT180',
    # Shared modules
    'DeviceClassifier',
    'VoltageDomainHandler',
    'PositionCalculator',
    'FillerGenerator',
    'LayoutValidator',
    'InnerPadHandler',
    'get_process_node_config',
    'get_template_file_paths',
    'list_supported_process_nodes',
    # Visualizers
    'visualize_layout',
    'visualize_layout_from_components',
    'visualize_layout_T180',
    'visualize_layout_from_components_T180',
]
