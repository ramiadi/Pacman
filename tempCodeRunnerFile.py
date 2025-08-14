def find_valid_direction(self, grid_blockSize, wall_list):
        """Find a valid direction that doesn't hit a wall"""
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
    
        # If completely surrounded, force movement anyway (emergency escape)
        # Pick a random direction and move, even if blocked
        emergency_direction = random.choice(self.directions)
        emergency_x, emergency_y = self.calculate_target(emergency_direction, grid_blockSize)
        return emergency_direction, emergency_x, emergency_y