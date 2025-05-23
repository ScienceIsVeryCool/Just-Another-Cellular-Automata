# config.py
class Config:
    # World
    WORLD_WIDTH = 1024
    WORLD_HEIGHT = 1024
    
    # Display
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    FPS = 30
    
    # Energy
    STARTING_ENERGY = 100
    MOVEMENT_COST = 2
    REPRODUCTION_COST = 50
    REPRODUCTION_THRESHOLD = 150
    
    # Food
    FOOD_ENERGY = 10
    FOOD_REGEN_RATE = 0.02
    
    # DNA
    MUTATION_RATE = 0.01
    MAX_GENOME_LENGTH = 500