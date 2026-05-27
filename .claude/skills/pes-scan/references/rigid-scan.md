# Rigid Scanning in Gaussian

Detailed guide for rigid potential energy surface scans, based on Sobereva's article (sobereva.com/474).

## Rigid scan fundamentals

In a rigid scan, Gaussian changes specified geometric variables step by step and computes a single-point energy at each step. Coordinates not being scanned remain at their initial values.

### Energy interpretation
Each scan step outputs energy according to the method used. See the `read-energy` skill for correct energy reading. In the scan summary at end of output:
- SCF methods (HF, DFT): energy under `SCF` column
- Post-HF: method-specific label (EUMP2, CCSD(T)=, etc.)

### Wavefunction propagation
Each step automatically uses the previous step's converged wavefunction as initial guess. This:
- Helps SCF convergence between adjacent similar structures
- Maintains electronic state continuity along the scan
- Can propagate wavefunction errors if one step converges to a wrong solution

**If SCF fails mid-scan or energy jumps:** Reduce step size. Smaller steps maintain better wavefunction continuity.

### `nosymm` keyword
Add `nosymm` when the scan changes the molecular point group. Common cases:
- Dihedral rotation (Cs → C1)
- Symmetry breaking / open-shell scans
- Any scan where symmetry is lost partway through

Without `nosymm`, Gaussian may fail or produce discontinuous trajectories. Conversely, if symmetry is maintained throughout (e.g., Li⁺ approaching benzene center along C6 axis), omit `nosymm` for speed.

## Example 1: Methanol OH dihedral scan

Scan the H-C-O-H dihedral rotation of methanol by 180° in 10° steps.

### Prerequisites
1. Optimize methanol at B3LYP/6-31G*
2. Save as Z-matrix (uncheck "Write Cartesians" in GaussView)

### Input file (methanol_scan.gjf)
```
# b3lyp/6-31g(d) scan nosymm

Title Card Required

0 1
 C
 H                  1            B1
 H                  1            B2    2            A1
 H                  1            B3    2            A2    3            D1    0
 O                  1            B4    2            A3    3            D2    0
 H                  5            B5    1            A4    2            D3    0

   B1             1.09337920
   B2             1.10125884
   B3             1.10125884
   B4             1.41863900
   B5             0.96872260
   A1           108.05956655
   A2           108.05956655
   A3           106.69693538
   A4           107.66742719
   D1           117.09085412
   D2          -121.45457294
   D3           180.00000000 18 10.
```

- D3 = H6-O5-C1-H2 dihedral — rotating this turns the OH group
- 180° / 10° = 18 steps, from 180° to 360°
- Total computed points: 19 (18 + initial)

### Viewing results
1. Load .log into GaussView
2. Results → Scan → see energy curve
3. Click any point to view structure and energy
4. Frame numbers: 1 = input structure, 19 = last scan step

**Chemical interpretation:** The curve shows two minima (global at D3=180°, local at ~300°) and a maximum when H atoms eclipse along the C-O axis. Use these structures as guesses for refined optimization/TS search.

## Example 2: Li⁺...benzene distance scan

Scan Li⁺ approaching benzene ring center from 5.0 Å to 2.0 Å in 0.3 Å steps.

### Cartesian coordinate approach
```
# M062X/6-311g(d) scan pop=always

Title Card Required

1 1
 C                  0.00000000    1.39650157    0.00000000
 C                  1.20940584    0.69825078   -0.00000000
 C                  1.20940584   -0.69825078   -0.00000000
 C                  0.00000000   -1.39650157    0.00000000
 C                 -1.20940584   -0.69825078    0.00000000
 C                 -1.20940584    0.69825078    0.00000000
 H                  0.00000000    2.48320512   -0.00000000
 H                  2.15051871    1.24160256   -0.00000000
 H                  2.15051871   -1.24160256   -0.00000000
 H                 -0.00000000   -2.48320512    0.00000000
 H                 -2.15051871   -1.24160256    0.00000000
 H                 -2.15051871    1.24160256    0.00000000
 Li                0. 0. Z

Z= 5.0 10 -0.3
```

