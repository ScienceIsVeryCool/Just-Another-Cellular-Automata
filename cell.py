# cell.py
class Cell:
    def __init__(self, id, x, y, organism_id):
        self.id = id
        self.x = x
        self.y = y
        self.organism_id = organism_id
        self.energy = 100
        self.age = 0

class Organism:
    def __init__(self, id, genome, traits):
        self.id = id
        self.genome = genome
        self.traits = traits
        self.cell_ids = set()
        self.birth_tick = 0
        self.color = self._extract_color()
    
    def _extract_color(self):
        """Extract color from traits"""
        for trait in self.traits:
            if trait.startswith("Color:"):
                return trait.split(":")[1]
        return "Green"

