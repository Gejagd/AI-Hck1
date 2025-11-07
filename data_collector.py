import csv
import os
import numpy as np
from datetime import datetime
from entities import DroneState

class DataCollector:
    def __init__(self):
        self.data = []
        self.episode = 0
        self.data_dir = "training_data"
        os.makedirs(self.data_dir, exist_ok=True)
        
    def add_observation(self, drone, survivors, action, reward, done):
        """
        Menambahkan data observasi
        
        Parameters:
            drone: Objek drone
            survivors: Daftar survivor
            action: Aksi yang diambil (0=atas, 1=kanan, 2=bawah, 3=kiri)
            reward: Reward yang didapat
            done: Apakah episode selesai
        """
        # Hitung jarak ke survivor terdekat
        min_dist = float('inf')
        for s in survivors:
            if not s.rescued:
                dist = np.sqrt((drone.x - s.x)**2 + (drone.y - s.y)**2)
                min_dist = min(min_dist, dist)
        
        # Normalisasi data
        state = [
            drone.x / 40,  # Normalisasi posisi x (40 = GRID_WIDTH)
            drone.y / 30,  # Normalisasi posisi y (30 = GRID_HEIGHT)
            drone.battery / 100.0,
            min_dist / np.sqrt(40**2 + 30**2),  # Normalisasi jarak maksimum
            int(drone.state == DroneState.EXPLORING),
            int(drone.state == DroneState.RESCUING),
            int(drone.state == DroneState.RETURNING)
        ]
        
        self.data.append({
            'episode': self.episode,
            'state': state,
            'action': action,
            'reward': reward,
            'done': done
        })
    
    def save_episode(self):
        """Menyimpan data episode ke file CSV"""
        if not self.data:
            return
            
        filename = f"{self.data_dir}/training_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            # Header
            writer.writerow([
                'episode',
                'x_pos', 'y_pos', 'battery', 'closest_survivor_dist',
                'is_exploring', 'is_rescuing', 'is_returning',
                'action', 'reward', 'done'
            ])
            
            for obs in self.data:
                writer.writerow([
                    obs['episode'],
                    *obs['state'],
                    obs['action'],
                    obs['reward'],
                    int(obs['done'])
                ])
        
        print(f"Data tersimpan di {filename}")
        self.data = []
        self.episode += 1

# Contoh penggunaan:
if __name__ == "__main__":
    collector = DataCollector()
    # Contoh data dummy
    class Drone:
        x, y = 10, 15
        battery = 75
        state = DroneState.EXPLORING
    
    collector.add_observation(Drone(), [], 1, 0.1, False)
    collector.save_episode()