Key points:
- Benzene placed in XY plane, center at (0,0,0)
- Li⁺ scans along Z axis: 5.0 → 2.0 Å
- `pop=always`: computes Mulliken charges at each step
- No `nosymm` needed — symmetry (C6v) maintained throughout
- M06-2X: good for weak interactions

### Charge transfer analysis
With `pop=always`, view Li charge evolution in Results → Scan → Plots → Plot Molecular Property → Atomic Charge → 13 (Li atom number).

**Observation:** At large distance, Li charge ≈ +1.0. As it approaches, electron density transfers from benzene to Li⁺, reducing the apparent charge. This is Mulliken charge — use ADCH or NPA for more reliable analysis.

### Z-matrix alternative with dummy atoms
Place a dummy atom X at benzene ring center (GaussView: select 6 carbons → Builder → X → Place Fragment at Centroid). Add H on X perpendicular to ring, replace H with Li. Save as Z-matrix — a variable will correspond to X-Li distance, which can be scanned.

### Rotating tilted rings
If the ring is not parallel to a Cartesian plane, rotate it first so the ring plane is parallel to XY. Use the method in sobereva.com/178 with VMD scripts to align the ring. Then scan Z coordinate.

## Example 3: HF bond dissociation curve

Scanning covalent bond homolysis (H-F → H· + F·) requires special treatment because the system transitions from closed-shell to open-shell (spin-polarized singlet / broken-symmetry) beyond the instability point.

### Two-step protocol (recommended)

**Step 1: Generate broken-symmetry wavefunction at large separation**
```
%chk=C:\HF.chk
# UB3LYP/def2TZVP guess=mix stable=opt

Title Card Required

0 1
F
H  1 B1

B1 4.0
```
- `U`: unrestricted open-shell
- `guess=mix`: breaks initial guess symmetry
- `stable=opt`: verifies and optimizes to true stable wavefunction
- Bond length 4.0 Å ensures complete dissociation

**Step 2: Scan from large to small distance**
```
%oldchk=C:\HF.chk
# UB3LYP/def2TZVP scan guess=read nosymm

Title Card Required

0 1
F
H  1 B1

B1 4.0 55 -0.06
```
- Reads broken-symmetry wavefunction from .chk
- Scans 55 steps × -0.06 Å: 4.0 → 0.7 Å
- Each step inherits the broken-symmetry character
- When distance < instability point, result equals restricted closed-shell

### One-step alternative (less reliable)
```
# UM062X/TZVP guess(always,mix) scan nosymm
```
- `guess(always,mix)`: re-generates guess at each step, attempts broken-symmetry
- Works for some systems (ethane C-C dissociation) but fails for HF
- May converge to wrong electronic state at intermediate distances

### Why `guess(always,mix)` fails for HF
At intermediate bond lengths, `guess=mix` may place both alpha and beta single electrons on F rather than one on each atom. Check with Multiwfn spin density analysis (sobereva.com/353).

### Heterolytic dissociation
NaCl → Na⁺ + Cl⁻ does NOT need symmetry breaking — both products are closed-shell. Standard scan works fine.

### Higher-level alternatives
- UCCSD(T): more accurate dissociation curves
- CASPT2: necessary for multiple bond breaking (strong static correlation)

## Example 4: 2D scan — water bond length and angle

Simultaneously scan both O-H bond lengths and the H-O-H angle.

```
# B3LYP/def2SVP scan

Title Card Required

0 1
 O
 H  1  B1
 H  1  B1  2  A1

B1 0.92 10 0.01
A1 95.0 10 2.0
```

- B1 (O-H): 0.92 → 1.02 Å, 10 steps
- A1 (H-O-H): 95° → 115°, 10 steps
- Total points: (10+1) × (10+1) = 121

**Cost estimation:** Compute one single-point to estimate time, then multiply by total points.

### Viewing 2D results
1. Extract summary data from output file end
2. Plot as surface/contour/heatmap in Origin, SigmaPlot, or Surfer
3. Or load into GaussView → Results → Scan → surface plot with contour projection

**Beyond 2D:** Gaussian can scan 3+ variables simultaneously, but results cannot be visualized directly in GaussView.

