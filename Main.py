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
pause_timer = 0
pause_duration = 60 # 1 second at 60 fps

# display title
pg.display.set_caption("Pacman Game")

# Create Grid
grid = Grid(0, 0, VINDU_HOYDE, VINDU_BREDDE, 40)

# Create Pacman
pacman = Pacman(400, 320, grid.blockSize, grid.blockSize, K_UP, K_DOWN, K_LEFT, K_RIGHT)

# Create spawn room (grid-aligned)
spawnRoom = SpawnRoom(grid.blockSize * 5, grid.blockSize * 5, grid.blockSize * 4, grid.blockSize * 5)
spawn_target_x = spawnRoom.x + (spawnRoom.width // 2 // grid.blockSize) * grid.blockSize
spawn_target_y = spawnRoom.y + (spawnRoom.height // 2 // grid.blockSize) * grid.blockSize

# Create food
food = Food(40, 50, 200, 200)

# Create Enemies (add weak_image_path argument)
red_ghost = Enemy(grid.blockSize * 10, grid.blockSize * 12 , grid.blockSize, grid.blockSize, "pictures/enemy_red.png", (255, 0, 0), "pictures/eaten_ghost.png", "pictures/enemy_eyes.png")
green_ghost = Enemy(grid.blockSize * 5, grid.blockSize * 14 , grid.blockSize, grid.blockSize, "pictures/enemy_green.png", (255, 184, 255), "pictures/eaten_ghost.png", "pictures/enemy_eyes.png")
blue_ghost = Enemy(grid.blockSize * 15 , grid.blockSize * 3, grid.blockSize, grid.blockSize, "pictures/enemy_blue.png",(0, 255, 255), "pictures/eaten_ghost.png", "pictures/enemy_eyes.png")
orange_ghost = Enemy(grid.blockSize * 18, grid.blockSize * 7, grid.blockSize, grid.blockSize, "pictures/enemy_orange.png", (255, 184, 82), "pictures/eaten_ghost.png", "pictures/enemy_eyes.png")
enemies = [red_ghost, green_ghost, blue_ghost, orange_ghost]

# Create border walls using the Wall class method
wall_generator = Wall(0, 0, 0, 0)  # Temporary instance
wall = wall_generator.border_wall(VINDU_BREDDE, VINDU_HOYDE, grid.blockSize)

# Add spawn room walls
spawn_walls = spawnRoom.create_spawn_walls(grid.blockSize)
wall.extend(spawn_walls)

# Alternative: Maze layout using grid + for-loop
# 1 = wall, 0 = empty
maze_layout = [
    "000000000000000000000000",  # row 0 -> border already handled
    "000000000100000000000000",  # row 1
    "001001101110110011110110",  # row 2 -> internal walls
    "001101000010011000100100",  # row 3
    "001100000000001010101101",  # row 4
    "000000000000100010101000",  # row 5
    "000110000000111110000010",  # row 6
    "000000000010010000111000",  # row 7
    "001100000000010111100010",  # row 8
    "001100000000000000001110",  # row 9
    "000001110110010101000000",  # row 10
    "001100000100110111100110",  # row 11
    "000110111110100000111100",  # row 12
    "000000000000001110000000",  # row 13
    "000000000000000000000000"   # row 14 -> border already handled
]
# Build walls from the layout
for row, line in enumerate(maze_layout):
    for col, char in enumerate(line):
        if char == "1":
            wall_piece = wall_generator.create_single_wall_line(
                start_x=col * grid.blockSize,
                start_y=row * grid.blockSize,
                length=1,   # just one block
                grid_blockSize=grid.blockSize
            )
            wall.extend(wall_piece)

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

    if pause_timer > 0:
        pause_timer -= 1
        for event in pg.event.get():
            if event.type == pg.QUIT:
                continue_game = False
        pg.display.flip()
        continue

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
    for enemy in enemies:
        if enemy.is_retreating:
            enemy.retreat_enemy_to_spawnRoom(spawn_target_x, spawn_target_y, grid, wall)
            # Check if enemy is inside the spawn room
            if (spawnRoom.x <= enemy.x < spawnRoom.x + spawnRoom.width and
                spawnRoom.y <= enemy.y < spawnRoom.y + spawnRoom.height):
                enemy.movement_enemy_speed(4)  # Reset speed to normal
                enemy.is_retreating = False
                enemy.is_weak = False
                enemy.just_eaten = False
        elif enemy.leaving_spawn:
            # Spawnroom gap at top center
            spawn_gap_x = spawnRoom.x + (spawnRoom.width // 2 // grid.blockSize) * grid.blockSize
            spawn_gap_y = spawnRoom.y  # Top edge
            enemy.leave_spawn((spawn_gap_x, spawn_gap_y), grid, wall)
            # If ghost reached the gap, smoothly move it outside
            if enemy.x == spawn_gap_x and enemy.y == spawn_gap_y:
                # Set next movement target to one block above the gap
                enemy.target_x = spawn_gap_x
                enemy.target_y = spawn_gap_y - grid.blockSize
                enemy.is_moving = True
                enemy.leaving_spawn = False
            
        else:
            # if enemy == red_ghost:
            #     enemy.chase_towards_pacman(pacman, grid, wall)
            enemy.moveEnemy(grid.blockSize, wall)

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
                enemy.movement_enemy_speed(2)
                enemy.is_weak = True
            # No need to set images here, handled in draw_enemy

    #Remove eaten power pellet from the list
    for powerPellet_to_remove in powerPellets_to_remove:
        all_power_pellets.remove(powerPellet_to_remove)

    # Checks when the power mode is active and decreases the timer
    if pacman.power_mode_active:
        pacman.power_mode_timer -= 1
        if pacman.power_mode_timer <= 0:
            pacman.power_mode_active = False
            # When the timer runs out, the enemies go to normal speed
            pacman.power_mode_active = False
            for enemy in enemies:
                enemy.movement_enemy_speed(4)
                enemy.is_weak = False

    # End the game if the pacman touches one of the ghost
    for enemy in enemies:
        if enemy.check_collision_pacman_enemy(pacman):
            if pacman.power_mode_active and enemy.is_weak and not enemy.just_eaten:
                enemy.is_retreating = True
                enemy.movement_enemy_speed(8)
                enemy.just_eaten = True
                if pause_timer == 0:  # Only set the pause if not already paused
                    pause_timer = pause_duration
            elif not (pacman.power_mode_active and enemy.is_weak):
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
        enemy.draw_enemy(vindu)
    
    # After drawing enemies, check if any normal ghost is stuck in spawn room and not already leaving
    for enemy in enemies:
        if not enemy.is_retreating and not enemy.leaving_spawn:
            # Check if ghost is inside spawn room (excluding the gap/door)
            if (spawnRoom.x <= enemy.x < spawnRoom.x + spawnRoom.width and
                spawnRoom.y <= enemy.y < spawnRoom.y + spawnRoom.height):
                enemy.leaving_spawn = True

    # Update everything here
    pg.display.flip() 

pg.quit()