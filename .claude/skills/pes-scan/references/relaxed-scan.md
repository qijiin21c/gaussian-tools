# Relaxed Scanning and GIC in Gaussian

Detailed guide for relaxed (constrained optimization) scans and Generalized Internal Coordinate (GIC) scanning, based on Sobereva's article (sobereva.com/474).

## Relaxed scan fundamentals

A relaxed scan performs a **constrained optimization** at each step: the specified variable is changed to the target value, while all other variables are optimized to minimize energy. This allows the geometry to "relax" naturally at each scan point.

### Key differences from rigid scan

| Aspect | Rigid scan | Relaxed scan |
|--------|-----------|-------------|
| Each step | Single-point | Constrained optimization |
| Cost per step | 1 SCF | 10-100+ SCF iterations |
| Non-scanned coords | Fixed | Optimized |
| Accuracy | Lower (no relaxation) | Higher (geometry relaxes) |
| Typical use | Dissociation curves, quick profiles | TS search, conformational search |

### Syntax
```
# PM7 opt=modredundant nosymm

[Cartesian coordinates]

atom1 atom2 [atom3] [atom4] S steps stepsize
```

- 2 atoms → bond length
- 3 atoms → bond angle
- 4 atoms → dihedral angle
- Initial value = current structure's corresponding variable
- To change initial value: modify geometry in GaussView first

### Multiple simultaneous scans
Add multiple S lines for multi-dimensional relaxed scans. 2D scans can be visualized in GaussView (Results → Scan → surface plot). Export data via right-click → Export Data for external plotting.

### Freezing atoms during scan
```
8 F
10 F
```
Add after the S line(s) to freeze specific atoms during the scan.

## Important caveats

### Cost
Relaxed scan is **at least 10× more expensive** than rigid scan at the same settings. Each optimization step computes gradients many times.

**Recommendation:** Use cheap methods — PM7, semi-empirical, or small-basis DFT. NOT CCSD(T) or large basis sets.

### Cannot reach exact extrema
Discretized steps won't land exactly on minima or transition states. Use the scan result's closest point as initial guess for a separate optimization.

### Energy jumps (discontinuities)
Energy jumps are **common and normal**. They occur when the constrained optimization crosses a saddle point and the structure jumps to a different potential basin.

Visual explanation: imagine a 2D PES where the scan variable is the vertical axis and an un-scanned variable is horizontal. At each scan step, the optimization moves horizontally to the nearest minimum (pink arrow direction). When the scan variable passes a saddle point (red dot), the nearest minimum jumps from one side of the PES to the other — causing an energy cliff.

**The highest point before the jump often resembles the transition state.** Use it as initial guess for `opt=TS`, but always inspect the structure first.

### Hysteresis
Gaussian uses the **previous step's optimized values** (not input values) as the starting point for each step's optimization. This causes:
- Scanning 360° dihedral: end point ≠ start point (energy and structure)
- "Lag" effect in the scan curve
- Path dependence (forward scan ≠ reverse scan)

### Three-atom-line errors
Optimization fails if three atoms become collinear mid-scan. Workarounds:
1. Adjust scan settings to avoid collinear configurations
2. Manually perform constrained optimization at the failed point
3. When collinear error occurs, take the last structure and continue optimization (Gaussian handles initial collinear geometry better)

### Method restrictions
Only methods with **analytic gradients** work for relaxed scans:
- HF, DFT, semi-empirical: yes
- MP2: yes (but expensive)
- CCSD(T): **NO** — no analytic gradients in Gaussian
- CCSD: very expensive even if available

Don't attempt CCSD(T)/aug-cc-pVQZ relaxed scans — it's computationally infeasible.

### Convergence issues
Same techniques as regular optimization:
- `opt=(modredundant,gdiis)` — switch to GDIIS algorithm
- `opt=(modredundant,calcfc)` — compute force constants at first step
- `opt=(modredundant,loose)` — relax convergence criteria (good for TS guess scanning)
- `maxcyc=NNN` — increase maximum cycles
- `recalc=N` — recompute Hessian every N steps

