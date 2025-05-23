# Cellular Evolution Simulator

## Setup
```bash
pip install pygame numpy scipy
```

## Run
```bash
python main.py                    # Start with default world
python main.py world_file.json    # Load saved world
```

## Controls
- **SPACE** - Pause/unpause
- **S** - Save world (when paused)
- **R/F** - Zoom in/out  
- **Mouse drag** - Pan camera

## DNA Traits
- `[Cell]` - Required base trait
- `[CanMove]` - Allows movement
- `[CanEat]` - Can consume food/cells
- `[Color:X]` - Visual color (Red/Blue/Green/Yellow/Purple)

## File Structure
- `main.py` - Entry point & game loop
- `world.py` - World simulation logic
- `cell.py` - Cell & organism classes
- `dna.py` - Genome parsing & mutation
- `food.py` - Food spawning & regeneration
- `renderer.py` - Pygame visualization
- `config.py` - All constants

## World Files
Saved worlds are JSON with:
- Organism positions & genomes
- Food locations
- Wall positions

Energy = Starting energy - genome length. Each character costs 1 energy/tick.

## Tips
- Shorter genomes = more efficient
- `[CanMove]` helps find food
- `[CanEat]` allows predation
- Food regenerates near existing food (Conway rules)

# Cellular Evolution Simulator - Logging Guide

## Overview

The cellular evolution simulator now includes comprehensive logging using Python's built-in `logging` module. The system provides multiple log levels and outputs to both console and file.

## Log Levels

### ERROR
- Critical errors that may cause the application to fail
- Failed file operations, initialization errors
- Always shown in console output

### WARNING  
- Non-critical issues that don't stop execution
- Invalid genomes, failed spawn attempts, missing organisms
- Shown in console by default

### INFO
- Important events and state changes
- Organism births/deaths, world loading/saving, major milestones
- Shown in console by default

### DEBUG
- Detailed execution information
- Individual cell movements, energy changes, mutation details
- Only saved to log files by default (not shown in console)

## Configuration

Edit `config.py` to customize logging behavior:

```python
# Logging settings in config.py
LOG_LEVEL = logging.DEBUG     # Change to INFO, WARNING, or ERROR
LOG_TO_FILE = True           # Set to False to disable file logging
```

## Log Output Locations

### Console Output
- Shows INFO, WARNING, and ERROR messages by default
- Real-time feedback during simulation
- Clean, readable format for monitoring

### File Output
- All log levels including DEBUG
- Saved to `logs/simulation_YYYYMMDD_HHMMSS.log`
- Detailed information for debugging and analysis
- Automatically creates `logs/` directory if needed

## Key Logging Features Added

### Main Simulation (`main.py`)
- Startup and shutdown events
- World loading/saving operations
- User input and camera controls
- Periodic status updates every 100 ticks
- Performance monitoring every 1000 ticks

### World Management (`world.py`)
- Organism spawning and death
- Cell reproduction and mutation
- Energy system tracking
- Spatial hash operations
- Environment setup and loading

### DNA System (`dna.py`)
- Genome parsing and validation
- Mutation events with before/after comparisons
- Trait extraction and validation
- Invalid genome detection

### Food System (`food.py`)
- Food spawning and consumption
- Gaussian cluster generation
- Conway-rule regeneration cycles
- Out-of-bounds prevention

### Rendering (`renderer.py`)
- Render performance and object counts
- Camera movement and zoom changes
- Display initialization
- Error handling for graphics operations

### Cell/Organism (`cell.py`)
- Object creation and initialization
- Color extraction from traits
- Entity relationship logging

## Usage Examples

### Running with Different Log Levels

```bash
# Normal operation (INFO level to console, DEBUG to file)
python main.py

# Only see warnings and errors in console
# Edit config.py: LOG_LEVEL = logging.WARNING
python main.py

# Maximum verbosity (all DEBUG messages to console)
# Edit config.py: LOG_LEVEL = logging.DEBUG, then change console_handler level
python main.py
```

### Monitoring Specific Events

Watch the console for key events:
- `INFO` - Organism births, deaths, world saves
- `WARNING` - Failed spawns, invalid genomes
- `ERROR` - Critical failures, file errors

Check log files for detailed analysis:
- Individual cell movements and energy changes
- Detailed mutation information
- Performance metrics and timing data

### Debugging Issues

1. Check console for immediate problems (ERROR/WARNING)
2. Examine log files for detailed DEBUG information
3. Look for patterns in organism behavior
4. Monitor energy flow and population dynamics

## Log File Analysis

Log files contain structured information perfect for:
- Analyzing evolution patterns
- Debugging simulation issues
- Performance optimization
- Research data collection

Example log entries:
```
2025-05-22 10:30:15 - world - INFO - Organism 42 reproduced -> Organism 43 at (150, 200)
2025-05-22 10:30:15 - dna - INFO - Insert mutation: '[Cell][CanMove]' -> '[Cell][CanMove][CanEat]' (added '[CanEat]')
2025-05-22 10:30:16 - world - DEBUG - Cell 85 moved from (149, 200) to (150, 200)
```

## Customization

To modify logging behavior:

1. **Change console verbosity**: Edit `console_handler.setLevel()` in `config.py`
2. **Add new log categories**: Create logger instances in new modules
3. **Custom formatting**: Modify `LOG_FORMAT` in `config.py`
4. **Disable file logging**: Set `LOG_TO_FILE = False`

The logging system is designed to be comprehensive yet performant, providing insights into every aspect of the simulation while maintaining good performance for real-time operation.