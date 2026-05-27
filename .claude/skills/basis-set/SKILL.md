---
name: basis-set
description: This skill should be used when the user asks to "choose basis set", "which basis set to use", "基组选择", "add diffuse functions", "def2 vs cc-pVTZ", "Pople basis set", "basis set for DFT", "basis set for CCSD(T)", "basis set for NMR", "basis set for weak interaction", "BSSE", "counterpoise", "mixed basis set", "basis set for polarizability", or mentions selecting basis sets for quantum chemistry calculations including DFT, post-HF, and task-specific recommendations.
version: 0.1.0
---

# Basis Set Selection Helper

Comprehensive guidance for choosing basis sets in quantum chemistry calculations, based on Sobereva's authoritative article (sobereva.com/341).

**Important:** Basis set choice depends on the system, problem type, required precision, available compute resources, and the program being used. Always consider all five factors before choosing.

## Pre-check: Five factors before choosing a basis set

Before deciding on a basis set, clarify:

1. **System** — How many atoms? What elements? (4th period and beyond may need pseudopotentials)
2. **Problem type** — Geometry optimization? Single-point energy? NMR? Weak interaction? Excited states?
3. **Required precision / theory method** — DFT vs post-HF vs multireference have fundamentally different basis set requirements
4. **Available compute resources** — How many cores? What's the maximum acceptable runtime?
5. **Program** — Gaussian has specific basis set conventions; some basis sets need to be imported from BSE (https://www.basissetexchange.org)

## Core principles

### DFT vs post-HF have fundamentally different basis set requirements

**DFT (and HF):**
- Don't need many high-angular-momentum basis functions
- s and p angular momentum functions are more important for improvement
- Going from 2-zeta (6-31G*) to 3-zeta (6-311G*) gives significant improvement
- Going from 6-311G(2d,p) to 6-311G(3df,2pd) costs much more with almost no improvement
- Timing dominated by two-electron integrals, proportional to GTF count^4
- **Best choice:** Fragment-contracted basis sets (def2, pcseg, Pople) with fewer GTFs
- **Avoid:** Dunning cc-pVnZ series for DFT — too many GTFs, lower cost-performance ratio

**Post-HF (MP2, CCSD(T), multireference, double-hybrid functionals):**
- Need more high-angular-momentum functions to describe electron dynamic correlation
- At minimum def2-TZVP or def-TZVP; 6-311G** is "flowers stuck in cow dung" for CCSD(T)
- Timing dominated by basis function count (determinant/configuration count)
- **Best choice:** Dunning cc-pVnZ series — optimized for electron correlation, suitable GTF/basis function ratio
- **Avoid:** Pople basis sets — extremely poor choice for post-HF

**MCSCF:** Focuses on static correlation, not dynamic. Basis set requirements same as DFT.

### Geometry optimization and frequency need MUCH smaller basis than single-point energy

This is the most basic常识 (common sense) for quantum chemistry researchers:

| Task | Recommended basis | Notes |
|------|-------------------|-------|
| Geometry optimization | 6-31G** or def2-SVP | Up to 6-311G** or def-TZVP for medium systems |
| Frequency analysis | Same as optimization | Must be identical to optimization level |
| Single-point energy | 1-2 tiers higher | Upgrade after optimization is complete |
| Transition state optimization | Same as minimum optimization | Same basis set requirements |
| IRC | Must match TS optimization | Same basis set, same theory level, same int/scrf |

Using def2-TZVP for geometry optimization is already a clear waste. Optimize with small/medium basis, then upgrade for single-point energy. This is universally accepted by all experienced practitioners.

### Pople basis sets are poorly constructed

- For DFT: use def2/pcseg at the same tier for better accuracy at similar cost
- For post-HF: Pople basis sets are an extremely poor choice — use cc-pVnZ instead
- Pople basis sets above 6-311+G(d,p) have essentially no practical value
- **6-31G and 6-311G without polarization are unusable** — the accuracy difference between 6-31G and 6-31G* is "sky vs earth"

### Diffuse functions: when to add, when NOT to add

**Must add diffuse functions:**
- Anions
- Rydberg states / excited states
- Dispersion-dominated weak interactions (pi-pi stacking, van der Waals)
- Dipole moment, polarizability, hyperpolarizability calculations
- Electron affinity calculations

**Do NOT add diffuse functions:**
- Geometry optimization (even for weak interaction systems — use 6-311G* instead of 6-31+G*)
- Frequency analysis
- NMR calculations (adds nothing, wastes time)
- Wavefunction analysis (AIM, RDG, electron density — diffuse functions have no effect)
- Population analysis (Mulliken, NBO, Mayer/Wiberg bond grades — diffuse functions make results USELESS)
- When in doubt: DON'T add diffuse functions

**Rule of thumb:** If you've read the guidelines above and still aren't sure whether to add diffuse functions — DON'T. Cases where people add them unnecessarily outnumber cases where they should be added by at least 10:1.

**Cost warning:** Adding one layer of sp diffuse functions to heavy atoms costs significantly more than increasing zeta level. 6-311G* is better than 6-31+G* for most cases (even without diffuse functions, the 3-zeta outer shell shows some diffuse character).

## Quick reference: DFT basis set tiers

| Tier | Basis sets | Notes |
|------|------------|-------|
| Joke | STO-3G | Minimal basis |
| Toy | 3-21G | Worst 2-zeta |
| Minimum acceptable | def2-SV(P) ≈ 6-31G* | 2-zeta |
| Decent | 6-311G** < def-TZVP | General 3-zeta |
| Ideal | def2-TZVP < def2-TZVPP ≈ pcseg-2 | Premium 3-zeta |
| Overkill | def2-QZVP ≈ pcseg-3 | 4-zeta, wasteful for DFT |

## Quick reference: Post-HF basis set tiers

| Tier | Basis sets | Notes |
|------|------------|-------|
| Minimum acceptable | def-TZVP | General 3-zeta |
| Good | cc-pVTZ ≈ def2-TZVPP | Premium 3-zeta |
| High precision | cc-pVQZ ≈ def2-QZVPP | 4-zeta |
| Overkill | cc-pV5Z | 5-zeta, use CBS extrapolation (TZ→QZ) instead |

**Note:** "Minimum acceptable" doesn't mean blindly using this level is publication-ready. It's the absolute floor below which results are unreliable.

## Mixed basis sets

Appropriate use of mixed basis sets can greatly reduce cost with minimal accuracy loss:

- **Regional:** Large basis (def2-TZVP) for reaction center, medium/small (6-31G* or 3-21G) for the rest
- **Localized charge:** Add diffuse functions only to atoms with heavy negative charge, not the entire system
- **Metal complexes:** Pseudopotential basis for transition metal, all-electron basis for light atoms

See Gaussian mixed basis input: sobereva.com/60

## BSSE (Basis Set Superposition Error)

Gaussian basis functions centered on atoms invade neighboring atom space, causing energy differences (complex minus fragments) to overestimate interaction strength.

- **Counterpoise correction:** Only for energy calculations — NEVER for geometry optimization or frequency analysis (no analytic derivatives, extremely slow for large systems, negligible structural improvement)
- **When to use:** Dispersion-dominated weak interactions, when compute resources allow (costs >2x complex single-point time)
- **Alternative:** gcp method (see sobereva.com/214)

## Polarization function balance for Pople basis sets

If you must use Pople basis sets, add polarization functions in this proper order:
`(d,p) → (2d,p) → (2df,2p) → (2df,2pd) → (3d2f,2pd) → (3d2f,3p2d)`

Using unbalanced combinations like `(3d,3p2d)` — excessive H polarization without any f on heavy atoms — is inappropriate.

For 2-zeta (6-31G), `(d,p)` or at most `(2d,p)` is enough. Using `6-31G(2df,2pd)` wastes resources on polarization when upgrading to 3-zeta would give far more improvement.

## Hydrogen: when to add polarization/diffuse

- **Add polarization to H:** Only for H-related calculations — hydrogen bonds, H-transfer reactions, protonation energies, H NMR
- **Add diffuse to H:** Almost never meaningful — skip unless specifically required

## Which tasks MUST use consistent basis sets?

Only these tasks require the same basis set as the geometry optimization:
1. IRC calculations
2. Frequency analysis

All other common tasks (single-point energy, NMR, wavefunction analysis, etc.) do NOT require the same basis set as optimization. This is a common beginner misconception.

## Task-specific basis set recommendations

| Task | Minimum | Good | Ideal |
|------|---------|------|-------|
| Single-point energy (DFT) | def2-TZVP | def2-TZVPP | def2-QZVP |
| Single-point energy (post-HF) | def-TZVP | cc-pVTZ | cc-pVQZ |
| Geometry optimization | 6-31G** | 6-311G** | def-TZVP |
| Weak interaction (DFT) | 6-31+G** / ma-def2-SVP | 6-311+G** / ma-def2-TZVP | jul-cc-pVTZ |
| Weak interaction (post-HF) | jun-cc-pVDZ | may-cc-pVTZ / jun-cc-pVTZ | aug-cc-pVQZ |
| NMR | pcSseg-0 | pcSseg-1 | pcSseg-2 |
| NMR (common basis) | def2-SVP | def2-TZVP | — |
| Spin-spin coupling J | pcJ-1 | IGLO-III | — |
| Barrier heights | 3-zeta + minimal diffuse | 3-zeta + sp diffuse on heavy atoms | — |
| Dipole moment | def2-SVPD | def2-TZVPD | aug-cc-pVTZ |
| Polarizability | ZPOL | jul-cc-pVDZ / aug-cc-pVDZ | aug-cc-pVTZ(-f,-d) |
| Hyperpolarizability | aug-cc-pVDZ | POL / aug-cc-pVTZ(-f,-d) | t-aug-cc-pVTZ |
| Frequency / IR / VCD | 6-31G* | def-TZVP | (no need to go higher) |
| Raman / ROA | Opt: 6-31G*, Polarizability: aug-cc-pVDZ | Two-step method | — |
| Solvation energy (SMD) | 6-31G* at M05-2X | — | (use parameterized level only) |
| Relativistic (all-electron) | cc-pVnZ-DK / SARC | UGBS (uncontracted) | — |
| Wavefunction analysis (AIM, RDG) | 6-31G* | 6-311G** / def-TZVP | (no improvement beyond) |
| Population analysis (NO diffuse!) | 6-31G* | 6-311G** | (diffuse = USELESS results) |
| Hyperfine coupling | EPR-II / EPR-III | IGLO-III / pcJ | — |
| Explicit correlation | cc-pVnZ-F12 | — | — |

## Additional Resources

For detailed methodology and task-specific recommendations, consult:

- **`references/basis-sets.md`** — Detailed explanation of DFT vs post-HF basis requirements, CBS extrapolation, basis set sources
- **`references/task-specific.md`** — Task-specific basis set selection guide with detailed reasoning for each case
