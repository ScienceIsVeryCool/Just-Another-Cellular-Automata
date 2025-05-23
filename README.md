# Cellular Evolution Simulator

A sophisticated artificial life simulation featuring evolving organisms with genetic traits, comprehensive statistics tracking, and real-time visualization.

## Features

- **Genetic Evolution**: Organisms with DNA-based traits that mutate and evolve
- **Energy Economy**: Food spawning, consumption, and energy management
- **Comprehensive Statistics**: Track population dynamics, genome diversity, and evolution patterns
- **Real-time Visualization**: Watch organisms interact, move, eat, and reproduce
- **Stats Dashboard**: Toggle between simulation view and detailed statistics
- **Cell Stacking Prevention**: Prevents exploitation strategies through position limits

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

### Simulation Controls
- **SPACE** - Pause/unpause simulation
- **S** - Save world (when paused)
- **T** - Toggle statistics view

### Camera Controls
- **R/F** - Zoom in/out (keyboard)
- **Mouse Scroll** - Zoom in/out
- **Middle Click** - Reset zoom to 1.0
- **Left Click + Drag** - Pan camera
- **F11** - Toggle fullscreen mode

## DNA Traits
- `[Cell]` - Required base trait for all organisms
- `[CanMove]` - Allows organism movement (costs energy)
- `[CanEat]` - Can consume food and other cells
- `[Color:X]` - Visual color options:
  - Green (default)
  - Blue
  - Red
  - Yellow
  - Purple

## Energy System
- **Starting Energy**: 200 - genome length
- **Energy Drain**: Every 30 ticks (1 second at 30 FPS)
- **Movement Cost**: 1 energy per move
- **Reproduction**: Requires 250+ energy, costs 80
- **Food Value**: 25 energy per food item
- **Cell Death**: Leaves 15 energy as food

## Statistics View

Press **T** to toggle the comprehensive statistics dashboard showing:

### Overview
- Runtime and performance metrics
- Current tick and tick rate
- Population summaries

### Population Dynamics
- Real-time cell, organism, and food counts
- Genome diversity tracking
- Extinction monitoring

### Life Events
- Birth/death rates and totals
- Mutation frequency
- Reproduction success rates

### Visualizations
- Population history graph
- Trait distribution
- Top performing genomes
- Notable events log

### Advanced Metrics
- Energy economy analysis
- Spatial distribution heatmaps
- Movement patterns
- Genome evolution tracking

## Configuration

Edit `config.py` to customize:

### World Settings
- `WORLD_WIDTH/HEIGHT`: World dimensions (default: 1024x1024)
- `SCREEN_WIDTH/HEIGHT`: Display size (default: 800x600)
- `MAX_CELLS_PER_LOCATION`: Cell stacking limit (default: 1)

### Energy Parameters
- `STARTING_ENERGY`: Base energy for new organisms
- `ENERGY_DRAIN_INTERVAL`: Ticks between energy drain
- `FOOD_ENERGY`: Energy gained from food
- `FOOD_REGEN_RATE`: Food regeneration probability

### Statistics
- `STATS_HISTORY_SIZE`: History buffer size
- `STATS_UPDATE_INTERVAL`: Update frequency

## File Structure
```
├── main.py          # Entry point & game loop
├── world.py         # World simulation logic
├── cell.py          # Cell & organism classes
├── dna.py           # Genome parsing & mutation
├── food.py          # Food spawning & regeneration
├── renderer.py      # Visualization & stats display
├── stats.py         # Statistics tracking system
├── config.py        # Configuration constants
└── logs/            # Simulation logs
```

## World Files

Saved worlds are JSON files containing:
- Organism positions and genomes
- Food locations and energy values
- Wall positions
- Statistics snapshot at save time

Example structure:
```json
{
  "width": 1024,
  "height": 1024,
  "organisms": [...],
  "food": {...},
  "walls": [...],
  "stats_snapshot": {...}
}
```

## Gameplay Tips

### Survival Strategies
- Shorter genomes are more energy-efficient
- `[CanMove]` helps find food but costs energy
- `[CanEat]` allows predation on other cells
- Balance traits for different ecological niches

### Evolution Patterns
- Food clusters create population centers
- Walls create geographic isolation
- Predators control population growth
- Colors help track lineages visually

### Statistics Analysis
- Monitor genome diversity for healthy evolution
- Track energy economy for system balance
- Watch for mass extinction events
- Identify successful trait combinations

## Logging

The simulator includes comprehensive logging:

### Log Levels
- **ERROR**: Critical failures
- **WARNING**: Non-critical issues
- **INFO**: Important events
- **DEBUG**: Detailed execution info

### Log Locations
- Console: INFO and above
- Files: All levels in `logs/simulation_YYYYMMDD_HHMMSS.log`

### Key Logged Events
- Organism births/deaths with locations
- Mutations with before/after genomes
- Population milestones
- Performance metrics
- Energy economy changes

## Technical Details

### Spatial Optimization
- Spatial hashing for efficient collision detection
- Grid size: 16x16 cells per hash bucket

### Performance
- Stats update every 10 ticks for efficiency
- Configurable FPS (default: 30)
- Energy drain interval reduces computation

### Mutation System
- Point mutations: 70% chance
- Trait insertion: 20% chance
- Trait deletion: 10% chance
- Mutation rate: 1% per reproduction

## Future Enhancements

Potential additions:
- Multicellular organisms
- Environmental factors (temperature, seasons)
- Neural network brains
- Sexual reproduction
- Resource types beyond food
- Territorial behaviors
- Communication traits

## Contributing

Feel free to fork and submit pull requests. Key areas for contribution:
- New trait types
- Performance optimizations
- Additional statistics
- Visualization improvements
- Save/load enhancements