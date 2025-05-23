# renderer.py
import pygame
import numpy as np
import logging
from typing import Optional
import math

logger = logging.getLogger('renderer')

class Camera:
    def __init__(self, screen_width, screen_height):
        logger.debug(f"Initializing camera for {screen_width}x{screen_height} screen")
        
        self.x = 0
        self.y = 0
        self.zoom = 1.0
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.dragging = False
        self.drag_start = (0, 0)
        
        logger.debug("Camera initialized at origin with zoom 1.0")
    
    def world_to_screen(self, wx, wy):
        """Convert world coordinates to screen"""
        sx = (wx - self.x) * self.zoom + self.screen_width // 2
        sy = (wy - self.y) * self.zoom + self.screen_height // 2
        return int(sx), int(sy)
    
    def get_visible_bounds(self):
        """Get world bounds visible on screen"""
        half_w = self.screen_width // (2 * self.zoom)
        half_h = self.screen_height // (2 * self.zoom)
        bounds = (
            int(self.x - half_w), int(self.y - half_h),
            int(self.x + half_w), int(self.y + half_h)
        )
        
        logger.debug(f"Camera visible bounds: ({bounds[0]}, {bounds[1]}) to ({bounds[2]}, {bounds[3]})")
        return bounds

class Renderer:
    def __init__(self, width, height):
        logger.info(f"Initializing renderer with {width}x{height} display")
        
        try:
            self.screen = pygame.display.set_mode((width, height))
            pygame.display.set_caption("Cellular Evolution")
            logger.debug("Pygame display initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize pygame display: {e}")
            raise
        
        self.screen_width = width
        self.screen_height = height
        self.camera = Camera(width, height)
        self.show_stats = False  # Toggle between simulation and stats view
        self.fullscreen = False
        
        try:
            self.font_small = pygame.font.Font(None, 16)
            self.font = pygame.font.Font(None, 24)
            self.font_large = pygame.font.Font(None, 32)
            logger.debug("Fonts loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load fonts: {e}")
            raise
        
        # Colors
        self.COLORS = {
            "Green": (0, 255, 0),
            "Blue": (0, 100, 255),
            "Red": (255, 50, 50),
            "Yellow": (255, 255, 0),
            "Purple": (200, 0, 200),
            "Wall": (100, 100, 100),
            "Food": (150, 100, 50),
            "Background": (20, 20, 20),
            "StatsBackground": (10, 10, 10),
            "TextPrimary": (255, 255, 255),
            "TextSecondary": (180, 180, 180),
            "GraphLine": (100, 200, 255),
            "GraphGrid": (50, 50, 50),
            "Success": (0, 255, 100),
            "Warning": (255, 200, 0),
            "Danger": (255, 50, 50)
        }
        
        logger.debug(f"Color palette initialized with {len(self.COLORS)} colors")
        logger.info("Renderer initialization complete")
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.fullscreen = not self.fullscreen
        
        if self.fullscreen:
            # Get current display info
            info = pygame.display.Info()
            self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
            self.screen_width = info.current_w
            self.screen_height = info.current_h
            logger.info(f"Switched to fullscreen mode: {self.screen_width}x{self.screen_height}")
        else:
            # Return to windowed mode
            from config import Config
            self.screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
            self.screen_width = Config.SCREEN_WIDTH
            self.screen_height = Config.SCREEN_HEIGHT
            logger.info(f"Switched to windowed mode: {self.screen_width}x{self.screen_height}")
        
        # Update camera dimensions
        self.camera.screen_width = self.screen_width
        self.camera.screen_height = self.screen_height
    
    def render(self, world, stats=None):
        """Render the world or statistics"""
        if self.show_stats and stats:
            self.render_stats(stats)
        else:
            self.render_world(world)
    
    def render_world(self, world):
        """Render the simulation world"""
        try:
            # Clear screen
            self.screen.fill(self.COLORS["Background"])
            
            # Get visible bounds
            x1, y1, x2, y2 = self.camera.get_visible_bounds()
            
            # Count rendered objects for debug logging
            food_rendered = 0
            walls_rendered = 0
            cells_rendered = 0
            
            # Render food
            for (fx, fy), energy in world.food_system.food_energy.items():
                if x1 <= fx <= x2 and y1 <= fy <= y2:
                    sx, sy = self.camera.world_to_screen(fx, fy)
                    size = max(2, int(3 * self.camera.zoom))
                    
                    try:
                        pygame.draw.rect(self.screen, self.COLORS["Food"],
                                       (sx, sy, size, size))
                        food_rendered += 1
                    except Exception as e:
                        logger.warning(f"Failed to render food at ({fx}, {fy}): {e}")
            
            # Render walls
            for wx, wy in zip(*world.walls.nonzero()):
                if x1 <= wx <= x2 and y1 <= wy <= y2:
                    sx, sy = self.camera.world_to_screen(wx, wy)
                    size = max(1, int(self.camera.zoom))
                    
                    try:
                        pygame.draw.rect(self.screen, self.COLORS["Wall"],
                                       (sx, sy, size, size))
                        walls_rendered += 1
                    except Exception as e:
                        logger.warning(f"Failed to render wall at ({wx}, {wy}): {e}")
            
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
                        
                        try:
                            pygame.draw.rect(self.screen, color,
                                           (sx, sy, size, size))
                            cells_rendered += 1
                        except Exception as e:
                            logger.warning(f"Failed to render cell {cell.id} at ({cell.x}, {cell.y}): {e}")
                    else:
                        logger.warning(f"Cell {cell.id} has invalid organism_id {cell.organism_id}")
            
            # Render HUD
            self._render_hud(world)
            
            # Update display
            pygame.display.flip()
            
            # Debug logging for render counts (only log periodically to avoid spam)
            total_rendered = food_rendered + walls_rendered + cells_rendered
            if total_rendered > 0:
                logger.debug(f"Rendered {cells_rendered} cells, {food_rendered} food, "
                           f"{walls_rendered} walls in visible area")
            
        except Exception as e:
            logger.error(f"Critical error during world rendering: {e}")
            logger.debug("Render error details:", exc_info=True)
            raise
    
    def _render_hud(self, world):
        """Render the heads-up display with controls"""
        stats = [
            f"Cells: {len(world.cells)}",
            f"Organisms: {len(world.organisms)}",
            f"Food: {len(world.food_system.food_energy)}",
            f"Zoom: {self.camera.zoom:.2f}",
            "",
            "Controls:",
            "SPACE: pause | S: save | T: stats",
            "R/F/Scroll: zoom | Middle: reset",
            "F11: fullscreen | Drag: pan"
        ]
        
        y = 10
        for stat in stats:
            try:
                if stat:  # Skip empty lines
                    text = self.font_small.render(stat, True, self.COLORS["TextPrimary"])
                    self.screen.blit(text, (10, y))
                y += 18
            except Exception as e:
                logger.warning(f"Failed to render HUD text '{stat}': {e}")
    
    def render_stats(self, stats):
        """Render comprehensive statistics view"""
        try:
            # Clear screen
            self.screen.fill(self.COLORS["StatsBackground"])
            
            # Get summary data
            summary = stats.get_summary()
            
            # Layout configuration
            margin = 20
            col_width = (self.screen_width - 3 * margin) // 2
            
            # Title
            title_text = self.font_large.render("Simulation Statistics", True, self.COLORS["TextPrimary"])
            title_rect = title_text.get_rect(center=(self.screen_width // 2, 30))
            self.screen.blit(title_text, title_rect)
            
            # Left column - General stats
            left_x = margin
            y = 70
            
            self._render_section("Overview", left_x, y, [
                f"Runtime: {self._format_time(summary['runtime'])}",
                f"Current Tick: {summary['current_tick']:,}",
                f"Tick Rate: {1.0/summary['performance']['avg_tick_duration']:.1f}/s" if summary['performance']['avg_tick_duration'] > 0 else "N/A"
            ])
            
            y += 100
            self._render_section("Population", left_x, y, [
                f"Cells: {summary['population']['cells']:,}",
                f"Organisms: {summary['population']['organisms']:,}",
                f"Food: {summary['population']['food']:,}",
                f"Genome Diversity: {summary['genome_diversity']}",
                f"Extinct Genomes: {summary['extinct_genomes']}"
            ])
            
            y += 140
            self._render_section("Life Events", left_x, y, [
                f"Total Births: {summary['total_births']:,}",
                f"Total Deaths: {summary['total_deaths']:,}",
                f"Birth Rate: {summary['birth_rate']:.2f}/s",
                f"Death Rate: {summary['death_rate']:.2f}/s",
                f"Mutations: {summary['total_mutations']:,}"
            ])
            
            # Right column - Graphs and advanced stats
            right_x = left_x + col_width + margin
            y = 70
            
            # Population graph
            if stats.population_history:
                self._render_population_graph(right_x, y, 
                                            col_width - margin, 120, 
                                            stats.population_history)
            
            y += 140
            # Trait distribution
            if summary['trait_distribution']:
                self._render_trait_distribution(right_x, y, summary['trait_distribution'])
            
            y += 140
            # Genome leaderboard
            leaderboard = stats.get_genome_leaderboard(5)
            if leaderboard:
                self._render_genome_leaderboard(right_x, y, leaderboard)
            
            # Notable events at bottom
            if stats.notable_events:
                self._render_notable_events(margin, self.screen_height - 150, 
                                          self.screen_width - 2 * margin, stats.notable_events)
            
            # Exit instructions
            exit_text = self.font.render("Press T to return to simulation", True, self.COLORS["TextSecondary"])
            exit_rect = exit_text.get_rect(center=(self.screen_width // 2, self.screen_height - 20))
            self.screen.blit(exit_text, exit_rect)
            
            pygame.display.flip()
            
        except Exception as e:
            logger.error(f"Error rendering statistics: {e}")
            logger.debug("Stats render error details:", exc_info=True)
    
    def _render_section(self, title, x, y, lines):
        """Render a statistics section"""
        # Title
        title_text = self.font.render(title, True, self.COLORS["TextPrimary"])
        self.screen.blit(title_text, (x, y))
        
        # Lines
        y += 30
        for line in lines:
            text = self.font_small.render(line, True, self.COLORS["TextSecondary"])
            self.screen.blit(text, (x + 10, y))
            y += 20
    
    def _render_population_graph(self, x, y, width, height, history):
        """Render a population history graph"""
        # Draw border
        pygame.draw.rect(self.screen, self.COLORS["GraphGrid"], 
                        (x, y, width, height), 1)
        
        # Title
        title = self.font_small.render("Population Over Time", True, self.COLORS["TextPrimary"])
        self.screen.blit(title, (x + 5, y - 20))
        
        if len(history) < 2:
            return
        
        # Get data points
        points = [(h.tick, h.total_cells) for h in history[-100:]]  # Last 100 points
        if not points:
            return
        
        # Find min/max for scaling
        min_pop = min(p[1] for p in points)
        max_pop = max(p[1] for p in points)
        pop_range = max_pop - min_pop if max_pop != min_pop else 1
        
        min_tick = points[0][0]
        max_tick = points[-1][0]
        tick_range = max_tick - min_tick if max_tick != min_tick else 1
        
        # Convert to screen coordinates
        screen_points = []
        for tick, pop in points:
            sx = x + int((tick - min_tick) / tick_range * (width - 10)) + 5
            sy = y + height - int((pop - min_pop) / pop_range * (height - 10)) - 5
            screen_points.append((sx, sy))
        
        # Draw line
        if len(screen_points) > 1:
            pygame.draw.lines(self.screen, self.COLORS["GraphLine"], 
                            False, screen_points, 2)
        
        # Draw labels
        pop_label = self.font_small.render(f"{max_pop:,}", True, self.COLORS["TextSecondary"])
        self.screen.blit(pop_label, (x + width + 5, y))
        
        pop_label = self.font_small.render(f"{min_pop:,}", True, self.COLORS["TextSecondary"])
        self.screen.blit(pop_label, (x + width + 5, y + height - 15))
    
    def _render_trait_distribution(self, x, y, traits):
        """Render trait distribution"""
        title_text = self.font.render("Trait Distribution", True, self.COLORS["TextPrimary"])
        self.screen.blit(title_text, (x, y))
        
        y += 30
        for trait, count in sorted(traits.items(), key=lambda x: x[1], reverse=True)[:5]:
            text = self.font_small.render(f"{trait}: {count}", True, self.COLORS["TextSecondary"])
            self.screen.blit(text, (x + 10, y))
            y += 20
    
    def _render_genome_leaderboard(self, x, y, leaderboard):
        """Render top genomes"""
        title_text = self.font.render("Top Genomes", True, self.COLORS["TextPrimary"])
        self.screen.blit(title_text, (x, y))
        
        y += 30
        for i, (genome, stats) in enumerate(leaderboard[:5]):
            # Truncate long genomes
            display_genome = genome if len(genome) <= 30 else genome[:27] + "..."
            text = self.font_small.render(
                f"{i+1}. {display_genome} (pop: {stats.peak_population})",
                True, self.COLORS["TextSecondary"]
            )
            self.screen.blit(text, (x + 10, y))
            y += 20
    
    def _render_notable_events(self, x, y, width, events):
        """Render notable events"""
        title_text = self.font.render("Notable Events", True, self.COLORS["TextPrimary"])
        self.screen.blit(title_text, (x, y))
        
        y += 25
        for event in list(events)[-3:]:  # Show last 3 events
            text = self.font_small.render(event, True, self.COLORS["TextSecondary"])
            self.screen.blit(text, (x + 10, y))
            y += 20
    
    def _format_time(self, seconds):
        """Format time in human-readable format"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}m"
        else:
            return f"{seconds/3600:.1f}h"