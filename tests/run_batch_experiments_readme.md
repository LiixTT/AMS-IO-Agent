# Batch Experiments - IO Ring Design

This project provides batch experiment capabilities for IO Ring design testing and validation.

## Experiment Types

The project supports IO Ring experiments for comprehensive testing across different configurations:

1. **IO Ring Experiments**: Test IO ring generation with various pad configurations, ring topologies, and voltage domains

## Usage

### IO Ring Batch Experiments

Run batch IO ring experiments for comprehensive testing.

#### Basic Usage

```bash
# Run all IO ring experiments
python tests/run_IO_Ring_batch.py

# Run with specific model
python tests/run_IO_Ring_batch.py --model-name deepseek

# Start from specific index
python tests/run_IO_Ring_batch.py --start-index 5

# Run only first 10 experiments
python tests/run_IO_Ring_batch.py --stop-index 10

# Dry run to preview experiments
python tests/run_IO_Ring_batch.py --dry-run
```

#### Experiment Configuration

- **Pad Configurations**: 3x3, 6x6, 12x12, 12x18, 18x18
- **Ring Topologies**: Single ring, Double ring
- **Design Types**: Digital, Analog, Mixed-signal
- **Voltage Domains**: Single domain, Multi-domain
- **Total Test Cases**: 20+ configurations

## Common Parameters

All experiment types support the following parameters:

### Model Configuration
- `--model-name`: Model name (e.g., 'claude', 'gpt-4o', 'deepseek')

### Experiment Range
- `--start-index`: Start from the Nth experiment (1-based)
- `--stop-index`: Run up to the Nth experiment (inclusive)

### Preview and Testing
- `--dry-run`: Preview mode, only list experiments to be run
- `--list-layouts`: List all available test configurations

### RAMIC Configuration
- `--ramic-port`: RAMIC bridge port number
- `--ramic-host`: RAMIC host address (default: localhost)

### Advanced Options

```bash
# List all available test cases
python tests/run_IO_Ring_batch.py --list-layouts

# Run specific range of tests
python tests/run_IO_Ring_batch.py --start-index 1 --stop-index 5 --model-name deepseek

# Use custom RAMIC port
python tests/run_IO_Ring_batch.py --ramic-port 9124
```

## Test Configurations

The IO ring experiments include various test cases covering:

1. **Single Ring Designs**:
   - Digital IO (3x3, 6x6, 12x12, 18x18)
   - Analog IO (6x6, 12x12)
   - Mixed-signal IO (12x12, 18x18)
   - Multi-voltage domain designs

2. **Double Ring Designs**:
   - High-density configurations (12x18, 18x18)
   - Multi-voltage domain support
   - Complex routing scenarios

3. **Technology Nodes**:
   - 28nm wire-bonding
   - 180nm wire-bonding

## Log Files

All experiment logs are saved in:
- IO Ring experiments: `logs/batch_io_ring/`

Log file naming format: `{test_name}_{timestamp}.log`

## Running Recommendations

### Single Machine Run
```bash
# Run all experiments directly (sequential execution)
python tests/run_IO_Ring_batch.py --model-name claude
```

### Parallel Run (if supported)

If running multiple instances in parallel:

```bash
# Terminal 1: Run first 10 experiments
python tests/run_IO_Ring_batch.py --start-index 1 --stop-index 10 --ramic-port 9123

# Terminal 2: Run next 10 experiments
python tests/run_IO_Ring_batch.py --start-index 11 --stop-index 20 --ramic-port 9124
```

## Notes

1. **Timeout Setting**: Each experiment has a reasonable timeout, automatically continues to next after timeout
2. **Auto Exit**: Script automatically handles experiment completion
3. **Error Handling**: If an experiment fails, script automatically continues to the next experiment
4. **Parallel Run**: If running in parallel, ensure each instance uses a different RAMIC port
5. **Resource Usage**: Each experiment consumes CPU and memory, monitor system resources

## Time Estimates

### IO Ring Experiments (20+ test cases)
- **Single Thread**: 20 experiments × 15 minutes ≈ 5 hours
- **2 Threads Parallel**: ≈ 2.5 hours

Actual time varies based on design complexity and model performance.

## Resume Running

If experiments are interrupted, you can continue from a specified position:

```bash
# Continue from the 10th experiment
python tests/run_IO_Ring_batch.py --start-index 10
```

## Advantages

✅ **Comprehensive Testing**: Cover various IO ring configurations and scenarios  
✅ **Automated Validation**: Automatic DRC, LVS verification  
✅ **Flexible Configuration**: Easily switch models and configurations via command line  
✅ **Progress Tracking**: Detailed logging and progress reporting  
✅ **Easy Extension**: Add new test cases by extending benchmark suite
