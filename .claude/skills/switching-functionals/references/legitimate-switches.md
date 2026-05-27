# Legitimate Functional Switches

Detailed examples and justifications for acceptable functional switching in quantum chemistry research, based on Sobereva's article (sobereva.com/631).

## Switch Type 1: Different problem types → different best functionals

### Example: Large conjugated organic system

**Ground-state geometry optimization: PBE0**
- JCTC, 12, 459 (2016): PBE0 nearly the best among common functionals for organic molecule geometry
- Widely used in literature — reviewers accept it
- Reasonable computational cost

**Electronic spectrum calculation: CAM-B3LYP**
- PBE0 has low HF% (25%) — tends to underestimate excitation energies for conjugated systems
- CAM-B3LYP is range-separated with high long-range HF% — well-established for conjugated system spectra
- Many literature precedents for CAM-B3LYP on conjugated systems
- **For ground-state geometry, CAM-B3LYP is not as good as PBE0** and is more expensive (range-separated)

**Reviewer defense:** Cite the benchmark for PBE0 geometry (JCTC, 12, 459, 2016) and the established use of CAM-B3LYP for conjugated system spectra.

### Example: Organic reaction mechanism

**Geometry optimization + frequency: B3LYP-D3(BJ)**
- Reliable for organic geometry
- Fast — good for exploring multiple TS and intermediate structures

**Single-point energy: DLPNO-CCSD(T)**
- Near-CCSD(T) accuracy at much lower cost
- Standard for high-quality reaction energies

**Justification:** Published example: wB97XD opt/TS + DLPNO-CCSD(T) SP for Li⁺ migration barriers (sobereva.com/630).

## Switch Type 2: Cheap for expensive tasks, expensive for critical SP

### Example: Weak interaction energy

**Optimization: B3LYP-D3(BJ)/def2-SVP**
- D3-corrected B3LYP gives reliable structures for weak interaction complexes
- JCTC benchmark shows B3LYP-D3(BJ) nearly the best for optimizing weak interaction systems
- Computationally affordable

**Single-point: PWPB95-D3/def2-TZVP**
- Double-hybrid — significantly more accurate than any standard DFT functional
- Significantly more expensive — but only one calculation needed
- Published example: wB97XD opt + wB97X-V SP for 18-carbon-ring motor system weak interaction energy (sobereva.com/684)

**Why not use PWPB95-D3 for optimization too?**
- Double-hybrid optimization is prohibitively expensive for most systems
- Geometry improvement from double-hybrid is marginal compared to D3-corrected DFT

### Example: Standard organic study with cost consideration

**Optimization + frequency: B3LYP-D3(BJ)/6-31G***
- Fast, reliable
- `int=fine` suffices (cheap grid)

**Single-point: M06-2X/def2-TZVP**
- Better for organic energetics, especially with weak interactions and conjugation
- More expensive — especially with `int=ultrafine` grid needed for M06-2X
- But only one calculation needed

**Note:** While this switch is justifiable, some reviewers may question it. To be completely safe, use M06-2X for everything — the cost difference is not huge (same tier), and M06-2X is slightly better for organic geometry anyway.

### Example: Pure functional optimization in ORCA/Turbomole

**Optimization + frequency (ORCA): BLYP-D3(BJ)/def2-SVP**
- With ORCA's excellent density fitting, pure functionals are >10× faster than hybrids for large systems
- See sobereva.com/214: "Resolution of identity" approach for large weak interaction systems
- B97-3c is also an excellent cheap choice for optimization

**Single-point (ORCA): wB97M-V/def2-TZVP**
- One of the best functionals available
- More expensive — but only one calculation

**Justification:** "Pure functional for optimization to save time via density fitting" is a well-established and reviewer-acceptable reason.

**Caveat:** Don't use pure functionals for:
- (Hyper)polarizability — pure functionals significantly overestimate
- Excitation energies (especially CT states) — pure functionals significantly underestimate

## Switch Type 3: Ground-state vs excited-state

### Example: CT state study

**Ground-state optimization: B3LYP**
- Reliable for ground-state geometry of organic molecules
- Fast and well-established

