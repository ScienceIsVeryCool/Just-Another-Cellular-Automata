# main.py
import pygame
import json
import sys
from datetime import datetime
from world import World
from renderer import Renderer
from config import Config

class Simulation:
    def __init__(self, world_file=None):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        self.tick = 0
        
        # Load or create world
        if world_file:
            with open(world_file) as f:
                self.world = World.from_dict(json.load(f))
        else:
            self.world = World(Config.WORLD_WIDTH, Config.WORLD_HEIGHT)
            self._spawn_initial_organisms()
        
        self.renderer = Renderer(Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT)
        
    def _spawn_initial_organisms(self):
        """Spawn default organisms for testing"""
        # Simple movers
        for i in range(20):
            self.world.spawn_organism("[Cell][CanMove]", 100, 100, 50)
        
        # Stationary
        for i in range(20):
            self.world.spawn_organism("[Cell][Color:Blue]", 900, 900, 50)
            
        # Predators
        for i in range(5):
            self.world.spawn_organism("[Cell][CanMove][CanEat]", 500, 500, 100)
    
    def run(self):
        while self.running:
            self.handle_events()
            
            if not self.paused:
                self.world.update()
                self.tick += 1
                
                if self.tick % 100 == 0:
                    print(f"Tick {self.tick}: {len(self.world.cells)} cells, "
                          f"{len(self.world.organisms)} organisms")
            
            self.renderer.render(self.world)
            self.clock.tick(Config.FPS)
        
        pygame.quit()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                    print("Paused" if self.paused else "Resumed")
                elif event.key == pygame.K_s and self.paused:
                    self.save_world()
                elif event.key == pygame.K_r:
                    self.renderer.camera.zoom *= 1.2
                elif event.key == pygame.K_f:
                    self.renderer.camera.zoom /= 1.2
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.renderer.camera.dragging = True
                    self.renderer.camera.drag_start = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.renderer.camera.dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if self.renderer.camera.dragging:
                    dx = event.pos[0] - self.renderer.camera.drag_start[0]
                    dy = event.pos[1] - self.renderer.camera.drag_start[1]
                    self.renderer.camera.x -= dx / self.renderer.camera.zoom
                    self.renderer.camera.y -= dy / self.renderer.camera.zoom
                    self.renderer.camera.drag_start = event.pos
    
    def save_world(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"world_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(self.world.to_dict(), f, indent=2)
        print(f"World saved to {filename}")

if __name__ == "__main__":
    sim = Simulation(sys.argv[1] if len(sys.argv) > 1 else None)
    sim.run()
