**$I$**: Light intensity (W or % of maximum)

**$\%\text{Yield}$**: Percent yield, $\%\text{Yield} = 100 \times \frac{C_{P,\text{out}}}{C_{S,\text{in}}}$
**$T$**: Reactor temperature (°C)

**$I$**: Light intensity (W or % of maximum)
# Dead Man’s Fingers  
## Automated Flow Platform for Bayesian Optimization (Xylopyridine Analogs)

This repository controls an automated flow-chemistry platform that optimizes a photochemical reaction of **xylopyridine analogs** using **Bayesian optimization**. Each iteration:
1) selects an analog + operating conditions,  
2) executes the experiment,  
3) quantifies performance online via **UV-Vis**, and  
4) proposes the next experiment.

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

## 1) Platform overview (hardware + data loop)

```mermaid
flowchart LR
  A[Analog selection\n6-way valve] --> B[Pump 1: Substrate feed\n(variable volume + flow)]
  B --> C[Pump 2: Dilution\n0.1 M HCl (aq)]
  C --> Vsolv[Co-solvent selection valve]
  Vsolv --> D[Pump 3: Co-solvent dilution]
  D --> E[Reactor bed\nPeltier heat/cool\n400 W tunable light]
  E --> Vout[Post-reactor switch valve]
  Vout -->|Collect| FC[Fraction collector]
  Vout -->|Analyze| F[Pump 4: Post-reactor dilution\n(target absorbance)]
  F --> G[UV-Vis detector]
  G --> H[Compute metrics\n% yield + throughput]
  H --> I[Bayesian optimization\npropose next experiment]
  I --> A

Module descriptions

6-way valve (analog selection): selects which xylopyridine analog feed is connected.

Pump 1 (substrate feed): meters the selected analog (flow rate and/or dose volume may be optimized).

Pump 2 (acid dilution): adds 0.1 M HCl(aq) (diluent stream).

Co-solvent selection valve + Pump 3: selects a co-solvent and adds it to reach the desired reaction composition.

Reactor bed: temperature-controlled via Peltier; irradiated by a 400 W tunable light source (software-controlled).

Post-reactor switch valve: routes effluent either to a fraction collector or to online UV analysis.

Pump 4 (UV conditioning): post-reactor dilution to hit a target absorbance range before UV-Vis.

UV-Vis + analysis: converts absorbance/spectra → concentration → % yield and throughput.

Optimizer: uses all prior results to propose the next experiment.

2) Variables, notation, and assumptions
Flow rates (use consistent units)


Flow rates (use consistent units)

**$F_1$**: Pump 1 flow rate (substrate feed), e.g., µL/min or mL/min

**$F_2$**: Pump 2 flow rate (acid dilution), e.g., µL/min or mL/min

**$F_3$**: Pump 3 flow rate (co-solvent dilution), e.g., µL/min or mL/min

**$F_4$**: Pump 4 flow rate (post-reactor dilution before UV-Vis), e.g., µL/min or mL/min

**$F_{123}$**: Total flow through the reactor (sum of Pumps 1–3): $F_{123} = F_1 + F_2 + F_3$

**$F_{1234}$**: Total flow through the UV-detector (sum of Pumps 1–4): $F_{1234} = F_1 + F_2 + F_3 + F_4$


Concentrations

**$C_0$**: xylopyridine concentration in Pump 1 feed (mol/L)

**$C_{S,\text{in}}$**: substrate concentration entering the reactor (mol/L)

**$C_{P,UV}$**: product concentration in the UV cell after Pump 4 (mol/L)

**$C_{P,\text{out}}$**: product concentration at reactor outlet (pre Pump 4) (mol/L)

Dilutions

**$D_4$**: Pump 4 dilution factor, $D_4 = \frac{F_{123} + F_4}{F_{123}}$

Temperature

**$T$**: Reactor temperature (°C)

Light Intensity

**$I$**: Light intensity (W or % of maximum)

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