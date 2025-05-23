# dna.py
import re
import random
import logging

logger = logging.getLogger('dna')

class DNAParser:
    def __init__(self):
        self.trait_pattern = re.compile(r'\[([^\]]+)\]')
        logger.debug("DNAParser initialized with trait pattern")
    
    def parse(self, genome):
        """Parse genome string into traits list"""
        logger.debug(f"Parsing genome: '{genome}'")
        
        traits = []
        matches = self.trait_pattern.findall(genome)
        
        if not matches:
            logger.warning(f"No trait patterns found in genome '{genome}'")
            return None
        
        if "Cell" not in matches:
            logger.warning(f"Required 'Cell' trait not found in genome '{genome}', found traits: {matches}")
            return None  # Invalid genome
        
        for match in matches:
            traits.append(match)
            logger.debug(f"Found trait: '{match}'")
        
        logger.debug(f"Successfully parsed {len(traits)} traits from genome: {traits}")
        return traits
    
    def mutate(self, genome, rate=0.01):
        """Mutate genome with given rate"""
        logger.debug(f"Attempting mutation on genome '{genome}' with rate {rate}")
        
        if random.random() > rate:
            logger.debug("No mutation occurred (random roll failed)")
            return genome
        
        mutation_type = random.choices(
            ['point', 'insert', 'delete'],
            weights=[0.7, 0.2, 0.1]
        )[0]
        
        logger.debug(f"Mutation type selected: {mutation_type}")
        
        if mutation_type == 'point':
            # Change one character
            if len(genome) == 0:
                logger.warning("Cannot perform point mutation on empty genome")
                return genome
                
            pos = random.randint(0, len(genome)-1)
            chars = list(genome)
            old_char = chars[pos]
            chars[pos] = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz:[]')
            new_genome = ''.join(chars)
            
            logger.info(f"Point mutation: '{genome}' -> '{new_genome}' (position {pos}: '{old_char}' -> '{chars[pos]}')")
            return new_genome
        
        elif mutation_type == 'insert':
            # Insert a trait
            new_traits = ["[CanMove]", "[CanEat]", "[Color:Red]", "[Color:Blue]"]
            trait = random.choice(new_traits)
            new_genome = genome + trait
            
            logger.info(f"Insert mutation: '{genome}' -> '{new_genome}' (added '{trait}')")
            return new_genome
        
        else:  # delete
            # Remove a trait
            traits = self.trait_pattern.findall(genome)
            if len(traits) <= 1:  # Keep at least [Cell]
                logger.debug("Delete mutation skipped - only one trait remaining (need to keep [Cell])")
                return genome
                
            # Don't remove the Cell trait
            removable_traits = [t for t in traits if t != "Cell"]
            if not removable_traits:
                logger.debug("Delete mutation skipped - no removable traits (only [Cell] present)")
                return genome
                
            remove = random.choice(removable_traits)
            new_genome = genome.replace(f"[{remove}]", "", 1)
            
            logger.info(f"Delete mutation: '{genome}' -> '{new_genome}' (removed '[{remove}]')")
            return new_genome