### Level of theory strategy
- **Relaxed scan itself:** cheap level (PM7, small-basis DFT)
- **Refinement:** single-point at better level for each scan point
- Never use expensive level directly for relaxed scan — waste of resources

## Example 1: C2H4ClBr relaxed dihedral scan

Same system as the gentor rigid scan example, but now with geometry relaxation.

### Input (C2H4ClBr_relax.gjf)
```
# PM7 opt=modredundant nosymm

Title Card Required

0 1
 C                  0.00000000    0.00000000    0.00000000
 H                  0.00000000    0.00000000    1.07000000
 H                  1.00880579    0.00000000   -0.35666635
 C                 -0.72596336    1.25740469   -0.51333288
 H                 -0.05342615    1.83983916   -1.10777699
 H                 -1.06223201    1.83983874    0.31888943
 Cl                -2.10874985    0.77839276   -1.49111051
 Br                -0.90038252   -1.55950848   -0.63666682

7 4 1 8 S 36 10.
```

Key differences from rigid scan:
- Cl7-C4-C1-Br8 set to 0° in initial structure
- 36 steps × 10° = 360° full rotation
- PM7 (semi-empirical, fast)
- `nosymm` keeps trajectory visually continuous
- Other coordinates (C-C bond length, bond angles) relax at each step

### Result analysis
- Energy curve shows minima at anti conformation (~180°), maximum at eclipsed (0°/360°)
- C-C bond length correlates with energy: higher steric hindrance → longer C-C bond
- Relaxed scan barrier is **lower** than rigid scan barrier (geometry relaxes to reduce strain)

## Example 2: ACE-ALA-NME conformational search

N-acetyl-N'-methylalanine dipeptide model. Find lowest-energy conformation via 2D relaxed scan.

### Key insight
- Methyl rotation: not worth scanning (small, chemically equivalent hydrogens)
- Peptide bond rotation (N-C=O): high barrier due to partial π conjugation, not relevant at room temperature
- Only scan the two flexible dihedrals: N1-C3 and C3-C6

### Input (ACE-ALA-NME.gjf)
```
# PM7 opt=modredundant

[coordinates]

5 3 1 15 S 6 60.
5 3 6 10 S 6 60.
```

6 steps × 60° = 360° for each dihedral. Total: 49 points.

### From scan to optimized structure
1. View surface plot in GaussView (Results → Scan)
2. Identify the lowest-energy point on the surface
3. Switch to that frame in GaussView
4. Save structure → separate optimization at better level (e.g., B3LYP-D3(BJ)/def2-SVP)
5. Optimize → verify with frequency calculation

**Note:** The scan's minimum point is approximate (coarse grid). Always refine with full optimization.

### When rigid scan would fail
Rigid scan of this flexible molecule would produce unreasonably high energies at many points due to severe atomic clashes that don't relax away. Relaxed scan is essential for flexible molecules.

## Example 3: Ethanol dehydration transition state search

Ethanol → ethylene + water. Use relaxed scan to find TS initial guess.

### Strategy
Scan the forming O-H distance (H transferring from methyl to hydroxyl oxygen). As this distance decreases, the structure approaches the TS.

### Input (ethanol_relax.gjf)
```
# PM7 opt=modredundant nosymm

[coordinates]

2 8 S 17 -0.1
```

- H2-O8 initial distance: 2.667 Å
- 17 steps × -0.1 Å = 2.667 → 0.967 Å (water O-H bond length)
- PM7: cheap, qualitatively correct for organic TS

### Interpreting the scan curve
The curve (read right-to-left since distance decreases):
1. Energy rises as C-H and C-O bonds stretch
2. Reaches a peak near the TS region
3. **Energy cliff**: next step suddenly drops — structure now resembles water + ethylene complex

**The peak structure** ≈ transition state. Use it as initial guess:

```
# B3LYP/6-31G(d) opt=TS

[peak structure coordinates from scan]
```

