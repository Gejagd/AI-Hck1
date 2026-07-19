import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle, Rectangle
import numpy as np


class SwarmRescueVisualization:
    """
    Visualisasi untuk simulasi Swarm Rescue menggunakan Matplotlib.
    """
    
    def __init__(self, model, figsize=(14, 10)):
        self.model = model
        self.fig, (self.ax_grid, self.ax_stats) = plt.subplots(1, 2, figsize=figsize, 
                                                                gridspec_kw={'width_ratios': [3, 1]})
        
        # Setup grid plot
        self.ax_grid.set_xlim(-1, model.width)
        self.ax_grid.set_ylim(-1, model.height)
        self.ax_grid.set_aspect('equal')
        self.ax_grid.set_title('Swarm Rescue Simulation', fontsize=16, fontweight='bold')
        self.ax_grid.set_xlabel('X Position')
        self.ax_grid.set_ylabel('Y Position')
        self.ax_grid.grid(True, alpha=0.3)
        
        # Setup stats plot
        self.ax_stats.axis('off')
        
        # Color scheme
        self.colors = {
            'base': '#FFD700',  # Gold
            'drone_exploring': '#1E90FF',  # DodgerBlue
            'drone_delivering': '#FF4500',  # OrangeRed
            'drone_returning': '#9370DB',  # MediumPurple
            'survivor_waiting': '#FF1493',  # DeepPink
            'survivor_rescued': '#32CD32',  # LimeGreen
            'detection_radius': '#87CEEB'  # SkyBlue
        }
        
        # Initialize plot elements
        self.drone_markers = []
        self.survivor_markers = []
        self.detection_circles = []
        self.base_marker = None
        self.stats_text = None
        
        plt.tight_layout()
    
    def draw_frame(self, frame_num=0):
        """Draw a single frame of the simulation"""
        # Clear previous frame
        self.ax_grid.clear()
        self.ax_stats.clear()
        
        # Reset grid settings
        self.ax_grid.set_xlim(-1, self.model.width)
        self.ax_grid.set_ylim(-1, self.model.height)
        self.ax_grid.set_aspect('equal')
        self.ax_grid.set_title(f'Swarm Rescue Simulation - Step {self.model.steps}', 
                               fontsize=16, fontweight='bold')
        self.ax_grid.set_xlabel('X Position')
        self.ax_grid.set_ylabel('Y Position')
        self.ax_grid.grid(True, alpha=0.3)
        self.ax_stats.axis('off')
        
        # Get current state
        state = self.model.get_grid_state()
        
        # Draw base station
        base_x, base_y = state['base']
        self.ax_grid.add_patch(Rectangle((base_x - 1, base_y - 1), 2, 2, 
                                        facecolor=self.colors['base'], 
                                        edgecolor='black', linewidth=2, 
                                        alpha=0.7, label='Base Station'))
        self.ax_grid.plot(base_x, base_y, 'k*', markersize=20, zorder=10)
        
        # Draw survivors
        for survivor in state['survivors']:
            x, y = survivor['pos']
            if survivor['rescued']:
                color = self.colors['survivor_rescued']
                marker = 'o'
                label = 'Survivor (Rescued)'
            else:
                color = self.colors['survivor_waiting']
                marker = 'X'
                label = 'Survivor (Waiting)'
            
            self.ax_grid.plot(x, y, marker, color=color, markersize=12, 
                            markeredgecolor='black', markeredgewidth=1, zorder=5)
        
        # Draw drones and their detection radius
        for drone in state['drones']:
            x, y = drone['pos']
            
            # Determine drone color based on mode
            if drone['mode'] == 0:  # EXPLORING
                color = self.colors['drone_exploring']
                mode_text = 'Exploring'
            elif drone['mode'] == 1:  # DELIVERING
                color = self.colors['drone_delivering']
                mode_text = 'Delivering'
            else:  # RETURN_TO_BASE
                color = self.colors['drone_returning']
                mode_text = 'Returning'
            
            # Draw detection radius (semi-transparent circle)
            if drone['battery'] > 0:
                circle = Circle((x, y), self.model.detection_radius, 
                              color=self.colors['detection_radius'], 
                              alpha=0.1, zorder=1)
                self.ax_grid.add_patch(circle)
            
            # Draw drone
            self.ax_grid.plot(x, y, 'o', color=color, markersize=15, 
                            markeredgecolor='black', markeredgewidth=2, zorder=8)
            
            # Add drone ID and battery level
            battery_color = 'green' if drone['battery'] > 50 else 'orange' if drone['battery'] > 20 else 'red'
            self.ax_grid.text(x, y + 1.5, f"D{drone['id']}", 
                            ha='center', va='bottom', fontsize=8, fontweight='bold')
            self.ax_grid.text(x, y - 1.5, f"{drone['battery']}%", 
                            ha='center', va='top', fontsize=7, 
                            color=battery_color, fontweight='bold')
        
        # Draw legend
        legend_elements = [
            patches.Patch(facecolor=self.colors['base'], edgecolor='black', label='Base Station'),
            plt.Line2D([0], [0], marker='X', color='w', markerfacecolor=self.colors['survivor_waiting'], 
                      markersize=10, label='Survivor (Waiting)', markeredgecolor='black'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=self.colors['survivor_rescued'], 
                      markersize=10, label='Survivor (Rescued)', markeredgecolor='black'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=self.colors['drone_exploring'], 
                      markersize=10, label='Drone (Exploring)', markeredgecolor='black'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=self.colors['drone_delivering'], 
                      markersize=10, label='Drone (Delivering)', markeredgecolor='black'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=self.colors['drone_returning'], 
                      markersize=10, label='Drone (Returning)', markeredgecolor='black'),
        ]
        self.ax_grid.legend(handles=legend_elements, loc='upper left', fontsize=8)
        
        # Draw statistics
        self._draw_statistics(state)
        
        return self.ax_grid, self.ax_stats
    
    def _draw_statistics(self, state):
        """Draw statistics panel"""
        # Calculate statistics
        total_survivors = len(state['survivors'])
        rescued_survivors = sum(1 for s in state['survivors'] if s['rescued'])
        active_drones = sum(1 for d in state['drones'] if d['battery'] > 0)
        avg_battery = np.mean([d['battery'] for d in state['drones']]) if state['drones'] else 0
        
        total_payloads = sum(d['payloads'] for d in state['drones'])
        
        # Mode distribution
        exploring = sum(1 for d in state['drones'] if d['mode'] == 0)
        delivering = sum(1 for d in state['drones'] if d['mode'] == 1)
        returning = sum(1 for d in state['drones'] if d['mode'] == 2)
        
        # Create statistics text
        stats_text = f"""
╔══════════════════════════════╗
║      MISSION STATISTICS      ║
╚══════════════════════════════╝

⏱️  Step: {self.model.steps}

👥 SURVIVORS
   • Total: {total_survivors}
   • Rescued: {rescued_survivors}
   • Waiting: {total_survivors - rescued_survivors}
   • Progress: {rescued_survivors/total_survivors*100:.1f}%

🚁 DRONES
   • Total: {len(state['drones'])}
   • Active: {active_drones}
   • Inactive: {len(state['drones']) - active_drones}

🔋 BATTERY
   • Average: {avg_battery:.1f}%
   • Total Payloads: {total_payloads}

📊 DRONE MODES
   • Exploring: {exploring}
   • Delivering: {delivering}
   • Returning: {returning}

🎯 EFFICIENCY
   • Rescue Rate: {rescued_survivors/max(1, self.model.steps):.3f}/step
   • Coverage: {len(self.model.shared_map)}/{total_survivors} found
        """
        
        self.ax_stats.text(0.05, 0.95, stats_text, 
                          transform=self.ax_stats.transAxes,
                          fontsize=10, verticalalignment='top',
                          fontfamily='monospace',
                          bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    def animate(self, frames=500, interval=100, save_path=None):
        """Create animation of the simulation"""
        def update(frame):
            if self.model.running:
                self.model.step()
            return self.draw_frame(frame)
        
        anim = FuncAnimation(self.fig, update, frames=frames, 
                           interval=interval, blit=False, repeat=False)
        
        if save_path:
            anim.save(save_path, writer='pillow', fps=10)
            print(f"Animation saved to {save_path}")
        
        plt.show()
        return anim
    
    def run_static(self, steps=100):
        """Run simulation and show final state"""
        for _ in range(steps):
            if self.model.running:
                self.model.step()
            else:
                break
        
        self.draw_frame()
        plt.show()
    
    def save_snapshot(self, filename='snapshot.png'):
        """Save current state as image"""
        self.draw_frame()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Snapshot saved to {filename}")
        plt.close()
