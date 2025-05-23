# main.py
import pygame
import json
import sys
import logging
from datetime import datetime
from world import World
from renderer import Renderer
from config import Config

# Setup logging before any other imports
Config.setup_logging()
logger = logging.getLogger('main')

class Simulation:
    def __init__(self, world_file=None):
        logger.info("Initializing Cellular Evolution Simulator")
        logger.debug(f"World file parameter: {world_file}")
        
        try:
            pygame.init()
            logger.debug("Pygame initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Pygame: {e}")
            raise
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        self.tick = 0
        logger.debug("Simulation state variables initialized")
        
        # Load or create world
        try:
            if world_file:
                logger.info(f"Loading world from file: {world_file}")
                with open(world_file) as f:
                    world_data = json.load(f)
                    logger.debug(f"World data loaded: {len(world_data.get('organisms', []))} organisms, "
                               f"{len(world_data.get('food', {}).get('food', []))} food items, "
                               f"{len(world_data.get('walls', []))} walls")
                self.world = World.from_dict(world_data)
                logger.info("World loaded successfully from file")
            else:
                logger.info("Creating new default world")
                self.world = World(Config.WORLD_WIDTH, Config.WORLD_HEIGHT)
                self._spawn_initial_organisms()
                logger.info("Default world created and populated")
        except FileNotFoundError:
            logger.error(f"World file not found: {world_file}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in world file {world_file}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load world: {e}")
            raise
        
        try:
            self.renderer = Renderer(Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT)
            logger.debug("Renderer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize renderer: {e}")
            raise
        
        logger.info("Simulation initialization complete")
        
    def _spawn_initial_organisms(self):
        """Spawn default organisms for testing"""
        logger.info("Spawning initial test organisms")
        
        # Simple movers
        mover_count = 0
        for i in range(20):
            organism = self.world.spawn_organism("[Cell][CanMove]", 100, 100, 50)
            if organism:
                mover_count += 1
        logger.info(f"Spawned {mover_count}/20 simple mover organisms")
        
        # Stationary
        stationary_count = 0
        for i in range(20):
            organism = self.world.spawn_organism("[Cell][Color:Blue]", 900, 900, 50)
            if organism:
                stationary_count += 1
        logger.info(f"Spawned {stationary_count}/20 stationary blue organisms")
            
        # Predators
        predator_count = 0
        for i in range(5):
            organism = self.world.spawn_organism("[Cell][CanMove][CanEat]", 500, 500, 100)
            if organism:
                predator_count += 1
        logger.info(f"Spawned {predator_count}/5 predator organisms")
        
        total_spawned = mover_count + stationary_count + predator_count
        logger.info(f"Initial organism spawn complete: {total_spawned} total organisms")
    
    def run(self):
        logger.info("Starting main simulation loop")
        frame_count = 0
        
        while self.running:
            try:
                self.handle_events()
                
                if not self.paused:
                    self.world.update()
                    self.tick += 1
                    
                    # Periodic status logging
                    if self.tick % 100 == 0:
                        cell_count = len(self.world.cells)
                        org_count = len(self.world.organisms)
                        food_count = len(self.world.food_system.food_energy)
                        
                        logger.info(f"Tick {self.tick}: {cell_count} cells, {org_count} organisms, {food_count} food")
                        
                        # Debug log for performance monitoring
                        if self.tick % 1000 == 0:
                            logger.debug(f"Performance check at tick {self.tick}: "
                                       f"Average {frame_count/(self.tick/100):.1f} FPS over last period")
                
                self.renderer.render(self.world)
                self.clock.tick(Config.FPS)
                frame_count += 1
                
            except Exception as e:
                logger.error(f"Error in main loop at tick {self.tick}: {e}")
                logger.debug("Exception details:", exc_info=True)
                # Continue running unless it's a critical error
                if isinstance(e, (KeyboardInterrupt, SystemExit)):
                    logger.info("Received shutdown signal")
                    break
        
        logger.info(f"Simulation ended after {self.tick} ticks and {frame_count} frames")
        pygame.quit()
        logger.debug("Pygame shut down cleanly")
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.info("Quit event received")
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                    state = "Paused" if self.paused else "Resumed"
                    logger.info(f"Simulation {state.lower()} by user")
                    print(state)
                elif event.key == pygame.K_s and self.paused:
                    logger.debug("Save world command received")
                    try:
                        self.save_world()
                    except Exception as e:
                        logger.error(f"Failed to save world: {e}")
                elif event.key == pygame.K_r:
                    old_zoom = self.renderer.camera.zoom
                    self.renderer.camera.zoom *= 1.2
                    logger.debug(f"Zoom in: {old_zoom:.2f} -> {self.renderer.camera.zoom:.2f}")
                elif event.key == pygame.K_f:
                    old_zoom = self.renderer.camera.zoom
                    self.renderer.camera.zoom /= 1.2
                    logger.debug(f"Zoom out: {old_zoom:.2f} -> {self.renderer.camera.zoom:.2f}")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    logger.debug(f"Camera drag started at {event.pos}")
                    self.renderer.camera.dragging = True
                    self.renderer.camera.drag_start = event.pos
                # NEW: Middle mouse button for reset zoom
                elif event.button == 2:  # Middle click
                    old_zoom = self.renderer.camera.zoom
                    self.renderer.camera.zoom = 1.0
                    logger.debug(f"Zoom reset: {old_zoom:.2f} -> 1.0")
                # NEW: Handle scroll wheel zoom
                elif event.button == 4:  # Scroll up
                    old_zoom = self.renderer.camera.zoom
                    self.renderer.camera.zoom *= 1.1
                    # Clamp zoom to reasonable limits
                    self.renderer.camera.zoom = min(self.renderer.camera.zoom, 10.0)
                    logger.debug(f"Scroll zoom in: {old_zoom:.2f} -> {self.renderer.camera.zoom:.2f}")
                elif event.button == 5:  # Scroll down
                    old_zoom = self.renderer.camera.zoom
                    self.renderer.camera.zoom /= 1.1
                    # Clamp zoom to reasonable limits
                    self.renderer.camera.zoom = max(self.renderer.camera.zoom, 0.1)
                    logger.debug(f"Scroll zoom out: {old_zoom:.2f} -> {self.renderer.camera.zoom:.2f}")
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    logger.debug("Camera drag ended")
                    self.renderer.camera.dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if self.renderer.camera.dragging:
                    dx = event.pos[0] - self.renderer.camera.drag_start[0]
                    dy = event.pos[1] - self.renderer.camera.drag_start[1]
                    old_x, old_y = self.renderer.camera.x, self.renderer.camera.y
                    self.renderer.camera.x -= dx / self.renderer.camera.zoom
                    self.renderer.camera.y -= dy / self.renderer.camera.zoom
                    self.renderer.camera.drag_start = event.pos
                    
                    # Only log significant camera movements to avoid spam
                    if abs(dx) > 5 or abs(dy) > 5:
                        logger.debug(f"Camera moved: ({old_x:.1f}, {old_y:.1f}) -> "
                                   f"({self.renderer.camera.x:.1f}, {self.renderer.camera.y:.1f})")
    
    def save_world(self):
        """Save the current world state to a JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"world_{timestamp}.json"
        
        try:
            logger.info(f"Saving world to {filename}")
            world_data = self.world.to_dict()
            
            with open(filename, 'w') as f:
                json.dump(world_data, f, indent=2)
            
            logger.info(f"World saved successfully: {len(world_data['organisms'])} organisms, "
                       f"{len(world_data['food']['food'])} food items, "
                       f"{len(world_data['walls'])} walls")
            print(f"World saved to {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save world to {filename}: {e}")
            logger.debug("Save error details:", exc_info=True)
            raise

if __name__ == "__main__":
    try:
        logger.info("=== Cellular Evolution Simulator Starting ===")
        logger.debug(f"Command line arguments: {sys.argv}")
        
        world_file = sys.argv[1] if len(sys.argv) > 1 else None
        sim = Simulation(world_file)
        sim.run()
        
    except Exception as e:
        logger.error(f"Critical error during simulation startup: {e}")
        logger.debug("Startup error details:", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("=== Cellular Evolution Simulator Shutdown ===")