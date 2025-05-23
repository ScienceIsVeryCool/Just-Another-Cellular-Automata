
# food.py
import numpy as np
from scipy.sparse import dok_matrix
import random

class FoodSystem:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.food_grid = dok_matrix((width, height), dtype=np.int8)
        self.food_energy = {}
    
    def spawn_gaussian_cluster(self, cx, cy, spread, density):
        """Spawn food in gaussian distribution"""
        for x in range(max(0, cx-spread*2), min(self.width, cx+spread*2)):
            for y in range(max(0, cy-spread*2), min(self.height, cy+spread*2)):
                dist_sq = (x-cx)**2 + (y-cy)**2
                prob = density * np.exp(-dist_sq / (2 * spread**2))
                
                if random.random() < prob:
                    self.spawn_food(x, y, 10)
    
    def spawn_food(self, x, y, energy):
        """Spawn food at position"""
        self.food_grid[x, y] = 1
        self.food_energy[(x, y)] = energy
    
    def eat_food(self, x, y):
        """Try to eat food at position"""
        if (x, y) in self.food_energy:
            energy = self.food_energy[(x, y)]
            del self.food_energy[(x, y)]
            self.food_grid[x, y] = 0
            return energy
        return 0
    
    def regenerate(self):
        """Conway-inspired food regeneration"""
        new_food = []
        
        # Check random sample of empty cells
        for _ in range(100):
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
        
        # Spawn new food
        for x, y in new_food:
            self.spawn_food(x, y, 10)
    
    def to_dict(self):
        """Convert to JSON-serializable format"""
        return {
            "food": [(int(x), int(y), self.food_energy.get((x,y), 10)) 
                    for x, y in zip(*self.food_grid.nonzero())]
        }
    
    @classmethod
    def from_dict(cls, data, width, height):
        """Create from dict"""
        system = cls(width, height)
        for x, y, energy in data.get("food", []):
            system.spawn_food(x, y, energy)
        return system
