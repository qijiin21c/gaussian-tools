# Why Optimization and Frequency Don't Need Large Basis Sets

Detailed analysis of basis set sensitivity for geometry optimization and frequency calculations, based on Sobereva's article (sobereva.com/387).

## Core principle

**Geometry optimization and frequency results are much less sensitive to basis set size than energy calculations.** Using a large basis set for opt/freq wastes significant computation time with minimal accuracy gain.

## HF molecule: complete basis set sensitivity data

HF molecule (6 electrons, single bond) — a minimal test case showing the dramatic difference in basis set sensitivity between geometry/frequency vs. energy:

| Basis set | GTF count | R(H-F) / Å | Error / Å | Error % | Frequency / cm⁻¹ | Error / cm⁻¹ | Error % | Energy / Hartree | Error / kJ/mol | Error % |
|-----------|-----------|------------|-----------|---------|-------------------|-------------|---------|------------------|----------------|---------|
| def2-SVP | 25 | 1.3940 | +0.0047 | **0.3%** | 1057.0 | +1.4 | **0.13%** | -199.46122 | 26.4 | **4.5%** |
| def2-SV(P) | 22 | 1.3969 | +0.0076 | 0.5% | 1052.9 | -2.7 | 0.26% | -199.45434 | 28.2 | 4.8% |
| def-TZVP | 50 | 1.3895 | +0.0002 | 0.01% | 1055.4 | -0.2 | 0.02% | -199.51173 | 0.4 | 0.07% |
| def2-TZVP | 53 | 1.3896 | +0.0003 | 0.02% | 1055.3 | -0.3 | 0.03% | -199.51145 | 0.4 | 0.07% |
| def2-TZVPP | 78 | 1.3894 | +0.0001 | 0.01% | 1055.4 | -0.2 | 0.02% | -199.51351 | 0.2 | 0.03% |
| def2-QZVP | 108 | 1.3893 | — | — | 1055.6 | — | — | -199.51457 | — | — |

**Key observations:**

1. **Bond length:** def2-SVP error is only 0.0047 Å (0.3%). This is far smaller than the intrinsic error of any DFT functional. Going to def2-QZVP gains only 0.0047 Å.

2. **Frequency:** def2-SVP error is only 1.4 cm⁻¹ (0.13%). Typical experimental frequency uncertainty is 10-20 cm⁻¹, and DFT functional error is 30-50 cm⁻¹. Basis set effect is negligible.

3. **Energy:** def2-SVP error is 26.4 kJ/mol (4.5%) — dramatically larger. This is why large basis sets are critical for single-point energy but NOT for geometry.

4. **Timing:** def2-QZVP has 108 GTFs vs. def2-SVP's 25. For a molecule with N atoms, the GTF count scales linearly, but the SCF cost scales as O(N³) to O(N⁴). def2-QZVP is roughly 10-50× more expensive than def2-SVP for the same molecule.

## Why this happens

The potential energy surface (PES) minimum **position** (geometry) and **curvature** (frequency) are much less sensitive to basis set size than the **absolute energy value** at that minimum.

- The PES shape (relative energies between nearby structures) converges quickly with basis set
- The absolute energy at the minimum converges much more slowly
- DFT functionals themselves have large intrinsic errors that dominate over basis set truncation errors for geometry

## JCTC 2023 systematic confirmation

DOI: 10.1021/acs.jctc.3c00388 — A systematic test of basis set effects on DFT geometry optimization across diverse systems. **Conclusion:** Basis set size has minimal impact on geometry accuracy compared to functional choice. The functional is the dominant factor; the basis set is secondary for geometry.

## The hydrogen polarization warning

While def2-SVP is sufficient, going below it is dangerous:

**def2-SV(P) vs def2-SVP:**
- def2-SV(P): Only hydrogen atoms have polarization functions (d functions)
- def2-SVP: All atoms (heavy + H) have polarization functions
- The difference is noticeable — def2-SV(P) gives R(H-F) = 1.3969 Å vs. def2-SVP's 1.3940 Å. def2-SVP is closer to the basis set limit.

**6-31G (no polarization):**
- No polarization on any atom — completely inadequate
- Bond lengths can be off by 0.01-0.02 Å
- Frequencies can be off by 50-100 cm⁻¹

**Minimum acceptable:** def2-SVP or 6-31G** (both are double-zeta with polarization on all atoms).

## Recommended basis sets for opt+freq

| Tier | Basis set | When to use |
|------|-----------|------------|
| **Ideal** | def2-SVP, 6-31G** | >95% of organic systems |
| **Good** | 6-31+G*, def2-SVPD | When anionic character or weak H-bonds present |
| **Acceptable** | def2-SV(P) | Quick optimization, not final |
| **Not acceptable** | 6-31G, STO-3G, 3-21G | Qualitatively wrong |

## Exceptions: when larger basis IS needed

### 1. Transition metal coordination bonds

