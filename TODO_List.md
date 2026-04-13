# TODO List — Paper Submission Roadmap

## Phase 1 — Critical Bug Fixes (do these first)

Solved 

- [ ] **Fix undefined variable bug** — `experimental_commands/execute_bo_iteration_commands.py:175`
  - `bo_parameters` is used before it's defined (defined 9 lines later at line 184)
  - Replace with `bo_ca/clearmpaign_state.bo_parameters` at the call site

- [x] **Fix missing import + broken relative import** — `production_run/production_run.py`
  - Line 51 calls `calculate_production_run_parameters()` with no import
  - Add: `from production_run.calculate_production_run_parameters import calculate_production_run_parameters`
  - Fix broken relative import on line 20

---

## Phase 2 — Complete the Production Run Module

- [ ] **Implement `generate_production_run_commands.py`** — currently an empty file
  - Mirror `generate_experimental_commands.py` pattern for scale-up conditions
  - Use `commands.py` CSV-saving pattern with `IterationState` instrument parameters

- [ ] **Wire production run into `main.py`**
  - Uncomment and fix the production run block (lines 123–132)
  - Pipeline: `extract_best_reaction_conditions.py` → `calculate_production_run_parameters.py` → `generate_production_run_commands.py`

- [x] **Add production run tests**
  - `test/test_production_run/test_extract_best_reaction_conditions.py` — Pareto selection, yield threshold filtering
  - `test/test_production_run/test_calculate_production_run_parameters.py` — mole production math, edge cases

---

## Phase 3 — Debugging & Robustness

TODO Need to inspect this, not affecting experiments but should resolve

- [ ] **Fix validation stubs** — `preprocessing/experimental_parameters.py`
  - `check_required_complete_workflow_parameters()` and `check_required_production_run_parameters()` are stubs
  - Logic error on lines 94–107: checks same condition twice
  - Implement proper key-presence validation

- [ ] **Distinguish hardware failure from intentional convergence** — `post_processing/detect_early_convergence.py`
  - Add a flag or return value to tell apart "converged early intentionally" vs "plateau due to hardware issue"
  - Propagate this flag up through `execute_bo_iteration_commands.py` for logging

- [ ] **Consistent error handling** in `execute_bo_iteration_commands.py`
  - Catch exception types from `utils/experiment_aborted.py` hierarchy distinctly
  - Ensure post-processing errors don't silently swallow hardware failures

---

## Phase 4 — Dead Code & Cleanup

- [ ] **Commented-out pump 4 code** — check mechanical status first, then either restore or document with a dated note
  - `experimental_commands/generate_instrument_config.py`
  - `experimental_commands/generate_wash_commands.py`
  - `main.py` lines 123–132 (restore after Phase 2)

- [ ] **Resolve priority TODOs** (27+ exist across codebase):
  - `run_bo_campaign.py:216` — magic number 30 default trials → move to config with fallback
  - `experiment_state.py` — empirical SEM values (currently 1.0 default) → add config override + document
  - `utils/test_response_surfaces.py` — expand or remove if unused

- [ ] **Remove empty file or implement it**: `experimental_commands/generate_production_run_commands.py`

- [x] **Fix relative import inconsistency** in `production_run/` — standardize to absolute imports

---

## Phase 5 — Test Expansion

| New Test File | What to Cover |
|---|---|
| ~~`test/test_production_run/test_extract_best_reaction_conditions.py`~~ ✓ Done | Pareto selection, yield threshold filtering |
| ~~`test/test_production_run/test_calculate_production_run_parameters.py`~~ ✓ Done | Mole production math, edge cases |
| `test/test_experimental_commands/test_execute_bo_iteration_commands.py` | Integration test using simulation mode (no hardware skip) |
| `test/test_post_processing/test_detect_early_convergence.py` | Hardware-failure vs intentional convergence |
| `test/test_preprocessing/test_experimental_parameters.py` | Validation functions (after Phase 3 fix) |

- [ ] Update `test/test_bayesian_optimizer/test_run_simulated_bo.py` to exercise full loop including production run
- [ ] Document what hardware the skipped tests in `test_experimental_commands/` require

---

## Phase 6 — Paper Submission Polish

- [ ] **Write README.md** — currently just headers
  - Add: project overview, installation (conda env), quick-start (simulation mode), config file format, paper citation placeholder, license

- [ ] **Standardize docstrings** — Google style is already most common; apply to new/changed functions only

- [ ] **Update copyright years** — some headers say 2025, others 2026 → standardize to 2026

- [ ] **Add a note** in `generate_instrument_config.py` clarifying pump 4 is a hardware issue, not a code bug

---

## Verification

Run full test suite after each phase:
```bash
/home/scott/anaconda3/envs/project_dead_mans_fingers/bin/python -m pytest test/ -v
```

End-to-end simulation check:
```bash
/home/scott/anaconda3/envs/project_dead_mans_fingers/bin/python main.py test/test_config_ax_demo.json --simulation
```