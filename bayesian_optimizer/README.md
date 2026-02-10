# Bayesian Optimizer Module

This module implements multi-objective Bayesian optimization for the project_dead_mans_fingers automated flow chemistry platform.

## Quick Reference

### Module Structure

```
bayesian_optimizer/
├── run_bo_campaign.py       # Campaign orchestrator (runs n trials)
├── init_or_load_ax.py       # Ax client initialization
├── evaluate_ax.py           # Experiment wrapper for Ax
├── experiment_executor.py   # Single experiment execution engine
└── state.py                 # Global state management
```

### Module Responsibilities

| Module | Purpose | Key Function |
|--------|---------|--------------|
| **run_bo_campaign.py** | High-level orchestrator for multi-trial optimization campaigns | `run_bo_campaign()` |
| **init_or_load_ax.py** | Creates or loads Ax client with search space and objectives | `_init_or_load_ax()` |
| **evaluate_ax.py** | Wraps experiment execution for Ax, handles errors | `evaluate_ax()` |
| **experiment_executor.py** | Executes single experiments (simulation or hardware) | `run_bayesian_optimization_iteration()` |
| **state.py** | Manages global state (parameters, cache, iteration counter) | Global variables |

### Call Chain

```
main.py
  └─ run_bo_campaign()           [run_bo_campaign.py]
      ├─ _init_or_load_ax()      [init_or_load_ax.py]
      └─ FOR each trial:
          └─ evaluate_ax()       [evaluate_ax.py]
              └─ run_bayesian_optimization_iteration()  [experiment_executor.py]
                  └─ Returns (percent_yield, throughput)
```

### File Naming Rationale

- **`run_bo_campaign.py`** - Runs the entire **campaign** (multiple trials)
- **`experiment_executor.py`** - Executes a single **experiment** (one trial)

Previously named `bayesian_optimization_run.py`, renamed for clarity.

## For More Details

See [BAYESIAN_OPTIMIZER_WORKFLOW.md](../BAYESIAN_OPTIMIZER_WORKFLOW.md) for comprehensive documentation including:
- Complete workflow explanation
- Detailed module descriptions
- Data flow diagrams
- Simulation vs hardware mode
- Troubleshooting guide
- Advanced usage examples
