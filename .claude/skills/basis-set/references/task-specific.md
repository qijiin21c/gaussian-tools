# Task-Specific Basis Set Selection Guide

Detailed basis set recommendations for specific calculation tasks, based on Sobereva's article.

## 1. Weak interactions

### Types of weak interactions

**Dispersion-dominated:**
- pi-pi stacking
- van der Waals attraction
- Need diffuse functions and BSSE treatment

**Electrostatic-dominated (with some dispersion):**
- Hydrogen bonds, dihydrogen bonds, halogen bonds
- pi-hydrogen bonds, carbon bonds, sulfur bonds, phosphorus bonds
- Less dependent on diffuse functions

### Interaction energy calculation basis sets

| Tier | DFT | Post-HF |
|------|-----|---------|
| Floor | 6-31+G** or ma-def2-SVP | jun-cc-pVDZ |
| Decent | 6-311+G** | may-cc-pVTZ |
| Good | ma-def2-TZVP | jun-cc-pVTZ |
| Ideal | — | jul-cc-pVTZ |
| Very ideal | — | aug-cc-pVQZ |
| Perfect | — | CBS |

For dispersion-dominated interactions, if compute resources allow, use counterpoise to correct BSSE. This costs >2x the complex single-point time.

### Geometry optimization for weak interaction systems

**Dispersion-dominated:**
- Ideal: may-cc-pVTZ
- Generally sufficient: 6-311+G**
- Acceptable: 6-311G** or def-TZVP

**Electrostatic-dominated:**
- Ideal: def-TZVP
- Acceptable: 6-31G** or def2-SVP

**Note:** For geometry optimization, 6-311G* (3-zeta, no diffuse) is often preferred over 6-31+G* (2-zeta, with diffuse) because:
- The 3-zeta outer shell shows some diffuse character
- 3-zeta describes valence electrons much more accurately than 2-zeta
- Results are comparable or better without the computational cost of diffuse functions

## 2. NMR calculations

### Recommended basis sets

**Best choice: pcSseg series** (JCTC, 11, 132) — specifically optimized for NMR calculations.

| Tier | Basis | Notes |
|------|-------|-------|
| Good | pcSseg-0 | Slightly larger than 3-21G, better than 6-31G** overall |
| Pretty ideal | pcSseg-1 | Only slightly larger than 6-31G**, results comparable to much larger def2-TZVP and cc-pVTZ |
| Marginal improvement | pcSseg-2 | Significantly larger than pcSseg-1, limited accuracy improvement — not very cost-effective |

**Common basis alternatives:**
- def2-TZVP: Good if pcSseg not available
- def2-SVP: If def2-TZVP is too expensive
- IGLO-II: Also good, but less recommended than pcSseg
- Pople: Not recommended. If you must use, at minimum 6-311G(2d,p)

### Spin-spin coupling constant J

**Must use specialized basis sets** with tight (large-exponent) basis functions near the nucleus:
- **Strongly recommended:** pcJ series (pcJ-1 is already good)
- **Also good:** IGLO-III
- General-purpose basis sets are completely unsuitable for J calculations

### Important: Do NOT add diffuse functions for NMR

Adding diffuse functions provides almost no improvement to NMR accuracy. This is a common beginner mistake.

### Important: No pseudopotentials on atoms being studied

The atoms being examined for NMR absolutely cannot use pseudopotential basis sets — pseudopotentials cannot represent inner electron shielding of the external magnetic field. However, using pseudopotentials on neighboring atoms is fine.

## 3. Barrier height calculations

Follow the general recommendations in the main skill file (Section 1.2).

**If using good 3-zeta level and compute resources allow further improvement:**
- Add minimal diffuse functions (s,p on heavy atoms only) for quantitative improvement
- Note: def2 series with diffuse functions shows less improvement for barrier heights than Pople series

**Do NOT add diffuse functions on 2-zeta basis sets** — the effort is better spent increasing zeta count, which gives much more accuracy improvement.

## 4. Dipole moment, polarizability, hyperpolarizability

These are the 1st, 2nd, and 3rd derivatives of energy with respect to external electric field, respectively.

**Must have diffuse functions** — results without diffuse functions are completely unusable. Requirements increase with derivative order.

