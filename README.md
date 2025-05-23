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