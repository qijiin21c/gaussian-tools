# Free Energy Calculation Workflow

Complete worked example and step-by-step workflow for computing solution-phase free energy, based on Sobereva's article (sobereva.com/327).

## Worked example: Ethylene oxide in ethanol

This example computes the standard-state (298.15 K, 1 M) free energy of ethylene oxide in ethanol solvent.

### Overview: Four calculations needed

| File | Purpose | Keywords |
|------|---------|----------|
| **1.gjf** | Optimization + frequency in solvent | `B3LYP/6-311G* scrf(SMD,solvent=ethanol) opt freq` |
| **2.gjf** | High-accuracy gas-phase single-point | `B2PLYPD3/def2TZVP` |
| **3.gjf** | Gas-phase single-point at SMD level | `M052X/6-31G*` |
| **4.gjf** | Solvent single-point at SMD level | `M052X/6-31G* scrf(SMD,solvent=ethanol)` |

All single-points (2-4) use the geometry from calculation 1 (`geom=allcheck`).

### Step 1: Optimization and frequency

**1.gjf:**
```
# B3LYP/6-311G* em=GD3BJ opt freq scrf(SMD,solvent=ethanol)

Ethylene oxide in ethanol - opt+freq

0 1
[coordinates]
```

From 1.out, extract:
```
Thermal correction to Gibbs Free Energy=    0.033857
```

**Note on solvent in opt/freq:** For ethylene oxide (neutral, no local charges), the solvent model is technically unnecessary — gas-phase and solvent structures are nearly identical. However, including it makes the template universally applicable to all systems, including ions where solvent is essential.

**Recommendation:** Consider using default IEFPCM instead of SMD for opt/freq — SMD can cause convergence issues and spurious imaginary frequencies for flexible systems. The results are nearly identical for opt/freq since only the polar part matters.

### Step 2: High-accuracy gas-phase single-point

**2.gjf:**
```
# B2PLYPD3/def2TZVP geom=allcheck

Ethylene oxide - gas phase high-accuracy SP

0 1
```

From 2.out, read the double-hybrid electronic energy. See the `read-energy` skill for correct energy reading (read `E(B2PLYP)=`, NOT `SCF Done`).

```
Electronic energy = -153.7254582 Hartree
```

### Step 3: Gas-phase single-point at SMD parameterized level

**3.gjf:**
```
# M052X/6-31G* geom=allcheck

Ethylene oxide - gas phase SMD-level SP

0 1
```

From 3.out:
```
E(M05-2X) = -153.758808 Hartree
```

### Step 4: Solvent single-point at SMD level

**4.gjf:**
```
# M052X/6-31G* scrf(SMD,solvent=ethanol) geom=allcheck

Ethylene oxide - solvent SMD-level SP

0 1
```

From 4.out:
```
E(M05-2X) = -153.765311 Hartree
```

### Computation

**Gas-phase free energy (298.15 K, 1 atm):**
```
G_gas = E_high_precision + Thermal_correction_to_G
      = -153.7254582 + 0.033857
      = -153.691601 Hartree
```

**Solvation free energy (1M → 1M):**
```
ΔG_solv = E_solvent - E_gas (at SMD level)
        = -153.765311 - (-153.758808)
        = -0.006503 Hartree
        = -4.08 kcal/mol
```

**Solution-phase free energy (298.15 K, 1 M):**
```
G_soln = G_gas + ΔG_solv + 1.89/627.51
       = -153.691601 + (-0.006503) + 0.003012
       = -153.695092 Hartree
```

## Three accuracy levels for gas-phase free energy

### Level 1: Lazy (not publication-quality)

```
# B3LYP/6-31G* opt freq
```

Read directly:
```
Sum of electronic and thermal Free Energies=    -153.691601
```

This uses B3LYP/6-31G* electronic energy — too inaccurate for publication.

### Level 2: Practical (recommended for most)

Two calculations:
```
# B3LYP/6-31G* opt freq                  → get thermal correction
# B2PLYP-D3(BJ)/def2-TZVP geom=allcheck  → get high-accuracy energy
```

```
G_gas = E_B2PLYP-D3 + Thermal_correction_to_G
```

This is the approach used in the worked example above.

### Level 3: Rigorous (for flexible systems)

1. Optimize at B3LYP/6-31G* (or similar mid-level)
2. High-accuracy single-point
3. Use Shermo (sobereva.com/552) for thermal correction:
   - Set `E=` in settings.ini to the high-accuracy single-point energy
   - Set `sclZPE=` to the appropriate frequency scaling factor for the opt level (see sobereva.com/221)
   - Set `ilowfreq=2` for Grimme's quasi-RRHO model
   - Run Shermo → read output free energy

```
G_gas = E_high_precision + Shermo_G_correction
```

