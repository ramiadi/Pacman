import pygame as pg
from os.path import join

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