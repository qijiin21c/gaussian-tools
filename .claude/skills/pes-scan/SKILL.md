---
name: pes-scan
description: This skill should be used when the user asks to "potential energy surface scan", "势能面扫描", "rigid scan", "柔性扫描", "relaxed scan", "scan dihedral", "scan bond length", "scan bond angle", "Gaussian scan keyword", "opt=modredundant scan", "2D scan", "二维扫描", "GIC scan", "generalized internal coordinate scan", "dimer distance scan", "dissociation curve", "conformational search scan", "transition state guess from scan", "dimerscan", "gentor", "broken symmetry scan", "symmetry breaking scan", or mentions scanning geometric parameters in Gaussian to explore potential energy surfaces.
version: 0.1.0
---

# Potential Energy Surface Scanning in Gaussian

Guide to rigid and relaxed potential energy surface scans in Gaussian, including special tools (dimerscan, gentor) and GIC-based scanning, based on Sobereva's article (sobereva.com/474).

**Core distinction:**
- **Rigid scan (`scan`)**: Change specified geometric variable(s), compute single-point at each step. Other coordinates remain fixed. Fast — each step is a single-point.
- **Relaxed scan (`opt=modredundant` + S)**: Change specified variable(s), perform constrained optimization at each step. Other coordinates relax to minimize energy. Expensive — each step is an optimization.

**When to use which:**
| Goal | Use |
|------|-----|
| Quick energy profile along a coordinate | Rigid scan |
| Dissociation curves, rotation profiles | Rigid scan |
| Conformational search aid | Relaxed scan |
| Transition state initial guess | Relaxed scan |
| Reaction mechanism exploration | Relaxed scan |
| Force field parameter fitting | Rigid scan |
| Accurate energetics with geometry relaxation | Relaxed scan |

## Quick reference: Rigid scan syntax

### In Z-matrix (internal coordinates)
```
# B3LYP/6-31G* scan nosymm

[molecule spec]

B1 1.30 10 0.1    ! scan bond: start=1.30, 10 steps, +0.1 per step
D3 180.0 18 10.   ! scan dihedral: start=180, 18 steps, +10 per step
```

Total points = steps + 1 (initial structure is always computed).

### In Cartesian coordinates
```
# M062X/6-311G(d) scan pop=always

[molecule spec]

Li  0.0  0.0  Z

Z= 5.0 10 -0.3   ! scan Z coordinate: start=5.0, 10 steps, -0.3 per step
```

### 2D rigid scan
```
# B3LYP/def2SVP scan

[molecule spec]

B1 0.92 10 0.01   ! first variable
A1 95.0 10 2.0    ! second variable
```
Total points = (10+1) × (10+1) = 121. Computational cost grows geometrically with dimensions.

## Quick reference: Relaxed scan syntax

```
# PM7 opt=modredundant nosymm

[Cartesian coordinates]

7 4 1 8 S 36 10.   ! scan dihedral 7-4-1-8: 36 steps, +10 degrees each
```

Format: `atom1 atom2 [atom3] [atom4] S steps stepsize`
- 2 atoms → bond length scan
- 3 atoms → bond angle scan
- 4 atoms → dihedral angle scan

Initial value = current structure's value. To change initial value, modify geometry in GaussView first.

## Critical pre-scan checklist

- [ ] **Method appropriate**: Rigid scan = same cost as single-point. Relaxed scan = same cost as optimization. Don't use expensive methods (CCSD(T), large basis) for relaxed scans.
- [ ] **`nosymm` for symmetry-breaking scans**: If scan changes point group (e.g., dihedral rotation), add `nosymm`. Otherwise Gaussian may fail or produce discontinuous trajectories.
- [ ] **`nosymm` for broken-symmetry**: Open-shell / dissociation scans need `nosymm`.
- [ ] **Step size reasonable**: If SCF fails mid-scan or energy shows jumps, reduce step size.
- [ ] **Floating point format**: Never write integers where Gaussian expects floats. `10.` or `10.0`, NOT `10`.
- [ ] **`pop=always` if you want properties at each step**: Mulliken charges, dipole moments, etc. Only computed at first step without this keyword.
- [ ] **Wavefunction continuity**: Each step uses previous step's converged wavefunction as guess. This maintains electronic state continuity but means wavefunction errors can propagate.

## Rigid scan: method-specific energy reading

| Method | Energy label in scan summary |
|--------|---------------------------|
| HF / DFT (non-double-hybrid) | `SCF` column |
| MP2 | `MP2=` (NOT SCF column) |
| Double-hybrid (B2PLYP) | `E(B2PLYP)=` (NOT SCF column) |
| CCSD(T) | `CCSD(T)=` |
| Semi-empirical (PM6, PM7) | `SCF` column |

See the `read-energy` skill for detailed energy reading guidance.

## Dissociation curve scanning

Scanning covalent bond breaking requires **symmetry breaking** treatment:

### Recommended two-step protocol
1. **Generate broken-symmetry wavefunction at large separation:**
```
%chk=C:\HF.chk
# UB3LYP/def2TZVP guess=mix stable=opt

0 1
F
H  1 B1

B1 4.0
```

