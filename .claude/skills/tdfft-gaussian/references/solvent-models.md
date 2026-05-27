# Solvent Models for TDDFT in Gaussian

Detailed guide to solvent model usage in TDDFT calculations, based on Sobereva's article (sobereva.com/266).

## Why solvent matters for excited states

Solvent affects excited states in multiple ways:
- **Excitation energy shift** — spectral peak red-shift or blue-shift
- **Intensity change** — absorption/emission strength modification
- **Peak broadening and distortion** — loss of fine structure
- **Excited-state geometry change** — different minimum structure
- **External conversion** — non-radiative deactivation

**Rule:** If the excitation occurs in solution, include solvent. The stronger the solvent polarity, the more important this becomes.

## Implicit solvent models

### PCM (Polarizable Continuum Model)
- Default in Gaussian's `scrf` keyword
- Treats solvent as a continuous medium with a dielectric constant
- Generally captures solvent effects on excitation energy, oscillator strength, and excited-state geometry reasonably

### COSMO
- Simpler than PCM, supported by some programs that don't have PCM
- Similar effectiveness for most purposes

## Solvent response to excitation: LR vs SS

When the solute is electronically excited, the solvent field must respond. There are two ways to handle this:

### Linear Response (LR)

**Mechanism:** Solvent correction to excitation energy = interaction between transition density and solvent polarization induced by transition density.

| Property | Value |
|----------|-------|
| **Cost** | Minimal overhead vs gas phase |
| **Analytic gradient** | Yes — suitable for excited-state optimization |
| **Accuracy** | Good for most cases |
| **Multiple states** | Computes all states simultaneously — suitable for spectra |
| **When it fails** | Charge-transfer excitations may need SS |

**Usage in Gaussian:**
```
# functional/basis TD(nstates=N) scrf=solvent=xxx
```
That's it. LR is the default behavior of `scrf` in TDDFT.

### State-Specific (SS) / External Iteration

**Mechanism:** Solvent directly responds to the specified excited state's electron density. Iterates until solvent field and excited-state density are fully self-consistent.

| Property | Value |
|----------|-------|
| **Cost** | ~10× more expensive (each iteration = full excitation calculation) |
| **Analytic gradient** | **No** — not suitable for excited-state optimization |
| **Accuracy** | Better for CT excitations; may be worse for others |
| **Multiple states** | One state at a time — unsuitable for spectra |
| **When to use** | High-accuracy single-point for CT excitations |

**Usage in Gaussian:**
```
# functional/basis TD(root=i) scrf(externaliteration,read,solvent=xxx)
```
Plus `noneq=write`/`noneq=read` for non-equilibrium solvent. See detailed protocols below.

**Gaussian 09:** Use `scrf(statespecific,...)` instead of `externaliteration` (equivalent).

## Equilibrium vs non-equilibrium solvent

Solvent polarization has two components:
- **Fast component** — solvent electronic structure polarization (instantaneous)
- **Slow component** — solvent molecular orientation polarization (slow)

| State | Fast | Slow |
|-------|------|------|
| **Equilibrium (eq)** | Relaxed | Relaxed |
| **Non-equilibrium (neq)** | Relaxed | Frozen at initial state |

### Which solvent state for which process?

| Process | Initial state | Final state | Reason |
|---------|--------------|-------------|--------|
| **Vertical absorption** | eq (ground state) | neq (excited state, slow frozen in ground-state configuration) | Process is too fast for solvent reorientation |
| **Vertical emission** | eq (excited state) | neq (ground state, slow frozen in excited-state configuration) | Same reason |
| **Adiabatic absorption/emission** | eq | eq | Both states fully relaxed (optimization) |

### Energy formulas

```
Vertical absorption  = E_ES(R_GS, neq) - E_GS(R_GS, eq)
Vertical emission    = E_ES(R_ES, eq) - E_GS(R_ES, neq)
Adiabatic (both)     = E_ES(R_ES, eq) - E_GS(R_GS, eq)
```

## LR solvent in Gaussian — the simple way

LR handles eq/neq automatically:

| Calculation | Solvent state for excited state |
|-------------|-------------------------------|
| **Single-point TD** (computing excitation at fixed geometry) | neq (LR-neq) — solvent slow part is in ground-state equilibrium, fast part responds to excitation |
| **Excited-state optimization** | eq (LR-eq) — solvent slow and fast parts both relax for the excited state as geometry changes |
| **Ground-state energy** (always) | eq (ground-state equilibrium) |

**Usage:** Just add `scrf=solvent=xxx`. Nothing else needed.

### LR workflow examples

#### UV-Vis in solvent
```
Step 1: # PBE1PBE/6-311G* opt scrf=solvent=ethanol
Step 2: # PBE1PBE/6-311G* TD(nstates=20) scrf=solvent=ethanol
```

