"""
Test script for the Ax Bayesian Optimization runner.
"""

from bayesian_optimizer import state
from bayesian_optimizer.ax_runner import run_bo_campaign

def test_ax_runner():
    """
    Test the Ax runner with simulated experiments.
    """
    print("="*80)
    print("TESTING Ax Bayesian Optimization Runner")
    print("="*80)
    
    # Configuration
    config_file = "test_config_simulated.json"
    state_path = "test_results/ax_state_test.json"
    trials = 5  # Run 5 test iterations
    save_every = 1  # Save state after every trial
    
    # Objective thresholds
    percent_yield_threshold = 50.0  # 50% yield minimum
    throughput_threshold = 5.0  # 5 nmol/min minimum
    
    # Noise for Ax (standard error of the mean)
    noise_sem = 0.1
    
    # Run in simulation mode
    simulation_mode = True
    
    print(f"\n1. Configuration:")
    print(f"   Config file: {config_file}")
    print(f"   State path: {state_path}")
    print(f"   Trials: {trials}")
    print(f"   Yield threshold: {percent_yield_threshold}%")
    print(f"   Throughput threshold: {throughput_threshold} nmol/min")
    print(f"   Simulation mode: {simulation_mode}")
    
    print(f"\n2. Running Bayesian Optimization Campaign...")
    print("-" * 80)
    
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
        
        print("-" * 80)
        print("\n✓ SUCCESS - Bayesian Optimization campaign completed!")
        print("="*80)
        print("TEST PASSED ✓")
        print("="*80)
        
    except Exception as e:
        print("-" * 80)
        print(f"\n✗ FAILED - Error occurred!")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {e}")
        
        import traceback
        print(f"\n   Full traceback:")
        traceback.print_exc()
        
        print("="*80)
        print("TEST FAILED ✗")
        print("="*80)
        raise


if __name__ == "__main__":
    test_ax_runner()
