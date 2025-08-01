import pygame as pg
from pygame.locals import (K_UP, K_DOWN, K_LEFT, K_RIGHT, K_w, K_s, K_a, K_d)
from os.path import join

# Initialize the game
pg.init()

# 
VINDU_BREDDE = 1000
VINDU_HOYDE = 600
vindu = pg.display.set_mode([VINDU_BREDDE, VINDU_HOYDE])
dt = 0
clock = pg.time.Clock()

#Make the pac man
class Pacman:
    def __init__(self, x, y, length, width, key_up, key_down, key_left, key_right):
        self.x = x
        self.y = y
        self.length = length
        self.width = width
        self.key_up = key_up
        self.key_down = key_down
        self.key_left = key_left
        self.key_right = key_right
        self.load_image()
    
    def load_image(self):
        #Load the pac man image
        try:
            self.image = pg.image.load(join("pictures/Pacman.png")).convert_alpha()
            self.image = pg.transform.scale(self.image, (self.length, self.width))
        except pg.error:
            # for a reason if the picture fail tp load, make a yellow circle
            self.image = pg.Surface((self.length, self.width), pg.SRCALPHA)
            pg.draw.circle(self.image, (255, 255, 0), (self.length//2, self.width//2), self.length//2)
    
    
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def movePacman(self, button):
        #Move the player using direction
        speed = 1  # Movement speed
        
        if button[self.key_up]:
            self.y -= speed
        elif button[self.key_down]:
            self.y += speed
        elif button[self.key_left]:
            self.x -= speed
        elif button[self.key_right]:
            self.x += speed

    def check_teleportation(self, window_height, window_width, gap_y, grid_blockSize):
        # Check if Pacman is in the gap area first
        if abs(self.y - gap_y) < grid_blockSize:
            # Check if Pacman completely left the left side (including its width)
            if self.x + self.length < 0:
                self.x = window_width - grid_blockSize
                return True
            # Check if Pacman completely left the right side
            elif self.x > window_width:
                self.x = 0
                return True
        
        return False


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

class Grid:
    def __init__(self, x, y, height, width, blockSize):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.blockSize = blockSize
        # Animation counter for rainbow cycling
        self.animation_counter = 0
    
    def get_rainbow_color(self):
        # Calculate hue for rainbow effect (0-360 degrees)
        # Divide by 60 to make it cycle every 1 second (at 60 FPS)
        hue = (self.animation_counter // 60) % 360
        
        # Create color using HSV (Hue, Saturation, Value)
        color = pg.Color(0)
        color.hsva = (hue, 100, 80, 100)  # Full saturation, 80% brightness
        return (color.r, color.g, color.b)
    
    def update_animation(self):
        # Increment animation counter each frame
        self.animation_counter += 1
    
    def drawGrid(self, screen):
        screen.fill((20, 20, 40))  # Dark blue-gray background
        
        # Draw vertical lines
        for i in range(0, self.width + 1, self.blockSize):
            pg.draw.line(screen, (50, 50, 50), (i, 0), (i, self.height), 1)
        
        # Draw horizontal lines
        for i in range(0, self.height + 1, self.blockSize):
            pg.draw.line(screen, (50, 50, 50), (0, i), (self.width, i), 1)
    

class SpawnRoom:
    def __init__(self, x, y, height, width):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.color = (0, 255, 255)
    
    def drawRoom(self, screen):
        pg.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height ))
    
    def create_spawn_walls(self, grid_blockSize):
        walls = []
        
        # Calculate gap position dynamically (center of room)
        gap_x = self.x + (self.width // 2 // grid_blockSize) * grid_blockSize
        
        # Top and bottom walls in same loop
        for x in range(self.x, self.x + self.width, grid_blockSize):
            # Top wall (skip gap block)
            if x != gap_x:
                walls.append(Wall(x, self.y, grid_blockSize, grid_blockSize))
            # Bottom wall (complete, no gap)
            walls.append(Wall(x, self.y + self.height - grid_blockSize, grid_blockSize, grid_blockSize))
        
        # Left and right walls in same loop
        for y in range(self.y, self.y + self.height, grid_blockSize):
            # Left wall
            walls.append(Wall(self.x, y, grid_blockSize, grid_blockSize))
            # Right wall (fixed positioning)
            walls.append(Wall(self.x + self.width - grid_blockSize, y, grid_blockSize, grid_blockSize))
        
        return walls



# display title
pg.display.set_caption("Pacman Game")
# Create Grid
grid = Grid(0, 0, VINDU_HOYDE, VINDU_BREDDE, 40)
# Create Pacman
pacman = Pacman(400, 300, grid.blockSize, grid.blockSize, K_UP, K_DOWN, K_LEFT, K_RIGHT)
# Create spawn room (grid-aligned)
spawnRoom = SpawnRoom(grid.blockSize * 5, grid.blockSize * 5, grid.blockSize * 4, grid.blockSize * 5)

# Create border walls using the Wall class method
wall_generator = Wall(0, 0, 0, 0)  # Temporary instance
wall = wall_generator.border_wall(VINDU_BREDDE, VINDU_HOYDE, grid.blockSize)

# Add spawn room walls
spawn_walls = spawnRoom.create_spawn_walls(grid.blockSize)
wall.extend(spawn_walls)

# You already have a wall_generator instance
test_corridor = wall_generator.create_corridor(
    start_x=grid.blockSize * 15, 
    start_y=grid.blockSize * 8, 
    length=grid.blockSize * 6, 
    direction='vertical', 
    grid_blockSize=grid.blockSize
)



wall.extend(test_corridor)

l_test = wall_generator.create_l_corridor(
    corner_x=grid.blockSize * 20,
    corner_y=grid.blockSize * 5, 
    h_length=grid.blockSize * 3,
    v_length=grid.blockSize * 3,
    grid_blockSize=grid.blockSize,
    opening_direction= 'left_up'
)
wall.extend(l_test)

continue_game = True
while continue_game:
    clock.tick()
    
    # Update animation counter in Grid class
    grid.update_animation()
    
    # Calculate current rainbow color from Grid class
    current_rainbow_color = grid.get_rainbow_color()
    
    for event in pg.event.get():
        if event.type == pg.QUIT:
            continue_game = False

    # Store old position BEFORE moving
    old_x = pacman.x
    old_y = pacman.y

    # check if a button is pressed and move
    button_pressed = pg.key.get_pressed()
    pacman.movePacman(button_pressed)

    # Check collision AFTER moving
    for single_wall in wall:
        if single_wall.check_wall_collision(pacman):
            pacman.x = old_x
            pacman.y = old_y
            break

    # Check for teleportation (calculate gap_y same way as in border_wall method)
    gap_y = (VINDU_HOYDE // 2 // grid.blockSize) * grid.blockSize
    pacman.check_teleportation(VINDU_HOYDE, VINDU_BREDDE, gap_y, grid.blockSize)

    # Draw grid first (background)
    grid.drawGrid(vindu)
    # Draw spawn room
    spawnRoom.drawRoom(vindu)
    # Draw multiple walls with rainbow colors and smart borders
    for single_wall in wall:
        single_wall.draw_wall(vindu, wall, current_rainbow_color)

    # Draw Pacman on top of grid
    pacman.draw(vindu)
    
    # Update everything here
    pg.display.flip() 

pg.quit()