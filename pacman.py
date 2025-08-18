import pygame as pg
from pygame.locals import (K_UP, K_DOWN, K_LEFT, K_RIGHT, K_w, K_s, K_a, K_d)
from os.path import join
import random

# Initialize the game
pg.init()

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

        self.target_x = x
        self.target_y = y
        self.is_moving = False
        self.movement_speed = 1

    def load_image(self):
        #Load the pac man image
        try:
            self.image = pg.image.load(join("pictures/Pacman.png")).convert_alpha()
            self.image = pg.transform.scale(self.image, (self.length, self.width))
        except Exception as e:
            # for a reason if the picture fail to load, make a yellow circle
            print(f"Pac man image loading failed: {e}")
            self.image = pg.Surface((self.length, self.width), pg.SRCALPHA)
            pg.draw.circle(self.image, (255, 255, 0), (self.length//2, self.width//2), self.length//2)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def movePacman(self, button, grid_blockSize, wall_list):
        
        if self.is_moving:
            # Calculate remaining distance to target
            distance_x = self.target_x - self.x
            distance_y = self.target_y - self.y

            # === X-AXIS MOVEMENT ===
            if abs(distance_x) > self.movement_speed:
                # Far from target - move at full speed
                if distance_x > 0:
                    self.x += self.movement_speed  # Move right
                else:
                    self.x -= self.movement_speed  # Move left
            elif distance_x != 0:
                # Close to target - snap to exact position
                self.x = self.target_x
            
            # === Y-AXIS MOVEMENT ===
            if abs(distance_y) > self.movement_speed:
                # Far from target - move at full speed
                if distance_y > 0:
                    self.y += self.movement_speed  # Move down
                else:
                    self.y -= self.movement_speed  # Move up
            elif distance_y != 0:
                # Close to target - snap to exact position
                self.y = self.target_y

            # Check if movement is complete
            if self.x == self.target_x and self.y == self.target_y:
                self.is_moving = False    

        else:
            # === INPUT HANDLING ===
            new_target_x = self.x
            new_target_y = self.y

            # Check for directional input
            if button[self.key_up]:
                new_target_y -= grid_blockSize
            elif button[self.key_down]:
                new_target_y += grid_blockSize
            elif button[self.key_left]:
                 new_target_x -= grid_blockSize
            elif button[self.key_right]:
                new_target_x += grid_blockSize

            # Only start movement if targets actually changed
            if new_target_x != self.x or new_target_y != self.y:
                has_wall = False
                for wall in wall_list:
                    if wall.x == new_target_x and wall.y == new_target_y:
                        has_wall = True
                        break
                if not has_wall:
                    self.target_x = new_target_x
                    self.target_y = new_target_y
                    self.is_moving = True

    def check_teleportation(self, window_height, window_width, gap_y, grid_blockSize):
        # Check if Pacman is in the gap area first
        if abs(self.y - gap_y) < grid_blockSize:
            # Check if Pacman completely left the left side (including its width)
            if self.x + self.length <= 0:
                self.x = window_width - grid_blockSize
                self.target_x = window_width - grid_blockSize
                return True
            # Check if Pacman completely left the right side
            elif self.x >= window_width:
                self.x = 0
                self.target_x = 0
                return True
        
        return False

class Enemy(pg.sprite.Sprite):
    def __init__(self, x, y, length, width, image_path, fallback_color):
        super().__init__()
        self.x = x
        self.y = y
        self.length = length
        self.width = width
        self.image_path = image_path
        self.fallback_color = fallback_color
        self.load_enemy_image()

        self.target_x = x
        self.target_y = y
        self.is_moving = False
        self.movement_speed = 0.8
        self.directions = ["up", "down", "left", "right"]
        self.current_direction = random.choice(self.directions)

    def load_enemy_image(self):
        try:
            self.image = pg.image.load(join(self.image_path)).convert_alpha()
            self.image = pg.transform.scale(self.image, (self.length, self.width))
        except pg.error:
            self.image = pg.Surface((self.length, self.width), pg.SRCALPHA)
            pg.draw.circle(self.image, (self.fallback_color), (self.length // 2, self.width // 2), self.length // 2)

    def draw_enemy(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def calculate_target(self, direction, grid_blockSize):
        new_target_x = self.x
        new_target_y = self.y
        
        if direction == "up":
            new_target_y -= grid_blockSize
        elif direction == "down":
            new_target_y += grid_blockSize
        elif direction == "left":
            new_target_x -= grid_blockSize
        elif direction == "right":
            new_target_x += grid_blockSize
        
        return new_target_x, new_target_y

    def has_wall_at(self, x, y, wall_list):
        # Check if position is out of bounds
        if x < 0 or y < 0 or x >= 1000 or y >= 600:
            return True
            
        for wall in wall_list:
            if wall.x == x and wall.y == y:
                return True
        return False

    def find_valid_direction(self, grid_blockSize, wall_list):
        # Try current direction first
        new_target_x, new_target_y = self.calculate_target(self.current_direction, grid_blockSize)
  
        if not self.has_wall_at(new_target_x, new_target_y, wall_list):
            return self.current_direction, new_target_x, new_target_y
        
        # Current direction is blocked, try all other directions
        available_directions = []
        
        for direction in self.directions:
            if direction != self.current_direction:
                test_x, test_y = self.calculate_target(direction, grid_blockSize)
                if not self.has_wall_at(test_x, test_y, wall_list):
                    available_directions.append((direction, test_x, test_y))
    
        # If we have valid directions, pick one randomly for variety
        if available_directions:
            chosen_direction = random.choice(available_directions)
            return chosen_direction[0], chosen_direction[1], chosen_direction[2]
        # If completely surrounded, return None to indicate no valid move
        return None, self.x, self.y

    def moveEnemy(self, grid_blockSize, wall_list):
        if self.is_moving:
            distance_x = self.target_x - self.x
            distance_y = self.target_y - self.y

            # X-axis movement
            if abs(distance_x) > self.movement_speed:
                if distance_x > 0:
                    self.x += self.movement_speed
                else:
                    self.x -= self.movement_speed
            elif distance_x != 0:
                self.x = self.target_x

            # Y-axis movement
            if abs(distance_y) > self.movement_speed:
                if distance_y > 0:
                    self.y += self.movement_speed
                else:
                    self.y -= self.movement_speed
            elif distance_y != 0:
                self.y = self.target_y

            # Check if movement is complete
            if self.x == self.target_x and self.y == self.target_y:
                self.is_moving = False
        else:
            # Find a valid direction and move
            valid_direction, target_x, target_y = self.find_valid_direction(grid_blockSize, wall_list)
            
            # Only move if we found a valid direction
            if valid_direction is not None:
                self.current_direction = valid_direction
                self.target_x = target_x
                self.target_y = target_y
                self.is_moving = True
            # If no valid direction found, stay put and try a different direction next frame
            else:
                self.current_direction = random.choice(self.directions)
    
    def check_collision_pacman_enemy(self, pacman):
        enemy_rect = pg.Rect(self.x + self.length // 4, self.y + self.width // 4, self.length // 2, self.width // 2)
        pacman_rect = pg.Rect(pacman.x + pacman.length // 4, pacman.y + pacman.width // 4, pacman.length // 2, pacman.width // 2)
        return enemy_rect.colliderect(pacman_rect)


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

class Food:
    def __init__(self, x, y, length, width):
        self.x = x
        self.y = y
        self.length = length
        self.width = width
    
    def draw(self, screen, grid_blockSize):
        pg.draw.circle(screen, (219, 219, 107), (self.x + self.length // 2, self.y + self.width // 2), grid_blockSize // 8)

    def create_food_everywhere(self, window_height, window_width, grid_blockSize, wall_list, spawn_room):
        foods = []

        for x in range(0, window_width, grid_blockSize):
            for y in range(0, window_height, grid_blockSize):
                has_wall = False
                in_spawn_room = False
                
                # Check if there's a wall at this position
                for wall in wall_list:
                    if wall.x == x and wall.y == y:
                        has_wall = True
                        break
                
                # Check if this position is inside the spawn room area
                if (spawn_room.x <= x < spawn_room.x + spawn_room.width and 
                    spawn_room.y <= y < spawn_room.y + spawn_room.height):
                    in_spawn_room = True
                
                # Only create food if there's no wall AND not in spawn room
                if not has_wall and not in_spawn_room:
                    food = Food(x, y, grid_blockSize, grid_blockSize)
                    foods.append(food)
        return foods
    
    def check_pacman_collision(self, pacman):
        # Create smaller collision rectangles for more precise collision
        food_rect = pg.Rect(self.x + self.length//4, self.y + self.width//4, self.length//2, self.width//2)
        pacman_rect = pg.Rect(pacman.x , pacman.y , pacman.length, pacman.width)
        return food_rect.colliderect(pacman_rect)


class PowerPellet:
    def __init__(self, x, y, length, width):
        self.x = x
        self.y = y 
        self.length = length
        self.width = width
        self.load_image()

    def load_image(self):
        #Load the pac man image
        try:
            self.image = pg.image.load(join("pictures/food-icon.png")).convert_alpha()
            self.image = pg.transform.scale(self.image, (self.length, self.width))
        except Exception as e:  # Catch ANY exception
            print(f"PowerPellet image loading failed: {e}")
            # Create white circle fallback
            self.image = pg.Surface((self.length, self.width), pg.SRCALPHA)
            pg.draw.circle(self.image, (255, 255, 255), (self.length//2, self.width//2), self.length//4)
    
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def check_pacman_collision(self, pacman):
        # Create smaller collision rectangles for more precise collision
        power_rect = pg.Rect(self.x + self.length//4, self.y + self.width//4, self.length//2, self.width//2)
        pacman_rect = pg.Rect(pacman.x , pacman.y , pacman.length, pacman.width)
        return power_rect.colliderect(pacman_rect)

    def make_multiple_power_pellets(self, positions, grid_blockSize):
        powerPellet_list = []
        for pos_x, pos_y in positions:
            powerPellet = PowerPellet(pos_x, pos_y, grid_blockSize, grid_blockSize)
            powerPellet_list.append(powerPellet)
        return powerPellet_list
    
    def check_overlap_between_powerPellets_and_food_to_remove(self, power_pellets, foods):
        food_to_remove = []
        for power_pellet in power_pellets:
            for food in foods:
                if power_pellet.x == food.x and power_pellet.y == food.y:
                    food_to_remove.append(food)
        return food_to_remove


# display title
pg.display.set_caption("Pacman Game")
# Create Grid
grid = Grid(0, 0, VINDU_HOYDE, VINDU_BREDDE, 40)
# Create Pacman
pacman = Pacman(400, 320, grid.blockSize, grid.blockSize, K_UP, K_DOWN, K_LEFT, K_RIGHT)
# Create spawn room (grid-aligned)
spawnRoom = SpawnRoom(grid.blockSize * 5, grid.blockSize * 5, grid.blockSize * 4, grid.blockSize * 5)
# Create food
food = Food(40, 50, 200, 200)
# Create Enemies
red_ghost = Enemy(grid.blockSize * 10, grid.blockSize * 12 , grid.blockSize, grid.blockSize, "pictures/enemy_red.png", (255, 0, 0))
green_ghost = Enemy(grid.blockSize * 5, grid.blockSize * 14 , grid.blockSize, grid.blockSize, "pictures/enemy_green.png", (255, 184, 255))
blue_ghost = Enemy(grid.blockSize * 15 , grid.blockSize * 3, grid.blockSize, grid.blockSize, "pictures/enemy_blue.png",(0, 255, 255))
orange_ghost = Enemy(grid.blockSize * 18, grid.blockSize * 7, grid.blockSize, grid.blockSize, "pictures/enemy_orange.png", (255, 184, 82))

# Create border walls using the Wall class method
wall_generator = Wall(0, 0, 0, 0)  # Temporary instance
wall = wall_generator.border_wall(VINDU_BREDDE, VINDU_HOYDE, grid.blockSize)

# Add spawn room walls
spawn_walls = spawnRoom.create_spawn_walls(grid.blockSize)
wall.extend(spawn_walls)

wall_gap_corridor_right = wall_generator.create_corridor(
    start_x=grid.blockSize * 23,
    start_y= grid.blockSize * 7,
    length=grid.blockSize * 1,
    direction='horizontal',
    grid_blockSize=grid.blockSize
)
wall.extend(wall_gap_corridor_right)

wall_gap_corridor_left = wall_generator.create_corridor(
    start_x=grid.blockSize * 1,
    start_y= grid.blockSize * 7,
    length=grid.blockSize * 1,
    direction='horizontal',
    grid_blockSize=grid.blockSize
)
wall.extend(wall_gap_corridor_left)

l_test = wall_generator.create_l_corridor(
    corner_x=grid.blockSize * 2,
    corner_y=grid.blockSize * 9, 
    h_length=grid.blockSize * 1,
    v_length=grid.blockSize * 2,
    grid_blockSize=grid.blockSize,
    opening_direction= 'left_up'
)
wall.extend(l_test)

# Create all food pellets everywhere (after all walls are created)
food_generator = Food(0, 0, 0, 0)  # Temporary instance for generation
all_foods = food_generator.create_food_everywhere(VINDU_HOYDE, VINDU_BREDDE, grid.blockSize, wall, spawnRoom)

# Create power pellets. 6 fixed positions
power_pellet_positions = [
    (80, 80),
    (880, 80),
    (80, 480),
    (880, 480),
    (80, 280),
    (880, 280)
]
powerPellet_generator = PowerPellet(0,0,0,0)
all_power_pellets = powerPellet_generator.make_multiple_power_pellets(power_pellet_positions, grid.blockSize)

# After creating all_food and all_power_pellets
overlapping_food = powerPellet_generator.check_overlap_between_powerPellets_and_food_to_remove(all_power_pellets, all_foods)

# Remove overlapping food AFTER creating both food and power pellets
for food_to_remove in overlapping_food:
    all_foods.remove(food_to_remove)

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

    # check if a button is pressed and move
    button_pressed = pg.key.get_pressed()
    pacman.movePacman(button_pressed, grid.blockSize, wall)
    red_ghost.moveEnemy(grid.blockSize, wall)
    green_ghost.moveEnemy(grid.blockSize, wall)
    blue_ghost.moveEnemy(grid.blockSize, wall)
    orange_ghost.moveEnemy(grid.blockSize, wall)

    # Check food collision and remove eaten food
    foods_to_remove = []
    for single_food in all_foods:
        if single_food.check_pacman_collision(pacman):
            foods_to_remove.append(single_food)
    
    # Remove eaten food from the list
    for food_to_remove in foods_to_remove:
        all_foods.remove(food_to_remove)

    # Check power pellet collision and remove eaten food
    powerPellets_to_remove = []
    for single_pellet in all_power_pellets:
        if single_pellet.check_pacman_collision(pacman):
            powerPellets_to_remove.append(single_pellet)    

    #Remove eaten power pellet from the list
    for powerPellet_to_remove in powerPellets_to_remove:
        all_power_pellets.remove(powerPellet_to_remove)

    # End the game if the pacman touches one of the ghost
    enemies = [red_ghost, green_ghost, blue_ghost, orange_ghost]
    for enemy in enemies:
        if enemy.check_collision_pacman_enemy(pacman):
            continue_game = False

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

    # Draw all food pellets
    for single_food in all_foods:
        single_food.draw(vindu, grid.blockSize)

   # Draw Multiple power pellets
    for single_power_pellet in all_power_pellets:
        single_power_pellet.draw(vindu)

    # Draw Pacman on top of grid
    pacman.draw(vindu)

    # Draw Enemies
    red_ghost.draw_enemy(vindu)
    green_ghost.draw_enemy(vindu)
    blue_ghost.draw_enemy(vindu)
    orange_ghost.draw_enemy(vindu)
    
    # Update everything here
    pg.display.flip() 

pg.quit()