#### S₁ optimization in solvent
```
Step 1: # PBE1PBE/6-311G* opt scrf=solvent=ethanol
Step 2: # PBE1PBE/6-311G* TD scrf=solvent=ethanol opt
```

#### Fluorescence in solvent
```
After Step 2 above, the last S0→S1 excitation energy IS the fluorescence emission energy.

IMPORTANT: Do NOT take the optimized structure and recompute separately.
At the optimized S1 structure, the excited state is in equilibrium solvent (LR-eq).
But for emission, the excited state should be in equilibrium solvent while the
ground state (final state) should be in non-equilibrium solvent. The last step
of the optimization already computed the correct value.

If you MUST recompute (e.g., with larger basis set), add TD(Eqsolv):
# PBE1PBE/def2TZVP TD(Eqsolv) scrf=solvent=ethanol
This forces the excited state to be in equilibrium solvent, consistent with emission.
```

#### Phosphorescence in solvent (LR)
```
Step 1: # B3LYP/6-31G* opt scrf=solvent=ethanol     (0 3 — T1 via UDFT)
Step 2: # B3LYP/6-31G* TD(triplet) scrf=solvent=ethanol  (0 1 — compute emission)
```

## SS solvent in Gaussian — the detailed way

SS requires manual handling of non-equilibrium solvent via `noneq=write` and `noneq=read`.

### SS workflow: Vertical absorption (S₀ → S₁)

**Step 1: Ground-state single-point, write solvent info to .chk**
```
# PBE1PBE/6-311G* scrf(read,solvent=ethanol)

[coordinates from S0 optimization]

noneq=write
```
This computes the ground state in equilibrium solvent and writes the slow-component solvent information to the .chk file. Record the `SCF Done` energy.

**Step 2: Excited-state calculation with non-equilibrium solvent**
```
# PBE1PBE/6-311G* TD scrf(externaliteration,read,solvent=ethanol) geom=check guess=read

noneq=read
```
This reads the ground-state solvent slow-component info and computes S₁ in non-equilibrium solvent. The output ends with:
```
After PCM corrections, the energy is  -153.527526510     a.u.
```
This is the excited-state energy in non-equilibrium solvent. Subtract Step 1's SCF Done energy to get the vertical absorption energy.

**Note:** This is expensive — many iterations to self-consist the solvent field with S₁ density.

### SS workflow: Fluorescence emission (S₁ → S₀)

**Step 1: Excited-state calculation, write solvent info to .chk**
```
# PBE1PBE/6-311G* TD scrf(externaliteration,read,solvent=ethanol)

[coordinates from S1 optimization]

noneq=write
```
Record the `After PCM corrections` energy (excited state in equilibrium solvent).

**Step 2: Ground-state calculation with non-equilibrium solvent**
```
#p PBE1PBE/6-311G* scrf(read,solvent=ethanol) geom=check guess=read

noneq=read
```
Record the `SCF Done` energy (ground state in non-equilibrium solvent).

**Fluorescence energy** = Step 1 energy - Step 2 energy.

### SS workflow: For the i-th excited state
Add `root=i` to the TD keyword:
```
# PBE1PBE/6-311G* TD(root=i) scrf(externaliteration,read,solvent=ethanol)
```

### SS workflow: Phosphorescence
Same as fluorescence, but use `TD(triplet)` in the excited-state step, and optimize T₁ using UDFT (0 3 multiplicity).

## LR vs SS comparison

| Aspect | LR | SS |
|--------|----|----|
| **Cost** | Low | 10× higher |
| **Gradient** | Yes (can optimize) | No (single-point only) |
| **Multiple states** | Yes | One at a time |
| **CT excitation** | Adequate | Better |
| **Local excitation** | Good | May be worse |
| **Setup complexity** | Trivial | Complex (write/read steps) |

**Recommendation:** Use LR for most cases. SS is only worth the trouble when:
1. You're studying charge-transfer excitations
2. You need the highest possible accuracy for a single state
3. You can afford the computational cost

## Solvent model troubleshooting

### "External iteration doesn't converge"
- SS external iteration can fail to converge for some systems
- Try increasing max cycles or using a different initial guess
- If it persists, fall back to LR

### "SS gives worse results than LR"
- This can happen for non-CT excitations
- SS is not universally better — only for CT states
- Error cancellation may favor LR for local excitations

### "Can I mix LR and SS?"
- No — choose one approach consistently
- LR for optimization, SS for single-point is theoretically possible but introduces inconsistency

## References

- sobereva.com/266 — This article (TDDFT in Gaussian)
- sobereva.com/265 — Excited state methods overview
- sobereva.com/224 — Plotting spectra with Multiwfn
- sobereva.com/383 — Conformer-weighted spectra plotting
