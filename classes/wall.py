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

    def create_corridor(self, start_x, start_y, length, direction, grid_blockSize):
        walls = []

        # Validate direction
        if direction not in ['horizontal', 'vertical']:
            return walls

        # Ensure grid alignment
        start_x = (start_x // grid_blockSize) * grid_blockSize
        start_y = (start_y // grid_blockSize) * grid_blockSize

        if direction == 'horizontal':
            # Top wall (above corridor)
            for x in range(start_x, start_x + length, grid_blockSize):
                walls.append(Wall(x, start_y - grid_blockSize, grid_blockSize, grid_blockSize))

            # Bottom wall (below corridor)
            for x in range(start_x, start_x + length, grid_blockSize):
                walls.append(Wall(x, start_y + grid_blockSize, grid_blockSize, grid_blockSize))
                 
        elif direction == 'vertical':
            # Left wall (left of corridor)
            for y in range(start_y, start_y + length, grid_blockSize):
                walls.append(Wall(start_x - grid_blockSize, y, grid_blockSize, grid_blockSize))

            # Right wall (right of corridor)
            for y in range(start_y, start_y + length, grid_blockSize):
                walls.append(Wall(start_x + grid_blockSize, y, grid_blockSize, grid_blockSize))

        return walls

    def create_l_corridor(self, corner_x, corner_y, h_length, v_length, grid_blockSize, opening_direction):
        walls = []
        # TODO: Implement L-corridor logic

        corner_x = (corner_x // grid_blockSize) * grid_blockSize
        corner_y = (corner_y // grid_blockSize) * grid_blockSize

        # Add validation checks

        # if the direction doesnt match with what is written, return empty
        if opening_direction not in ['right_down', 'left_down', 'right_up', 'left_up']:
            return walls
        # if the length (horizontal or vertical) is not defined by a positive number, return empty
        if h_length <= 0 or v_length <= 0:
            return walls

        # Make a method for directions to make the code more DRY (do not repeat yourself)
        def create_h_line(start_x, end_x, y_pos):
            for x in range(start_x, end_x, grid_blockSize):
                walls.append(Wall(x, y_pos, grid_blockSize, grid_blockSize))
        
        def create_v_line(start_y, end_y, x_pos):
            for y in range(start_y, end_y, grid_blockSize):
                walls.append(Wall(x_pos, y, grid_blockSize, grid_blockSize))
        
        def create_border(x_pos, y_pos):
            walls.append(Wall(x_pos, y_pos, grid_blockSize, grid_blockSize))

        # Wall shapes
        # right_down
        #   - - - - - - - -
        #   |
        #   |
        if opening_direction == 'right_down':
            create_h_line(corner_x, corner_x + h_length, corner_y - grid_blockSize)
            create_v_line(corner_y, corner_y + v_length, corner_x - grid_blockSize)
            create_border(corner_x - grid_blockSize, corner_y - grid_blockSize)
        # left_down
        # - - - - - - -
        #             |
        #             |
        elif opening_direction == 'left_down':
            create_h_line(corner_x - h_length + grid_blockSize, corner_x + grid_blockSize, corner_y - grid_blockSize)
            create_v_line(corner_y, corner_y + v_length, corner_x + grid_blockSize)
            create_border(corner_x + grid_blockSize, corner_y - grid_blockSize)

        # right_up
        # |
        # |
        # - - - - - - - -
        elif opening_direction == 'right_up':
            create_h_line(corner_x, corner_x + h_length, corner_y + grid_blockSize)
            create_v_line(corner_y - v_length + grid_blockSize, corner_y + grid_blockSize, corner_x - grid_blockSize)
            create_border(corner_x - grid_blockSize, corner_y + grid_blockSize)

        # left_up
        #                 |
        #                 |
        # - - - - - - - - -
        elif opening_direction == 'left_up':
            create_h_line(corner_x - h_length + grid_blockSize, corner_x + grid_blockSize, corner_y + grid_blockSize)
            create_v_line(corner_y - v_length + grid_blockSize, corner_y + grid_blockSize, corner_x + grid_blockSize)
            create_border(corner_x + grid_blockSize, corner_y + grid_blockSize)
        return walls 
