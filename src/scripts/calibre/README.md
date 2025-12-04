# Calibre Scripts

Calibre verification scripts for different technology nodes.

## Directory Structure

- **T28/** - 28nm technology node rule files and templates
- **T180/** - 180nm technology node rule files and templates
- **env_common.csh** - Unified environment configuration file
- **run_drc.csh** - Unified DRC script (supports both 28nm and 180nm)
- **run_lvs.csh** - Unified LVS script (supports both 28nm and 180nm)
- **run_pex.csh** - Unified PEX script (supports both 28nm and 180nm)

## Configuration

### Environment Setup

1. Edit `env_common.csh` to configure:
   - PDK layer map paths (`PDK_LAYERMAP_28`, `PDK_LAYERMAP_180`)
   - Calibre installation path (`MGC_HOME`)
   - Include files for LVS (`incFILE_28`, `incFILE_180`)
   - Default process node (`PROCESS_NODE`)
   - Run directories (`DRC_RUN_DIR`, `LVS_RUN_DIR`, `PEX_RUN_DIR`)

2. Set `CDS_LIB_PATH` in project `.env` file or in `env_common.csh`:
   ```
   CDS_LIB_PATH=/absolute/path/to/cds.lib
   ```

## Usage

### DRC (Design Rule Check)

```bash
# Basic usage (default view: layout, default process from env_common.csh)
./run_drc.csh <library> <topCell>

# Specify view
./run_drc.csh <library> <topCell> <view>

# Specify view and process node
./run_drc.csh <library> <topCell> <view> <process>
```

### LVS (Layout vs Schematic)

```bash
# Basic usage (default view: layout, default process from env_common.csh)
./run_lvs.csh <library> <topCell>

# Specify view
./run_lvs.csh <library> <topCell> <view>

# Specify view and process node
./run_lvs.csh <library> <topCell> <view> <process>
```

### PEX (Parasitic Extraction)

```bash
# Basic usage (default view: layout, default process from env_common.csh)
./run_pex.csh <library> <topCell>

# Specify view
./run_pex.csh <library> <topCell> <view>

# Specify view and process node
./run_pex.csh <library> <topCell> <view> <process>

# Specify view, process node, and run directory
./run_pex.csh <library> <topCell> <view> <process> <runDir>
```

## Examples

```bash
# Run DRC for 28nm process with default layout view
./run_drc.csh LLM_Layout_Design test_DRC layout 28

# Run LVS for 180nm process with custom view
./run_lvs.csh LLM_Layout_Design test_v2 myLayoutView 180

# Run PEX using default process node and view
./run_pex.csh LLM_Layout_Design test_PEX

# Run PEX with custom run directory
./run_pex.csh LLM_Layout_Design test_PEX layout 28 /custom/path/pex
```

## Notes

- All scripts automatically source `env_common.csh` for configuration
- Rule files are located in `T28/` and `T180/` subdirectories
- Output files are written to directories specified in `env_common.csh`
- The scripts support both "28" and "28nm" style process node specifications
