# 🔧 Implementation Guide - Completing agent.py

## Current Status

Your `agent.py` file has the basic structure but needs to be completed with the full implementation. Below is the complete code you need to add.

## Step-by-Step Instructions

### 1. Save Your Current Work

First, make sure to save any unsaved changes in `agent.py`.

### 2. Complete the Implementation

Replace or update your `agent.py` with the following complete implementation:

```python
from mesa import Agent
import random
import math

# Konstanta Status
STATUS_EXPLORING = 0
STATUS_DELIVERING = 1
STATUS_RETURN_TO_BASE = 2

class DroneAgent(Agent):
    def __init__(self, unique_id, model, detection_radius=3, max_payloads=3):
        super().__init__(unique_id, model)
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
            # Cari korban terdekat yang belum diselamatkan
            closest_survivor = None
            min_distance = float('inf')
            
            for survivor_pos, survivor_info in self.model.shared_map.items():
                if not survivor_info['is_rescued'] and not survivor_info['being_helped']:
                    distance = self.calculate_distance(self.pos, survivor_pos)
                    if distance < min_distance:
                        min_distance = distance
                        closest_survivor = survivor_pos
            
            # Jika ada korban dan cukup dekat, jadikan target
            if closest_survivor and min_distance < self.detection_radius * 2:
                self.target_coords = closest_survivor
                self.mode = STATUS_DELIVERING
                self.model.shared_map[closest_survivor]['being_helped'] = True
                print(f"Drone {self.unique_id} menemukan korban di {closest_survivor} (jarak: {min_distance:.1f})")

    def explore_area(self):
        """
        Logika: Cari sel terdekat yang belum pernah dikunjungi, lalu pindah ke sana.
        Gunakan self.model.grid.move_agent(self, new_position)
        """
        # Tandai posisi saat ini sebagai sudah dikunjungi
        self.visited_cells.add(self.pos)
        
        # Cari tetangga yang valid
        possible_moves = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,  # 8 arah
            include_center=False
        )
        
        # Filter: prioritaskan sel yang belum dikunjungi
        unvisited = [pos for pos in possible_moves if pos not in self.visited_cells]
        
        if unvisited:
            # Pilih sel yang belum dikunjungi secara random (eksplorasi)
            new_position = random.choice(unvisited)
        elif possible_moves:
            # Jika semua sudah dikunjungi, pilih random
            new_position = random.choice(possible_moves)
        else:
            return  # Tidak bisa bergerak
        
        self.model.grid.move_agent(self, new_position)

    def check_for_survivors(self):
        """
        Logika: Cek sel di sekitar (radius R). Jika ada Korban:
        1. Ubah mode jadi DELIVERING.
        2. Broadcast ke Shared Map (self.model.shared_map).
        """
        if self.current_payloads == 0:
            return  # Tidak ada payload untuk dikirim
        
        # Cek area dalam radius deteksi
        x, y = self.pos
        for dx in range(-self.detection_radius, self.detection_radius + 1):
            for dy in range(-self.detection_radius, self.detection_radius + 1):
                check_pos = (x + dx, y + dy)
                
                # Cek apakah posisi valid
                if not self.model.grid.out_of_bounds(check_pos):
                    # Cek apakah ada survivor di posisi ini
                    cell_contents = self.model.grid.get_cell_list_contents([check_pos])
                    for agent in cell_contents:
                        if isinstance(agent, SurvivorAgent) and not agent.is_rescued:
                            # Survivor ditemukan!
                            distance = self.calculate_distance(self.pos, check_pos)
                            if distance <= self.detection_radius:
                                self.target_coords = check_pos
                                self.mode = STATUS_DELIVERING
                                
                                # Update shared map
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
        Logika: Gunakan A* sederhana (atau hanya pergerakan X/Y)
        untuk bergerak ke self.target_coords.
        """
        if self.target_coords is None:
            self.mode = STATUS_EXPLORING
            return
        
        # Simple pathfinding: bergerak ke arah target
        current_x, current_y = self.pos
        target_x, target_y = self.target_coords
        
        # Hitung arah
        dx = 0 if target_x == current_x else (1 if target_x > current_x else -1)
        dy = 0 if target_y == current_y else (1 if target_y > current_y else -1)
        
        new_position = (current_x + dx, current_y + dy)
        
        # Cek apakah posisi valid
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
        
        # Cek apakah sudah sampai di target
        if self.pos == self.target_coords:
            # Cari survivor di posisi ini
            cell_contents = self.model.grid.get_cell_list_contents([self.pos])
            for agent in cell_contents:
                if isinstance(agent, SurvivorAgent) and not agent.is_rescued:
                    # Selamatkan survivor
                    agent.is_rescued = True
                    self.current_payloads -= 1
                    self.survivors_rescued += 1
                    
                    # Update shared map
                    if self.target_coords in self.model.shared_map:
                        self.model.shared_map[self.target_coords]['is_rescued'] = True
                        self.model.shared_map[self.target_coords]['being_helped'] = False
                    
                    print(f"Drone {self.unique_id} menyelamatkan korban di {self.pos}! (Payloads tersisa: {self.current_payloads})")
                    
                    # Kembali ke mode exploring
                    self.target_coords = None
                    self.mode = STATUS_EXPLORING
                    return
            
            # Jika tidak ada survivor (mungkin sudah diselamatkan drone lain)
            self.target_coords = None
            self.mode = STATUS_EXPLORING

    def return_to_base(self):
        """Return to base untuk recharge dan reload payloads"""
        if self.target_coords is None:
            self.target_coords = self.base_position
        
        # Bergerak ke base
        self.move_to_target()
        
        # Cek apakah sudah sampai di base
        if self.pos == self.base_position:
            # Recharge dan reload
            self.battery = self.max_battery
            self.current_payloads = self.max_payloads
            print(f"Drone {self.unique_id} di-recharge di base! Battery: {self.battery}, Payloads: {self.current_payloads}")
            
            # Kembali ke mode exploring
            self.target_coords = None
            self.mode = STATUS_EXPLORING

    def calculate_distance(self, pos1, pos2):
        """Hitung jarak Euclidean antara dua posisi"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)


class SurvivorAgent(Agent):
    def __init__(self, unique_id, model, is_rescued=False):
        super().__init__(unique_id, model)
        self.is_rescued = is_rescued
        self.rescue_time = None  # Waktu ketika diselamatkan
    
    def step(self):
        """Survivor tidak bergerak, hanya menunggu diselamatkan"""
        if self.is_rescued and self.rescue_time is None:
            self.rescue_time = self.model.schedule.steps
```

