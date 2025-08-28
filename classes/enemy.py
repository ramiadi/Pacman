import pygame as pg
import random
from os.path import join

class Enemy(pg.sprite.Sprite):
    def __init__(self, x, y, length, width, image_path, fallback_color, weak_image_path=None):
        super().__init__()
        self.x = x
        self.y = y
        self.length = length
        self.width = width
        self.image_path = image_path
        self.fallback_color = fallback_color
        self.weak_image_path = weak_image_path if weak_image_path else "pictures/eaten_ghost.png"
        # Load both images at init
        self.normal_image = self.load_enemy_image(self.image_path, self.fallback_color)
        self.weak_image = self.load_enemy_image(self.weak_image_path, (0, 0, 139))
        self.target_x = x
        self.target_y = y
        self.is_moving = False
        self.movement_speed = 4
        self.directions = ["up", "down", "left", "right"]
        self.current_direction = random.choice(self.directions)

    def load_enemy_image(self, path, color):
        try:
            image = pg.image.load(join(path)).convert_alpha()
            image = pg.transform.scale(image, (self.length, self.width))
        except Exception as e:
            print(f"Enemy image loading failed ({path}): {e}")
            image = pg.Surface((self.length, self.width), pg.SRCALPHA)
            pg.draw.circle(image, color, (self.length // 2, self.width // 2), self.length // 2)
        return image

    def draw_enemy(self, screen, is_weak):
        img = self.weak_image if is_weak else self.normal_image
        screen.blit(img, (self.x, self.y))

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
    
    def chase_towards_pacman(self, pacman, grid_blockSize, wall_list):
        ghost_grid_x = self.x // grid_blockSize
        ghost_grid_y = self.y // grid_blockSize
        pacman_grid_x = pacman.x // grid_blockSize
        pacman_grid_y = pacman.y // grid_blockSize

        if self.x % grid_blockSize == 0 and self.y % grid_blockSize == 0:
            directions = []
            if ghost_grid_x < pacman_grid_x:
                directions.append("right")
            elif ghost_grid_x > pacman_grid_x:
                directions.append("left")
            if ghost_grid_y < pacman_grid_y:
                directions.append("down")
            elif ghost_grid_y > pacman_grid_y:
                directions.append("up")
                
            for direction in directions:
                next_x, next_y = self.calculate_target(direction, grid_blockSize)
                if not self.has_wall_at(next_x, next_y, wall_list):
                    self.target_x = next_x
                    self.target_y = next_y
                    self.is_moving = True
                    self.current_direction = direction
                    return
