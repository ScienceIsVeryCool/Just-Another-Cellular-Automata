
# renderer.py
import pygame
import numpy as np

class Camera:
    def __init__(self, screen_width, screen_height):
        self.x = 0
        self.y = 0
        self.zoom = 1.0
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.dragging = False
        self.drag_start = (0, 0)
    
    def world_to_screen(self, wx, wy):
        """Convert world coordinates to screen"""
        sx = (wx - self.x) * self.zoom + self.screen_width // 2
        sy = (wy - self.y) * self.zoom + self.screen_height // 2
        return int(sx), int(sy)
    
    def get_visible_bounds(self):
        """Get world bounds visible on screen"""
        half_w = self.screen_width // (2 * self.zoom)
        half_h = self.screen_height // (2 * self.zoom)
        return (
            int(self.x - half_w), int(self.y - half_h),
            int(self.x + half_w), int(self.y + half_h)
        )

class Renderer:
    def __init__(self, width, height):
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Cellular Evolution")
        self.camera = Camera(width, height)
        self.font = pygame.font.Font(None, 24)
        
        # Colors
        self.COLORS = {
            "Green": (0, 255, 0),
            "Blue": (0, 100, 255),
            "Red": (255, 50, 50),
            "Yellow": (255, 255, 0),
            "Purple": (200, 0, 200),
            "Wall": (100, 100, 100),
            "Food": (150, 100, 50),
            "Background": (20, 20, 20)
        }
    
    def render(self, world):
        """Render the world"""
        self.screen.fill(self.COLORS["Background"])
        
        # Get visible bounds
        x1, y1, x2, y2 = self.camera.get_visible_bounds()
        
        # Render food
        for (fx, fy), energy in world.food_system.food_energy.items():
            if x1 <= fx <= x2 and y1 <= fy <= y2:
                sx, sy = self.camera.world_to_screen(fx, fy)
                size = max(2, int(3 * self.camera.zoom))
                pygame.draw.rect(self.screen, self.COLORS["Food"],
                               (sx, sy, size, size))
        
        # Render walls
        for wx, wy in zip(*world.walls.nonzero()):
            if x1 <= wx <= x2 and y1 <= wy <= y2:
                sx, sy = self.camera.world_to_screen(wx, wy)
                size = max(1, int(self.camera.zoom))
                pygame.draw.rect(self.screen, self.COLORS["Wall"],
                               (sx, sy, size, size))
        
        # Render cells
        for cell in world.cells.values():
            if x1 <= cell.x <= x2 and y1 <= cell.y <= y2:
                organism = world.organisms.get(cell.organism_id)
                if organism:
                    color = self.COLORS.get(organism.color, self.COLORS["Green"])
                    sx, sy = self.camera.world_to_screen(cell.x, cell.y)
                    size = max(2, int(4 * self.camera.zoom))
                    
                    # Brighter if more energy
                    brightness = min(1.0, cell.energy / 200)
                    color = tuple(int(c * brightness) for c in color)
                    
                    pygame.draw.rect(self.screen, color,
                                   (sx, sy, size, size))
        
        # Render stats
        stats = [
            f"Cells: {len(world.cells)}",
            f"Organisms: {len(world.organisms)}",
            f"Food: {len(world.food_system.food_energy)}",
            f"Zoom: {self.camera.zoom:.2f}",
            "SPACE: pause, S: save, R/F: zoom"
        ]
        
        y = 10
        for stat in stats:
            text = self.font.render(stat, True, (255, 255, 255))
            self.screen.blit(text, (10, y))
            y += 25
        
        pygame.display.flip()
