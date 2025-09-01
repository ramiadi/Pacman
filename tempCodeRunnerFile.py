if enemy.is_retreating:
            enemy.retreat_enemy_to_spawnRoom(spawn_target_x, spawn_target_y, grid, wall, pacman.power_mode_active, spawnRoom)
        elif hasattr(enemy, "leaving_spawn") and enemy.leaving_spawn:
            enemy.leave_spawnroom(spawnRoom, grid.blockSize, wall)
        else:
            if enemy == red_ghost:
                enemy.chase_towards_pacman(pacman, grid, wall)
        enemy.moveEnemy(grid.blockSize, wall)