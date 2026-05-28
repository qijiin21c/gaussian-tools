---
name: lanthanide-complexes
description: This skill should be used when the user asks to "lanthanide complex calculation", "镧系配合物计算", "actinide complex", "SDD pseudopotential lanthanide", "MWB28 MWB56", "f orbital SCF convergence", "stable=opt lanthanide", "DKH lanthanide", "SARC basis set", "x2c basis set lanthanide", "lanthanide spin multiplicity", "4f electron", "rare earth complex DFT", or mentions Gaussian quantum chemistry calculations for lanthanide/actinide metal complexes including pseudopotential selection, relativistic treatment, SCF convergence, and wavefunction stability.
version: 0.1.0
---

# Lanthanide/Actinide Complex Calculation Guide

Comprehensive guidance for performing DFT calculations on lanthanide and actinide metal complexes using Gaussian, based on Sobereva's authoritative article (sobereva.com/581).

**Prerequisites:** This is an advanced topic. If your quantum chemistry experience is limited, read all referenced articles first. If you cannot yet handle organic system calculations proficiently, start with sobereva.com/355 before tackling lanthanide/actinide systems.

## Why lanthanide/actinide calculations are harder

Compared to main-group and even transition metal complexes:
1. **Spin multiplicity determination** is more complex
2. **SCF convergence is much harder** — f-orbital near-degeneracy causes severe convergence problems
3. **Wavefunction instability is more common** — `stable=opt` is strongly recommended
4. **Higher coordination numbers** and more complex coordination environments
5. **Relativistic effects are significant** — must be considered

## Workflow overview

| Step | Pseudopotential | Purpose |
|------|----------------|---------|
| **1. Geometry optimization + frequency** | Large-core (大核) ECP | Easy SCF convergence, no f-electron description needed |
| **2. Single-point energy + properties** | Small-core (小核) ECP or all-electron | Better accuracy, explicit f-electron description |
| **3. Wavefunction analysis** | Small-core ECP or all-electron | Must use stable wavefunction (`stable=opt`) |

**Rationale:** Large-core ECPs pseudize the 4f electrons, making SCF much easier. Small-core ECPs explicitly describe 4f electrons, giving better accuracy but much harder SCF. Use large-core for opt+freq (where level sensitivity is low), small-core for energy/properties.

## 1. Functional selection

| Priority | Functional | Notes |
|----------|-----------|-------|
| **First choice** | PBE0 | Widely used for lanthanide complexes (e.g., Inorg. Chem., 58, 411, 2019) |
| **Also good** | BP86, TPSS, TPSSh | Suitable for transition metal complexes, also work for lanthanides |
| **Not ideal** | B3LYP | Commonly used but not the best choice for lanthanides |

See sobereva.com/272 for detailed functional selection guidance.

## 2. Pseudopotential selection

### Stuttgart (SDD) pseudopotentials — first choice

For lanthanides/actinides, Stuttgart pseudopotentials (also called SDD) are preferred. See sobereva.com/373 and sobereva.com/188 for pseudopotential background.

Gaussian's built-in Stuttgart pseudopotentials for Ho (Z=67) include:

| ECP | Type | Core electrons | Use case |
|-----|------|---------------|----------|
| **MWB28** | Small-core | 28 (1s-3d) | High accuracy, explicit 4f description. SCF very hard. |
| **MWB56** | Large-core | 56 (1s-4d + 10 of 11 4f) | For Ho(III). Easy SCF. Lower accuracy. |
| **MWB57** | Large-core | 57 (1s-4d + all 11 4f) | For Ho(II). |
| **MHF56/57** | Non-relativistic | — | **Do NOT use** — fitted without relativistic effects, results are useless |

**Note:** `SDD` in Gaussian for Ho = `MWB28` (small-core).

### Large-core vs small-core comparison

| Aspect | Large-core (大核) | Small-core (小核) |
|--------|-------------------|-------------------|
| 4f electrons | Pseudized (not described) | Explicitly described |
| SCF convergence | Much easier | Extremely difficult |
| Cost | Lower | Higher |
| Accuracy | Moderate | Better |
| Transferability | Poor — not suitable for processes with significant coordination changes | Good — universal |
| **Recommended for** | Geometry optimization + frequency | Single-point energy, excited states, wavefunction analysis, reactions with bond breaking/forming |

**Large-core limitation:** Poor transferability — not suitable for studying processes where coordination changes significantly (coordination bond formation/breaking, isomerization). Requires correct valence state judgment.

**Recommendation:** Use large-core for opt+freq, small-core for single-point energy, property calculations, excited states, and wavefunction analysis (see sobereva.com/156).

### Alternative pseudopotentials

- **def2-TZVP / def2-QZVP** for lanthanides — includes pseudopotential part, uses Stuttgart MWB28 small-core ECP. Not built into Gaussian — must copy from Turbomole basis library.
- **def series** for actinides — similar to def2 but for actinides. Also not built into Gaussian.
- **Lanl2 ECP** — supports La, U, Np, Pu but rarely used.
- **CRENBL large-core** — supports lanthanides/actinides but outdated.

