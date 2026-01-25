# Dead Man’s Fingers  
## Automated Flow Platform for Bayesian Optimization (Xylopyridine Analogs)

This repository controls an automated flow-chemistry platform that optimizes photochemical reactions of xylopyridine analogs using Bayesian optimization. In each campaign, the platform:

1) Selects a set of xylopyridine analogs.

2) Initializes a Bayesian optimization routine over experimental conditions.

3) Executes experiments based on optimizer-proposed conditions.

4) Quantifies each experiment via UV–Vis spectroscopy, calculating yield and throughput.

5) Proposes the next experiment iteratively.

6) Terminates when predefined stopping criteria are met.

7) Optionally transitions the optimized conditions to a production run to generate a target quantity (grams or moles) of the selected analog.

---

## High Priority TODOs

- [ ] Add light safety interlock: auto shutoff if UV-Vis errors or absorbance is out of range
- [ ] Connect Arduino-controlled light intensity and integrate with experiment orchestration
- [ ] Prevent overwriting prior run outputs (iteration-stamped directories + hard fails on collisions)
- [ ] Add a live optimization GUI: progress plots + snapshot export + optional full UV-Vis spectrum export (e.g., every N runs)
- [ ] Enable per-analog Bayesian optimization (hold analog constant; optimize within each analog)
- [ ] Add a GUI for setting BO parameters (run count, bounds, objectives) to avoid terminal configuration
- [ ] Add a short “Getting Started” tutorial for new users (hardware map + run procedure)
- [ ] Provide a Linux-based production runner for stable BO execution
- [ ] Refactor to production-grade code after a stable workflow is validated

## Low Priority TODOs

- [ ] Add a pre-check valve path to UV-Vis to verify concentration prior to each reaction step

---

# TODO Need to figure out how to clean it up to make sure it clearer to the reader 
## Module Descriptions

- **6-Way Valve 1 (Analog Selection)**  
  Selects which xylopyridine analog is routed to the system for optimization.
  The valve position (**$V_1$**) selects analog to use before the optimization begins.

- **Pump 1 (Substrate Feed)**  
  Delivers the selected xylopyridine analog dissolved in 0.1 M HCl(aq).  
  The flow rate (**$F_1$**) is a tunable optimization parameter.

- **Pump 2 (Dilution Feed)**  
  Adds 0.1 M HCl(aq) for dilution.  
  The flow rate (**$F_2$**) is a tunable optimization parameter.

- **6-Way Valve 2 + Pump 3 (Co-solvent Selection)**  
  The optimizer selects the co-solvent via valve position and controls its flow rate using Pump 3.  
  The valve position (**$V_2$**) flow rate (**$F_3$**) is a tunable optimization parameter.

- **Temperature Control (Peltier Module)**  
  Regulates the reactor temperature.  
  The setpoint temperature (**$T$**, °C) is a tunable optimization parameter.

- **Light Source (Photoreactor)**  
  Mirror-box photoreactor providing 365 nm irradiation with a tunable power output (0–400 W).  
  The Light intensity (**$I$**) is a tunable optimization parameter.

- **2-Way Valve 1 (Analysis Routing)**  
  Directs the reactor effluent either to the UV–Vis detector during optimization or to an alternative outlet when analysis is not required.
  The valve position (**$V_3$**) is selected before the optimization begins

- **Pump 4 (UV Conditioning)**  
  Performs post-reactor dilution to achieve a target absorbance range prior to UV–Vis analysis, maintaining a standardized concentration before detection.
  The flow rate (**$F_4$**) is a tunable optimization parameter.


- **UV–Vis Detector and Analysis**  
  Measures absorbance of reactants and products and converts spectra to concentrations.  
  These values are used to calculate ** percent yield** and **throughput**.

- **10-Way Valve 1 (Waste Selection)**  
  Routes the reactor output to the appropriate waste stream based on the selected xylopyridine analog.
  The valve position (**$V_4$**) is selected before the optimization begins

- **Bayesian Optimizer**  
  Aggregates all prior experimental results and proposes the next set of experimental conditions.
 

2) Variables, notation, and assumptions
Flow rates (use consistent units)


Flow rates (use consistent units)

- **$F_1$**: Pump 1 flow rate (substrate feed), e.g., µL/min or mL/min

- **$F_2$**: Pump 2 flow rate (acid dilution), e.g., µL/min or mL/min

- **$F_3$**: Pump 3 flow rate (co-solvent dilution), e.g., µL/min or mL/min