### When to use this approach
- **Not for every reaction** — most TS guesses can be found by manual construction
- **Only when necessary** — complex reactions where TS geometry is hard to envision
- **Use `opt=loose`** to reduce scan cost when only seeking TS guess

**Always inspect the peak structure first** — don't blindly use every peak as TS guess. The structure must resemble the expected transition state.

## Example 4: Cyclobutane ring opening to butane diradical

Pull apart one C-C bond of cyclobutane until it becomes an open-chain butane diradical.

### Input (cyclobutane_relax.gjf)
```
# UM062X/6-31G* guess(mix,always) opt=modredundant pop=always nosymm

[coordinates]

1 2 S 11 0.2
```

Key settings:
- **`U`**: unrestricted — required for diradical state
- **`guess(mix,always)`**: generate broken-symmetry guess at each step
- **`pop=always`**: compute spin populations at each step (for tracking diradical character)
- **`nosymm`**: continuity + broken-symmetry reliability
- **M06-2X**: good for organic diradicals
- 11 steps × 0.2 Å: from equilibrium to ~open-chain distance

### Result interpretation
- Energy rises sharply during C-C bond stretching
- At ~2.5 Å, energy plateaus — bond is fully broken
- Further elongation only causes conformational changes (small energy changes)
- Approximate bond energy ≈ (E_last - E_first) × 2625.5 kJ/mol (rough, unrefined)

### Spin population analysis
In GaussView: Plots → Plot Molecular Property → Atomic Charge → Mulliken Spin population → atom 1.

**Observation:**
- First 5 steps: spin population = 0 (closed-shell)
- From step 6: spin population ≈ 1.0 (diradical character emerges)
- Sign flips mid-scan are normal — `guess(always,mix)` re-generates guess each step, so alpha/beta assignment may swap. Look at absolute values.

## GIC (Generalized Internal Coordinate) scanning

Gaussian 16+ feature. More flexible than standard relaxed scans through mathematical expressions and custom constraints.

### Basic syntax
```
# B3LYP/def2TZVP opt=addgic

[coordinates]

var1(inactive)=expression1
var2(inactive)=expression2
scan(StepSize=X,NSteps=Y)=scan_expression
constraint(freeze)=constraint_expression
```

- `opt=addgic`: read GIC definitions
- `(inactive)`: variable is not an optimization target, only used for constraint definition
- `scan(...)`: not a keyword but a variable name; parentheses contain scan parameters
- R(i,j), A(i,j,k), D(i,j,k,l): distance, angle, dihedral
- `0.529177`: Bohr-to-Ångstrom conversion factor

### GIC operators and functions
Standard mathematical operations: +, -, *, /, ^, sqrt(), sin(), cos(), etc. Arbitrary expressions allowed for scan variables and constraints.

### Stability warning
G16 GIC code can be **unstable** — seemingly reasonable settings may fail unexpectedly. Known bugs in A.03 version. May improve in future versions.

## GIC Example 1: Geometric center distance scan

Scan distance between water and N₂ geometric centers in the H₂O···N₂ dimer.

### Why GIC is needed
Standard relaxed scans cannot use dummy atoms in scan definitions. GIC can define geometric centers as variables and scan their distance.

### Input (H2O_N2_gic.gjf)
```
# b3lyp/tzvp em=gd3bj opt=addgic

Title Card Required

0 1
 N                 -2.09851100   -0.04510800    0.06118400
 N                 -1.02140600    0.07296400   -0.07499500
 O                  1.65885690   -0.14665701    0.01859668
 H                  1.94081190    0.77130999    0.08101768
 H                  0.70784690   -0.10669701   -0.12803832
 X                  1.43583857    0.17265199   -0.00947465
 X                 -1.55995850    0.01392800   -0.00690550

XH2O(inactive)=XCntr(3-5)
YH2O(inactive)=YCntr(3-5)
ZH2O(inactive)=ZCntr(3-5)
XN2(inactive)=XCntr(1,2)
YN2(inactive)=YCntr(1,2)
ZN2(inactive)=ZCntr(1,2)
scan(StepSize=0.1,NSteps=10)=sqrt[(XH2O-XN2)^2+(YH2O-YN2)^2+(ZH2O-ZN2)^2]*0.529177
```