For transition metal complexes with metal-ligand coordination bonds, def2-SVP vs def2-TZVP difference is significant:
- Metal-ligand bond lengths: def2-SVP error ~0.05-0.10 Å vs. def2-TZVP
- Coordination geometry (octahedral vs. tetrahedral distortion) can be affected
- **Recommendation:** def2-TZVP or def2-TZVPP for TM complex optimization

### 2. Large conjugated systems with delocalization

18-carbon ring (C₁₈) example (sobereva.com/515):
- def2-SVP: Gives wrong bond alternation pattern — equalizes bonds due to insufficient description of electron delocalization
- 6-311G* or def-TZVP: Correct alternating single-triple bond pattern
- **Recommendation:** 6-311G* or def-TZVP for large conjugated systems

### 3. High-precision vibrational frequencies

When frequency accuracy is critical (e.g., isotope effect studies, thermodynamic precision):
- def2-TZVP reduces frequency error from 1.4 cm⁻¹ to 0.3 cm⁻¹ (HF example)
- For DFT, the functional error dominates, but basis set still matters at the ~5 cm⁻¹ level

## Raman/ROA: two-step basis set separation

Raman and ROA (Raman Optical Activity) calculations require computing the derivative of the polarizability tensor with respect to nuclear displacement. This is sensitive to basis set, especially diffuse functions.

**Two-step approach:**

1. **Optimization + frequency (no diffuse functions):**
   ```
   # B3LYP-D3(BJ)/def2-SVP opt freq
   ```
   Get structure, confirm minima (no imaginary frequencies), extract thermochemical data.

2. **Polarizability derivative (with diffuse functions):**
   ```
   # B3LYP-D3(BJ)/def2-TZVP+diffuse freq=Raman
   ```
   Compute Raman/ROA intensities at the already-optimized geometry.

**Why this works:** The polarizability derivative is sensitive to the electron density tail (diffuse region), while the geometry is not. Adding diffuse functions only where needed saves time.

## CCSD(T) energy + DFT opt/freq: why it's justified

A common and well-justified computational pattern:
- **Optimization + frequency:** DFT/def2-SVP (e.g., B3LYP-D3(BJ)/def2-SVP)
- **Single-point energy:** CCSD(T)/def2-TZVP or larger

**Justification:** Comput. Theor. Chem., 1200, 113249 (2021) systematically tested DFT geometry + CCSD(T) energy across multiple systems. Key findings:
- DFT-optimized geometries are close enough to CCSD(T) geometries that the energy difference is negligible
- The energy error from using DFT geometry vs. CCSD(T) geometry is ~0.5-1 kJ/mol
- The overall accuracy gain from CCSD(T) over DFT energy is ~10-50 kJ/mol
- Therefore, the geometry mismatch error is a small fraction of the total improvement

**Practical implication:** This pairing is not just cost-effective — it's scientifically sound. The DFT geometry is "good enough" for CCSD(T) energy evaluation.

## Frequency thermodynamics: quasi-RRHO matters more than basis set

For computing thermochemical corrections from frequency calculations, the treatment of low-frequency modes (<100 cm⁻¹) has a much larger impact than basis set size.

**Harmonic oscillator approximation breakdown:**
- Low-frequency modes are often better described as hindered rotors
- Quasi-RRHO (quasi-rigid-rotor-harmonic-oscillator) corrections can change free energy by several kcal/mol
- This is far larger than the basis set effect on frequency (<1 cm⁻¹ from def2-SVP to def2-QZVP)

**Practical recommendation:** Focus on proper low-frequency mode treatment (see small-imag-freq skill) rather than increasing basis set for frequency calculations.

## Time savings comparison

For a medium-sized organic molecule (~50 atoms):

| Level | Opt time (relative) | SP time (relative) | Total |
|-------|-------------------|-------------------|-------|
| B3LYP-D3(BJ)/def2-SVP opt → B3LYP-D3(BJ)/def2-TZVP SP | 1× | 3× | 4× |
| B3LYP-D3(BJ)/def2-TZVP opt → B3LYP-D3(BJ)/def2-TZVP SP | 5× | 3× | 8× |
| B3LYP-D3(BJ)/def2-SVP opt → CCSD(T)/def2-TZVP SP | 1× | 100× | 101× |

Using def2-SVP for opt/freq saves ~80% of the DFT computation time while preserving geometry and frequency accuracy.

## References

- sobereva.com/387 — This article (basis set for opt/freq)
- sobereva.com/341 — Basis set selection guide
- sobereva.com/515 — Carbon ring C₁₈
- sobereva.com/282 — HF% table for functionals
- J. Chem. Theory Comput., 2023, DOI: 10.1021/acs.jctc.3c00388 — Systematic basis set test for DFT geometry
- Comput. Theor. Chem., 1200, 113249 (2021) — DFT geometry + CCSD(T) energy validation
