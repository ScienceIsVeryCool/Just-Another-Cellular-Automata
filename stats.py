# stats.py
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import numpy as np

logger = logging.getLogger('stats')

@dataclass
class PopulationSnapshot:
    """Point-in-time population data"""
    tick: int
    timestamp: float
    total_cells: int
    total_organisms: int
    total_food: int
    births: int = 0
    deaths: int = 0
    mutations: int = 0
    food_consumed: int = 0
    cells_eaten: int = 0

@dataclass
class GenomeStats:
    """Statistics for a specific genome"""
    genome: str
    first_seen: int
    last_seen: int
    peak_population: int
    total_births: int
    total_deaths: int
    avg_lifespan: float
    trait_set: set = field(default_factory=set)

class SimulationStats:
    """Comprehensive statistics tracking for the cellular evolution simulation"""
    
    def __init__(self, history_size: int = 1000):
        logger.info(f"Initializing statistics tracker with history size {history_size}")
        
        # Configuration
        self.history_size = history_size
        self.start_time = time.time()
        self.current_tick = 0
        
        # Real-time counters
        self.total_births = 0
        self.total_deaths = 0
        self.total_mutations = 0
        self.total_food_consumed = 0
        self.total_cells_eaten = 0
        self.total_movements = 0
        self.total_reproduction_attempts = 0
        self.failed_reproduction_attempts = 0
        
        # Per-tick counters (reset each update)
        self.tick_births = 0
        self.tick_deaths = 0
        self.tick_mutations = 0
        self.tick_food_consumed = 0
        self.tick_cells_eaten = 0
        self.tick_movements = 0
        
        # Historical data
        self.population_history = deque(maxlen=history_size)
        self.food_history = deque(maxlen=history_size)
        self.genome_diversity_history = deque(maxlen=history_size)
        
        # Genome tracking
        self.genome_stats: Dict[str, GenomeStats] = {}
        self.active_genomes: Dict[str, int] = defaultdict(int)  # genome -> count
        self.extinct_genomes: List[Tuple[str, GenomeStats]] = []
        
        # Trait distribution
        self.trait_counts: Dict[str, int] = defaultdict(int)
        self.trait_combinations: Dict[frozenset, int] = defaultdict(int)
        
        # Spatial statistics
        self.cell_density_grid = None
        self.movement_heatmap = None
        self.death_locations = deque(maxlen=500)
        self.birth_locations = deque(maxlen=500)
        
        # Performance metrics
        self.update_times = deque(maxlen=100)
        self.tick_durations = deque(maxlen=100)
        self.last_update_time = time.time()
        
        # Interesting events
        self.notable_events = deque(maxlen=50)
        self.longest_lived_organism = None
        self.most_successful_genome = None
        self.largest_population_tick = 0
        self.largest_population_count = 0
        
        # Energy economy
        self.total_energy_in_system = 0
        self.energy_history = deque(maxlen=history_size)
        self.energy_distribution = []
        
        logger.debug("Statistics tracker initialized with all subsystems")
    
    def update(self, world, tick: int):
        """Update statistics with current world state"""
        start_time = time.time()
        self.current_tick = tick
        
        # Calculate current population stats
        current_cells = len(world.cells)
        current_organisms = len(world.organisms)
        current_food = len(world.food_system.food_energy)
        
        # Create snapshot
        snapshot = PopulationSnapshot(
            tick=tick,
            timestamp=time.time(),
            total_cells=current_cells,
            total_organisms=current_organisms,
            total_food=current_food,
            births=self.tick_births,
            deaths=self.tick_deaths,
            mutations=self.tick_mutations,
            food_consumed=self.tick_food_consumed,
            cells_eaten=self.tick_cells_eaten
        )
        
        # Update histories
        self.population_history.append(snapshot)
        self.food_history.append(current_food)
        
        # Update genome statistics
        self._update_genome_stats(world)
        
        # Update trait distribution
        self._update_trait_distribution(world)
        
        # Update spatial statistics
        self._update_spatial_stats(world)
        
        # Update energy economy
        self._update_energy_stats(world)
        
        # Check for notable events
        self._check_notable_events(world, snapshot)
        
        # Update performance metrics
        update_time = time.time() - start_time
        self.update_times.append(update_time)
        
        # Calculate tick duration
        current_time = time.time()
        tick_duration = current_time - self.last_update_time
        self.tick_durations.append(tick_duration)
        self.last_update_time = current_time
        
        # Reset per-tick counters
        self.tick_births = 0
        self.tick_deaths = 0
        self.tick_mutations = 0
        self.tick_food_consumed = 0
        self.tick_cells_eaten = 0
        self.tick_movements = 0
        
        logger.debug(f"Stats update completed in {update_time:.3f}s")
    
    def _update_genome_stats(self, world):
        """Update genome-related statistics"""
        # Reset active genome counts
        self.active_genomes.clear()
        
        # Count active genomes
        for organism in world.organisms.values():
            genome = organism.genome
            self.active_genomes[genome] += 1
            
            # Update or create genome stats
            if genome not in self.genome_stats:
                self.genome_stats[genome] = GenomeStats(
                    genome=genome,
                    first_seen=self.current_tick,
                    last_seen=self.current_tick,
                    peak_population=1,
                    total_births=1,
                    total_deaths=0,
                    avg_lifespan=0.0,
                    trait_set=set(organism.traits)
                )
                logger.info(f"New genome discovered: '{genome}' with traits {organism.traits}")
            else:
                stats = self.genome_stats[genome]
                stats.last_seen = self.current_tick
                stats.peak_population = max(stats.peak_population, self.active_genomes[genome])
        
        # Check for extinctions
        for genome, stats in list(self.genome_stats.items()):
            if genome not in self.active_genomes and stats.last_seen < self.current_tick:
                self.extinct_genomes.append((genome, stats))
                logger.info(f"Genome extinct: '{genome}' (lived {stats.last_seen - stats.first_seen} ticks)")
                del self.genome_stats[genome]
        
        # Update diversity metric
        genome_count = len(self.active_genomes)
        self.genome_diversity_history.append(genome_count)
    
    def _update_trait_distribution(self, world):
        """Update trait distribution statistics"""
        self.trait_counts.clear()
        self.trait_combinations.clear()
        
        for organism in world.organisms.values():
            # Count individual traits
            for trait in organism.traits:
                self.trait_counts[trait] += 1
            
            # Count trait combinations
            trait_set = frozenset(organism.traits)
            self.trait_combinations[trait_set] += 1
    
    def _update_spatial_stats(self, world):
        """Update spatial distribution statistics"""
        if self.cell_density_grid is None:
            # Initialize grids
            grid_size = 32  # Divide world into 32x32 chunks
            grid_w = world.width // grid_size + 1
            grid_h = world.height // grid_size + 1
            self.cell_density_grid = np.zeros((grid_w, grid_h))
            self.movement_heatmap = np.zeros((grid_w, grid_h))
        
        # Reset density grid
        self.cell_density_grid.fill(0)
        
        # Count cells per grid square
        grid_size = 32
        for cell in world.cells.values():
            gx = min(cell.x // grid_size, self.cell_density_grid.shape[0] - 1)
            gy = min(cell.y // grid_size, self.cell_density_grid.shape[1] - 1)
            self.cell_density_grid[gx, gy] += 1
    
    def _update_energy_stats(self, world):
        """Update energy-related statistics"""
        total_cell_energy = sum(cell.energy for cell in world.cells.values())
        total_food_energy = sum(world.food_system.food_energy.values())
        self.total_energy_in_system = total_cell_energy + total_food_energy
        self.energy_history.append(self.total_energy_in_system)
        
        # Energy distribution among cells
        if world.cells:
            energies = [cell.energy for cell in world.cells.values()]
            self.energy_distribution = {
                'min': min(energies),
                'max': max(energies),
                'mean': np.mean(energies),
                'median': np.median(energies),
                'std': np.std(energies)
            }
    
    def _check_notable_events(self, world, snapshot):
        """Check for and record notable events"""
        # Population milestones
        if snapshot.total_cells > self.largest_population_count:
            self.largest_population_count = snapshot.total_cells
            self.largest_population_tick = self.current_tick
            self.notable_events.append(
                f"Tick {self.current_tick}: New population record: {snapshot.total_cells} cells"
            )
        
        # Mass extinction event
        if self.tick_deaths > snapshot.total_cells * 0.5 and snapshot.total_cells > 10:
            self.notable_events.append(
                f"Tick {self.current_tick}: Mass extinction! {self.tick_deaths} deaths"
            )
        
        # Diversity milestone
        genome_count = len(self.active_genomes)
        if genome_count > 0 and genome_count % 10 == 0:
            if not hasattr(self, '_last_diversity_milestone') or self._last_diversity_milestone != genome_count:
                self._last_diversity_milestone = genome_count
                self.notable_events.append(
                    f"Tick {self.current_tick}: Genome diversity reached {genome_count} unique genomes"
                )
    
    # Event recording methods (called by world.py)
    def record_birth(self, organism_id: int, parent_id: Optional[int], genome: str, x: int, y: int):
        """Record a birth event"""
        self.tick_births += 1
        self.total_births += 1
        self.birth_locations.append((x, y, self.current_tick))
        
        if genome in self.genome_stats:
            self.genome_stats[genome].total_births += 1
        
        logger.debug(f"Birth recorded: organism {organism_id} with genome '{genome}' at ({x}, {y})")
    
    def record_death(self, organism_id: int, genome: str, x: int, y: int, age: int):
        """Record a death event"""
        self.tick_deaths += 1
        self.total_deaths += 1
        self.death_locations.append((x, y, self.current_tick))
        
        if genome in self.genome_stats:
            stats = self.genome_stats[genome]
            stats.total_deaths += 1
            # Update average lifespan
            if stats.total_deaths > 0:
                stats.avg_lifespan = ((stats.avg_lifespan * (stats.total_deaths - 1) + age) / 
                                    stats.total_deaths)
        
        logger.debug(f"Death recorded: organism {organism_id} with genome '{genome}' at ({x}, {y}), age {age}")
    
    def record_mutation(self, old_genome: str, new_genome: str):
        """Record a mutation event"""
        self.tick_mutations += 1
        self.total_mutations += 1
        logger.debug(f"Mutation recorded: '{old_genome}' -> '{new_genome}'")
    
    def record_food_consumed(self, amount: int):
        """Record food consumption"""
        self.tick_food_consumed += 1
        self.total_food_consumed += 1
    
    def record_cell_eaten(self):
        """Record cell predation"""
        self.tick_cells_eaten += 1
        self.total_cells_eaten += 1
    
    def record_movement(self, x: int, y: int):
        """Record cell movement"""
        self.tick_movements += 1
        self.total_movements += 1
        
        # Update movement heatmap
        if self.movement_heatmap is not None:
            grid_size = 32
            gx = min(x // grid_size, self.movement_heatmap.shape[0] - 1)
            gy = min(y // grid_size, self.movement_heatmap.shape[1] - 1)
            self.movement_heatmap[gx, gy] += 1
    
    def record_reproduction_attempt(self, success: bool):
        """Record reproduction attempt"""
        self.total_reproduction_attempts += 1
        if not success:
            self.failed_reproduction_attempts += 1
    
    def get_summary(self) -> dict:
        """Get a summary of current statistics"""
        runtime = time.time() - self.start_time
        
        # Calculate rates
        birth_rate = self.total_births / max(runtime, 1)
        death_rate = self.total_deaths / max(runtime, 1)
        
        # Get recent population if available
        recent_pop = self.population_history[-1] if self.population_history else None
        
        summary = {
            'runtime': runtime,
            'current_tick': self.current_tick,
            'total_births': self.total_births,
            'total_deaths': self.total_deaths,
            'total_mutations': self.total_mutations,
            'birth_rate': birth_rate,
            'death_rate': death_rate,
            'population': {
                'cells': recent_pop.total_cells if recent_pop else 0,
                'organisms': recent_pop.total_organisms if recent_pop else 0,
                'food': recent_pop.total_food if recent_pop else 0
            },
            'genome_diversity': len(self.active_genomes),
            'extinct_genomes': len(self.extinct_genomes),
            'trait_distribution': dict(self.trait_counts),
            'energy_economy': {
                'total': self.total_energy_in_system,
                'distribution': self.energy_distribution
            },
            'performance': {
                'avg_update_time': np.mean(self.update_times) if self.update_times else 0,
                'avg_tick_duration': np.mean(self.tick_durations) if self.tick_durations else 0
            }
        }
        
        return summary
    
    def get_genome_leaderboard(self, top_n: int = 10) -> List[Tuple[str, GenomeStats]]:
        """Get the most successful genomes by various metrics"""
        # Sort by peak population
        active_sorted = sorted(
            self.genome_stats.items(),
            key=lambda x: x[1].peak_population,
            reverse=True
        )
        
        return active_sorted[:top_n]
    
    def get_trait_analysis(self) -> dict:
        """Analyze trait effectiveness"""
        analysis = {}
        
        for trait, count in self.trait_counts.items():
            # Calculate average lifespan for organisms with this trait
            trait_genomes = [g for g, stats in self.genome_stats.items() 
                           if trait in stats.trait_set]
            
            if trait_genomes:
                avg_lifespan = np.mean([self.genome_stats[g].avg_lifespan 
                                      for g in trait_genomes if g in self.genome_stats])
                total_pop = sum(self.active_genomes.get(g, 0) for g in trait_genomes)
                
                analysis[trait] = {
                    'current_count': count,
                    'total_population': total_pop,
                    'avg_lifespan': avg_lifespan,
                    'genome_count': len(trait_genomes)
                }
        
        return analysis