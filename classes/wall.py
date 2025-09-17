import pygame as pg

class Wall:
    def __init__(self, x, y, height, width):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.color = (20, 20, 40)  # Classic Pacman blue
    
    def draw_wall(self, screen, all_walls=None, rainbow_color=None):
        # Always use the original wall color for the fill
        pg.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
        if all_walls is not None:
            # Smart border drawing - use rainbow color for borders only
            self.draw_smart_borders(screen, all_walls, rainbow_color)
        else:
            # Fallback: draw full border with rainbow color
            border_color = rainbow_color if rainbow_color else (255, 0, 0)
            pg.draw.rect(screen, border_color, (self.x, self.y, self.width, self.height), 2)
    
    def draw_smart_borders(self, screen, all_walls, rainbow_color=None):
        # Use rainbow color for borders if provided, otherwise use red
        border_color = rainbow_color if rainbow_color else (255, 0, 0)
        
        # Check for adjacent walls
        has_left = self.has_adjacent_wall(all_walls, self.x - self.width, self.y)
        has_right = self.has_adjacent_wall(all_walls, self.x + self.width, self.y)
        has_top = self.has_adjacent_wall(all_walls, self.x, self.y - self.height)
        has_bottom = self.has_adjacent_wall(all_walls, self.x, self.y + self.height)
        
        # Draw borders only where there's no adjacent wall
        if not has_left:  # Left border
            pg.draw.line(screen, border_color, (self.x, self.y), (self.x, self.y + self.height), 2)
        if not has_right:  # Right border
            pg.draw.line(screen, border_color, (self.x + self.width, self.y), (self.x + self.width, self.y + self.height), 2)
        if not has_top:  # Top border
            pg.draw.line(screen, border_color, (self.x, self.y), (self.x + self.width, self.y), 2)
        if not has_bottom:  # Bottom border
            pg.draw.line(screen, border_color, (self.x, self.y + self.height), (self.x + self.width, self.y + self.height), 2)
    
    def has_adjacent_wall(self, all_walls, check_x, check_y):
        # Check if there's a wall at the specified position
        for wall in all_walls:
            if wall.x == check_x and wall.y == check_y:
                return True
        return False
        
    def check_wall_collision(self, pacman):
        wall_rect = pg.Rect(self.x, self.y, self.width, self.height)
        pacman_rect = pg.Rect(pacman.x, pacman.y, pacman.length, pacman.width)
        return wall_rect.colliderect(pacman_rect)
    
    def border_wall(self, window_width, window_height, grid_blockSize):
        walls = []
        gap_y = self.y + (window_height // 2 // grid_blockSize) * grid_blockSize

        for x in range(0, window_width, grid_blockSize):
            walls.append(Wall(x, 0, grid_blockSize, grid_blockSize))
            walls.append(Wall(x, window_height - grid_blockSize, grid_blockSize, grid_blockSize))

        for y in range(grid_blockSize, window_height - grid_blockSize, grid_blockSize):
            if y != gap_y:
                walls.append(Wall(0, y, grid_blockSize, grid_blockSize))
                walls.append(Wall(window_width - grid_blockSize, y, grid_blockSize, grid_blockSize)) 
        return walls

    def create_single_wall_line(self, start_x, start_y, length, grid_blockSize):
        walls = []

        start_x = (start_x // grid_blockSize) * grid_blockSize
        start_y = (start_y // grid_blockSize) * grid_blockSize

        for x in range(start_x, start_x + length, grid_blockSize):
            walls.append(Wall(x, start_y, grid_blockSize, grid_blockSize))
        return walls
