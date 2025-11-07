from mesa import Agent

# Konstanta Status
STATUS_EXPLORING = 0
STATUS_DELIVERING = 1
# ... dll

class DroneAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.mode = STATUS_EXPLORING
        self.battery = 100
        self.target_coords = None # Koordinat korban yang dituju

    def step(self):
        # 1. Cek Baterai
        if self.battery <= 0:
            print(f"Drone {self.unique_id} kehabisan baterai!")
            return # Drone berhenti

        self.battery -= 1 # Kurangi baterai setiap langkah

        # 2. Cek Komunikasi (Shared Map)
        self.listen_to_map() 

        # 3. Ambil Keputusan Berdasarkan Mode
        if self.mode == STATUS_EXPLORING:
            self.explore_area()
            self.check_for_survivors()
        elif self.mode == STATUS_DELIVERING:
            self.move_to_target()
            self.deliver_payload()
        
        return_base_itself()

    def listen_to_map(self):
        # Logika: Jika ada korban di Shared Map yang belum diselamatkan, 
        # dan saya dalam mode EXPLORING, jadikan itu target.
        pass

    def explore_area(self):
        # Logika: Cari sel terdekat yang belum pernah dikunjungi, lalu pindah ke sana.
        # Gunakan self.model.grid.move_agent(self, new_position)
        pass

    def check_for_survivors(self):
        # Logika: Cek sel di sekitar (radius R). Jika ada Korban:
        # 1. Ubah mode jadi DELIVERING.
        # 2. Broadcast ke Shared Map (self.model.shared_map).
        pass

    def move_to_target(self):
        # Logika: Gunakan A* sederhana (atau hanya pergerakan X/Y) 
        # untuk bergerak ke self.target_coords.
        pass

    def deliver_payload(self):
        # Logika: Jika sudah sampai di target, ubah status Korban
        # dan ubah mode kembali jadi EXPLORING.
        pass

class SurvivorAgent(Agent):
    def __init__(self, unique_id, model, is_rescued=False):
        super().__init__(unique_id, model)
        self.is_rescued = is_rescued
        # ... tambahkan status lain jika perlu