**Why Level 3 for flexible systems?** Gaussian's standard RRHO (rigid-rotor harmonic oscillator) model poorly handles low-frequency vibrational modes, leading to large entropy errors for flexible molecules. Shermo's quasi-RRHO model treats low-frequency modes as free rotors (Grimme's approach), giving much more accurate entropies.

## Composite method shortcut

For small systems (≤30 atoms, or more with a powerful server):

```
# G4
```

From output:
```
G4 Free Energy=    -153.691601
```

This is the gas-phase free energy at near-chemical accuracy.

**Composite method ranking (accuracy vs cost):**

| Method | Accuracy | Max practical size |
|--------|----------|-------------------|
| W1 | Highest | ~10 atoms |
| CBS-APNO | Very high | ~10 atoms |
| G4 | High | ~20 atoms |
| G4(MP2) | Good | ~25 atoms |
| CBS-QB3 | Good | ~25 atoms |
| G3(MP2B3) | Decent | ~30 atoms |
| CBS-4M | Outdated | ~30 atoms |

**Recommended:** G4 or G4(MP2) for most small-molecule work. CBS-4M is outdated — don't use it.

## Quick approximate approach

For a rough estimate with fewer steps:

1. `opt freq` (with or without solvent) → thermal correction to G or H
2. High-level single-point in solvent → solvated electronic energy
3. G_soln ≈ E_solvent(high-level) + Thermal_correction + 1.89 kcal/mol

**Trade-off:** Faster but computes ΔG_solv at the high level rather than the SMD-parameterized M05-2X/6-31G* level — lower accuracy for the solvation part.

## Temperature variation

To compute solution-phase free energy at a different temperature (e.g., 320 K):

1. Add `temperature=320` to the opt/freq calculation (1.gjf):
```
# B3LYP/6-311G* em=GD3BJ opt freq scrf(SMD,solvent=ethanol) temperature=320
```

2. Follow the same computation workflow

**Assumption:** This assumes ΔG_solv is temperature-independent — the implicit solvent parameters (fitted at 298.15 K) are used at all temperatures. This is an approximation but often acceptable.

Shermo can also provide thermodynamic data at arbitrary temperatures once you have the frequency output.

## Dispersion correction notes

- **B3LYP:** D3 correction usually unnecessary for opt/freq of non-weak-interaction systems, but including it improves generality as a template
- **B2PLYP (double-hybrid):** D3 correction is **essential**, even for non-weak-interaction systems — it significantly improves thermochemistry
- See sobereva.com/413 on when DFT-D3 is needed, and sobereva.com/557 on when B3LYP optimization is appropriate

## Template input files for other systems

For systems without 4th-row or heavier elements:

**1.gjf (opt+freq in solvent):**
```
# B3LYP/6-311G* em=GD3BJ opt freq scrf(IEFPCM,solvent=ethanol)

Title

0 1
[coordinates]
```

**2.gjf (high-accuracy gas SP):**
```
# B2PLYPD3/def2TZVP geom=allcheck

Title

0 1
```

**3.gjf (gas SP at SMD level):**
```
# M052X/6-31G* geom=allcheck

Title

0 1
```

**4.gjf (solvent SP at SMD level):**
```
# M052X/6-31G* scrf(SMD,solvent=ethanol) geom=allcheck

Title

0 1
```

For systems with heavy elements (4th row+), replace 6-31G* or 6-311G* with appropriate pseudopotential basis sets (SDD, Lanl2TZ(f), etc.). See sobereva.com/373.

## Common pitfalls in the workflow

| Pitfall | Consequence | Fix |
|---------|------------|-----|
| Reading `SCF Done` for double-hybrid (file 2) | Wrong energy — got DFT part, not full DH energy | Read `E(B2PLYP)=` |
| Using different geometries for gas and solvent SP | Inconsistent ΔG_solv | Use same geometry (geom=allcheck) |
| Forgetting the 1.89 kcal/mol correction | Result doesn't match experimental definition | Always add it |
| Computing ΔG_solv at B2PLYP/def2-TZVP level | Worse than M05-2X/6-31G* — SMD not parameterized for this level | Use M05-2X/6-31G* for ΔG_solv |
| Using 6-31+G* instead of 6-31G* for SMD | SMD was parameterized with 6-31G*, even for anions | Use 6-31G* |
| Computing dissolution enthalpy from implicit solvent | Not parameterized — meaningless | Only ΔG_solv is available |

## References

- sobereva.com/327 — This article (solvation free energy)
- sobereva.com/488 — Where to read double-hybrid energy from Gaussian output
- sobereva.com/552 — Shermo program for thermodynamic data
- sobereva.com/221 — Frequency scaling factors
- sobereva.com/413 — When to use DFT-D3
- sobereva.com/557 — When B3LYP optimization is appropriate
- sobereva.com/373 — Pseudopotential basis set selection
- sobereva.com/278 — Small imaginary frequencies after optimization
- J. Phys. Chem. A, 114, 13442 (2010) — Correct use of continuum solvent models
