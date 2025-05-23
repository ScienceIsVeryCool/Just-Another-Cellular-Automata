# food.py
import numpy as np
import logging
from scipy.sparse import dok_matrix
import random

logger = logging.getLogger('food')

class FoodSystem:
    def __init__(self, width, height):
        logger.info(f"Initializing food system for {width}x{height} world")
        
        self.width = width
        self.height = height
        self.food_grid = dok_matrix((width, height), dtype=np.int8)
        self.food_energy = {}
        
        logger.debug("Food system data structures initialized")
    
    def spawn_gaussian_cluster(self, cx, cy, spread, density):
        """Spawn food in gaussian distribution"""
        logger.info(f"Spawning Gaussian food cluster at ({cx}, {cy}) with spread={spread}, density={density}")
        
        food_spawned = 0
        search_radius = spread * 2
        
        for x in range(max(0, cx-search_radius), min(self.width, cx+search_radius)):
            for y in range(max(0, cy-search_radius), min(self.height, cy+search_radius)):
                dist_sq = (x-cx)**2 + (y-cy)**2
                prob = density * np.exp(-dist_sq / (2 * spread**2))
                
                if random.random() < prob:
                    self.spawn_food(x, y, 10)
                    food_spawned += 1
        
        logger.info(f"Gaussian cluster spawning complete: {food_spawned} food items created")
    
    def spawn_food(self, x, y, energy):
        """Spawn food at position"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            logger.warning(f"Attempted to spawn food outside world bounds at ({x}, {y})")
            return
            
        if (x, y) in self.food_energy:
            logger.debug(f"Overwriting existing food at ({x}, {y}) - old energy: {self.food_energy[(x, y)]}, new energy: {energy}")
        else:
            logger.debug(f"Spawning food at ({x}, {y}) with energy {energy}")
            
        self.food_grid[x, y] = 1
        self.food_energy[(x, y)] = energy
    
    def eat_food(self, x, y):
        """Try to eat food at position"""
        if (x, y) in self.food_energy:
            energy = self.food_energy[(x, y)]
            del self.food_energy[(x, y)]
            self.food_grid[x, y] = 0
            
            logger.debug(f"Food eaten at ({x}, {y}) - energy gained: {energy}")
            return energy
        
        logger.debug(f"No food found at ({x}, {y}) to eat")
        return 0
    
    def regenerate(self):
        """Conway-inspired food regeneration"""
        logger.debug("Starting food regeneration cycle")
        
        new_food = []
        attempts = 0
        
        # Check random sample of empty cells
        for _ in range(100):
            attempts += 1
            x = random.randint(1, self.width-2)
            y = random.randint(1, self.height-2)
            
            if self.food_grid[x, y] == 0:
                # Count neighbors
                neighbors = 0
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        if self.food_grid[x+dx, y+dy] == 1:
                            neighbors += 1
                
                # Conway rules
                if neighbors == 2 or neighbors == 3:
                    if random.random() < 0.1:
                        new_food.append((x, y))
                        logger.debug(f"Food regeneration candidate at ({x}, {y}) with {neighbors} neighbors")
        
        # Spawn new food
        regenerated_count = 0
        for x, y in new_food:
            self.spawn_food(x, y, 10)
            regenerated_count += 1
        
        if regenerated_count > 0:
            logger.info(f"Food regeneration complete: {regenerated_count} new food items from {attempts} attempts")
        else:
            logger.debug(f"No food regenerated this cycle (checked {attempts} locations)")
    
    def to_dict(self):
        """Convert to JSON-serializable format"""
        logger.debug("Converting food system to dictionary")
        
        result = {
            "food": [(int(x), int(y), self.food_energy.get((x,y), 10)) 
                    for x, y in zip(*self.food_grid.nonzero())]
        }
        
        logger.debug(f"Food system serialization complete: {len(result['food'])} food items")
        return result
    
    @classmethod
    def from_dict(cls, data, width, height):
        """Create from dict"""
        logger.info(f"Loading food system from dictionary for {width}x{height} world")
        
        system = cls(width, height)
        food_count = 0
        
        for x, y, energy in data.get("food", []):
            system.spawn_food(x, y, energy)
            food_count += 1
        
        logger.info(f"Food system loaded successfully: {food_count} food items")
        return system