---
name: tdfft-gaussian
description: This skill should be used when the user asks to "TDDFT Gaussian", "TD(nstates", "vertical excitation Gaussian", "fluorescence TDDFT", "phosphorescence TDDFT", "S1 optimization", "T1 optimization", "TD(triplet)", "absorption spectrum TDDFT", "TD root", "density out=wfn", "LR solvent TDDFT", "SS solvent TDDFT", "ExternalIteration", "nstates setting", "TD 50-50", "open-shell TDDFT", "Gaussian excited state opt", "kasha rule fluorescence", "TD opt freq", or mentions using Gaussian's TDDFT keyword to compute excited states, absorption/fluorescence/phosphorescence spectra, or excited-state properties.
version: 0.1.0
---

# TDDFT in Gaussian — Excited States and Spectra

Practical guide for computing excited states, absorption, fluorescence, and phosphorescence spectra using TDDFT in Gaussian, based on Sobereva's article (sobereva.com/266).

## Three idealized transition types

| Type | Process | Computational steps |
|------|---------|-------------------|
| **Vertical absorption** | S₀(R_GS) → Sₙ(R_GS) | 1. Optimize S₀ geometry. 2. Compute TD excitation at S₀ geometry. |
| **Vertical emission** | Sₙ(R_ES) → S₀(R_ES) | 1. Optimize Sₙ geometry. 2. Compute TD excitation at Sₙ geometry (this is the emission energy). |
| **Adiabatic absorption** | S₀(R_GS) → Sₙ(R_ES) | 1. Optimize S₀, get E_GS(R_GS). 2. Optimize Sₙ, get E_ES(R_ES). 3. ΔE = E_ES(R_ES) - E_GS(R_GS). |

**Correspondence with experiment:**
- Vertical absorption ≈ experimental absorption maximum
- Vertical emission ≈ experimental emission maximum
- Adiabatic excitation ≈ experimental 0-0 transition energy

## Fluorescence vs phosphorescence

| Property | Fluorescence | Phosphorescence |
|----------|-------------|-----------------|
| **Initial state** | Singlet excited (usually S₁) | Triplet excited (T₁) |
| **Kasha rule** | Usually from S₁ → S₀ | From T₁ → S₀ |
| **Spin allowed?** | Yes | No (spin-forbidden) |
| **Oscillator strength** | Non-zero | Zero without spin-orbit coupling |
| **Lifetime** | Short | Much longer |
| **Gaussian TD keyword** | `TD(root=1)` (default) | `TD(triplet)` or UDFT |

Kasha rule exceptions: e.g., Azulene emits from S₂, not S₁.

## TD keyword basics

```
# functional/basis TD(options)
```

### Common TD options

| Option | Default | Description |
|--------|---------|-------------|
| `nstates=N` | 3 | Compute N lowest excited states |
| `root=i` | 1 | Target the i-th excited state (for opt, freq, properties) |
| `singlet` | Yes | Compute singlet excited states (closed-shell ground state only) |
| `triplet` | No | Compute triplet excited states (closed-shell ground state only) |
| `50-50` | No | Compute N singlets AND N triplets simultaneously |

### Open-shell ground states

For open-shell ground states (radicals), you **cannot** specify singlet/triplet. The program computes whatever states emerge, and you identify them by `<S²>`:

| `<S²>` ideal | Multiplicity |
|-------------|-------------|
| 0.0 | Singlet |
| 0.75 | Doublet |
| 2.0 | Triplet |
| 3.75 | Quartet |
| 6.0 | Quintet |

Example: If `<S²>` = 0.85 for an excited state of a radical → close to 0.75 → doublet.

## nstates setting guidelines

### For studying a specific excited state
- If interested in the i-th state, compute **at least i states** (must compute all lower states first)
- **Recommendation:** Compute i+3 states, or i+5 for safety
- Gaussian uses Davidson iteration — the highest computed states have larger errors
- Don't compute far more than needed — wastes time

