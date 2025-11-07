import pygame
import random
import math
import sys
from entities import Drone, Survivor, DroneState
from ai_controller import AIController

# Initialize Pygame
pygame.init()

# Constants
GRID_WIDTH, GRID_HEIGHT = 75, 75  # Ukuran grid dalam sel (100x100 sel)
GRID_SIZE = 10 # Ukuran setiap sel dalam pixel (10x10 pixel per sel)
WIDTH = GRID_WIDTH * GRID_SIZE  # Lebar window: 100 * 10 = 1000 pixel
HEIGHT = GRID_HEIGHT * GRID_SIZE  # Tinggi window: 100 * 10 = 1000 pixel
FPS = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)
ORANGE = (255, 165, 0)

class Simulation:
    def __init__(self, num_drones=10, num_survivors=15):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Swarm Rescue Simulation with AI")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        
        # Initialize AI Controller
        self.ai_controller = AIController()
        
        # Initialize grid
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # Base camp position (center of the grid)
        self.base_camp_x = GRID_WIDTH // 2
        self.base_camp_y = GRID_HEIGHT // 2
        
        # Initialize drones at base camp
        self.drones = [
            Drone(
                self.base_camp_x, 
                self.base_camp_y, 
                i,
                ai_controller=self.ai_controller
            ) for i in range(num_drones)
        ]
        
        # Initialize survivors
        self.survivors = [
            Survivor(
                random.randint(0, GRID_WIDTH-1), 
                random.randint(0, GRID_HEIGHT-1)
            ) for _ in range(num_survivors)
        ]
        
        self.running = True
        self.paused = False
        self.time_elapsed = 0
        self.rescued_count = 0
        self.steps = 0
        
        if target_x > self.x:
            dx = 1
        elif target_x < self.x:
            dx = -1
            
        if target_y > self.y:
            dy = 1
        elif target_y < self.y:
            dy = -1
            
        # Jika tidak perlu bergerak diagonal, pilih satu arah secara acak
        if dx != 0 and dy != 0:
            if random.random() < 0.5:
                dy = 0
            else:
                dx = 0
                
        # Cek tabrakan dengan drone lain
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Jika posisi baru bertabrakan dengan drone lain, coba arah lain
        if any(drone.x == new_x and drone.y == new_y for drone in other_drones if drone != self):
            # Coba arah alternatif
            if dx != 0:
                dx = 0
                dy = 1 if random.random() < 0.5 else -1
            else:
                dx = 1 if random.random() < 0.5 else -1
                dy = 0
                
            new_x = self.x + dx
            new_y = self.y + dy
            
            # Jika masih bertabrakan, coba arah acak
            if any(drone.x == new_x and drone.y == new_y for drone in other_drones if drone != self):
                moves = [(0,1), (1,0), (0,-1), (-1,0)]
                random.shuffle(moves)
                for move in moves:
                    dx, dy = move
                    new_x = self.x + dx
                    new_y = self.y + dy
                    if not any(drone.x == new_x and drone.y == new_y for drone in other_drones if drone != self):
                        break
        
        # Pastikan tidak keluar dari batas
        new_x = max(0, min(new_x, grid_width - 1))
        new_y = max(0, min(new_y, grid_height - 1))
        
        self.x, self.y = new_x, new_y
        self.battery = max(0, self.battery - 0.1)
        
    def detect_survivors(self, survivors, grid):
        detected = []
        for survivor in survivors:
            if not survivor.rescued:
                dist = math.sqrt((self.x - survivor.x)**2 + (self.y - survivor.y)**2)
                if dist <= self.detection_radius:
                    detected.append((survivor, dist))
        # Urutkan berdasarkan jarak terdekat
        detected.sort(key=lambda x: x[1])
        return [survivor for survivor, _ in detected]

