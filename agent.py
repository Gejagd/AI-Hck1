from mesa import Agent
import math

# Konstanta Status
STATUS_EXPLORING = 0
STATUS_DELIVERING = 1
STATUS_RETURN_TO_BASE = 2


class DroneAgent(Agent):
    """
    Ditulis untuk Mesa 3.5.x. Perubahan dari Mesa 2.x:
    - Constructor tidak lagi menerima `unique_id` (auto-assigned oleh Mesa,
      diakses tetap lewat `self.unique_id`).
    - `super().__init__(model)` saja, tanpa unique_id.
    - Pakai `self.random` (proxy ke `self.model.random`) alih-alih modul
      `random` global, supaya hasil simulasi reproducible lewat seed model.
    """

    def __init__(self, model, detection_radius=3, max_payloads=3):
        super().__init__(model)
        self.mode = STATUS_EXPLORING
        self.battery = 100
        self.max_battery = 100
        self.target_coords = None  # Koordinat korban yang dituju
        self.detection_radius = detection_radius
        self.max_payloads = max_payloads
        self.current_payloads = max_payloads
        self.visited_cells = set()  # Track explored cells
        self.survivors_rescued = 0
        self.base_position = None  # Will be set by model

    def step(self):
        # 1. Cek Baterai
        if self.battery <= 0:
            print(f"Drone {self.unique_id} kehabisan baterai di posisi {self.pos}!")
            return  # Drone berhenti

        # 2. Cek apakah perlu kembali ke base
        if self.battery < 30 or self.current_payloads == 0:
            if self.mode != STATUS_RETURN_TO_BASE:
                print(f"Drone {self.unique_id} kembali ke base (Battery: {self.battery}, Payloads: {self.current_payloads})")
                self.mode = STATUS_RETURN_TO_BASE
                self.target_coords = self.base_position

        # 3. Cek Komunikasi (Shared Map)
        self.listen_to_map()

        # 4. Ambil Keputusan Berdasarkan Mode
        if self.mode == STATUS_EXPLORING:
            self.explore_area()
            self.check_for_survivors()
        elif self.mode == STATUS_DELIVERING:
            self.move_to_target()
            self.deliver_payload()
        elif self.mode == STATUS_RETURN_TO_BASE:
            self.return_to_base()

        # 5. Kurangi baterai setiap langkah
        self.battery -= 1

    def listen_to_map(self):
        """
        Logika: Jika ada korban di Shared Map yang belum diselamatkan,
        dan saya dalam mode EXPLORING, jadikan itu target.
        """
        if self.mode == STATUS_EXPLORING and self.current_payloads > 0:
            closest_survivor = None
            min_distance = float('inf')

            for survivor_pos, survivor_info in self.model.shared_map.items():
                if not survivor_info['is_rescued'] and not survivor_info['being_helped']:
                    distance = self.calculate_distance(self.pos, survivor_pos)
                    if distance < min_distance:
                        min_distance = distance
                        closest_survivor = survivor_pos

            if closest_survivor and min_distance < self.detection_radius * 2:
                self.target_coords = closest_survivor
                self.mode = STATUS_DELIVERING
                self.model.shared_map[closest_survivor]['being_helped'] = True
                print(f"Drone {self.unique_id} menemukan korban di {closest_survivor} (jarak: {min_distance:.1f})")

    def explore_area(self):
        """
        Logika: Cari sel terdekat yang belum pernah dikunjungi, lalu pindah ke sana.
        """
        self.visited_cells.add(self.pos)

        possible_moves = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False
        )

        unvisited = [pos for pos in possible_moves if pos not in self.visited_cells]

        if unvisited:
            new_position = self.random.choice(unvisited)
        elif possible_moves:
            new_position = self.random.choice(possible_moves)
        else:
            return

        self.model.grid.move_agent(self, new_position)

    def check_for_survivors(self):
        """
        Logika: Cek sel di sekitar (radius R). Jika ada Korban, ubah mode
        jadi DELIVERING dan broadcast ke Shared Map.
        """
        if self.current_payloads == 0:
            return

        x, y = self.pos
        for dx in range(-self.detection_radius, self.detection_radius + 1):
            for dy in range(-self.detection_radius, self.detection_radius + 1):
                check_pos = (x + dx, y + dy)

                if not self.model.grid.out_of_bounds(check_pos):
                    cell_contents = self.model.grid.get_cell_list_contents([check_pos])
                    for agent in cell_contents:
                        if isinstance(agent, SurvivorAgent) and not agent.is_rescued:
                            distance = self.calculate_distance(self.pos, check_pos)
                            if distance <= self.detection_radius:
                                self.target_coords = check_pos
                                self.mode = STATUS_DELIVERING

                                if check_pos not in self.model.shared_map:
                                    self.model.shared_map[check_pos] = {
                                        'is_rescued': False,
                                        'being_helped': True,
                                        'discovered_by': self.unique_id
                                    }
                                    print(f"Drone {self.unique_id} menemukan korban baru di {check_pos}!")
                                return

    def move_to_target(self):
        """
        Logika: Pergerakan sederhana menuju self.target_coords.
        """
        if self.target_coords is None:
            self.mode = STATUS_EXPLORING
            return

        current_x, current_y = self.pos
        target_x, target_y = self.target_coords

        dx = 0 if target_x == current_x else (1 if target_x > current_x else -1)
        dy = 0 if target_y == current_y else (1 if target_y > current_y else -1)

        new_position = (current_x + dx, current_y + dy)

        if not self.model.grid.out_of_bounds(new_position):
            self.model.grid.move_agent(self, new_position)
            self.visited_cells.add(new_position)

    def deliver_payload(self):
        """
        Logika: Jika sudah sampai di target, ubah status Korban
        dan ubah mode kembali jadi EXPLORING.
        """
        if self.target_coords is None:
            self.mode = STATUS_EXPLORING
            return

        if self.pos == self.target_coords:
            cell_contents = self.model.grid.get_cell_list_contents([self.pos])
            for agent in cell_contents:
                if isinstance(agent, SurvivorAgent) and not agent.is_rescued:
                    agent.is_rescued = True
                    self.current_payloads -= 1
                    self.survivors_rescued += 1

                    if self.target_coords in self.model.shared_map:
                        self.model.shared_map[self.target_coords]['is_rescued'] = True
                        self.model.shared_map[self.target_coords]['being_helped'] = False

                    print(f"Drone {self.unique_id} menyelamatkan korban di {self.pos}! (Payloads tersisa: {self.current_payloads})")

                    self.target_coords = None
                    self.mode = STATUS_EXPLORING
                    return

            self.target_coords = None
            self.mode = STATUS_EXPLORING

    def return_to_base(self):
        """Return to base untuk recharge dan reload payloads"""
        if self.target_coords is None:
            self.target_coords = self.base_position

        self.move_to_target()

        if self.pos == self.base_position:
            self.battery = self.max_battery
            self.current_payloads = self.max_payloads
            print(f"Drone {self.unique_id} di-recharge di base! Battery: {self.battery}, Payloads: {self.current_payloads}")

            self.target_coords = None
            self.mode = STATUS_EXPLORING

    def calculate_distance(self, pos1, pos2):
        """Hitung jarak Euclidean antara dua posisi"""
        return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)


class SurvivorAgent(Agent):
    def __init__(self, model, is_rescued=False):
        super().__init__(model)
        self.is_rescued = is_rescued
        self.rescue_time = None  # Waktu ketika diselamatkan

    def step(self):
        """Survivor tidak bergerak, hanya menunggu diselamatkan"""
        if self.is_rescued and self.rescue_time is None:
            self.rescue_time = self.model.steps
