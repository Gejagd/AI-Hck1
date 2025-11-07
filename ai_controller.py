import random
import math
import numpy as np
from entities import DroneState
from data_collector import DataCollector
from ai_learner import DroneAI

class AIController:
    def __init__(self, training_mode=True):
        self.explored = set()
        self.survivor_locations = set()
        self.training_mode = training_mode
        
        # Initialize AI components
        self.ai_learner = DroneAI()
        self.data_collector = DataCollector()
        
        # Load pre-trained model if available
        try:
            self.ai_learner.load_model()
            print("Model AI berhasil dimuat!")
        except:
            print("Tidak ada model yang ditemukan, memulai training baru...")
        
    def update_drone(self, drone, grid_width, grid_height, other_drones, survivors, episode_done=False):
        """Update drone's state and position based on AI logic"""
        if drone.battery <= 0:
            return False, 0
            
        # Handle RETURNING state (returning to base)
        if drone.state == DroneState.RETURNING:
            # Check if reached base (within 2 cells)
            if abs(drone.x - (grid_width // 2)) <= 2 and abs(drone.y - (grid_height // 2)) <= 2:
                drone.state = DroneState.EXPLORING
                drone.has_payload = True
                drone.survivor = None
                print(f"\n=== Drone {drone.id} returned to base and is ready for new mission ===\n")
                return True, 10  # Reward for successful return
                
            # Move towards base
            dx = 1 if (grid_width // 2) > drone.x else (-1 if (grid_width // 2) < drone.x else 0)
            dy = 1 if (grid_height // 2) > drone.y else (-1 if (grid_height // 2) < drone.y else 0)
            
            # Move if not at base
            if dx != 0 or dy != 0:
                new_x = drone.x + dx
                new_y = drone.y + dy
                
                # Ensure within bounds and no collision
                if (0 <= new_x < grid_width and 
                    0 <= new_y < grid_height and 
                    not any(d.x == new_x and d.y == new_y for d in other_drones)):
                    drone.x, drone.y = new_x, new_y
                    return True, 0.1  # Small reward for moving towards base
            return False, 0
            
        other_drones = [d for d in other_drones if d is not drone and d.battery > 0]
        
        # Initialize drone movement properties if they don't exist
        if not hasattr(drone, 'move_counter'):
            drone.move_counter = 0
            drone.move_direction = random.choice([0, 1, 2, 3])  # 0: up, 1: right, 2: down, 3: left
            drone.steps_in_direction = 0
            drone.max_steps = random.randint(5, 15)  # Random steps before changing direction
        
        # Check if we need to change direction
        change_direction = False
        
        # Always change direction if we're at the edge and trying to move out of bounds
        if (drone.x <= 1 and drone.move_direction == 3) or \
           (drone.x >= grid_width - 2 and drone.move_direction == 1) or \
           (drone.y <= 1 and drone.move_direction == 0) or \
           (drone.y >= grid_height - 2 and drone.move_direction == 2):
            change_direction = True
            
        # Also change direction randomly or after max_steps
        if random.random() < 0.1 or drone.steps_in_direction >= drone.max_steps:
            change_direction = True
            
        if change_direction:
            # Choose a new direction that keeps us within bounds
            possible_directions = []
            
            # Check which directions are valid (not going out of bounds)
            if drone.x > 1:  # Can move left
                possible_directions.append(3)
            if drone.x < grid_width - 2:  # Can move right
                possible_directions.append(1)
            if drone.y > 1:  # Can move up
                possible_directions.append(0)
            if drone.y < grid_height - 2:  # Can move down
                possible_directions.append(2)
                
            # If no valid directions (shouldn't happen but just in case)
            if not possible_directions:
                possible_directions = [0, 1, 2, 3]
                
            # Avoid going back the same way if possible
            opposite_dir = (drone.move_direction + 2) % 4
            if opposite_dir in possible_directions and len(possible_directions) > 1:
                possible_directions.remove(opposite_dir)
                
            # Choose new direction
            drone.move_direction = random.choice(possible_directions)
            drone.steps_in_direction = 0
            drone.max_steps = random.randint(5, 15)
        
        # Determine movement based on current direction
        dx, dy = 0, 0
        direction = ""
        if drone.move_direction == 0:   # Up
            dy = -1
            direction = "UP"
        elif drone.move_direction == 1:  # Right
            dx = 1
            direction = "RIGHT"
        elif drone.move_direction == 2:  # Down
            dy = 1
            direction = "DOWN"
        else:  # Left
            dx = -1
            direction = "LEFT"
            
        drone.steps_in_direction += 1
        drone.move_counter += 1
        
        # Print debug info for this drone
        if not hasattr(self, 'last_print'):
            self.last_print = {}
        
        if drone.id not in self.last_print or self.last_print[drone.id] > 20:
            print(f"Drone {drone.id} at ({drone.x}, {drone.y}) moving {direction}")
            self.last_print[drone.id] = 0
        else:
            self.last_print[drone.id] += 1
            
        # Calculate new position with strict boundary checking
        new_x = drone.x + dx
        new_y = drone.y + dy
        
        # Ensure we do not go out of grid bounds
        if new_x < 0 or new_x >= grid_width or new_y < 0 or new_y >= grid_height:
            # If trying to go out of bounds, change direction and stay in bounds
            drone.move_direction = (drone.move_direction + 1) % 4
            drone.steps_in_direction = 0
            # Keep position within bounds
            drone.x = max(0, min(grid_width - 1, drone.x))
            drone.y = max(0, min(grid_height - 1, drone.y))
            return False, 0
            
        # Check for collisions with other drones
        if not any(d.x == new_x and d.y == new_y for d in other_drones):
            # Update position
            drone.x, drone.y = new_x, new_y
        
        # Update explored areas
        self.explored.add((drone.x, drone.y))
        
        # Update drone state based on new position
        detected = drone.detect_survivors(survivors)
        
        # Handle state transitions
        if drone.state == DroneState.EXPLORING and drone.has_payload:
            # If we detect survivors, try to rescue the closest one
            if detected:
                for survivor in detected:
                    # Skip already rescued survivors (just in case)
                    if survivor.rescued:
                        continue
                        
                    # If we're next to the survivor, rescue them
                    if (abs(drone.x - survivor.x) <= 1 and abs(drone.y - survivor.y) <= 1):
                        # Rescue the survivor
                        survivor.rescued = True
                        drone.state = DroneState.RETURNING  # Change to RETURNING state
                        drone.survivor = survivor
                        drone.has_payload = False
                        print(f"\n=== Drone {drone.id} FOUND survivor at ({survivor.x}, {survivor.y}), returning to base ===\n")
                        return True, 20  # Reward for finding survivor
                    else:
                        # Move towards the survivor if we're not already next to them
                        dx = 1 if survivor.x > drone.x else (-1 if survivor.x < drone.x else 0)
                        dy = 1 if survivor.y > drone.y else (-1 if survivor.y < drone.y else 0)
                        
                        # Only move if it won't go out of bounds
                        new_x = drone.x + dx
                        new_y = drone.y + dy
                        
                        if (0 <= new_x < grid_width and 
                            0 <= new_y < grid_height and 
                            not any(d.x == new_x and d.y == new_y for d in other_drones)):
                            drone.x, drone.y = new_x, new_y
                            return True, 0.5  # Small reward for moving towards survivor
                        
                        print(f"Drone {drone.id} moving towards survivor at ({survivor.x}, {survivor.y})")
                        return False, 0
        
        elif drone.state == DroneState.RESCUING:
            if drone.x == 0 and drone.y == 0:
                # Reached base, drop off survivor
                drone.state = DroneState.EXPLORING
                drone.survivor = None
                drone.has_payload = True
                print(f"\n=== Drone {drone.id} delivered survivor to base! ===\n")
        
        # Update battery
        drone.battery = max(0, drone.battery - 0.1)
        
        # For now, return a fixed reward since we're not using learning yet
        reward = 0
        
        return True, reward
        
        # Convert action to movement
        dx, dy = 0, 0
        direction = ""
        if action == 0:   # Up
            dy = -1
            direction = "UP"
        elif action == 1:  # Right
            dx = 1
            direction = "RIGHT"
        elif action == 2:  # Down
            dy = 1
            direction = "DOWN"
        elif action == 3:  # Left
            dx = -1
            direction = "LEFT"
            
        # Print debug info for this drone
        if not hasattr(self, 'last_print'):
            self.last_print = {}
        
        if drone.id not in self.last_print or self.last_print[drone.id] > 10:
            print(f"Drone {drone.id} at ({drone.x}, {drone.y}) moving {direction}")
            self.last_print[drone.id] = 0
        else:
            self.last_print[drone.id] += 1
            
        # Apply movement (with boundary checking)
        new_x = max(0, min(grid_width - 1, drone.x + dx))
        new_y = max(0, min(grid_height - 1, drone.y + dy))
        
        # Check for collisions with other drones
        if not any(d.x == new_x and d.y == new_y for d in other_drones):
            drone.x, drone.y = new_x, new_y
        
        # Update drone state based on new position
        detected = drone.detect_survivors(survivors)
        
        # Handle state transitions
        if drone.state == DroneState.EXPLORING:
            if detected and drone.has_payload:
                survivor = detected[0]
                if (abs(drone.x - survivor.x) <= 1 and abs(drone.y - survivor.y) <= 1):
                    # Rescue the survivor
                    survivor.rescued = True
                    drone.state = DroneState.RESCUING
                    drone.survivor = survivor
                    drone.has_payload = False
                    print(f"Drone {drone.id} found survivor at ({survivor.x}, {survivor.y})")
        
        elif drone.state == DroneState.RESCUING:
            if drone.x == 0 and drone.y == 0:
                # Reached base, drop off survivor
                drone.state = DroneState.EXPLORING
                drone.survivor = None
                drone.has_payload = True
                print(f"Drone {drone.id} delivered survivor to base")
        
        # Update battery
        drone.battery = max(0, drone.battery - 0.1)
        
        # Calculate reward and update model
        reward = self.ai_learner.get_reward(drone, prev_state, survivors, action)
        
        # Print debug info (uncomment for more verbose output)
        # print(f"Drone {drone.id} at ({drone.x}, {drone.y}) moving {direction}, state: {drone.state}, battery: {drone.battery:.1f}")
        
        # For training, update the model
        if self.training_mode:
            self.ai_learner.train_step(
                drone, survivors, action, 
                self.ai_learner.get_state(drone, survivors),
                episode_done
            )
        
        # Save data for analysis
        self.data_collector.add_observation(
            drone, survivors, action, reward, episode_done
        )
        
        return True, reward
    
    def save_training_data(self):
        """Save collected training data to disk"""
        self.data_collector.save_episode()
        
    def save_model(self):
        """Save the trained model"""
        self.ai_learner.save_model()
        print("Model AI berhasil disimpan!")
    
    def _handle_exploring(self, drone, detected, grid_width, grid_height, other_drones, survivors):
        """Handle drone behavior when in EXPLORING state"""
        # If we detect survivors and have payload capacity
        if detected and drone.has_payload:
            survivor = detected[0]
            if survivor.rescued:
                # Skip already rescued survivors
                return self._explore(drone, grid_width, grid_height, other_drones, survivors)
                
            if (abs(drone.x - survivor.x) <= 1 and abs(drone.y - survivor.y) <= 1):
                # Rescue the survivor
                survivor.rescued = True
                drone.state = DroneState.RESCUING
                drone.survivor = survivor
                drone.has_payload = False
                return True
            else:
                # Move towards the survivor
                return self._move_towards(drone, survivor.x, survivor.y, grid_width, grid_height, other_drones)
        else:
            # Explore unknown areas or move towards potential survivor locations
            return self._explore(drone, grid_width, grid_height, other_drones, survivors)
    
    def _handle_rescuing(self, drone, grid_width, grid_height, other_drones):
        """Handle drone behavior when in RESCUING state"""
        if drone.x == 0 and drone.y == 0:
            # Reached base, drop off survivor
            drone.state = DroneState.EXPLORING
            drone.survivor = None
            drone.has_payload = True
            return True
        else:
            # Return to base
            return self._move_towards(drone, 0, 0, grid_width, grid_height, other_drones)
    
    def _handle_returning(self, drone, grid_width, grid_height, other_drones):
        """Handle drone behavior when in RETURNING state"""
        if drone.x == 0 and drone.y == 0:
            # Reached base, recharge
            drone.battery = 100
            drone.state = DroneState.EXPLORING
            return True
        else:
            # Return to base
            return self._move_towards(drone, 0, 0, grid_width, grid_height, other_drones)
    
    def _explore(self, drone, grid_width, grid_height, other_drones, survivors):
        """Explore the map to find survivors with improved exploration"""
        # Get all possible directions with some randomness
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(directions)  # Randomize direction priority
        
        # Check each direction for exploration potential
        best_dir = None
        best_score = -1
        
        # Get positions of other drones to avoid
        other_drone_positions = {(d.x, d.y) for d in other_drones}
        
        for dx, dy in directions:
            new_x = drone.x + dx
            new_y = drone.y + dy
            
            # Skip if out of bounds or occupied by another drone
            if (not (0 <= new_x < grid_width and 0 <= new_y < grid_height) or 
                (new_x, new_y) in other_drone_positions):
                continue
                
            # Calculate exploration score based on:
            # 1. How many nearby cells are unexplored
            # 2. Distance from other drones (avoid clustering)
            # 3. Random factor to break ties
            
            # Exploration component
            exploration_score = 0
            for dx2, dy2 in [(-1,0), (1,0), (0,-1), (0,1)]:
                sx, sy = new_x + dx2, new_y + dy2
                if (0 <= sx < grid_width and 0 <= sy < grid_height and 
                    (sx, sy) not in self.explored):
                    exploration_score += 1
            
            # Distance from other drones component (try to spread out)
            min_dist = float('inf')
            for d in other_drones:
                dist = (d.x - new_x)**2 + (d.y - new_y)**2
                min_dist = min(min_dist, dist)
            
            # Combine scores with weights
            score = (exploration_score * 2 +  # More weight to exploration
                     min_dist * 0.5 +        # Some weight to spreading out
                     random.random())         # Random factor for exploration
            
            if score > best_score and not any(d.x == new_x and d.y == new_y for d in other_drones):
                best_score = score
                best_dir = (dx, dy)
        
        if best_dir:
            dx, dy = best_dir
            drone.x += dx
            drone.y += dy
            drone.battery = max(0, drone.battery - 0.1)
            return True
            
        return False
    
    def _move_towards(self, drone, target_x, target_y, grid_width, grid_height, other_drones):
        """Move drone towards a target position"""
        dx = 0
        dy = 0
        
        if target_x > drone.x:
            dx = 1
        elif target_x < drone.x:
            dx = -1
            
        if target_y > drone.y:
            dy = 1
        elif target_y < drone.y:
            dy = -1
        
        # Move in one direction at a time (avoid diagonal movement)
        if dx != 0 and dy != 0:
            if random.random() < 0.5:
                dy = 0
            else:
                dx = 0
        
        new_x = max(0, min(drone.x + dx, grid_width - 1))
        new_y = max(0, min(drone.y + dy, grid_height - 1))
        
        # Check for collisions with other drones
        if not any(d.x == new_x and d.y == new_y for d in other_drones):
            drone.x = new_x
            drone.y = new_y
            drone.battery = max(0, drone.battery - 0.1)
            return True
            
        return False