## dimerscan: dimer rigid scanning

For dimer scans where Gaussian's native scan cannot express the desired coordinate (H-bond distance, center-of-mass distance, etc.).

### Workflow
1. Prepare `dimer.txt`:
```
13 13         ! atoms in monomer A, atoms in monomer B
0 1 0 1       ! charge spin A, charge spin B
[monomer A Cartesian coordinates]
[monomer B Cartesian coordinates]
```

2. Run dimerscan (download from sobereva.com/469):
   - Input dimer.txt path
   - Specify atom pair to scan (e.g., `9,20`)
   - Set initial distance, steps, step size
   - Outputs: `scan.xyz` (trajectory)

3. Convert with xyz2QC (from molclus package):
   - Set template.gjf keywords (e.g., `# PM6D3`)
   - Run xyz2QC → selects scan.xyz → Gaussian.gjf

4. Run Gaussian.gjf, extract energies with `grep "E(RPM6D3)"` or similar

5. Plot in Origin/Excel

### Example: Phenol dimer H-bond distance
Scan H9-O20 from 1.7 Å, 20 steps, 0.1 Å increment.

**Note:** If monomer atoms are interleaved in the file, reorder so each monomer's atoms are consecutive (GaussView: Select Fragment → Ctrl+X → new window → Ctrl+Shift+V → save).

### Example: Host-guest complex
For fullerene-host separation scan where no atoms exist at the scan endpoints:
1. Add dummy atoms (X) at scan points on host and guest
2. Merge coordinates into dimer.txt
3. Scan dummy atom distance
4. Remove dummy atoms from final structures

**Plotting convention:** Subtract the minimum-point energy from all points so the curve shows energy relative to the minimum — this has chemical meaning.

## gentor: dihedral rigid scanning with group rotation

For rotation scans where the entire attached group should rotate together (not just one dihedral angle).

### Why gentor is needed
In Gaussian rigid scan, rotating one dihedral angle only moves the four atoms involved — other atoms don't follow. This produces increasingly distorted structures. gentor rotates the entire group.

### Workflow
1. Save structure as .xyz:
```
8
comment line (any text)
[Cartesian coordinates]
```

2. Configure `gentor.ini`:
```
1-4      ! rotate around bond between atoms 1 and 4
e10      ! every 10 degrees (360° total = 36 structures)
```

3. Run gentor → produces `traj.xyz`

4. Convert with xyz2QC → Gaussian.gjf

5. Run Gaussian, extract energies, add dihedral values (from GaussView or arithmetic progression)

### Example: C2H4ClBr C-C rotation
Scan Cl-C-C-Br dihedral by rotating around C1-C4 bond, 360° in 10° steps.

**Result interpretation:** Energy maxima at eclipsed conformations (Cl/Br overlap), minima at anti conformation. Note: rigid scan overestimates rotational barrier because other coordinates don't relax.

## SCANsplit: wavefunction extraction from scan

Use SCANsplit tool (sobereva.com/199) to extract each scan step's wavefunction into individual single-point input files. Then:
1. Batch-run single-points to get .fch/.wfn files
2. Use Multiwfn to analyze charge distribution, bonding, etc. at each step
3. Animate properties along the scan trajectory

See sobereva.com/200 for bond order curve and ELF/LOL/RDG animation examples.

## References

- sobereva.com/474 — This article (PES scanning)
- sobereva.com/469 — SAPT energy decomposition vs dimer distance
- sobereva.com/199 — SCANsplit tool for extracting wavefunctions
- sobereva.com/200 — Bond order and ELF/LOL/RDG animation along reaction
- sobereva.com/460 — Transition state search with opt=TS, QST2, QST3
- sobereva.com/297 — Symmetry and nosymm keyword
- sobereva.com/353 — Spin density and spin population analysis
- sobereva.com/82 — Fragment-combined wavefunctions and spin-polarized singlets
- sobereva.com/113 — Density difference plots with Multiwfn
- bbs.keinsci.com/thread-2388-1-1.html — gentor usage
- keinsci.com/research/molclus.html — molclus package (dimerscan, xyz2QC)
