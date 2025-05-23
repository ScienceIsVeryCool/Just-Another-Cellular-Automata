# world.py
import numpy as np
import logging
from scipy.sparse import dok_matrix
from collections import defaultdict
import random
from cell import Cell, Organism
from food import FoodSystem
from dna import DNAParser
from config import Config
from typing import Optional

logger = logging.getLogger('world')

class World:
    def __init__(self, width, height):
        logger.info(f"Initializing world with dimensions {width}x{height}")
        
        self.width = width
        self.height = height
        self.cells = {}  # cell_id -> Cell
        self.organisms = {}  # organism_id -> Organism
        self.spatial_hash = defaultdict(set)
        self.walls = dok_matrix((width, height), dtype=bool)
        self.food_system = FoodSystem(width, height)
        self.next_cell_id = 0
        self.next_organism_id = 0
        self.dna_parser = DNAParser()
        self.tick_counter = 0  # NEW: For energy drain timing
        self.stats = None  # Will be set by main.py
        
        logger.debug("World data structures initialized")
        self._setup_default_environment()
        logger.info("World initialization complete")
    
    def set_stats_tracker(self, stats):
        """Set the statistics tracker"""
        self.stats = stats
        logger.debug("Statistics tracker linked to world")
    
    def _setup_default_environment(self):
        """Create some walls and food clusters"""
        logger.info("Setting up default environment")
        
        # Simple walls
        wall_count = 0
        for x in range(200, 250):
            self.walls[x, 300] = True
            self.walls[x, 700] = True
            wall_count += 2
        logger.debug(f"Created {wall_count} wall segments")
        
        # Enhanced food clusters - MORE FOOD
        logger.debug("Spawning initial food clusters")
        self.food_system.spawn_gaussian_cluster(200, 200, 60, 0.4)  # Larger, denser
        self.food_system.spawn_gaussian_cluster(800, 800, 60, 0.4)  # Larger, denser
        self.food_system.spawn_gaussian_cluster(500, 500, 80, 0.3)  # Larger spread
        # Add more clusters
        self.food_system.spawn_gaussian_cluster(100, 600, 40, 0.3)
        self.food_system.spawn_gaussian_cluster(700, 200, 40, 0.3)
        
        total_food = len(self.food_system.food_energy)
        logger.info(f"Default environment setup complete: {wall_count} walls, {total_food} food items")
    
    def spawn_organism(self, genome, x, y, spread):
        """Spawn an organism near x,y with given genome"""
        logger.debug(f"Attempting to spawn organism with genome '{genome}' near ({x}, {y}) with spread {spread}")
        
        traits = self.dna_parser.parse(genome)
        if not traits:
            logger.warning(f"Failed to parse genome '{genome}' - no valid traits found")
            return None
        
        logger.debug(f"Parsed traits from genome: {traits}")
            
        # Find spawn location
        for attempt in range(100):
            dx = random.randint(-spread, spread)
            dy = random.randint(-spread, spread)
            spawn_x = max(0, min(self.width-1, x + dx))
            spawn_y = max(0, min(self.height-1, y + dy))
            
            # Check cell stacking limit
            existing_cells = self._get_cells_at_position(spawn_x, spawn_y)
            
            if (not self.walls[spawn_x, spawn_y] and 
                len(existing_cells) < Config.MAX_CELLS_PER_LOCATION):
                
                # Create organism
                organism = Organism(self.next_organism_id, genome, traits)
                self.organisms[self.next_organism_id] = organism
                organism.birth_tick = self.tick_counter  # Track birth time
                logger.debug(f"Created organism {self.next_organism_id} with color {organism.color}")
                self.next_organism_id += 1
                
                # Create initial cell with FIXED energy calculation
                cell = Cell(self.next_cell_id, spawn_x, spawn_y, organism.id)
                cell.energy = Config.STARTING_ENERGY - len(genome)  # Still subtract genome length once
                self.cells[self.next_cell_id] = cell
                organism.cell_ids.add(cell.id)
                
                logger.debug(f"Created cell {self.next_cell_id} at ({spawn_x}, {spawn_y}) "
                           f"with energy {cell.energy}")
                self.next_cell_id += 1
                
                # Update spatial hash
                self._update_spatial_hash(cell)
                
                # Record birth in stats
                if self.stats:
                    self.stats.record_birth(organism.id, None, genome, spawn_x, spawn_y)
                
                logger.info(f"Successfully spawned organism {organism.id} at ({spawn_x}, {spawn_y}) "
                          f"after {attempt + 1} attempts")
                return organism
        
        logger.warning(f"Failed to find spawn location for organism near ({x}, {y}) after 100 attempts")
        return None
    
    def _get_cells_at_position(self, x, y):
        """Get all cells at a specific position"""
        cells = []
        hash_key = self._get_hash(x, y)
        for cell_id in self.spatial_hash[hash_key]:
            cell = self.cells.get(cell_id)
            if cell and cell.x == x and cell.y == y:
                cells.append(cell)
        return cells
    
    def update(self):
        """Main update loop"""
        initial_cells = len(self.cells)
        initial_organisms = len(self.organisms)
        self.tick_counter += 1
        
        # NEW: Only drain energy every ENERGY_DRAIN_INTERVAL ticks
        should_drain_energy = (self.tick_counter % Config.ENERGY_DRAIN_INTERVAL == 0)
        
        # Update cells
        dead_cells = []
        reproduced_count = 0
        moved_count = 0
        ate_food_count = 0
        ate_cell_count = 0
        energy_drained_count = 0
        
        for cell_id, cell in list(self.cells.items()):
            organism = self.organisms.get(cell.organism_id)
            if not organism:
                logger.warning(f"Cell {cell_id} has invalid organism_id {cell.organism_id}")
                dead_cells.append(cell_id)
                continue
            
            # Age the cell
            cell.age += 1
                
            # NEW: Energy drain only happens periodically
            if should_drain_energy:
                energy_before = cell.energy
                # FIXED: Much gentler energy drain
                energy_cost = len(organism.genome) * Config.GENOME_ENERGY_COST
                cell.energy -= energy_cost
                energy_drained_count += 1
                logger.debug(f"Cell {cell_id} energy drain: {energy_before} -> {cell.energy} "
                            f"(cost: {energy_cost})")
            
            # Execute behaviors
            if "CanMove" in organism.traits:
                old_pos = (cell.x, cell.y)
                moved = self._move_cell(cell)
                if moved:
                    moved_count += 1
                    if self.stats:
                        self.stats.record_movement(cell.x, cell.y)
                    logger.debug(f"Cell {cell_id} moved from {old_pos} to ({cell.x}, {cell.y})")
            
            if "CanEat" in organism.traits:
                energy = self.food_system.eat_food(cell.x, cell.y)
                if energy > 0:
                    cell.energy += energy
                    ate_food_count += 1
                    if self.stats:
                        self.stats.record_food_consumed(energy)
                    logger.debug(f"Cell {cell_id} ate food and gained {energy} energy")
                else:
                    # Try to eat other cells
                    eaten = self._try_eat_cell(cell, organism)
                    if eaten:
                        ate_cell_count += 1
                        if self.stats:
                            self.stats.record_cell_eaten()
                        logger.debug(f"Cell {cell_id} successfully ate another cell")
            
            # Death check
            if cell.energy <= 0:
                dead_cells.append(cell_id)
                logger.debug(f"Cell {cell_id} marked for death (energy: {cell.energy})")
            
            # Reproduction check
            elif cell.energy > Config.REPRODUCTION_THRESHOLD:
                reproduced = self._try_reproduce(cell, organism)
                if reproduced:
                    reproduced_count += 1
                    logger.debug(f"Cell {cell_id} successfully reproduced")
        
        # Process deaths
        death_count = len(dead_cells)
        for cell_id in dead_cells:
            self._kill_cell(cell_id)
        
        # Update food
        self.food_system.regenerate()
        
        # Update statistics
        if self.stats and self.tick_counter % Config.STATS_UPDATE_INTERVAL == 0:
            self.stats.update(self, self.tick_counter)
        
        # Log summary of update
        final_cells = len(self.cells)
        final_organisms = len(self.organisms)
        
        if death_count > 0 or reproduced_count > 0 or moved_count > 0 or should_drain_energy:
            summary = (f"Tick {self.tick_counter} - Cells: {initial_cells}->{final_cells} "
                      f"(+{reproduced_count} births, -{death_count} deaths), "
                      f"Organisms: {initial_organisms}->{final_organisms}, "
                      f"Actions: {moved_count} moves, {ate_food_count} food eaten, "
                      f"{ate_cell_count} cells eaten")
            
            if should_drain_energy:
                summary += f", {energy_drained_count} cells drained energy"
            
            logger.debug(summary)
    
    def _move_cell(self, cell):
        """Move cell in random direction"""
        directions = [(0,1), (1,0), (0,-1), (-1,0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            new_x = cell.x + dx
            new_y = cell.y + dy
            
            if (0 <= new_x < self.width and 0 <= new_y < self.height and
                not self.walls[new_x, new_y]):
                
                # Check cell stacking limit
                existing_cells = self._get_cells_at_position(new_x, new_y)
                if len(existing_cells) < Config.MAX_CELLS_PER_LOCATION:
                    # Update spatial hash
                    self._remove_from_spatial_hash(cell)
                    cell.x = new_x
                    cell.y = new_y
                    self._update_spatial_hash(cell)
                    
                    # Movement cost
                    cell.energy -= Config.MOVEMENT_COST
                    
                    if self.stats:
                        self.stats.tick_movements += 1
                        self.stats.total_movements += 1
                    
                    return True
        
        logger.debug(f"Cell {cell.id} could not move - all adjacent spaces blocked or full")
        return False
    
    def _try_eat_cell(self, predator, pred_organism):
        """Try to eat adjacent cells"""
        adjacent = self._get_adjacent_cells(predator.x, predator.y)
        
        for target in adjacent:
            if target.organism_id != predator.organism_id:
                # Eat the cell
                energy_gained = target.energy // 2
                predator.energy += energy_gained
                logger.debug(f"Cell {predator.id} ate cell {target.id} and gained {energy_gained} energy")
                self._kill_cell(target.id)
                return True
        
        return False
    
    def _try_reproduce(self, cell, organism):
        """Attempt reproduction with mutation"""
        if self.stats:
            self.stats.record_reproduction_attempt(False)  # Assume failure until success
            
        # Find empty adjacent space
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
            new_x = cell.x + dx
            new_y = cell.y + dy
            
            if (0 <= new_x < self.width and 0 <= new_y < self.height and
                not self.walls[new_x, new_y]):
                
                # Check cell stacking limit
                existing_cells = self._get_cells_at_position(new_x, new_y)
                if len(existing_cells) < Config.MAX_CELLS_PER_LOCATION:
                    # Mutate genome
                    new_genome = self.dna_parser.mutate(organism.genome)
                    new_traits = self.dna_parser.parse(new_genome)
                    
                    if new_traits:
                        # Create offspring
                        offspring = Organism(self.next_organism_id, new_genome, new_traits)
                        offspring.birth_tick = self.tick_counter
                        self.organisms[self.next_organism_id] = offspring
                        
                        logger.debug(f"Reproduction: Parent genome '{organism.genome}' -> "
                                   f"Offspring genome '{new_genome}'")
                        
                        # Record mutation if genome changed
                        if new_genome != organism.genome and self.stats:
                            self.stats.record_mutation(organism.genome, new_genome)
                        
                        self.next_organism_id += 1
                        
                        # Create offspring cell
                        offspring_cell = Cell(self.next_cell_id, new_x, new_y, offspring.id)
                        offspring_cell.energy = Config.STARTING_ENERGY - len(new_genome)
                        self.cells[self.next_cell_id] = offspring_cell
                        offspring.cell_ids.add(offspring_cell.id)
                        self.next_cell_id += 1
                        
                        # Update spatial hash
                        self._update_spatial_hash(offspring_cell)
                        
                        # Reproduction cost
                        cell.energy -= Config.REPRODUCTION_COST
                        
                        # Record birth in stats
                        if self.stats:
                            self.stats.record_birth(offspring.id, organism.id, new_genome, new_x, new_y)
                            self.stats.record_reproduction_attempt(True)  # Success!
                        
                        logger.info(f"Organism {organism.id} reproduced -> Organism {offspring.id} "
                                  f"at ({new_x}, {new_y})")
                        return True
                    else:
                        logger.warning(f"Reproduction failed: mutated genome '{new_genome}' "
                                     f"produced no valid traits")
        
        logger.debug(f"Cell {cell.id} could not reproduce - no adjacent empty spaces")
        return False
    
    def _kill_cell(self, cell_id):
        """Remove cell and potentially organism"""
        cell = self.cells.get(cell_id)
        if not cell:
            logger.warning(f"Attempted to kill non-existent cell {cell_id}")
            return
        
        logger.debug(f"Killing cell {cell_id} at ({cell.x}, {cell.y}) with {cell.energy} energy")
            
        # Leave decay food - ENHANCED
        self.food_system.spawn_food(cell.x, cell.y, Config.DECAY_FOOD_ENERGY)
        
        # Remove from spatial hash
        self._remove_from_spatial_hash(cell)
        
        # Remove from organism
        organism = self.organisms.get(cell.organism_id)
        if organism:
            organism.cell_ids.discard(cell_id)
            if not organism.cell_ids:
                # Calculate organism age
                age = self.tick_counter - organism.birth_tick
                
                # Record death in stats
                if self.stats:
                    self.stats.record_death(organism.id, organism.genome, cell.x, cell.y, age)
                
                logger.info(f"Organism {organism.id} died (last cell removed)")
                del self.organisms[organism.id]
        
        # Remove cell
        del self.cells[cell_id]
    
    def get_cell_at(self, x, y):
        """Get first cell at position (for compatibility)"""
        cells = self._get_cells_at_position(x, y)
        return cells[0] if cells else None
    
    def _get_adjacent_cells(self, x, y):
        """Get all cells adjacent to position"""
        adjacent = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                cells = self._get_cells_at_position(x + dx, y + dy)
                adjacent.extend(cells)
        return adjacent
    
    def _get_hash(self, x, y):
        """Spatial hash function"""
        return (x // 16, y // 16)
    
    def _update_spatial_hash(self, cell):
        """Add cell to spatial hash"""
        hash_key = self._get_hash(cell.x, cell.y)
        self.spatial_hash[hash_key].add(cell.id)
    
    def _remove_from_spatial_hash(self, cell):
        """Remove cell from spatial hash"""
        hash_key = self._get_hash(cell.x, cell.y)
        self.spatial_hash[hash_key].discard(cell.id)
    
    def to_dict(self):
        """Convert world to JSON-serializable dict"""
        logger.debug("Converting world to dictionary for serialization")
        
        result = {
            "width": self.width,
            "height": self.height,
            "organisms": [
                {
                    "genome": org.genome,
                    "cells": [(self.cells[cid].x, self.cells[cid].y) 
                             for cid in org.cell_ids if cid in self.cells]
                }
                for org in self.organisms.values()
            ],
            "food": self.food_system.to_dict(),
            "walls": [(int(x), int(y)) for x, y in zip(*self.walls.nonzero())]
        }
        
        logger.debug(f"World serialization complete: {len(result['organisms'])} organisms, "
                    f"{len(result['food']['food'])} food items, {len(result['walls'])} walls")
        return result
    
    @classmethod
    def from_dict(cls, data):
        """Create world from dict"""
        logger.info(f"Loading world from dictionary: {data['width']}x{data['height']}")
        
        world = cls(data["width"], data["height"])
        
        # Load walls
        wall_count = 0
        for x, y in data.get("walls", []):
            world.walls[x, y] = True
            wall_count += 1
        logger.debug(f"Loaded {wall_count} walls")
        
        # Load food
        world.food_system = FoodSystem.from_dict(data["food"], data["width"], data["height"])
        food_count = len(world.food_system.food_energy)
        logger.debug(f"Loaded {food_count} food items")
        
        # Load organisms
        organism_count = 0
        for org_data in data.get("organisms", []):
            if org_data["cells"]:
                x, y = org_data["cells"][0]
                organism = world.spawn_organism(org_data["genome"], x, y, 0)
                if organism:
                    organism_count += 1
                
                # Add additional cells for multicellular
                for x, y in org_data["cells"][1:]:
                    # TODO: Implement multicellular loading
                    logger.debug(f"Skipping additional cell at ({x}, {y}) - multicellular not implemented")
                    pass
        
        logger.info(f"World loaded successfully: {organism_count} organisms, "
                   f"{food_count} food items, {wall_count} walls")
        
        return world