See sobereva.com/60 for Gaussian mixed basis/ECP input format.

## 3. All-electron relativistic calculation basis sets

Gaussian supports DKH2 and DKH4 scalar relativistic Hamiltonians. DKH2 is very common; DKH4 is more precise but slightly more expensive.

### For DKH2

| Element | Recommended basis | Notes |
|---------|------------------|-------|
| **Lanthanide** | SARC (3-zeta) or SARC2-DKH2 (4-zeta) | Good results, not too expensive. Available on BSE. Two versions: DKH2 and ZORA — use DKH2 version. |
| **Ligand (1st-4th period)** | Jorge DKH2-optimized (DZ-TZ) or def2-DKH (ORCA only) | Jorge: search "Jorge" on BSE. Covers elements 1-103. def2-DKH is built into ORCA only. |
| **Ligand (post-HF)** | Dunning cc-pVnZ-DK | For post-HF calculations. |

### For DKH4

| Element | Recommended basis | Notes |
|---------|------------------|-------|
| **All elements (1st-6th period)** | x2c-SVPall, x2c-TZVPall, x2c-QZVPall | Designed for X2C Hamiltonian, works well for DKH4 too. "all" = scalar relativistic; "all-2c" = 2-component (larger, not needed for DKH4 scalar). Available on BSE and Turbomole. |

## 4. Spin multiplicity

For lanthanide complexes, spin multiplicity depends on the 4f electron configuration.

**Example: Ho(III) with 10 4f electrons:**
- Can be singlet, triplet, or quintet
- With large-core ECP (4f pseudized): only 8 valence electrons (5s²5p⁶) on Ho, ligands are closed-shell → use **singlet**
- With small-core ECP (4f explicit): must determine multiplicity. Typically high-spin: 7 alpha + 3 beta = 7-3+1 = **quintet**

**If uncertain:** Try all possible multiplicities (singlet, triplet, quintet, etc.) and compare energies. Don't need full SCF convergence — energy converged to 0.00001 a.u. is sufficient to determine the ground state.

## 5. SCF convergence

Lanthanide/actinide complexes with small-core ECPs are notorious for SCF convergence difficulty:

- 74+ SCF cycles to converge is common; 100+ cycles is not unusual
- Many standard SCF convergence methods that work for other systems fail here

**Practical recommendations:**
- `SCF=maxcyc=200` — acceptable for lanthanide/actinide despite being generally discouraged
- `SCF=conver=6` — relax convergence by 2 orders of magnitude if tiny oscillations prevent convergence at the end. **Warning:** Gaussian 16 refuses to do energy derivative tasks, TDDFT, or `stable=opt` without tight convergence (conver=8).
- **BHandHLYP trick:** If nothing works, first converge with BHandHLYP (50% HF → large gap → easier convergence for near-degenerate systems), then read converged wavefunction as guess for PBE0 calculation.

## 6. Wavefunction stability

**Strongly recommend `stable=opt`** for all lanthanide/actinide single-point calculations.

Lanthanide/actinide complexes easily converge to unstable wavefunctions. `stable=opt` detects instability and attempts to optimize to a stable wavefunction.

**Signs of instability:**
- Negative first excitation energy in TDDFT
- Large orbital mixing coefficients between occupied and virtual orbitals of the same type (e.g., beta 4f → beta 4f*)

**After stability optimization:**
- Check `<S²>` value — should match ideal value for the spin state (e.g., 6.0 for quintet)
- `<S²>` close to ideal = weak spin polarization (alpha and beta orbitals spatially matched)
- Energy typically drops significantly (e.g., 10+ kJ/mol)

See sobereva.com/82 for detailed discussion.

## Recommended workflow example

### Step 1: Opt + Freq (large-core ECP, singlet)
```
#p pbe1pbe/genecp em=gd3bj int=fine opt freq

[molecular coordinates]

C O H
6-31G*
****
Ho
MWB56
****

Ho
MWB56
```

### Step 2: Single-point + stability (small-core ECP, correct multiplicity)
```
#p PBE1PBE/genecp em=gd3bj int=fine stable=opt SCF=maxcyc=200

[molecular coordinates from step 1]

C O H
6-311G*
****
Ho
SDD
****

Ho
SDD
```

### Step 3: All-electron DKH4 (higher accuracy)
```
#p PBE1PBE/gen em=gd3bj int(DKHSO,fine) stable=opt

[molecular coordinates]

[custom x2c-TZVPall basis definitions from BSE]
```

## Additional Resources

For detailed methodology and comprehensive coverage, consult:

- **`references/workflow.md`** — Step-by-step workflow example with Ho(III) complex, structure building, SCF convergence tricks, stability analysis
- **`references/analysis.md`** — Wavefunction analysis: Mulliken population, atomic charge, oxidation state (LOBA), AIM topology, RDG, coordination number, CDA, IR spectrum