- Water geometric center: atoms 3-5 (O, H, H)
- N₂ geometric center: atoms 1-2 (N, N)
- Scan expression: Euclidean distance between centers, converted to Å
- Initial distance: ~3.0 Å, scan 10 steps × 0.1 Å → 4.0 Å
- Dummy atoms (X) placed at geometric centers for visualization

### Result
- Each step increases center-to-center distance
- Monomer orientations relax to minimize interaction energy
- May terminate prematurely due to G16 GIC instability

## GIC Example 2: Synchronous methylene rotation in 1,3-butadiene

Rotate both terminal CH₂ groups of s-cis-1,3-butadiene synchronously.

### Input (butadiene_gic.gjf)
```
# opt=addgic UPM7 guess(mix,always)

Title Card Required

0 1
[coordinates]

scan(StepSize=-10.0,NSteps=13)=D(6,4,1,2)
rcons(freeze)=D(4,6,8,9)-D(6,4,1,2)
```

- Scan: D(6,4,1,2) — right CH₂ dihedral, 13 steps × -10° = -130° (clockwise)
- Constraint: D(4,6,8,9) - D(6,4,1,2) = constant (frozen at initial value)
- This forces the left CH₂ to rotate by the same amount as the right CH₂
- `U` + `guess(mix,always)`: when CH₂ rotates ~90°, the C=C π bonds break → diradical character

### Chemical interpretation
- At maximum energy (step 10): both CH₂ perpendicular to C-C-C-C plane
- π bonds on both sides destroyed → one unpaired electron each on C1 and C8
- Middle two carbons form a new π bond between them
- C1-C8 bonding is prevented by the dihedral constraint (would form cyclobutene if allowed)

## molclus: the better conformational search tool

For molecules with 2+ rotatable bonds, multi-dimensional relaxed scanning is impractical (cost explodes with dimensions).

**Recommended:** Use molclus (keinsci.com/research/molclus) for conformational search:
- Free, flexible, accuracy controllable
- Uses molecular dynamics or meta-dynamics to explore conformations
- Much more efficient than grid-based scanning
- Read gentor documentation (bbs.keinsci.com/thread-2388-1-1.html) for scan-based conformational search

## Common mistakes with relaxed scans

| Mistake | Why it's wrong | Fix |
|---------|---------------|-----|
| `CCSD(T)/aug-cc-pVQZ opt=modredundant` | No analytic gradients + infeasible cost | Use cheap method + single-point refinement |
| Asking "is the peak a TS?" without checking structure | Peak structure may not resemble the reaction TS | Always inspect the structure first |
| Using relaxed scan for every TS search | Most TS guesses can be built manually | Only use when TS geometry is truly hard to envision |
| Expecting 360° scan to return to start | Hysteresis prevents exact return | Accept the mismatch; it's inherent to the algorithm |
| Rigid scan for flexible molecule conformations | Unrelaxed clashes give unreasonably high energies | Use relaxed scan or molclus |
| `guess(always,mix)` spin population sign flips | Not an error — alpha/beta assignment changes per step | Look at absolute values |

## References

- sobereva.com/474 — This article (PES scanning)
- sobereva.com/404 — GIC and constrained optimization in Gaussian
- sobereva.com/164 — Helping geometry optimization converge
- sobereva.com/460 — Transition state search with opt=TS, QST2, QST3
- sobereva.com/387 — Why optimization and frequency don't need large basis sets
- sobereva.com/353 — Spin density and spin population analysis
- sobereva.com/252 — Multiwfn weak interaction analysis (RDG, IGM, AIM)
- sobereva.com/423 — Temperature, pressure, isotope effects
- keinsci.com/research/molclus.html — molclus conformational search
