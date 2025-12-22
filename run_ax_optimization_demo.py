"""
Ax Bayesian Optimization Demo - Run a complete optimization campaign.

This script runs a Bayesian optimization campaign using the Ax platform
with simulated experiments. Results are saved to: ./ax_optimization_demo_results/
"""

from bayesian_optimizer.ax_runner import run_bo_campaign

def main():
    """
    Run Ax Bayesian Optimization campaign with simulated experiments.
    """
    print("="*80)
    print("AX BAYESIAN OPTIMIZATION DEMO")
    print("="*80)
    print()
    print("This will run a multi-objective Bayesian optimization to maximize:")
    print("  1. Percent Yield")
    print("  2. Throughput (nmol/min)")
    print()
    print("Results will be saved to: ./ax_optimization_demo_results/")
    print("="*80)
    print()
    
    # Configuration
    config_file = "test_config_ax_demo.json"
    output_dir = "./ax_optimization_demo_results"
    state_path = f"{output_dir}/ax_optimization_state.json"
    trials = 10  # Run 10 optimization trials
    save_every = 1  # Save state after every trial
    
    # Objective thresholds (minimum acceptable values)
    percent_yield_threshold = 50.0  # 50% yield minimum
    throughput_threshold = 5.0  # 5 nmol/min minimum
    
    # Noise estimate for Ax (standard error of the mean)
    noise_sem = 0.1
    
    # Run in simulation mode with 30x time speedup
    simulation_mode = True
    
    print(f"Configuration:")
    print(f"  Config file: {config_file}")
    print(f"  Output directory: {output_dir}")
    print(f"  State file: {state_path}")
    print(f"  Number of trials: {trials}")
    print(f"  Yield threshold: {percent_yield_threshold}%")
    print(f"  Throughput threshold: {throughput_threshold} nmol/min")
    print(f"  Simulation mode: {simulation_mode} (30x speedup)")
    print()
    print("-" * 80)
    print()
    
    try:
        run_bo_campaign(
            input_experimental_parameters=config_file,
            trials=trials,
            state_path=state_path,
            save_every=save_every,
            objA_threshold=percent_yield_threshold,
            objB_threshold=throughput_threshold,
            noise_sem=noise_sem,
            simulation_mode=simulation_mode,
        )
        
        print()
        print("="*80)
        print("OPTIMIZATION COMPLETE!")
        print("="*80)
        print()
        print(f"Results saved to: {output_dir}/")
        print(f"  - Optimization state: {state_path}")
        print(f"  - Experimental data: {output_dir}/BO_results_ax_demo.csv")
        print(f"  - UV-Vis plots: {output_dir}/realtime_uvvis_iteration_*.png")
        print(f"  - Summary plots: {output_dir}/bo_optimization_summary.png")
        print()
        print("✓ SUCCESS")
        print("="*80)
        
    except Exception as e:
        print()
        print("="*80)
        print("✗ OPTIMIZATION FAILED")
        print("="*80)
        print(f"Error: {e}")
        print()
        
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