### Dipole moment

| Tier | Basis | Notes |
|------|-------|-------|
| Near-perfect | def2-TZVPD | Essentially no basis set level error |
| Very good | aug-cc-pVTZ | Excellent but much more expensive |
| Fallback 1 | aug-cc-pVDZ | If def2-TZVPD is too expensive |
| Fallback 2 | def2-SVPD | If aug-cc-pVDZ is too expensive |
| Last resort | — | Give up or use ORCA with RI |

**Pople basis sets for dipole moment are terrible — absolutely do not use.**

### Polarizability

Most cost-effective basis sets (small to large):
1. ZPOL (Sadlej)
2. jul-cc-pVDZ
3. aug-cc-pVDZ
4. POL (Sadlej)
5. aug-cc-pVTZ(-f,-d) — aug-cc-pVTZ with heavy atom f and light atom d polarization removed
6. LPol-ds (Sadlej)

**Note:** def2-SVPD etc. (def2 series with D suffix, optimized for polarizability) are less cost-effective than the above but usable if desired.

For pseudopotentials: Use LFK pseudopotential basis (modified from SBKJC) for polariz accuracy comparable to all-electron POL basis.

See sobereva.com/345 for Sadlej basis set Gaussian definitions.

### First hyperpolarizability

Most cost-effective basis sets (small to large):
1. aug-cc-pVDZ
2. POL
3. aug-cc-pVTZ(-f,-d)
4. LPol-ds
5. LPol-fs

For ultra-high precision on small systems:
- t-aug-cc-pVTZ or aug-pcseg-3 (similar size, ~2x basis functions of LPol-ds)
- Use adddiffuse tool (sobereva.com/347) to generate even-tempered diffuse functions if needed

## 5. Vibrational frequency and related spectra

### Frequency / IR / VCD

For large systems:
- **Sufficient:** 6-31G*
- **Maximum needed:** def-TZVP
- **Do NOT go higher** — it's purely wasted time

**Reason:** These calculations are based on the harmonic approximation and require frequency scaling factors to correct systematic errors. After scaling, results from small, medium, and large basis sets are essentially identical. Using large basis sets for these tasks is beginner behavior.

See sobereva.com/221 for frequency scaling factors.

### Raman / ROA

These are vibration spectra but require diffuse functions because they involve polarizability derivatives with respect to vibrational coordinates.

**Recommended two-step method** (J. Chem. Theory Comput., 7, 3323, 2011):
1. Optimization + frequency analysis: No diffuse functions needed (6-31G* to def-TZVP is enough)
2. Polarizability derivative calculation: Add diffuse functions (>= aug-cc-pVDZ)

This is cheaper than using diffuse functions throughout with no accuracy loss. Gaussian supports this two-step method.

ROA and Raman are vibration spectra, so frequency scaling factors should also be applied.

**Do NOT add diffuse functions for NMR.** (Repeated because this is such a common mistake.)

## 6. All-electron relativistic calculations

When using DKH, ZORA, X2C relativistic Hamiltonians:

**Must use basis sets specifically optimized for relativistic calculations:**
- cc-pVnZ-DK series
- SARC series
- Or fully uncontracted basis sets like UGBS

See sobereva.com/156 for available relativistic basis sets.

**Absolutely do NOT use ordinary basis sets from Section 1.2** for all-electron relativistic calculations.

**Critical error:** Some beginners use pseudopotential basis sets with DKH2 relativistic Hamiltonian — this gives completely wrong results! Relativistic Hamiltonians require all-electron basis sets.

**Exception:** If only considering spin-orbit coupling (not scalar relativistic effects), ordinary all-electron basis sets and pseudopotentials can be used normally.

## 7. Wavefunction analysis

### Real-space function analysis

