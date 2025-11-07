# 🚁 Swarm Rescue - Multi-Agent Drone Disaster Response Simulation

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

A sophisticated multi-agent simulation system demonstrating coordinated drone swarms for disaster response and survivor rescue operations. Built with Mesa framework for agent-based modeling.

## 🎯 Project Overview

**Swarm Rescue** simulates a team of autonomous drones that:
- 🔍 **Explore** disaster areas to detect survivors
- 📡 **Communicate** via shared map to avoid redundant searching
- 🎯 **Coordinate** rescue operations efficiently
- 📦 **Deliver** aid payloads to survivors
- 🔋 **Manage** battery and resource constraints
- 🏠 **Return** to base for recharging and reloading

### Key Features

- **Multi-Agent Coordination**: Drones share information through a global communication map
- **Intelligent Exploration**: Random exploration with visited cell tracking
- **Dynamic State Management**: Drones switch between EXPLORING, DELIVERING, and RETURN_TO_BASE modes
- **Resource Constraints**: Battery management and payload capacity
- **Real-time Visualization**: Beautiful Matplotlib-based animation with statistics
- **Configurable Parameters**: Customize grid size, drone count, detection radius, and more
- **Data Collection**: Built-in metrics tracking for analysis

## 🏗️ Architecture

### Agent Types

1. **DroneAgent**
   - States: `position`, `battery`, `mode`, `payloads`, `visited_cells`
   - Behaviors: `explore`, `detect`, `move_to_target`, `deliver`, `return_to_base`
   - Detection radius: Configurable sensor range

2. **SurvivorAgent**
   - States: `position`, `is_rescued`, `rescue_time`
   - Passive agents waiting for rescue

### Model Components

- **Grid Environment**: 2D MultiGrid for spatial simulation
- **Shared Communication Map**: Global knowledge base for drone coordination
- **Scheduler**: RandomActivation for agent step execution
- **Data Collector**: Automatic metrics tracking

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or download the repository**

```bash
cd AIH
```

2. **Create virtual environment (recommended)**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

## 🚀 Usage

### Basic Usage

Run with default parameters:

```bash
python main.py
```

### Advanced Usage

#### Custom Configuration

```bash
# Large-scale simulation
python main.py --drones 10 --survivors 50 --width 80 --height 80

# High detection radius
python main.py --detection-radius 5

# Fast simulation without animation
python main.py --no-animation --steps 200
```

#### Save Output

```bash
# Save animation as GIF
python main.py --save-animation rescue_mission.gif

# Save final snapshot
python main.py --no-animation --steps 100 --save-snapshot final_state.png
```

#### Reproducible Results

```bash
# Use random seed for reproducibility
python main.py --seed 42
```

### Command-Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--width` | int | 50 | Grid width |
| `--height` | int | 50 | Grid height |
| `--drones` | int | 5 | Number of drones |
| `--survivors` | int | 20 | Number of survivors |
| `--detection-radius` | int | 3 | Drone detection radius |
| `--seed` | int | None | Random seed |
| `--no-animation` | flag | False | Disable animation |
| `--steps` | int | 500 | Maximum simulation steps |
| `--interval` | int | 100 | Animation interval (ms) |
| `--save-animation` | str | None | Save animation path |
| `--save-snapshot` | str | None | Save snapshot path |

## 📊 Visualization

The simulation provides rich visual feedback:

### Grid View
- 🟡 **Base Station**: Central recharge/reload point
- 🔵 **Exploring Drones**: Searching for survivors
- 🔴 **Delivering Drones**: En route to rescue
- 🟣 **Returning Drones**: Going back to base
- ❌ **Waiting Survivors**: Need rescue (pink)
- ⭕ **Rescued Survivors**: Successfully saved (green)
- 🔵 **Detection Radius**: Transparent circles around drones

### Statistics Panel
- ⏱️ Current step count
- 👥 Survivor statistics (total, rescued, waiting, progress)
- 🚁 Drone status (total, active, inactive)
- 🔋 Battery levels and payload counts
- 📊 Mode distribution (exploring/delivering/returning)
- 🎯 Efficiency metrics (rescue rate, coverage)

## 🧪 Example Scenarios

### Scenario 1: Quick Rescue (Small Scale)
```bash
python main.py --drones 3 --survivors 10 --width 30 --height 30
```

### Scenario 2: Large Disaster Area
```bash
python main.py --drones 8 --survivors 40 --width 70 --height 70 --detection-radius 4
```

### Scenario 3: Limited Resources
```bash
python main.py --drones 4 --survivors 30 --detection-radius 2
```

## 🎓 Technical Details

### Optimization Goal

The system optimizes:
```
maximize (survivors_rescued + survivors_found) / time_elapsed
```

### Drone Decision Logic

1. **Battery Check**: Return to base if battery < 30% or no payloads
2. **Communication**: Check shared map for known survivors
3. **Mode Execution**:
   - **EXPLORING**: Random walk with visited cell tracking
   - **DELIVERING**: Move toward target survivor
   - **RETURN_TO_BASE**: Navigate back to base
4. **Detection**: Scan within radius for survivors
5. **Delivery**: Rescue survivor when at target location

### Coordination Strategy

- **Shared Map**: Global communication prevents duplicate efforts
- **Being Helped Flag**: Marks survivors being targeted by other drones
- **Distance-Based Assignment**: Drones target nearest unassigned survivors
- **Dynamic Reallocation**: Drones switch targets based on new discoveries

## 🔬 For Hackathon Judges

### Innovation Points

1. **Multi-Agent Coordination**: Demonstrates emergent swarm behavior
2. **Resource Management**: Realistic battery and payload constraints
3. **Scalability**: Handles various grid sizes and agent counts
4. **Visualization**: Professional real-time monitoring
5. **Extensibility**: Easy to add new features (thermal imaging, obstacles, etc.)

### Potential Extensions

- 🌡️ **Thermal Imaging**: Add heat signature detection
- 🚧 **Obstacles**: Implement pathfinding around barriers
- 📶 **Limited Communication**: Simulate range-based communication
- 🤖 **Reinforcement Learning**: Train drones with RL algorithms
- 🌐 **Real Drone Integration**: Connect to DJI SDK or similar APIs
- 🗺️ **3D Terrain**: Extend to 3D environment with elevation

## 📈 Performance Metrics

The system tracks:
- Total survivors rescued
- Time to complete mission
- Battery efficiency
- Coverage percentage
- Rescue rate per step
- Drone utilization

## 🤝 Contributing

This project was built for a hackathon demonstration. Feel free to:
- Add new features
- Improve algorithms
- Enhance visualization
- Optimize performance

## 📄 License

MIT License - Feel free to use for educational and demonstration purposes.

## 🙏 Acknowledgments

- Built with [Mesa](https://mesa.readthedocs.io/) - Agent-based modeling framework
- Visualization powered by [Matplotlib](https://matplotlib.org/)
- Inspired by real-world disaster response challenges

## 📞 Contact

For questions or collaboration opportunities, please reach out!

---

**Made with ❤️ for disaster response innovation**

🚁 *Saving lives through intelligent coordination* 🚁
