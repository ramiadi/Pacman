import pygame as pg
from classes.wall import Wall

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