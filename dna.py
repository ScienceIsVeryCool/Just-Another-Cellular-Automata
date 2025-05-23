# dna.py
import re
import random

class DNAParser:
    def __init__(self):
        self.trait_pattern = re.compile(r'\[([^\]]+)\]')
    
    def parse(self, genome):
        """Parse genome string into traits list"""
        traits = []
        matches = self.trait_pattern.findall(genome)
        
        if not matches or "Cell" not in matches:
            return None  # Invalid genome
        
        for match in matches:
            traits.append(match)
        
        return traits
    
    def mutate(self, genome, rate=0.01):
        """Mutate genome with given rate"""
        if random.random() > rate:
            return genome
        
        mutation_type = random.choices(
            ['point', 'insert', 'delete'],
            weights=[0.7, 0.2, 0.1]
        )[0]
        
        if mutation_type == 'point':
            # Change one character
            pos = random.randint(0, len(genome)-1)
            chars = list(genome)
            chars[pos] = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz:[]')
            return ''.join(chars)
        
        elif mutation_type == 'insert':
            # Insert a trait
            new_traits = ["[CanMove]", "[CanEat]", "[Color:Red]", "[Color:Blue]"]
            trait = random.choice(new_traits)
            return genome + trait
        
        else:  # delete
            # Remove a trait
            traits = self.trait_pattern.findall(genome)
            if len(traits) > 1:  # Keep at least [Cell]
                remove = random.choice(traits[1:])
                return genome.replace(f"[{remove}]", "", 1)
        
        return genome
