from enum import Enum

class DroneState(Enum):
    EXPLORING = 1
    RESCUING = 2
    RETURNING = 3

class Survivor:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rescued = False
        self.rescue_time = 0

class Drone:
    def __init__(self, x, y, drone_id, ai_controller=None):
        self.x = x
        self.y = y
        self.id = drone_id
        self.state = DroneState.EXPLORING
        self.battery = 100
        self.survivor = None
        self.has_payload = True
        self.detection_radius = 3
        self.ai_controller = ai_controller
        self.target_x = None
        self.target_y = None
        
    def update(self, grid_width, grid_height, other_drones, survivors, episode_done=False):
        """Update drone state based on AI controller's decisions
        
        Args:
            grid_width: Width of the simulation grid
            grid_height: Height of the simulation grid
            other_drones: List of other drones in the simulation
            survivors: List of survivors in the simulation
            episode_done: Whether the current episode is done (all survivors rescued)
            
        Returns:
            Tuple of (updated, reward) where updated is a boolean indicating if the drone moved,
            and reward is the reward for the action taken
        """
        if self.ai_controller:
            return self.ai_controller.update_drone(
                self, grid_width, grid_height, other_drones, survivors, episode_done
            )
        return False, 0  # No movement if no AI controller
        
    def detect_survivors(self, survivors):
        """Detect nearby survivors within detection radius"""
        detected = []
        for survivor in survivors:
            if not survivor.rescued:
                dist_sq = (self.x - survivor.x)**2 + (self.y - survivor.y)**2
                if dist_sq <= self.detection_radius**2:
                    detected.append((survivor, dist_sq**0.5))
        # Sort by distance (closest first)
        detected.sort(key=lambda x: x[1])
        return [survivor for survivor, _ in detected]