- **$F_4$**: Pump 4 flow rate (post-reactor dilution before UV-Vis), e.g., µL/min or mL/min

- **$F_{123}$**: Total flow through the reactor (sum of Pumps 1–3): $F_{123} = F_1 + F_2 + F_3$

- **$F_{1234}$**: Total flow through the UV-detector (sum of Pumps 1–4): $F_{1234} = F_1 + F_2 + F_3 + F_4$


Concentrations

- **$C_1$**: xylopyridine concentration in Pump 1 feed (nmol/L)

- **$C_{S,\text{in}}$**: substrate concentration entering the reactor bed(nmol/L)

- **$C_{S,\text{out}}$**: substrate concentration exiting the reactor bed(nmol/L)

- **$C_{P,\text{out}}$**: product concentration exiting the reactor bed(nmol/L)

- **$C_{S,UV}$**: substrate concentration in the UV cell after Pump 4 (mol/L)

- **$C_{P,UV}$**: product concentration in the UV cell after Pump 4 (mol/L)

Dilutions

- **$D_4$**: Pump 4 dilution factor, $D_4 = \frac{F_{123} + F_4}{F_{123}}$

Temperature

- **$T$**: Reactor temperature (°C)

Light Intensity

- **$I$**: Light intensity (W or % of maximum)

Assumptions used for dilution math

Junctions are treated as well-mixed (ideal mixing).

Pumps 2–4 contain no xylopyridine (diluent only).

Pump 4 is post-reactor and does not change true reactor throughput.

3) Step-by-step: one optimization iteration (with math)
Step 0 — Prepare and prime (one-time per run)

Fill reservoirs (analogs, 0.1 M HCl, co-solvents, Pump 4 diluent).

Prime lines and remove bubbles (especially the UV flow cell).

Set safe defaults (Peltier setpoint, light off/standby).

Verify the post-reactor valve can switch between Collect and Analyze.

Step 1 — Optimizer proposes an experiment

For iteration k, the optimizer proposes a condition vector xk, typically including:

analog identity (6-way valve position): VP1

Pump 1: F1, V1

Pump 2: F2, V2

co-solvent identity (valve position) and Pump 3: VP2, F3, V3

reactor temperature: T

light settings (wavelength/intensity/time as implemented)

mode: Collect vs Analyze

Pump 4: F4, V4 (if analyzing)

Step 2 — Select analog + co-solvent (valves)

Set the analog selection valve to the chosen xylopyridine analog.

Set the co-solvent selection valve to the chosen co-solvent reservoir.

If switching streams, perform a short flush before starting the UV acquisition window.

Step 3 — Compute substrate concentration entering the reactor (dilution math)


After Pump 2 (acid dilution):

Pump 2 adds diluent (no xylopyridine), so the concentration after Pump 2 is:

$$
C_2 = C_0 \cdot \frac{F_1}{F_1 + F_2}
$$

After Pump 3 (co-solvent dilution):

Pump 3 adds additional diluent (no xylopyridine), so the concentration after Pump 3 is:

$$
C_3 = C_0 \cdot \frac{F_1}{F_1 + F_2 + F_3}
$$



The substrate concentration entering the reactor is:

$$
C_{S,\text{in}} = C_3
$$

Step 4 — Configure reactor conditions

Set Peltier to T and allow stabilization (your tolerance/time).

Apply light settings and turn the light on for the experiment window.

Step 5 — Choose post-reactor routing (Collect vs Analyze)

Collect mode: route to fraction collector for offline sampling.

Analyze mode: route to Pump 4 → UV-Vis.

Step 6 — If analyzing: Pump 4 dilution factor

Pump 4 dilutes the reactor effluent before UV-Vis.


The concentration at the UV flow cell after Pump 4 is:

$$
C_{UV} = C_{out} \cdot \frac{F_{123}}{F_{123} + F_4}
$$

	​



Define the Pump 4 dilution factor:

$$
 D_4 = \frac{F_{123} + F_4}{F_{123}}
$$

$$
C_{out} = C_{UV} \cdot D_4
$$
out
	​

=C
UV
	​

D
4
	​



If you target a UV concentration $C_{UV,\text{target}}$ (or equivalent absorbance target), then:

$$
F_4 = F_{123} \cdot \left( \frac{C_{out}}{C_{UV,\text{target}}} - 1 \right)
$$

In practice, 
Cout
C
out
	​

 is not known ahead of time; 
