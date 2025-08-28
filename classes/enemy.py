import pygame as pg
import random
import heapq
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
    
    def chase_towards_pacman(self, pacman, grid, wall_list):
        # Get grid size (in cells)
        grid_blockSize = grid.blockSize
        grid_width = grid.width // grid_blockSize  # Or use grid.width // grid.blockSize if you pass grid
        grid_height = grid.height // grid_blockSize  # Or use grid.height // grid.blockSize if you pass grid

        ghost_grid = (self.x // grid_blockSize, self.y // grid_blockSize)
        pacman_grid = (pacman.x // grid_blockSize, pacman.y // grid_blockSize)
        if ghost_grid == pacman_grid:
            return  # Already at Pacman

        # Find path
        path = self.a_star_pathfind(ghost_grid, pacman_grid, wall_list, grid_blockSize, grid_width, grid_height)
        if path:
            next_cell = path[0]  # First step
            self.target_x = next_cell[0] * grid_blockSize
            self.target_y = next_cell[1] * grid_blockSize
            self.is_moving = True
    
    # Every line under, is almost a copy of this website: https://www.geeksforgeeks.org/dsa/a-search-algorithm/
    @staticmethod
    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def a_star_pathfind(self, start, goal, wall_list, grid_blockSize, grid_width, grid_height):
        wall_cells = set((wall.x // grid_blockSize, wall.y // grid_blockSize) for wall in wall_list)
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.manhattan(start, goal)}

        while open_set:
            _, current = heapq.heappop(open_set)
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path
            
            neighbors = []
            
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = current[0] + dx, current[1] + dy
                if 0 <= nx < grid_width and 0 <= ny < grid_height:
                    if (nx, ny) not in wall_cells:
                        neighbors.append((nx, ny))

            for neighbor in neighbors:
                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.manhattan(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return []
