import pygame as pg
from pygame.locals import (K_UP, K_DOWN, K_LEFT, K_RIGHT, K_w, K_s, K_a, K_d)
from classes.pacman import Pacman
from classes.enemy import Enemy
from classes.wall import Wall
from classes.grid import Grid
from classes.spawnroom import SpawnRoom
from classes.food import Food
from classes.powerpellet import PowerPellet

# Initialize the game
pg.init()

VINDU_BREDDE = 1000
VINDU_HOYDE = 600
vindu = pg.display.set_mode([VINDU_BREDDE, VINDU_HOYDE])
dt = 0
clock = pg.time.Clock()

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
# Create Enemies (add weak_image_path argument)
red_ghost = Enemy(grid.blockSize * 10, grid.blockSize * 12 , grid.blockSize, grid.blockSize, "pictures/enemy_red.png", (255, 0, 0), "pictures/eaten_ghost.png")
green_ghost = Enemy(grid.blockSize * 5, grid.blockSize * 14 , grid.blockSize, grid.blockSize, "pictures/enemy_green.png", (255, 184, 255), "pictures/eaten_ghost.png")
blue_ghost = Enemy(grid.blockSize * 15 , grid.blockSize * 3, grid.blockSize, grid.blockSize, "pictures/enemy_blue.png",(0, 255, 255), "pictures/eaten_ghost.png")
orange_ghost = Enemy(grid.blockSize * 18, grid.blockSize * 7, grid.blockSize, grid.blockSize, "pictures/enemy_orange.png", (255, 184, 82), "pictures/eaten_ghost.png")
enemies = [red_ghost, green_ghost, blue_ghost, orange_ghost]
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
    # The game runs in 60 fps
    clock.tick(60)
    
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
    red_ghost.chase_towards_pacman(pacman, grid, wall)
    red_ghost.moveEnemy(grid.blockSize,  wall)
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
            # power mode is active and enemies goes slower 600 / 60 fps = 10 seconds slow
            pacman.activate_power_mode(600)  
            for enemy in enemies:
                enemy.movement_speed = 2
            # No need to set images here, handled in draw_enemy

    #Remove eaten power pellet from the list
    for powerPellet_to_remove in powerPellets_to_remove:
        all_power_pellets.remove(powerPellet_to_remove)

    # Checks when the power mode is active and decreases the timer
    if pacman.power_mode_active:
        pacman.power_mode_timer -= 1
        if pacman.power_mode_timer <= 0:
            # When the timer runs out, the enemies go to normal speed
            pacman.power_mode_active = False
            for enemy in enemies:
                enemy.movement_speed = 4

    # End the game if the pacman touches one of the ghost
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
    for enemy in enemies:
        enemy.draw_enemy(vindu, pacman.power_mode_active)
    
    # Update everything here
    pg.display.flip() 

pg.quit()