For electron density, ELF, electrostatic potential, AIM, RDG analysis:
- **Qualitatively correct:** 6-31G* is enough
- **More than sufficient:** 6-311G** or def-TZVP
- **For anions:** Add one layer of s,p diffuse functions
- **Going larger:** No use — these real-space functions converge quickly with basis set size
- **Adding diffuse functions:** Has almost no effect on real-space function distribution — only wastes time (but doesn't make results worse)

**NBO analysis:** Same basis set requirements as real-space analysis.

### Direct basis-function-based analysis

For CDA analysis, Mayer bond order, Wiberg bond order, Mulliken analysis, SCPA analysis, PDOS/OPDOS plots based on Mulliken/SCPA in Multiwfn:

- **Recommended:** 6-311G** (results are NOT better than 6-31G**)
- **Do NOT go to 4-zeta:** Results get worse
- **ABSOLUTELY DO NOT use diffuse functions:** Results are USELESS, USELESS, USELESS!

Diffuse functions have no chemical meaning, so methods that partition atomic space based directly on basis functions give terrible results with diffuse functions. This mistake appears frequently even in high-IF journal papers — authors lacking wavefunction analysis常识.

References:
- sobereva.com on atomic charge comparison (www.whxb.pku.edu.cn/CN/abstract/abstract27818.shtml)
- GCDA method (doi.org/10.12677/japc.2015.44013)
- Molecular orbital composition calculation (化学学报,69,2393)

**With pseudopotentials:** Must use small-core pseudopotentials for wavefunction analysis. See sobereva.com/156.

## 8. Solvation energy (dissolution free energy)

When using implicit solvent models for solvation energy:

**Must use the level the solvent model was parameterized at:**
- SMD is best parameterized at M05-2X/6-31G*
- Recommend computing dissolution free energy at M05-2X/6-31G* with SMD
- Using larger basis sets (e.g., aug-cc-pVTZ) actually makes results worse

See sobereva.com/327 for detailed discussion.

**Note:** Optimization and single-point do NOT need the same solvent model.

## 9. Periodic system calculations

For Gaussian, Crystal and other Gaussian-basis periodic programs:

- 6-31G** (commonly used for isolated systems) is also suitable for organic periodic systems
- Many molecular basis sets are NOT directly suitable for periodic calculations (e.g., 6-311G* for Si)
  - These often have small-exponent diffuse-like functions useful for molecular orbital tails but unnecessary (and problematic) in periodic systems
  - Need to manually increase exponents or remove such functions
- Basis sets with diffuse functions are absolutely unusable for periodic calculations
- Some basis sets have redundant functions that should be removed

**Recommended periodic basis sets** (from Crystal website, format needs conversion):
- https://www.crystal.unito.it/basis_sets.html
- pob-TZVP: Modified from def2-TZVP for solid-state calculations
- pob-DZVP-rev2 and pob-TZVP-rev2 (2019): Improved SCF stability and lattice constants vs. original pob
- Alternative source: https://www.chemiebn.uni-bonn.de/pctc/mulliken-center/software/ssc_basis/basis

## 10. Hyperfine coupling

Fermi contact is the main source of hyperfine coupling constants — requires spin density at the nucleus.

**Recommended:**
- EPR-II, EPR-III (Gaussian built-in, optimized for DFT hyperfine coupling, defined for H, B, C, N, O, F only)
- IGLO-III or pcJ series (suitable for nuclear spin-spin coupling, also work for hyperfine)

These basis sets have tight s functions that better describe spin density at the nucleus.

## 11. Explicit correlation calculations

Must use basis sets specifically optimized for explicit correlation:
- Most well-known: cc-pVnZ-F12 series

## 12. Density fitting accelerated calculations

**Recommendation:** Use basis sets with dedicated auxiliary (density fitting) basis sets.
- def2 series: Has dedicated auxiliary basis sets — best performance
- Pople series: No dedicated auxiliary basis sets — program auto-generates them, which costs more and gives less acceleration
- Borrowing auxiliary basis sets from similar or higher tier basis sets works but is imperfect

See sobereva.com/214 for density fitting acceleration details.

## 13. BSSE and counterpoise

BSSE (Basis Set Superposition Error): Gaussian basis functions centered on atoms invade neighboring atom space, causing interaction energy calculations to overestimate binding strength.

**Solutions:**
- **Counterpoise:** Only for energy calculations — NEVER for geometry optimization or frequency analysis
  - No analytic derivatives at counterpoise-corrected level
  - Extremely slow for large systems
  - Negligible structural improvement
- **gcp:** Alternative correction method (see sobereva.com/214)

See sobereva.com/46 for BSSE and Gaussian's handling.