### For computing spectra
Three factors determine how many states are needed:
1. **Wavelength range** (primary) — more states → higher energy range covered
2. **System** (primary) — more conjugation, more heteroatoms, more atoms → more states needed
3. **Method** (secondary) — higher HF% → higher excitation energies → fewer states needed for same range

| System type | Typical nstates |
|-------------|----------------|
| Small molecule | 10 |
| Medium conjugated | 30-60 |
| Large conjugated | 100+ |

**Tip:** Test with ZINDO or small basis set first to estimate needed states.

**DEmin keyword:** If you need to compute higher-energy states after an initial run, see sobereva.com/348 for batch computation.

## T1 optimization — two methods

### Method 1: UDFT (strongly recommended)
```
Charge/multiplicity: 0 3
Keywords: # PBE1PBE/6-31G* opt
```
- Direct SCF optimization of T₁ state
- **Cost:** Only slightly more than singlet optimization
- **Limitation:** Only works for T₁ (lowest triplet)

### Method 2: TDDFT
```
Charge/multiplicity: 0 1
Keywords: # PBE1PBE/6-31G* TD(triplet) opt
```
- Computes singlet reference → TDDFT for T₁ → optimize
- **Cost:** ~10× more expensive than UDFT
- **Advantage:** Can optimize any triplet state (T₂, T₃...), gives orbital transition info

**Common mistake:** Writing `0 3` with `TD(triplet) opt` — this computes nothing meaningful!

## Excited-state wavefunction and properties

**Default:** TDDFT outputs ground-state density, multipoles, and wavefunction analysis.

**To get excited-state properties:** Add `density` keyword:
```
#p PBE1PBE/TZVP TD(nstates=5,root=2) density
```
Now dipole moment, Mulliken charges, etc. are for the 2nd excited state.

**To get excited-state .wfn file:**
```
#p PBE1PBE/TZVP TD(nstates=5,root=2) density out=wfn
[coordinates]

path/to/output.wfn
```
The .wfn file contains the excited-state natural orbitals.

**Note:** The .chk file still stores ground-state DFT orbitals. To store excited-state natural orbitals in .chk, see Multiwfn manual Chapter 4 or sobereva.com/379. Simpler: generate excited-state natural orbitals from .fch in Multiwfn (sobereva.com/403).

## Solvent model quick reference

| Model | Keyword | Cost | Analytic gradient | When to use |
|-------|---------|------|-------------------|-------------|
| **Linear response (LR)** | `scrf=solvent=xxx` (default) | Low | Yes | **Default for everything** — opt, spectra |
| **State-specific (SS)** | `scrf(externaliteration,solvent=xxx)` | High (10×) | No | High-accuracy single-point for CT states |

### Equilibrium vs non-equilibrium solvent

| Process | Initial state solvent | Final state solvent |
|---------|----------------------|-------------------|
| **Vertical absorption** | eq | neq |
| **Vertical emission** | eq | neq |
| **Adiabatic (opt)** | eq | eq |

**LR in Gaussian:** Automatically handles eq/neq correctly. Just add `scrf=solvent=xxx`.

**SS in Gaussian:** Requires manual `noneq=write`/`noneq=read` steps. See `references/solvent-models.md` for detailed workflow.

**Recommendation:** Use LR for most cases. SS is expensive, loses analytic gradient, and may not give better results unless studying CT excitations.

## Quick-reference workflows

### UV-Vis absorption spectrum (gas phase)
```
Step 1: # PBE1PBE/6-31G* opt
Step 2: #p PBE1PBE/TZVP TD(nstates=20)
        → Use Multiwfn to plot UV-Vis (sobereva.com/224)
```

### Fluorescence spectrum (gas phase, Kasha rule assumed)
```
Step 1: # PBE1PBE/6-311G* opt          (S0 optimization, optional if structure known)
Step 2: # PBE1PBE/6-311G* TD opt       (S1 optimization)
        → Last S0→S1 excitation energy = fluorescence emission energy
        → Use Multiwfn to plot fluorescence (zero out S2, S3 oscillator strengths)
```