### 3. Key Changes from Your Original

The complete implementation adds:

1. **Import statements**: Added `random` and `math` modules
2. **Additional constants**: `STATUS_RETURN_TO_BASE = 2`
3. **Enhanced DroneAgent attributes**:
   - `max_battery`, `detection_radius`, `max_payloads`
   - `current_payloads`, `visited_cells`, `survivors_rescued`
   - `base_position`

4. **Complete method implementations**:
   - `listen_to_map()`: Checks shared map for known survivors
   - `explore_area()`: Random walk with visited cell tracking
   - `check_for_survivors()`: Scans detection radius for survivors
   - `move_to_target()`: Simple pathfinding toward target
   - `deliver_payload()`: Rescues survivor at target location
   - `return_to_base()`: Returns to base for recharge/reload
   - `calculate_distance()`: Helper for distance calculations

5. **Enhanced SurvivorAgent**:
   - Added `rescue_time` tracking
   - Added `step()` method

### 4. Testing Your Implementation

After updating `agent.py`, test it with:

```bash
# Install dependencies first
pip install -r requirements.txt

# Run basic simulation
python main.py

# Run with custom parameters
python main.py --drones 8 --survivors 30

# Run analysis (takes longer)
python analyze.py
```

### 5. Expected Behavior

When running correctly, you should see:
- Drones exploring the grid (blue circles)
- Detection radius shown as transparent circles
- Survivors marked with X (pink = waiting, green circle = rescued)
- Real-time statistics panel
- Console output showing drone activities

### 6. Troubleshooting

If you encounter errors:

1. **Import errors**: Make sure all dependencies are installed
2. **Attribute errors**: Ensure you've updated the entire `DroneAgent.__init__` method
3. **Grid errors**: Check that `model.py` is in the same directory
4. **Visualization errors**: Install matplotlib with `pip install matplotlib`

## Next Steps

Once `agent.py` is complete:

1. ✅ Run the basic simulation
2. ✅ Try different parameters
3. ✅ Run the analysis script for performance metrics
4. ✅ Save animations and snapshots for your presentation
5. ✅ Customize parameters for your hackathon demo

Good luck with your hackathon! 🚁🎉
