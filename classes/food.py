import pygame as pg

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
