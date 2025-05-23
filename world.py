
# world.py
import numpy as np
from scipy.sparse import dok_matrix
from collections import defaultdict
import random
from cell import Cell, Organism
from food import FoodSystem
from dna import DNAParser
from config import Config

class World:
    def __init__(self, width, height):
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
        
        self._setup_default_environment()
    
    def _setup_default_environment(self):
        """Create some walls and food clusters"""
        # Simple walls
        for x in range(200, 250):
            self.walls[x, 300] = True
            self.walls[x, 700] = True
        
        # Food clusters
        self.food_system.spawn_gaussian_cluster(200, 200, 50, 0.3)
        self.food_system.spawn_gaussian_cluster(800, 800, 50, 0.3)
        self.food_system.spawn_gaussian_cluster(500, 500, 100, 0.2)
    
    def spawn_organism(self, genome, x, y, spread):
        """Spawn an organism near x,y with given genome"""
        traits = self.dna_parser.parse(genome)
        if not traits:
            return None
            
        # Find spawn location
        for _ in range(100):
            dx = random.randint(-spread, spread)
            dy = random.randint(-spread, spread)
            spawn_x = max(0, min(self.width-1, x + dx))
            spawn_y = max(0, min(self.height-1, y + dy))
            
            if not self.walls[spawn_x, spawn_y] and not self.get_cell_at(spawn_x, spawn_y):
                # Create organism
                organism = Organism(self.next_organism_id, genome, traits)
                self.organisms[self.next_organism_id] = organism
                self.next_organism_id += 1
                
                # Create initial cell
                cell = Cell(self.next_cell_id, spawn_x, spawn_y, organism.id)
                cell.energy = Config.STARTING_ENERGY - len(genome)
                self.cells[self.next_cell_id] = cell
                organism.cell_ids.add(cell.id)
                self.next_cell_id += 1
                
                # Update spatial hash
                self._update_spatial_hash(cell)
                
                return organism
        return None
    
    def update(self):
        """Main update loop"""
        # Update cells
        dead_cells = []
        for cell_id, cell in list(self.cells.items()):
            organism = self.organisms.get(cell.organism_id)
            if not organism:
                dead_cells.append(cell_id)
                continue
                
            # Energy drain
            cell.energy -= len(organism.genome)
            
            # Execute behaviors
            if "CanMove" in organism.traits:
                self._move_cell(cell)
            
            if "CanEat" in organism.traits:
                energy = self.food_system.eat_food(cell.x, cell.y)
                if energy > 0:
                    cell.energy += energy
                else:
                    # Try to eat other cells
                    self._try_eat_cell(cell, organism)
            
            # Death check
            if cell.energy <= 0:
                dead_cells.append(cell_id)
            
            # Reproduction check
            elif cell.energy > Config.REPRODUCTION_THRESHOLD:
                self._try_reproduce(cell, organism)
        
        # Process deaths
        for cell_id in dead_cells:
            self._kill_cell(cell_id)
        
        # Update food
        self.food_system.regenerate()
    
    def _move_cell(self, cell):
        """Move cell in random direction"""
        directions = [(0,1), (1,0), (0,-1), (-1,0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            new_x = cell.x + dx
            new_y = cell.y + dy
            
            if (0 <= new_x < self.width and 0 <= new_y < self.height and
                not self.walls[new_x, new_y] and not self.get_cell_at(new_x, new_y)):
                
                # Update spatial hash
                self._remove_from_spatial_hash(cell)
                cell.x = new_x
                cell.y = new_y
                self._update_spatial_hash(cell)
                
                # Movement cost
                cell.energy -= Config.MOVEMENT_COST
                break
    
    def _try_eat_cell(self, predator, pred_organism):
        """Try to eat adjacent cells"""
        adjacent = self._get_adjacent_cells(predator.x, predator.y)
        
        for target in adjacent:
            if target.organism_id != predator.organism_id:
                # Eat the cell
                energy_gained = target.energy // 2
                predator.energy += energy_gained
                self._kill_cell(target.id)
                break
    
    def _try_reproduce(self, cell, organism):
        """Attempt reproduction with mutation"""
        # Find empty adjacent space
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
            new_x = cell.x + dx
            new_y = cell.y + dy
            
            if (0 <= new_x < self.width and 0 <= new_y < self.height and
                not self.walls[new_x, new_y] and not self.get_cell_at(new_x, new_y)):
                
                # Mutate genome
                new_genome = self.dna_parser.mutate(organism.genome)
                new_traits = self.dna_parser.parse(new_genome)
                
                if new_traits:
                    # Create offspring
                    offspring = Organism(self.next_organism_id, new_genome, new_traits)
                    self.organisms[self.next_organism_id] = offspring
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
                break
    
    def _kill_cell(self, cell_id):
        """Remove cell and potentially organism"""
        cell = self.cells.get(cell_id)
        if not cell:
            return
            
        # Leave decay food
        self.food_system.spawn_food(cell.x, cell.y, 5)
        
        # Remove from spatial hash
        self._remove_from_spatial_hash(cell)
        
        # Remove from organism
        organism = self.organisms.get(cell.organism_id)
        if organism:
            organism.cell_ids.discard(cell_id)
            if not organism.cell_ids:
                del self.organisms[organism.id]
        
        # Remove cell
        del self.cells[cell_id]
    
    def get_cell_at(self, x, y):
        """Get cell at position"""
        hash_key = self._get_hash(x, y)
        for cell_id in self.spatial_hash[hash_key]:
            cell = self.cells.get(cell_id)
            if cell and cell.x == x and cell.y == y:
                return cell
        return None
    
    def _get_adjacent_cells(self, x, y):
        """Get all cells adjacent to position"""
        adjacent = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                cell = self.get_cell_at(x + dx, y + dy)
                if cell:
                    adjacent.append(cell)
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
        return {
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
    
    @classmethod
    def from_dict(cls, data):
        """Create world from dict"""
        world = cls(data["width"], data["height"])
        
        # Load walls
        for x, y in data.get("walls", []):
            world.walls[x, y] = True
        
        # Load food
        world.food_system = FoodSystem.from_dict(data["food"], data["width"], data["height"])
        
        # Load organisms
        for org_data in data.get("organisms", []):
            if org_data["cells"]:
                x, y = org_data["cells"][0]
                organism = world.spawn_organism(org_data["genome"], x, y, 0)
                
                # Add additional cells for multicellular
                for x, y in org_data["cells"][1:]:
                    # TODO: Implement multicellular loading
                    pass
        
        return world