class Simulation:
    def __init__(self, num_drones=10, num_survivors=15):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Swarm Rescue Simulation with AI")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        
        # Inisialisasi AI Controller
        self.ai_controller = AIController()
        
        # Inisialisasi grid
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # Inisialisasi drone dengan AI Controller
        self.drones = [
            Drone(
                random.randint(0, GRID_WIDTH-1), 
                random.randint(0, GRID_HEIGHT-1), 
                i,
                ai_controller=self.ai_controller
            ) for i in range(num_drones)
        ]
        
        # Inisialisasi korban
        self.survivors = [
            Survivor(
                random.randint(0, GRID_WIDTH-1), 
                random.randint(0, GRID_HEIGHT-1)
            ) for _ in range(num_survivors)
        ]
        
        self.running = True
        self.time_elapsed = 0
        self.rescued_count = 0
        self.steps = 0
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def update(self):
        self.time_elapsed += 1
        self.steps += 1
        
        # Check if all survivors are rescued
        all_rescued = all(s.rescued for s in self.survivors)
        
        # Update each drone
        total_reward = 0
        active_drones = 0
        
        for drone in self.drones:
            if drone.battery <= 0:
                continue
                
            other_drones = [d for d in self.drones if d is not drone and d.battery > 0]
            
            # Update drone using AI controller
            updated, reward = drone.update(
                GRID_WIDTH, 
                GRID_HEIGHT, 
                other_drones, 
                self.survivors,
                episode_done=all_rescued
            )
            
            if updated:
                total_reward += reward
                active_drones += 1
            
            # If drone is returning to base with a survivor, make sure survivor is marked as rescued
            if (hasattr(drone, 'survivor') and drone.survivor and 
                not drone.survivor.rescued and 
                drone.x == 0 and drone.y == 0):
                drone.survivor.rescued = True
        
        # Update rescued count
        self.rescued_count = sum(1 for s in self.survivors if s.rescued)
        
        # Print average reward for monitoring training progress
        if active_drones > 0 and self.steps % 100 == 0:
            avg_reward = total_reward / active_drones
            print(f"Step: {self.steps}, Avg Reward: {avg_reward:.2f}, Rescued: {self.rescued_count}/{len(self.survivors)}")
        
        # Save training data and model periodically
        if self.steps % 1000 == 0:
            self.ai_controller.save_training_data()
            self.ai_controller.save_model()
        
        # Check if all survivors are rescued
        if all(survivor.rescued for survivor in self.survivors):
            print(f"Semua korban telah diselamatkan dalam {self.steps} langkah!")
            self.running = False
    
    def draw(self):
        self.screen.fill(WHITE)
        
        # Gambar grid
        for x in range(0, WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (WIDTH, y))
        
        # Gambar base (0,0)
        pygame.draw.rect(self.screen, (200, 255, 200), (0, 0, GRID_SIZE, GRID_SIZE))
        
        # Gambar korban
        for survivor in self.survivors:
            color = GREEN if survivor.rescued else RED
            pygame.draw.rect(self.screen, color, 
                           (survivor.x * GRID_SIZE, survivor.y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        
        # Gambar drone
        for drone in self.drones:
            if drone.battery > 0:
                # Warna berdasarkan status
                if drone.state == DroneState.RESCUING:
                    color = YELLOW
                elif drone.state == DroneState.RETURNING:
                    color = ORANGE
                else:
                    # Gradient biru berdasarkan level baterai
                    blue_intensity = int(100 + (drone.battery / 100) * 155)
                    color = (0, 0, blue_intensity)
                
                # Gambar drone
                center_x = int((drone.x + 0.5) * GRID_SIZE)
                center_y = int((drone.y + 0.5) * GRID_SIZE)
                
                pygame.draw.circle(self.screen, color, 
                                 (center_x, center_y), 
                                 GRID_SIZE // 2 - 2)
                
                # Tampilkan ID drone dan level baterai
                id_text = self.font.render(str(drone.id), True, WHITE)
                battery_text = self.font.render(f"{int(drone.battery)}%", True, WHITE)
                
                self.screen.blit(id_text, (drone.x * GRID_SIZE + 5, drone.y * GRID_SIZE + 2))
                self.screen.blit(battery_text, (drone.x * GRID_SIZE + 5, (drone.y + 0.7) * GRID_SIZE))
        
        # Tampilkan informasi
        info_text = f"Waktu: {self.time_elapsed} | Langkah: {self.steps} | Terselamatkan: {self.rescued_count}/{len(self.survivors)}"
        text_surface = self.font.render(info_text, True, BLACK)
        pygame.draw.rect(self.screen, WHITE, (0, 0, WIDTH, 30))
        self.screen.blit(text_surface, (10, 5))
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
            # Hentikan jika semua korban sudah diselamatkan
            if self.rescued_count >= len(self.survivors):
                print("Semua korban telah diselamatkan!")
                self.running = False
        
        pygame.quit()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Drone Rescue Simulation')
    parser.add_argument('--drones', type=int, default=5, help='Number of drones (reduced from 10 for better performance)')
    parser.add_argument('--survivors', type=int, default=10, help='Number of survivors (reduced from 15 for better performance)')
    args = parser.parse_args()
    
    print("=== Drone Rescue Simulation with AI ===")
    print(f"Drones: {args.drones}, Survivors: {args.survivors}")
    print("Controls:")
    print("- ESC: Quit")
    print("- SPACE: Pause/Resume")
    
    sim = Simulation(num_drones=args.drones, num_survivors=args.survivors)
    sim.run()