#!/usr/bin/env python3
"""
Swarm Rescue - Multi-Agent Drone Disaster Response Simulation
Main entry point for running the simulation.
"""

import argparse
import sys
from model import SwarmRescueModel
from visualization import SwarmRescueVisualization


def main():
    parser = argparse.ArgumentParser(
        description='Swarm Rescue - Multi-Agent Drone Disaster Response Simulation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default parameters (animated)
  python main.py
  
  # Run with custom parameters
  python main.py --drones 8 --survivors 30 --width 60 --height 60
  
  # Run without animation (faster)
  python main.py --no-animation --steps 200
  
  # Save animation as GIF
  python main.py --save-animation simulation.gif
  
  # Save final snapshot
  python main.py --no-animation --steps 100 --save-snapshot result.png
        """
    )
    
    # Simulation parameters
    parser.add_argument('--width', type=int, default=50,
                       help='Grid width (default: 50)')
    parser.add_argument('--height', type=int, default=50,
                       help='Grid height (default: 50)')
    parser.add_argument('--drones', type=int, default=5,
                       help='Number of drones (default: 5)')
    parser.add_argument('--survivors', type=int, default=20,
                       help='Number of survivors (default: 20)')
    parser.add_argument('--detection-radius', type=int, default=3,
                       help='Drone detection radius (default: 3)')
    parser.add_argument('--seed', type=int, default=None,
                       help='Random seed for reproducibility (default: None)')
    
    # Visualization parameters
    parser.add_argument('--no-animation', action='store_true',
                       help='Run without animation (faster)')
    parser.add_argument('--steps', type=int, default=500,
                       help='Maximum number of steps (default: 500)')
    parser.add_argument('--interval', type=int, default=100,
                       help='Animation interval in ms (default: 100)')
    parser.add_argument('--save-animation', type=str, default=None,
                       help='Save animation to file (e.g., simulation.gif)')
    parser.add_argument('--save-snapshot', type=str, default=None,
                       help='Save final snapshot to file (e.g., result.png)')
    
    args = parser.parse_args()
    
    # Print banner
    print("=" * 70)
    print("🚁 SWARM RESCUE - Multi-Agent Drone Disaster Response Simulation 🚁")
    print("=" * 70)
    print(f"\n📋 Configuration:")
    print(f"   Grid Size: {args.width}x{args.height}")
    print(f"   Drones: {args.drones}")
    print(f"   Survivors: {args.survivors}")
    print(f"   Detection Radius: {args.detection_radius}")
    print(f"   Max Steps: {args.steps}")
    if args.seed:
        print(f"   Random Seed: {args.seed}")
    print()
    
    # Create model
    print("🔧 Initializing simulation...")
    model = SwarmRescueModel(
        width=args.width,
        height=args.height,
        num_drones=args.drones,
        num_survivors=args.survivors,
        detection_radius=args.detection_radius,
        seed=args.seed
    )
    
    # Create visualization
    viz = SwarmRescueVisualization(model)
    
    print("✅ Simulation initialized!")
    print(f"🎯 Mission: Rescue {args.survivors} survivors using {args.drones} drones")
    print("\n🚀 Starting simulation...\n")
    
    # Run simulation
    try:
        if args.no_animation:
            # Run without animation
            viz.run_static(steps=args.steps)
            
            if args.save_snapshot:
                viz.save_snapshot(args.save_snapshot)
        else:
            # Run with animation
            viz.animate(
                frames=args.steps,
                interval=args.interval,
                save_path=args.save_animation
            )
    except KeyboardInterrupt:
        print("\n\n⚠️  Simulation interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during simulation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Print final statistics
    print("\n" + "=" * 70)
    print("📊 FINAL STATISTICS")
    print("=" * 70)
    
    total_survivors = sum(1 for a in model.schedule.agents 
                         if hasattr(a, 'is_rescued'))
    rescued_survivors = sum(1 for a in model.schedule.agents 
                           if hasattr(a, 'is_rescued') and a.is_rescued)
    
    print(f"⏱️  Total Steps: {model.schedule.steps}")
    print(f"👥 Survivors Rescued: {rescued_survivors}/{total_survivors} ({rescued_survivors/total_survivors*100:.1f}%)")
    print(f"🔍 Survivors Found: {len(model.shared_map)}/{total_survivors}")
    
    active_drones = sum(1 for a in model.schedule.agents 
                       if hasattr(a, 'battery') and a.battery > 0)
    print(f"🚁 Active Drones: {active_drones}/{args.drones}")
    
    if rescued_survivors == total_survivors:
        print("\n🎉 SUCCESS! All survivors rescued!")
    elif active_drones == 0:
        print("\n⚠️  MISSION INCOMPLETE: All drones depleted")
    else:
        print(f"\n⏸️  SIMULATION ENDED: {rescued_survivors} survivors rescued")
    
    print("=" * 70)
    print("\n✨ Thank you for using Swarm Rescue!")


if __name__ == "__main__":
    main()
