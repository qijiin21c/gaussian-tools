# TDDFT Comprehensive Guide

Detailed guide to TDDFT for excited state calculations, based on Sobereva's article (sobereva.com/265).

## Why TDDFT became the standard

Historical progression:
1. **Semi-empirical + CI** — rough, early days
2. **CIS (Configuration Interaction Singles)** — based on HF orbitals, poor accuracy (overestimates by 1-2 eV)
3. **TDDFT** — comparable cost to CIS, significantly better accuracy. Now the default.

Early TDDFT lacked analytic gradients (Gaussian 03), making excited-state optimization extremely expensive (each step = 6N excitation energy calculations for N geometric variables). CIS was used for optimization, TDDFT for single-point energy. Modern programs (Gaussian 09+) support TDDFT analytic gradients, making CIS obsolete for most purposes.

**TDDFT analytic 2nd derivatives** are not yet widely available (only Q-Chem among mainstream programs). For excited-state frequencies (needed for vibronic coupling), one must either use CIS (has 2nd derivatives) or accept the high cost of numerical TDDFT frequencies.

## Functional selection in detail

### The HF% rule

There is a well-established trend: **higher HF exchange percentage → higher computed excitation energy**.

| HF% range | Typical functionals | Excitation energy tendency |
|-----------|-------------------|---------------------------|
| **0% (pure/GGA)** | PBE, BLYP, TPSS | Severely underestimated |
| **~20%** | B3LYP (20%) | Slight underestimation (singlets) |
| **~25%** | PBE0 (25%) | No systematic bias — **ideal** |
| **~37-42%** | PBE38 (37.5%), BMK (42%) | Slight overestimation |
| **~50-54%** | BHandHLYP (50%), M06-2X (54%) | Overestimated |
| **100% long-range** | CAM-B3LYP, wB97XD, LC-wPBE | Overestimated for LE, correct for CT/Rydberg |

This rule applies to most systems. For large conjugated systems (dyes), benchmark studies (JCP, 132, 184103) suggest 25% HF is too low and underestimates excitation energies.

### Valence local excitation — singlet

**PBE0 is the best choice** — error ~0.1-0.3 eV relative to CC3/CASPT2 benchmarks.

B3LYP is close behind but statistically slightly worse. Both have no systematic over/underestimation tendency on average.

For large conjugated systems (dye molecules), consider:
- **PBE38** (37.5% HF) — JCP, 132, 184103 recommends this
- **BMK** (42% HF) — also recommended for dyes

### Valence local excitation — triplet

The situation is fundamentally different:
- **Almost all methods underestimate** triplet excitation energies
- The HF% trend still exists but is much weaker than for singlets
- **M06-2X** performs well for triplets
- PBE0/B3LYP are mediocre
- TDA approximation actually improves triplet results

### Charge-transfer (CT) excitation

CT excitation: electron excitation causes significant electron-hole separation, resulting in long-range electron density transfer.

**Traditional DFT exchange functionals have incorrect long-range behavior**, causing large errors for CT excitations unless they have very high HF% (like M06-2X).

**Range-separated functionals** (developed since ~2000):
| Functional | Long-range HF% | Notes |
|-----------|---------------|-------|
| **CAM-B3LYP** | 65% | Recommended for CT |
| **wB97XD** | 100% | Range-separated + dispersion correction |
| **LC-wPBE** | 100% | Long-range corrected |

These use high (up to 100%) HF exchange at long range, dramatically reducing CT error. **Trade-off:** Local excitation accuracy is notably worse than PBE0.

**ω parameter tuning:** Range-separated functional results depend strongly on the ω parameter, just as hybrid results depend on HF%. ω is system-dependent — optimize before computing. See sobereva.com/346.

**Geometry matters too:** Low-HF% functionals produce wrong excited-state geometries for CT systems. Example (JCTC, 8, 2359, 2012): CAM-B3LYP gives nearly parallel adjacent phenyl rings in an excited state, while B3LYP gives perpendicular rings. **Do not use low-HF% or pure functionals for optimizing CT system structures.**

