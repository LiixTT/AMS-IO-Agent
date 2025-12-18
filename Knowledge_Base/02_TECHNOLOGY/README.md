# Technology-Specific DRC Rules

Technology node specific design rule check (DRC) parameters for IO ring design.

## Directories

- **T28/** - 28nm process DRC rules
- **T180/** - 180nm process DRC rules

## Purpose

Contains technology-specific DRC rules including minimum spacing, minimum width, and metal layer configurations for different process nodes.

## Usage

Load the appropriate technology configuration based on your target process node:
- For 28nm designs: Load `T28/T28_Technology.md`
- For 180nm designs: Load `T180/T180_Technology.md`

These rules are used to validate IO ring layouts and ensure DRC compliance.
