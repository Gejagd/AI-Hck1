#!/usr/bin/env python3
"""
Analysis script for Swarm Rescue simulation.
Runs multiple simulations and generates performance charts.
"""

import matplotlib.pyplot as plt
import numpy as np
from model import SwarmRescueModel
import pandas as pd


def run_experiment(num_drones, num_survivors, num_runs=5, max_steps=500):
    """
    Run multiple simulations with given parameters and collect statistics.
    """
    results = []
    
    for run in range(num_runs):
        print(f"Running experiment: {num_drones} drones, {num_survivors} survivors, run {run+1}/{num_runs}")
        
        model = SwarmRescueModel(
            width=50,
            height=50,
            num_drones=num_drones,
            num_survivors=num_survivors,
            detection_radius=3,
            seed=run  # Different seed for each run
        )
        
        # Run simulation
        for step in range(max_steps):
            if model.running:
                model.step()
            else:
                break
        
        # Collect results
        total_survivors = sum(1 for a in model.schedule.agents if hasattr(a, 'is_rescued'))
        rescued_survivors = sum(1 for a in model.schedule.agents 
                               if hasattr(a, 'is_rescued') and a.is_rescued)
        
        results.append({
            'num_drones': num_drones,
            'num_survivors': num_survivors,
            'run': run,
            'steps_taken': model.schedule.steps,
            'survivors_rescued': rescued_survivors,
            'survivors_found': len(model.shared_map),
            'rescue_rate': rescued_survivors / total_survivors,
            'efficiency': rescued_survivors / model.schedule.steps if model.schedule.steps > 0 else 0
        })
    
    return results


def compare_drone_counts():
    """
    Compare performance with different numbers of drones.
    """
    print("\n" + "="*70)
    print("EXPERIMENT 1: Comparing Different Drone Counts")
    print("="*70 + "\n")
    
    drone_counts = [3, 5, 8, 10]
    num_survivors = 20
    all_results = []
    
    for num_drones in drone_counts:
        results = run_experiment(num_drones, num_survivors, num_runs=5)
        all_results.extend(results)
    
    df = pd.DataFrame(all_results)
    
    # Create plots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Performance Comparison: Different Drone Counts', fontsize=16, fontweight='bold')
    
    # Plot 1: Steps taken
    ax1 = axes[0, 0]
    df_grouped = df.groupby('num_drones')['steps_taken'].agg(['mean', 'std'])
    ax1.bar(df_grouped.index, df_grouped['mean'], yerr=df_grouped['std'], 
            capsize=5, alpha=0.7, color='steelblue')
    ax1.set_xlabel('Number of Drones')
    ax1.set_ylabel('Steps Taken')
    ax1.set_title('Average Steps to Complete Mission')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Rescue rate
    ax2 = axes[0, 1]
    df_grouped = df.groupby('num_drones')['rescue_rate'].agg(['mean', 'std'])
    ax2.bar(df_grouped.index, df_grouped['mean'], yerr=df_grouped['std'], 
            capsize=5, alpha=0.7, color='forestgreen')
    ax2.set_xlabel('Number of Drones')
    ax2.set_ylabel('Rescue Rate')
    ax2.set_title('Average Rescue Rate (Rescued/Total)')
    ax2.set_ylim([0, 1.1])
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Efficiency
    ax3 = axes[1, 0]
    df_grouped = df.groupby('num_drones')['efficiency'].agg(['mean', 'std'])
    ax3.bar(df_grouped.index, df_grouped['mean'], yerr=df_grouped['std'], 
            capsize=5, alpha=0.7, color='coral')
    ax3.set_xlabel('Number of Drones')
    ax3.set_ylabel('Efficiency (Rescued/Step)')
    ax3.set_title('Average Rescue Efficiency')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Survivors found vs rescued
    ax4 = axes[1, 1]
    df_grouped = df.groupby('num_drones')[['survivors_found', 'survivors_rescued']].mean()
    x = np.arange(len(df_grouped.index))
    width = 0.35
    ax4.bar(x - width/2, df_grouped['survivors_found'], width, label='Found', alpha=0.7, color='orange')
    ax4.bar(x + width/2, df_grouped['survivors_rescued'], width, label='Rescued', alpha=0.7, color='green')
    ax4.set_xlabel('Number of Drones')
    ax4.set_ylabel('Count')
    ax4.set_title('Survivors Found vs Rescued')
    ax4.set_xticks(x)
    ax4.set_xticklabels(df_grouped.index)
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('drone_count_comparison.png', dpi=300, bbox_inches='tight')
    print("\n✅ Chart saved as 'drone_count_comparison.png'")
    plt.show()
    
    return df