**Excited-state (CT) optimization: wB97XD**
- B3LYP fails for CT states — low HF% cannot describe charge transfer
- Chem. Soc. Rev., 42, 845 (2013): For CT or Rydberg EES, "it is mandatory to use range-separated hybrids (we recommend CAM-B3LYP or wB97X-D) to reach physically meaningful estimates"
- B3LYP also fails for CT state geometry optimization

**Justification:** Ground and excited states are fundamentally different physical problems with different requirements.

**If you want to be completely safe:** Use wB97XD for both. It works well for organic ground states too — the additional cost for ground-state optimization is negligible compared to excited-state optimization cost.

### Warning: Don't mix functionals for density difference analysis

When computing density difference between ground and excited states (e.g., for visualization in Multiwfn):
- **Must use the same functional for both ground and excited state**
- Different functionals have different electron distributions
- Computing ρ_excited(wB97XD) - ρ_ground(B3LYP) introduces artificial features
- The density difference would reflect functional differences, not just excitation character

## Switch Type 4: Method comparison study

### Example: Benchmarking functional accuracy for polarizability

**Optimization: PBE0/def2-TZVP** (one reasonable functional for all structures)
**Property calculation:**
- Functional A: PBE0
- Functional B: B3LYP
- Functional C: M06-2X
- Functional D: wB97XD

**Justification:** The study IS about comparing functionals. Using one consistent geometry eliminates geometry as a confounding variable.

## Switch Type 5: Gas-phase opt for multi-solvent study

### Example: Vertical ionization energy in 8 solvents

**Optimization: gas-phase**
- Solvent has negligible effect on this molecule's geometry (verified by test calculation or known from similar systems)
- Saves 7 redundant optimizations

**Single-point: SMD in each of 8 solvents**
- All 8 calculations on the same geometry

**Justification:** Clear cost saving with well-understood justification. If solvent effect on geometry is known to be negligible, gas-phase optimization is appropriate.

**Contrast with:** If the molecule has significant local charges (ions, zwitterions), solvent DOES affect geometry — then you MUST optimize in solvent.

## Switch Type 6: High-level composite method approach

### Example: Thermochemistry with composite method

**Optimization + frequency: B3LYP-D3(BJ)/def2-SVP**
- Used in JPCA, 121, 4379 (2017) composite method
- Reliable geometry and thermal corrections

**Single-point: DLPNO-CCSD(T)/def2-TZVP**
- High-accuracy electronic energy
- Empirical post-corrections applied

**Justification:** This is the approach used in published composite methods — well-established and defended by the methodology literature.

## Switching basis sets: acceptable patterns

| Pattern | Acceptable? | Why |
|---------|-----------|-----|
| opt: def2-SVP → SP: def2-TZVP | Yes | SP basis clearly higher tier |
| opt: def2-SVP → SP: def2-QZVP | Yes | Even better — approaching basis limit |
| opt: 6-31G* → SP: def2-TZVP | Yes | SP basis clearly higher tier |
| opt: 6-31G** → SP: def2-SVP | No | Same tier — no justification |
| opt: def2-TZVP → SP: def2-SVP | No | SP basis lower than opt — backwards |
| opt: cc-pVDZ → SP: cc-pVTZ | Yes | SP basis higher tier |
| opt: cc-pVTZ → SP: CBS extrapolation | Yes | SP uses extrapolation for accuracy |

**Rule of thumb:** SP basis should be equal to or higher quality than opt basis. Same-tier switching without justification looks arbitrary.

## References

- sobereva.com/631 — This article (switching functionals)
- sobereva.com/272 — DFT functional selection guide
- sobereva.com/413 — When DFT-D3 is needed
- sobereva.com/557 — When to use B3LYP for optimization
- sobereva.com/214 — RI approach for large weak interaction systems in ORCA
- sobereva.com/684 — 18-carbon-ring molecular motor design (wB97XD opt + wB97X-V SP)
- sobereva.com/630 — 18-carbon-ring Li optical switch (wB97XD opt + DLPNO-CCSD(T) SP)
- J. Chem. Theory Comput., 12, 459 (2016) — PBE0 geometry benchmark
- Chem. Soc. Rev., 42, 845 (2013) — CT state optimization requirements
- J. Phys. Chem. A, 121, 4379 (2017) — B3LYP-D3(BJ) + DLPNO-CCSD(T) thermochemistry
