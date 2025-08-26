import pygame as pg

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
    