import pygame as pg
from os.path import join

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
        self.movement_speed = 5
        self.power_mode_active = False
        self.power_mode_timer = 0

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
    
    def activate_power_mode(self, duration):
        self.power_mode_active = True
        self.power_mode_timer = duration