### Rydberg excitation

Rydberg excitation: electron is excited to a high-order, diffuse virtual orbital.

Requirements:
1. **Diffuse basis functions are essential** — minimum 6-31+G*, recommended aug-cc-pVTZ, ideally d-aug-cc-pVTZ
2. **Range-separated functional or high-HF% functional** — same as CT
3. TDDFT accuracy doesn't match d-aug-cc-pVTZ precision — if using such basis, upgrade the method too

### Identifying CT and Rydberg excitations

See sobereva.com/284 for illustrated classification. Key indicators:
- Large electron-hole separation distance
- Small electron-hole overlap integral
- Charge transfer index Δr
- Multiwfn electron-hole analysis (sobereva.com/434)
- NTO analysis (sobereva.com/377)

## Ghost states

Low-HF% functionals (especially GGA, but also B3LYP) can produce **ghost states** for large conjugated systems:

| Property | Ghost state |
|----------|------------|
| Excitation energy | Artificially low |
| CT character | Yes |
| Oscillator strength | Very small |
| Physical meaning | None — SIE artifact |

Ghost states waste computation time and may push real (interesting) states above your state count limit. They have minimal impact on the computed absorption spectrum (low oscillator strength) but cost valuable CPU time.

**Solution:** Use range-separated functional or higher HF% functional.

## Tamm-Dancoff Approximation (TDA)

TDA ignores the B matrix in the TDDFT eigenvalue problem:

```
Full TDDFT:  [ A  B ] [ X ]     [ A ] [ X ]
             [ B* A*] [ Y ] = ω [-B*] [ Y ]   → TDA: A X = ω X
```

This makes TDDFT formally equivalent to CIS on DFT orbitals.

### Pros of TDA
- Slightly faster computation
- Easier to program
- **Improves triplet excitation accuracy**
- Required for hybrid functionals in some programs (ORCA 3.0.3)
- Pure functionals don't have this restriction in ORCA

### Cons of TDA
- **Slightly worse singlet excitation accuracy** (though some studies find slight improvement — possibly error cancellation)
- **Underestimates oscillator strengths** (dx.doi.org/10.1021/ct400597f)
- **Worse for UV-Vis and ECD spectra**

### When to use TDA
- Triplet-only studies
- When program requires it (ORCA hybrid functionals)
- Quick pre-screening

### When NOT to use TDA
- UV-Vis spectrum simulation
- ECD (circular dichroism) spectrum
- When accurate oscillator strengths are needed

## Double-hybrid TDDFT

Double-hybrids (B2PLYP, B2GP-PLYP, DSD-PBEP86) can be used for TDDFT calculations in a CIS(D)-like perturbative correction scheme.

**ORCA only** — not supported in Gaussian.

| Functional | Performance | Notes |
|-----------|------------|-------|
| **B2PLYP** | 30% better than PBE0 for valence singlets | Weakest double-hybrid |
| **B2GP-PLYP** | Better than B2PLYP | JCP, 132, 184103 |
| **DSD-PBEP86** | Similar to B2GP-PLYP | Available in ORCA 5.x |

Cost is higher than regular TDDFT but much lower than EOM-CCSD.

## Solvent effects in excited state calculations

Solvent effects are **more important for excited states than ground states** because the solute-solvent interaction differs between ground and excited states, causing differential energy level shifts.

### TDDFT + PCM capabilities
- Non-equilibrium solvation — accounts for different response times of solvent electronic and orientational polarization
- State-specific calculations — response to excited-state density
- Linear response (LR-PCM) — standard approach

### When to use explicit solvent
- Strong specific solute-solvent interactions (H-bonding, coordination)
- Use a few explicit solvent molecules + implicit PCM for bulk effect

### QM/MM for complex environments
- Protein environment: use QM/MM or background point charges
- Complex solvent dynamics (spectral broadening, detail loss): requires molecular dynamics simulation