def compare_survivor_counts():
    """
    Compare performance with different numbers of survivors.
    """
    print("\n" + "="*70)
    print("EXPERIMENT 2: Comparing Different Survivor Counts")
    print("="*70 + "\n")
    
    num_drones = 5
    survivor_counts = [10, 20, 30, 40]
    all_results = []
    
    for num_survivors in survivor_counts:
        results = run_experiment(num_drones, num_survivors, num_runs=5)
        all_results.extend(results)
    
    df = pd.DataFrame(all_results)
    
    # Create plots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Performance Comparison: Different Survivor Counts', fontsize=16, fontweight='bold')
    
    # Plot 1: Steps taken
    ax1 = axes[0, 0]
    df_grouped = df.groupby('num_survivors')['steps_taken'].agg(['mean', 'std'])
    ax1.plot(df_grouped.index, df_grouped['mean'], marker='o', linewidth=2, markersize=8, color='steelblue')
    ax1.fill_between(df_grouped.index, 
                     df_grouped['mean'] - df_grouped['std'],
                     df_grouped['mean'] + df_grouped['std'],
                     alpha=0.3, color='steelblue')
    ax1.set_xlabel('Number of Survivors')
    ax1.set_ylabel('Steps Taken')
    ax1.set_title('Steps vs Survivor Count')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Rescue rate
    ax2 = axes[0, 1]
    df_grouped = df.groupby('num_survivors')['rescue_rate'].agg(['mean', 'std'])
    ax2.plot(df_grouped.index, df_grouped['mean'], marker='s', linewidth=2, markersize=8, color='forestgreen')
    ax2.fill_between(df_grouped.index,
                     df_grouped['mean'] - df_grouped['std'],
                     df_grouped['mean'] + df_grouped['std'],
                     alpha=0.3, color='forestgreen')
    ax2.set_xlabel('Number of Survivors')
    ax2.set_ylabel('Rescue Rate')
    ax2.set_title('Rescue Rate vs Survivor Count')
    ax2.set_ylim([0, 1.1])
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Efficiency
    ax3 = axes[1, 0]
    df_grouped = df.groupby('num_survivors')['efficiency'].agg(['mean', 'std'])
    ax3.plot(df_grouped.index, df_grouped['mean'], marker='^', linewidth=2, markersize=8, color='coral')
    ax3.fill_between(df_grouped.index,
                     df_grouped['mean'] - df_grouped['std'],
                     df_grouped['mean'] + df_grouped['std'],
                     alpha=0.3, color='coral')
    ax3.set_xlabel('Number of Survivors')
    ax3.set_ylabel('Efficiency (Rescued/Step)')
    ax3.set_title('Efficiency vs Survivor Count')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Scalability
    ax4 = axes[1, 1]
    df_grouped = df.groupby('num_survivors')['survivors_rescued'].agg(['mean', 'std'])
    ax4.plot(df_grouped.index, df_grouped['mean'], marker='D', linewidth=2, markersize=8, 
             color='purple', label='Actual Rescued')
    ax4.plot(df_grouped.index, df_grouped.index, '--', linewidth=2, color='gray', 
             label='Ideal (All Rescued)', alpha=0.7)
    ax4.fill_between(df_grouped.index,
                     df_grouped['mean'] - df_grouped['std'],
                     df_grouped['mean'] + df_grouped['std'],
                     alpha=0.3, color='purple')
    ax4.set_xlabel('Number of Survivors')
    ax4.set_ylabel('Survivors Rescued')
    ax4.set_title('Scalability Analysis')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('survivor_count_comparison.png', dpi=300, bbox_inches='tight')
    print("\n✅ Chart saved as 'survivor_count_comparison.png'")
    plt.show()
    
    return df


def main():
    """Run all experiments"""
    print("🚁 SWARM RESCUE - Performance Analysis")
    print("="*70)
    print("This script will run multiple experiments to analyze performance.")
    print("This may take several minutes...\n")
    
    # Run experiments
    df1 = compare_drone_counts()
    df2 = compare_survivor_counts()
    
    # Save results to CSV
    df1.to_csv('drone_count_results.csv', index=False)
    df2.to_csv('survivor_count_results.csv', index=False)
    
    print("\n" + "="*70)
    print("📊 ANALYSIS COMPLETE")
    print("="*70)
    print("\n✅ Results saved:")
    print("   - drone_count_comparison.png")
    print("   - survivor_count_comparison.png")
    print("   - drone_count_results.csv")
    print("   - survivor_count_results.csv")
    print("\n✨ Analysis complete!")


if __name__ == "__main__":
    main()
