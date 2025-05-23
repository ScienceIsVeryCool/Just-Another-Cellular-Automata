# config.py
import logging
import sys
from datetime import datetime

class Config:
    # World
    WORLD_WIDTH = 1024
    WORLD_HEIGHT = 1024
    
    # Display
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    FPS = 30
    
    # Energy System - FIXED FOR SURVIVAL
    STARTING_ENERGY = 200  # Increased from 100
    ENERGY_DRAIN_INTERVAL = 30  # NEW: Drain energy every 30 ticks (once per second at 30 FPS)
    GENOME_ENERGY_COST = 1  # NEW: Reduced from len(genome) to 1 per genome length
    MOVEMENT_COST = 1  # Reduced from 2
    REPRODUCTION_COST = 80  # Increased from 50 to make reproduction more strategic
    REPRODUCTION_THRESHOLD = 250  # Increased from 150
    
    # Food System - ENHANCED
    FOOD_ENERGY = 25  # Increased from 10
    FOOD_REGEN_RATE = 0.05  # Increased from 0.02
    DECAY_FOOD_ENERGY = 15  # NEW: Energy from cell death (was hardcoded to 5)
    
    # DNA
    MUTATION_RATE = 0.01
    MAX_GENOME_LENGTH = 500
    
    # Cell stacking limit
    MAX_CELLS_PER_LOCATION = 1  # Prevent cell stacking exploitation
    
    # Statistics
    STATS_HISTORY_SIZE = 1000  # How many ticks of history to keep
    STATS_UPDATE_INTERVAL = 10  # Update stats every N ticks for performance
    
    # Logging
    LOG_LEVEL = logging.DEBUG  # Change to INFO, WARNING, or ERROR as needed
    LOG_TO_FILE = True
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    @classmethod
    def setup_logging(cls):
        """Configure logging for the entire application"""
        # Create logs directory if it doesn't exist
        import os
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # Create logger
        logger = logging.getLogger()
        logger.setLevel(cls.LOG_LEVEL)
        
        # Clear any existing handlers
        logger.handlers.clear()
        
        # Create formatters
        formatter = logging.Formatter(cls.LOG_FORMAT, cls.LOG_DATE_FORMAT)
        
        # Console handler - shows INFO and above by default
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler for detailed logs - shows all levels
        if cls.LOG_TO_FILE:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_handler = logging.FileHandler(f'logs/simulation_{timestamp}.log')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        # Set specific logger levels for different modules
        logging.getLogger('world').setLevel(cls.LOG_LEVEL)
        logging.getLogger('cell').setLevel(cls.LOG_LEVEL)
        logging.getLogger('dna').setLevel(cls.LOG_LEVEL)
        logging.getLogger('food').setLevel(cls.LOG_LEVEL)
        logging.getLogger('renderer').setLevel(cls.LOG_LEVEL)
        logging.getLogger('main').setLevel(cls.LOG_LEVEL)
        logging.getLogger('stats').setLevel(cls.LOG_LEVEL)
        
        logger.info("Logging system initialized")
        logger.debug(f"Log level set to: {logging.getLevelName(cls.LOG_LEVEL)}")
        logger.debug(f"Logging to file: {cls.LOG_TO_FILE}")