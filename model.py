from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from agent import DroneAgent, SurvivorAgent


class SwarmRescueModel(Model):
    """
    Model untuk simulasi Swarm Rescue.
    Drones berkoordinasi untuk menemukan dan menyelamatkan survivors.

    Ditulis untuk Mesa 3.5.x. Perubahan utama dari Mesa 2.x:
    - Tidak ada lagi `mesa.time` / scheduler class (RandomActivation dkk).
      Aktivasi agent sekarang lewat AgentSet: `self.agents.shuffle_do("step")`.
    - `unique_id` agent di-assign otomatis oleh Mesa, tidak perlu (dan tidak
      boleh) di-set manual di constructor.
    - Agent otomatis terdaftar ke `model.agents` saat dibuat, jadi tidak perlu
      `schedule.add(...)` lagi.
    - Random seed dikelola lewat `super().__init__(seed=seed)`, dan
      `self.random` dipakai untuk semua randomisasi supaya reproducible.
    - Step counter (`self.steps`) otomatis bertambah tiap `self.step()`
      dipanggil, jadi tidak perlu dikelola manual (dulu `schedule.steps`).
    """

    def __init__(self, width=50, height=50, num_drones=5, num_survivors=20,
                 detection_radius=3, seed=None):
        super().__init__(seed=seed)  # Mesa mengelola RNG (self.random) dari sini

        # Parameter model
        self.width = width
        self.height = height
        self.num_drones = num_drones
        self.num_survivors = num_survivors
        self.detection_radius = detection_radius

        # Grid (Mesa 3.x: MultiGrid masih sama seperti sebelumnya)
        self.grid = MultiGrid(width, height, torus=False)

        # Shared map untuk komunikasi antar drone
        # Format: {(x, y): {'is_rescued': bool, 'being_helped': bool, 'discovered_by': drone_id}}
        self.shared_map = {}

        # Base position (pusat grid)
        self.base_position = (width // 2, height // 2)

        # Statistik
        self.survivors_found = 0
        self.survivors_rescued = 0
        self.total_battery_used = 0

        # Buat drone agents (Mesa 3.x: tidak ada unique_id manual)
        for _ in range(num_drones):
            drone = DroneAgent(
                model=self,
                detection_radius=detection_radius,
                max_payloads=3
            )
            drone.base_position = self.base_position

            # Tempatkan drone di base (agent sudah otomatis masuk ke model.agents)
            self.grid.place_agent(drone, self.base_position)

        # Buat survivor agents (random positions)
        for _ in range(num_survivors):
            survivor = SurvivorAgent(model=self)

            # Tempatkan survivor di posisi random (tidak di base), pakai
            # self.random supaya konsisten dengan seed yang dikelola Mesa
            while True:
                x = self.random.randrange(self.width)
                y = self.random.randrange(self.height)
                pos = (x, y)

                # Pastikan tidak di base dan tidak terlalu dekat dengan base
                distance_from_base = ((x - self.base_position[0]) ** 2 +
                                       (y - self.base_position[1]) ** 2) ** 0.5
                if distance_from_base > 5:
                    self.grid.place_agent(survivor, pos)
                    break

        # Data collector untuk tracking metrics
        # (m.agents menggantikan m.schedule.agents di Mesa 3.x)
        self.datacollector = DataCollector(
            model_reporters={
                "Survivors Found": lambda m: len([s for s in m.shared_map.values()]),
                "Survivors Rescued": lambda m: sum(1 for s in m.shared_map.values() if s['is_rescued']),
                "Active Drones": lambda m: sum(1 for a in m.agents
                                              if isinstance(a, DroneAgent) and a.battery > 0),
                "Average Battery": lambda m: sum(a.battery for a in m.agents
                                                if isinstance(a, DroneAgent)) / m.num_drones,
                "Total Rescued": lambda m: sum(a.survivors_rescued for a in m.agents
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
        # Mesa 3.x: ganti RandomActivation dengan AgentSet.shuffle_do("step")
        # (`self.steps` otomatis bertambah 1 setiap method step() ini dipanggil)
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)

        # Update statistik
        self.survivors_rescued = sum(1 for s in self.shared_map.values() if s['is_rescued'])

        # Cek apakah semua survivor sudah diselamatkan
        total_survivors = sum(1 for a in self.agents if isinstance(a, SurvivorAgent))
        rescued_survivors = sum(1 for a in self.agents
                               if isinstance(a, SurvivorAgent) and a.is_rescued)

        if rescued_survivors == total_survivors:
            print(f"\n🎉 Semua {total_survivors} survivors berhasil diselamatkan dalam {self.steps} langkah!")
            self.running = False

        # Cek apakah semua drone kehabisan baterai
        active_drones = sum(1 for a in self.agents
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

        for agent in self.agents:
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
