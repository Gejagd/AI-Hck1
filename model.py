from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from agent import DroneAgent, SurvivorAgent
import random


class SwarmRescueModel(Model):
    """
    Model untuk simulasi Swarm Rescue.
    Drones berkoordinasi untuk menemukan dan menyelamatkan survivors.
    """
    
    def __init__(self, width=50, height=50, num_drones=5, num_survivors=20, 
                 detection_radius=3, seed=None):
        super().__init__()
        
        # Set random seed untuk reproducibility
        if seed is not None:
            random.seed(seed)
        
        # Parameter model
        self.width = width
        self.height = height
        self.num_drones = num_drones
        self.num_survivors = num_survivors
        self.detection_radius = detection_radius
        
        # Grid dan scheduler
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)
        
        # Shared map untuk komunikasi antar drone
        # Format: {(x, y): {'is_rescued': bool, 'being_helped': bool, 'discovered_by': drone_id}}
        self.shared_map = {}
        
        # Base position (pusat grid)
        self.base_position = (width // 2, height // 2)
        
        # Statistik
        self.survivors_found = 0
        self.survivors_rescued = 0
        self.total_battery_used = 0
        
        # Buat drone agents
        for i in range(num_drones):
            drone = DroneAgent(
                unique_id=i,
                model=self,
                detection_radius=detection_radius,
                max_payloads=3
            )
            drone.base_position = self.base_position
            
            # Tempatkan drone di base
            self.grid.place_agent(drone, self.base_position)
            self.schedule.add(drone)
        
        # Buat survivor agents (random positions)
        for i in range(num_survivors):
            survivor = SurvivorAgent(
                unique_id=num_drones + i,
                model=self
            )
            
            # Tempatkan survivor di posisi random (tidak di base)
            while True:
                x = random.randrange(self.width)
                y = random.randrange(self.height)
                pos = (x, y)
                
                # Pastikan tidak di base dan tidak terlalu dekat dengan base
                distance_from_base = ((x - self.base_position[0])**2 + 
                                     (y - self.base_position[1])**2)**0.5
                if distance_from_base > 5:
                    self.grid.place_agent(survivor, pos)
                    break
            
            self.schedule.add(survivor)
        
        # Data collector untuk tracking metrics
        self.datacollector = DataCollector(
            model_reporters={
                "Survivors Found": lambda m: len([s for s in m.shared_map.values()]),
                "Survivors Rescued": lambda m: sum(1 for s in m.shared_map.values() if s['is_rescued']),
                "Active Drones": lambda m: sum(1 for a in m.schedule.agents 
                                              if isinstance(a, DroneAgent) and a.battery > 0),
                "Average Battery": lambda m: sum(a.battery for a in m.schedule.agents 
                                                if isinstance(a, DroneAgent)) / m.num_drones,
                "Total Rescued": lambda m: sum(a.survivors_rescued for a in m.schedule.agents 
                                              if isinstance(a, DroneAgent))
            },
            agent_reporters={
                "Battery": lambda a: a.battery if isinstance(a, DroneAgent) else None,
                "Mode": lambda a: a.mode if isinstance(a, DroneAgent) else None,
                "Payloads": lambda a: a.current_payloads if isinstance(a, DroneAgent) else None,
                "Rescued": lambda a: a.is_rescued if isinstance(a, SurvivorAgent) else None
            }
        )
        
        self.running = True
        self.datacollector.collect(self)
    
    def step(self):
        """Advance the model by one step."""
        self.schedule.step()
        self.datacollector.collect(self)
        
        # Update statistik
        self.survivors_rescued = sum(1 for s in self.shared_map.values() if s['is_rescued'])
        
        # Cek apakah semua survivor sudah diselamatkan
        total_survivors = sum(1 for a in self.schedule.agents if isinstance(a, SurvivorAgent))
        rescued_survivors = sum(1 for a in self.schedule.agents 
                               if isinstance(a, SurvivorAgent) and a.is_rescued)
        
        if rescued_survivors == total_survivors:
            print(f"\n🎉 Semua {total_survivors} survivors berhasil diselamatkan dalam {self.schedule.steps} langkah!")
            self.running = False
        
        # Cek apakah semua drone kehabisan baterai
        active_drones = sum(1 for a in self.schedule.agents 
                           if isinstance(a, DroneAgent) and a.battery > 0)
        if active_drones == 0:
            print(f"\n⚠️ Semua drone kehabisan baterai! Survivors diselamatkan: {rescued_survivors}/{total_survivors}")
            self.running = False
    
    def get_grid_state(self):
        """Return current state of the grid for visualization"""
        grid_state = {
            'drones': [],
            'survivors': [],
            'base': self.base_position
        }
        
        for agent in self.schedule.agents:
            if isinstance(agent, DroneAgent):
                grid_state['drones'].append({
                    'id': agent.unique_id,
                    'pos': agent.pos,
                    'battery': agent.battery,
                    'mode': agent.mode,
                    'payloads': agent.current_payloads
                })
            elif isinstance(agent, SurvivorAgent):
                grid_state['survivors'].append({
                    'id': agent.unique_id,
                    'pos': agent.pos,
                    'rescued': agent.is_rescued
                })
        
        return grid_state