2. **Scan from large to small distance, reading wavefunction:**
```
%oldchk=C:\HF.chk
# UB3LYP/def2TZVP scan guess=read nosymm

0 1
F
H  1 B1

B1 4.0 55 -0.06
```

### One-step alternative (less reliable)
```
# UM062X/TZVP guess(always,mix) scan nosymm
```
Re-generates guess at each step. May fail for some systems where `guess=mix` alone doesn't reach the true ground state.

**Note:** Heterolytic dissociation (e.g., NaCl → Na⁺ + Cl⁻) does NOT need symmetry breaking — products are closed-shell.

## Dimer rigid scanning with dimerscan

For scans where Gaussian's native `scan` keyword can't express the desired coordinate (e.g., H-bond distance between monomers, center-of-mass distance):

1. Use **dimerscan** (from sobereva.com/469) to generate scan.xyz trajectory
2. Use **xyz2QC** (from molclus package, keinsci.com/research/molclus) to convert to multi-step Gaussian input
3. Run Gaussian, extract energies, plot externally

**Input format for dimerscan (dimer.txt):**
```
13 13          ! atoms in monomer A, atoms in monomer B
0 1 0 1        ! charge spin for A, charge spin for B
[monomer A coordinates]
[monomer B coordinates]
```

**Use case:** H-bond distance scan, host-guest separation, any inter-fragment distance where no direct atom pair exists.

## Dihedral rigid scanning with gentor

For rotation scans where the entire group should rotate together (not just one dihedral angle):

1. Convert structure to .xyz format
2. Configure `gentor.ini`: `1-4` (bond axis) + `e10` (every 10 degrees)
3. Run gentor → produces traj.xyz
4. Convert with xyz2QC → Gaussian.gjf
5. Run Gaussian, extract energies

See molclus documentation: bbs.keinsci.com/thread-2388-1-1.html

## Relaxed scan: important caveats

- **Much more expensive than rigid scan** — at least 10× the cost per step
- **Use cheap methods** — PM7, semi-empirical, or small-basis DFT. NOT CCSD(T) or large basis sets.
- **Cannot reach exact minimum/TS** — discretized steps won't land exactly on extrema. Refine with separate optimization.
- **Energy jumps are common** — when the optimization crosses a saddle point, the relaxed structure can jump to a different basin. This is normal.
- **Hysteresis** — Gaussian uses previous step's optimized values (not input values) as starting point. Scanning 360° may not return to the starting structure/energy.
- **Three-atom-line errors** — optimization fails if three atoms become collinear mid-scan. Workaround: manual constrained optimization at the failed point, then continue.
- **No CCSD(T) relaxed scans** — only methods with analytic gradients work. CCSD(T) has no analytic gradients in Gaussian.

### Using scan peaks for transition state search

When a relaxed scan curve shows an energy jump (cliff), the highest point before the jump often resembles the TS structure:

1. Identify the peak in the scan curve
2. Check that the structure looks like a reasonable TS
3. Use that structure as initial guess for `opt=TS`
4. Use cheap level for the scan, then refine at higher level

**Don't blindly use every peak as TS guess** — always inspect the structure first.

## GIC (Generalized Internal Coordinate) scanning

Available in Gaussian 16+. More flexible than standard relaxed scans.

### Syntax
```
# B3LYP/def2TZVP opt=addgic

[coordinates]

variable_name(expression)=definition
scan(StepSize=0.1,NSteps=10)=mathematical_expression
constraint_name(freeze)=constraint_expression
```

### Use cases GIC enables that standard scans cannot:
- Distance between geometric centers of fragments
- Synchronous rotation of multiple dihedrals
- Complex mathematical expressions as scan variables
- Custom constraint combinations

**Warning:** G16 GIC code can be unstable — reasonable settings may fail unexpectedly.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Using `scan` for relaxed scan | Use `opt=modredundant` + S line |
| Using expensive method for relaxed scan | Use PM7 or small-basis DFT; single-point at better level afterward |
| Integer step size (`10` instead of `10.`) | Always use floating point: `10.` or `10.0` |
| Not using `nosymm` when symmetry changes | Add `nosymm` for any scan that changes point group |
| Trusting rigid rotation barrier | Rigid scan overestimates barrier; use relaxed scan for realistic profile |
| CCSD(T) relaxed scan | Not possible — no analytic gradients. Use cheap method + single-point |
| Assuming 360° relaxed scan returns to start | Hysteresis prevents exact return; expect mismatch |

## Additional Resources

- **`references/rigid-scan.md`** — Detailed rigid scan examples: methanol dihedral, Li⁺...benzene distance, HF dissociation curve, 2D water scan, dimerscan/gentor workflows
- **`references/relaxed-scan.md`** — Detailed relaxed scan examples: C2H4ClBr dihedral, ACE-ALA-NME conformational search, ethanol dehydration TS search, cyclobutane ring opening, GIC scanning with geometric centers and synchronous rotation
