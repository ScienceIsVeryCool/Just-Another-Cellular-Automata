# cell.py
import logging

logger = logging.getLogger('cell')

class Cell:
    def __init__(self, id, x, y, organism_id):
        self.id = id
        self.x = x
        self.y = y
        self.organism_id = organism_id
        self.energy = 100
        self.age = 0
        
        logger.debug(f"Created cell {id} at ({x}, {y}) for organism {organism_id}")

class Organism:
    def __init__(self, id, genome, traits):
        self.id = id
        self.genome = genome
        self.traits = traits
        self.cell_ids = set()
        self.birth_tick = 0
        self.color = self._extract_color()
        
        logger.debug(f"Created organism {id} with genome '{genome}' and traits {traits}")
        logger.debug(f"Organism {id} assigned color: {self.color}")
    
    def _extract_color(self):
        """Extract color from traits"""
        for trait in self.traits:
            if trait.startswith("Color:"):
                color = trait.split(":")[1]
                logger.debug(f"Extracted color '{color}' from trait '{trait}'")
                return color
        
        logger.debug("No color trait found, defaulting to Green")
        return "Green"