### Limitations
Neither implicit nor explicit solvent models capture:
- Spectral broadening due to solvent dynamics
- Loss of spectral fine structure in solution
- These require explicit solvent simulation (MD + QM/MM)

## Estimating the number of states

### Rule of thumb
The number of states needed depends strongly on the atom count:
- **Few atoms:** ~10 states may reach sufficient energy
- **50-atom organic molecule:** ~100 states needed to cover 2-7 eV UV-Vis range
- **100+ atoms:** 200+ states may be needed

### Risk of under-computing
Too few states → miss high-energy excitations → must recompute (computing 20 then 10 more states costs much more than computing 30 at once).

### Risk of over-computing
Too many states → longer computation time. TDDFT cost scales with the number of states.

### sTDA pre-scan
The simplified TDA (sTDA, JCP, 138, 244104) method:
- Nearly zero extra cost beyond a ground-state single-point
- Gives approximate excitation energies to estimate how many states are needed
- For very large systems needing hundreds of states, use sTDA results directly (偏差不算小 but acceptable for large systems)

## TDDFT's remaining weaknesses

TDDFT is fundamentally limited in two areas:

### 1. Conical intersections / PES crossings
- **TDDFT cannot correctly describe** potential energy surface crossings
- This remains the domain of multireference methods (CASSCF, CASPT2, MRCI)
- Exception: S₀-T₁ crossings can be handled by DFT (different multiplicity)

### 2. Double excitations
- TDDFT within the adiabatic approximation cannot describe double excitations
- Better than CIS (which also fails), but still inadequate
- Methods that handle double excitations: CASPT2, EOM-CCSD(T), EOM-CCSDT, MRCI

### Areas for improvement
1. Widespread implementation of TDDFT analytic 2nd derivatives
2. Further functional improvement — possibly optimizing functionals specifically for excitation energies
3. Linear-scaling techniques for larger systems (fragmentation approaches work well for model systems but struggle with CT excitations involving long-range coupling)

## What computed excitation energy actually represents

### Vertical excitation energy vs experiment
- Computed vertical excitation energy ≈ experimental absorption maximum
- Typically **overestimates by 0.1-0.3 eV** because:
  - No vibrational coupling considered
  - Real process is not perfectly vertical
- Even with perfectly accurate vertical excitation energy, this overestimation would persist

### Adiabatic excitation energy vs experiment
- Computed adiabatic excitation energy ≈ experimental 0-0 transition energy
- Typically **overestimates by ~0.1 eV** because excited-state ZPE is usually lower than ground-state ZPE

### When comparison fails
If computed spectra don't match experiment, the method itself may not be at fault. Contributing factors:
- Vibrational coupling (see vibronic spectra guide)
- Solvent effects (linear response vs state-specific, equilibrium vs non-equilibrium, explicit interactions)
- Overlapping absorption bands from different transitions

**Key principle:** Understand exactly what you are computing before comparing to experiment.

## References

- sobereva.com/265 — This article (excited state methods overview)
- sobereva.com/284 — Classification of electronic excitations
- sobereva.com/437 — Multiwfn excited state analysis methods
- sobereva.com/434 — Electron-hole analysis for excitation characterization
- sobereva.com/377 — NTO analysis
- sobereva.com/346 — optDFTw tool for ω parameter optimization
- sobereva.com/282 — HF% of common functionals
- sobereva.com/224 — Plotting spectra with Multiwfn
- sobereva.com/223 — Vibrationally resolved electronic spectra
- Chem. Soc. Rev., 42, 845-856 (2013) — Introductory review on excited state computation
- JCP, 132, 184103 — TDDFT benchmark study
- JCTC, 8, 2359 (2012) — CT excited state geometry dependence on functional
- JCP, 138, 244104 — sTDA method
- dx.doi.org/10.1021/ct400597f — TDA oscillator strength underestimation