F4
F
4
	​

 is typically set from prior runs or adjusted to keep absorbance in range.

Step 7 — UV-Vis quantification (absorbance → concentration)

Option A: Beer–Lambert at a single wavelength

$$
A(\lambda) = \varepsilon(\lambda) \, l \, c \implies c = \frac{A(\lambda)}{\varepsilon(\lambda) \, l}
$$
A(λ)
	​


Option B: Calibration model (recommended)

CP,UV=f(UV spectrum)
C
P,UV
	​

=f(UV spectrum)

Undo Pump 4 dilution to estimate product concentration at the reactor outlet:

CP,out=CP,UVD4
C
P,out
	​

$$
C_{P,\text{out}} = C_{P,UV} \cdot D_4
$$
=C
P,UV
	​

D
4
	​

Step 8 — Percent yield

For 1:1 stoichiometry (substrate → product):

$$
\%\text{Yield} = 100 \times \frac{C_{P,\text{out}}}{C_{S,\text{in}}}
$$

	​


If you measure remaining substrate instead:

$$
\%\text{Conversion} = 100 \times \left(1 - \frac{C_{S,\text{out}}}{C_{S,\text{in}}}\right)
$$

C
S,out
	​

	​

)
Step 9 — Throughput

True reactor throughput uses the reactor flow 
F123
F
123
	​

 (excluding Pump 4):

$$
\dot{n}_P = C_{P,\text{out}} \cdot F_{123} \quad [\text{mol/min}]
$$
	​

=C
P,out
	​

F
123
	​

[mol/min]

Convert to mol/hr:

$$
\dot{n}_P(\text{mol/hr}) = 60 \cdot C_{P,\text{out}} \cdot F_{123}
$$
P,out
	​

F
123
	​


Mass throughput (optional):

$$
\dot{m}_P = \dot{n}_P \cdot MW_P \quad [\text{g/min}]
$$
	​

=
n
˙
P
	​

MW
P
	​

[g/min]
Step 10 — Bayesian optimization (how next conditions are chosen)

We model the objective 
f(x)
f(x) (e.g., yield, throughput, or a combined score) with a probabilistic surrogate (commonly a Gaussian Process):

$$
f(x) \sim \mathcal{GP}(m(x), k(x, x'))
$$

Given data 
D={(xi,yi)}i=1n
D={(x
i
	​

,y
i
	​

)}
i=1
n
	​

, the surrogate predicts:

$$
p(f(x) \mid D) = \mathcal{N}(\mu(x), \sigma^2(x))
$$

An acquisition function 
a(x)
a(x) trades off exploitation and exploration.

Expected Improvement (EI)
Let 
y∗=max⁡iyi
y
∗
=max
i
	​

y
i
	​

 and 
Z=μ(x)−y∗σ(x)
Z=
σ(x)
μ(x)−y
∗
	​


$$
y^* = \max_i y_i
$$

$$
Z = \frac{\mu(x) - y^*}{\sigma(x)}
$$

$$
	ext{EI}(x) = (\mu(x) - y^*) \Phi(Z) + \sigma(x) \phi(Z)
$$

Upper Confidence Bound (UCB)

$$
	ext{UCB}(x) = \mu(x) + \kappa \sigma(x)
$$

The next experiment is chosen by:

xn+1=arg⁡max⁡xa(x)
x
n+1
	​

=arg
x
max
	​

a(x)

subject to feasibility constraints (flow limits, temperature limits, solvent availability, etc.).

4) Optional: combined objective (yield + throughput)

If optimizing both, a common scalar objective is:

$$
y = w_Y \left( \frac{\%\text{Yield}}{100} \right) + w_T \left( \frac{\dot{n}_P}{\dot{n}_{P,\max}} \right), \quad w_Y + w_T = 1
$$
	​

+w
T
	​

=1
5) What gets logged each iteration

For each run 
k
k, store:

Valve states: analog selection, co-solvent selection, post-reactor routing

Pump setpoints: 
F1,F2,F3,F4
F
1
	​

,F
2
	​

,F
3
	​

,F
4
	​

 and Pump 1 dose 
V1
V
1
	​

 (or duration)

Reactor setpoints: temperature 
T
T, light settings

UV-Vis data: raw spectra/absorbance + processed concentrations

Metrics: %Yield, 
n˙P
n
˙
P
	​

, and scalar objective (if used)

Quality flags: saturation, bubbles, out-of-range absorbance, instrument errors, etc.