### Phosphorescence (gas phase)
```
Method A (recommended):
Step 1: # B3LYP/6-31G* opt              (0 3 multiplicity — T1 optimization via UDFT)
Step 2: # B3LYP/6-31G* TD(triplet)      (0 1 multiplicity — compute T1→S0)
        → First triplet excitation energy = phosphorescence emission energy

Method B (more accurate, no transition info):
Step 1: # B3LYP/6-31G* opt              (0 3 — get T1 energy at T1 geometry)
Step 2: # B3LYP/6-31G*                  (0 1 — get S0 energy at T1 geometry)
        → E(step1) - E(step2) = phosphorescence energy
```

### UV-Vis in solvent (LR, recommended)
```
Step 1: # PBE1PBE/6-311G* opt scrf=solvent=ethanol
Step 2: # PBE1PBE/6-311G* TD(nstates=20) scrf=solvent=ethanol
        → Plot UV-Vis with Multiwfn
```

### Fluorescence in solvent (LR)
```
Step 1: # PBE1PBE/6-311G* opt scrf=solvent=ethanol
Step 2: # PBE1PBE/6-311G* TD scrf=solvent=ethanol opt   (S1 in solvent)
        → Last S0→S1 energy = fluorescence in solvent
        → Do NOT re-compute on the optimized structure — solvent would be wrong (neq vs eq)
        → If you must recompute with larger basis: add TD(Eqsolv)
```

## TDDFT frequency, TS, and IRC

### TDDFT frequency
- **Gaussian 16:** Supports analytic Hessian — write `TD freq` normally
- **Gaussian 09:** No analytic Hessian — numerical via 6N gradient steps (extremely expensive). Avoid for large systems.
- **Alternative:** Use CIS for excited-state frequencies (has analytic 2nd derivatives) — less accurate but much faster.

### Excited-state transition state search
- **Gaussian 16:** `# B3LYP/6-31G* TD(root=2,nstates=5) opt(TS,calcfc,noeigen)` — normal TS search
- **Gaussian 09:** Avoid `calcfc` (too expensive). Use `opt=(TS,modRedundant,noeigen)` or `opt=(TS,gediis,noeigen)`

### Excited-state IRC
- **Gaussian 16:** Normal IRC with `TD` keyword
- **Gaussian 09:** Use `IRC(gradientonly,euler)` — lower success rate

## Common pitfalls

| Pitfall | Consequence | Fix |
|---------|-------------|-----|
| **Preserving ground-state symmetry for excited-state opt** | Converges to saddle point with imaginary frequencies | Distort structure slightly before Sₙ optimization |
| **Wrong conformer for spectrum** | Spectrum disagrees with experiment | Use Molclus (keinsci.com/research/molclus) for conformer search; Boltzmann-weight spectra (sobereva.com/383) |
| **Negative excitation energies** | Unstable reference wavefunction | Run `stable=opt` single-point, then `guess=read` for TD |
| **nstates too small for spectrum** | Incomplete spectral range | Test with ZINDO/small basis first; use DEmin for batch computation |
| **0 3 + TD(triplet) opt** | Meaningless result | Use either `0 3` without TD (UDFT), or `0 1` with `TD(triplet)` |
| **Re-computing fluorescence on optimized structure** | Wrong solvent state (eq vs neq) | Use emission energy from last step of opt, or add `TD(Eqsolv)` |

## Additional Resources

For detailed methodology and comprehensive coverage, consult:

- **`references/solvent-models.md`** — Detailed LR vs SS solvent workflows: equilibrium vs non-equilibrium solvent theory, step-by-step SS protocol with noneq=write/read, when to use SS vs LR, fluorescence/phosphorescence in solvent
- **`references/advanced-topics.md`** — Excited-state wavefunction analysis (density keyword, natural orbitals, Multiwfn), PES crossing effects on optimization, conformer-weighted spectra, negative excitation energy troubleshooting, symmetry breaking for excited-state optimization
