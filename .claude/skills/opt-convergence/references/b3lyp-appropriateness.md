# When to Use B3LYP for Geometry Optimization

Detailed discussion of when B3LYP is appropriate for geometry optimization in quantum chemistry research, based on Sobereva's article (sobereva.com/557).

## Why B3LYP survives for optimization

B3LYP (Becke, 3-parameter, Lee-Yang-Parr, 1994) is completely obsolete for single-point energy calculations. For organic systems, persisting with B3LYP for energy computation can even lead to paper rejection (see bbs.keinsci.com/thread-12773-1-1.html).

However, for geometry optimization, B3LYP retains practical value:

### Advantage 1: Speed
Among hybrid functionals in Gaussian, B3LYP is one of the fastest due to its simple functional form. Compared to:
- M06-2X (complex meta-hybrid)
- wB97XD, CAM-B3LYP (range-separated)
- Other Minnesota functionals

B3LYP is noticeably cheaper.

### Advantage 2: Low grid sensitivity
B3LYP produces a smooth potential energy surface even on coarse integration grids. For Gaussian 16 users, `int=fine` (cheaper than the default `ultrafine`) often suffices.

In contrast, modern meta-hybrid functionals (especially M06-2X) are much more grid-sensitive. With insufficient grid quality, they may:
- Fail to converge during optimization
- Converge with spurious imaginary frequencies
- For M06-2X on weak interaction systems, even `int=ultrafine` may be insufficient

See sobereva.com/69 on grid integration in DFT.

### Advantage 3: Literature precedent
Massive numbers of papers use B3LYP for optimization. For most systems, no other functional has a particularly significant advantage over B3LYP for structural optimization. Reviewers rarely question B3LYP for geometry.

## The universal recommendation: B3LYP-D3(BJ)

**Always add DFT-D3 dispersion correction to B3LYP for optimization.** Even when weak interactions are not obviously present.

Reasons:
- D3 is "free" — no additional computational cost
- Improves accuracy universally
- Eliminates reviewer criticism
- Adds universality to templates — you don't need to know what system the user will run

This is why scripts like the RESP charge calculator (sobereva.com/476) use B3LYP-D3(BJ) rather than bare B3LYP — you never know what system someone will throw at it.

See sobereva.com/413 on "do I need DFT-D3?", sobereva.com/210 on using DFT-D, and sobereva.com/83 on DFT-D.

## System-by-system analysis

### Weak interaction systems

**Never use bare B3LYP** — it describes dispersion completely incorrectly.

**Ar₂ dimer example** (from Chem. Rev., 116, 5105, 2016):
- B3LYP: No minimum at all — cannot even find the dimer structure
- B3LYP-D3: Minimum position close to the accurate result

**DNA base pairs** (from JACS, 130, 16055, 2008):
- Without dispersion correction: π-π stacking distances are completely wrong (TPSS behaves like B3LYP here)
- With D2/D3 correction: Structure matches experiment well
- H-bond distances are OK without D3 (electrostatic-dominated), but π-π stacking (dispersion-dominated) fails completely

**Electrostatic-dominated H-bonds:** Water dimer — B3LYP is qualitatively correct because H-bond is primarily electrostatic. See sobereva.com/513 on H-bond nature. But D3 still provides quantitative improvement.

**Cation-anion interactions:** Case-dependent.
- Sodium acetate: Na⁺-acetate attraction is almost entirely electrostatic/polarization — D3 optional
- Ionic liquids: Ions are large with flexible chains — dispersion affects binding energy and ion conformation — D3 recommended

**Conformational/conformational search:** Always use B3LYP-D3(BJ). Example: Remdesivir conformational search (bbs.keinsci.com/thread-16255-1-1.html) — many rotatable bonds, dispersion clearly affects conformer structures and relative energies.

**Benchmark:** JCTC article (referenced in bbs.keinsci.com/thread-19495-1-1.html) found B3LYP-D3(BJ) has nearly the highest accuracy among functionals for optimizing weak interaction systems. It's both cheap and accurate.

### Organic molecules (main-group, no weak interactions, no large conjugation)

B3LYP performs well for standard organic molecules:
- JCTC, 8, 2165 (2012): B3LYP nearly the best among common functionals for optimizing small diverse molecules — better than M06-2X
- JCTC, 12, 459 (2016): PBE0 nearly best, but B3LYP is well within the reasonable range
- JPCL, 11, 9957 (2020): B3LYP essentially the best when evaluated by geometry energy offset (GEO) parameter

B3LYD is used as the optimization level in many composite thermochemistry methods:
- G4, G3//B3LYP, CBS-QB3: All based on B3LYP optimization
- JPCA, 121, 4379 (2017): Uses B3LYP-D3(BJ) for opt+freq + DLPNO-CCSD(T) for high-accuracy SP

**Recommendation:** Even for non-weak-interaction organic systems, add D3 for universality.

### Transition metal complexes

B3LYP is widely used for transition metal complex optimization — acceptable but not optimal.

**Metal-ligand bond lengths:** B3LYP is consistently mediocre in benchmarks:
- JCTC, 2, 1282 (2006): B3LYP average performance
- JCTC, 13, 5291 (2017): TPSSh often outstanding

**When B3LYP is fine:**
- You only care about ligand chemistry (e.g., reactions on ligands)
- General structure without concern for precise metal-ligand distances

**When to use something else:**
- Metal-ligand bond length accuracy is critical → TPSSh
- Metal-metal bonds → **Never use B3LYP** (see below)

**Metal-metal bonds (d-block):**
Example: [V(Cp)]₂Pn with V-V bond (JCTC, 8, 908, 2012):
- Experimental V-V: 2.538 Å
- BP86 (pure functional): 2.568 Å — excellent
- TPSS, PBE: similar to BP86
- **B3LYP: 2.994 Å — qualitatively wrong**

For direct metal-metal bonding with strong static correlation, **always use pure functionals** (BP86, TPSS, PBE, SCAN). Never use hybrid functionals.

### Large π-conjugated systems

**B3LYP fails for large conjugated systems** — a fact many people don't know.

**Root cause:** Self-interaction error (SIE). B3LYP has significant electron self-interaction error, causing:
- **Overdelocalization** of wavefunctions (opposite of HF, which overlocalizes)
- **Forces fully coplanar conformations** in extended π-systems
- **Equalizes bond lengths** along conjugation paths

See sobereva.com/282 for HF% table of different functionals.

**[18]Annulene** (Angew. Chem. Int. Ed., 43, 4200, 2004):
- Experimental: Unequal C-C bonds, non-planar
- B3LYP: Equal C-C bonds, planar D6h — wrong
- wB97XD: Unequal bonds, D3 symmetry, slight out-of-plane distortion from H-H steric — correct

**Carbon ring C₁₈** (Carbon, 165, 468, 2020; sobereva.com/515):
- B3LYP, PBE0, TPSSh (low-HF%): Equal C-C bonds — wrong
- wB97XD, high-HF% functionals: Alternating long-short bonds — matches CCSD and AFM experiment
- The problem extends to all functionals with similar HF% to B3LYP

**[IF6]⁻** (Inorg. Chem., 47, 5485, 2008):
- CCSD(T)/aug-cc-pVTZ: C3v minimum (iodine has lone pair), Oh is higher energy and not a minimum
- B3LYP/def2-TZVP: Oh minimum with no imaginary frequencies — wrong
- wB97XD: Oh has 3 degenerate imaginary frequencies; removing symmetry gives C3v minimum with no imaginary frequencies — correct. ELF analysis shows lone pair on iodine as expected.
- MP2 and B2PLYP have the same problem as B3LYP for this system

**Recommendation:** For large conjugated systems, use wB97XD. M06-2X also works but is more grid-sensitive.

**Practical tip:** If unsure about a system's electronic structure, optimize with both B3LYP and wB97XD. If results agree, B3LYP is probably fine. If they differ significantly, B3LYP's result is likely unreliable.

### Excited state optimization

Ground-state and excited-state optimization performance are **completely uncorrelated**. The excited-state PES is much harder to describe than the ground-state PES.

**B3LYP for excited states:** Average error is small but some systems are qualitatively wrong. JCTC, 14, 3715 (2018):
- B3LYP: Small average error but qualitative failures for some systems
- PBE0, wB97XD: All tested systems reasonable, though average error slightly larger than B3LYP

**Charge-transfer (CT) excited states:**
- B3LYP cannot describe CT excitation energies (insufficient HF%)
- B3LYP also fails for CT state PES and optimization
- Chem. Soc. Rev., 42, 845 (2013): B3LYP gives nearly perpendicular benzene ring structure for a CT state — qualitatively wrong. CAM-B3LYP gives correct structure.

**For CT or Rydberg excited states:** Must use range-separated hybrids (CAM-B3LYP, wB97X-D). The Chem. Soc. Rev. paper emphasizes this is **mandatory** for physically meaningful results.

See sobereva.com/265 on excited state methods, sobereva.com/284 on excitation classification, sobereva.com/434 on hole-electron analysis, sobereva.com/550 on customizing range-separated functionals.

**Note:** Ground-state and excited-state optimization functionals don't need to match. B3LYP for ground state + wB97XD for excited state is fine in principle (though some reviewers may question it — to avoid this, use wB97XD for both).

### Transition state optimization

B3LYP for organic reaction TS is generally reasonable and remains widely used.

TS optimization benchmarks are rare:
- Org. Biomol. Chem., 9, 689 (2011): Compares many functionals for TS structures but has methodological flaws. Conclusion: "B3LYP still has an important role" but not well-supported by data. However, it's useful to cite if reviewers question B3LYP for TS.

**For organic TS:** wB97XD or M06-2X typically more accurate, but B3LYP is fine if the resulting structure looks reasonable.

**For non-organic TS:** If no guidance on better functionals, try B3LYP first.

**Warning:** Finding a TS with one imaginary frequency doesn't guarantee it's correct.

**F + H₂ → HF + H radical reaction example:**
- B2PLYP-D3(BJ)/def-TZVP: Angle 116.3°, F-H 1.600 Å, H-H 0.765 Å — matches MRCI/jul-cc-pV5Z (113.7°, 1.554 Å, 0.771 Å) well
- M06-2X: Angle too large but qualitatively correct
- **B3LYP: Qualitatively wrong** — IRC from this TS gives HF+H on both sides, not the correct reactant/product

### Clusters

| Cluster type | B3LYP appropriate? | Better alternatives |
|-------------|-------------------|---------------------|
| Carbon clusters | Yes | — |
| Boron clusters | Probably not | PBE0, TPSSh (JPCA, 123, 10454, 2019) |
| Gold clusters | **NO** — very poor | TPSSh best, PBE0 acceptable (JPCA, 121, 2410, 2017) |
| d-block metal clusters | **NO** | BP86, TPSS, SCAN (pure functionals) |
| Metal lattice constants | **NO** — garbage | PBE0, HSE (JCP, 127, 024103, 2007) |

For Ag cluster surface models (sobereva.com/540), PBE0-D3(BJ) is used instead of B3LYP-D3(BJ) partly due to B3LYP's poor performance for metal clusters.

### High-precision thermochemistry

B3LYP is the default optimization level in many composite methods:
- G4, G3//B3LYP, CBS-QB3: B3LYP-based optimization
- JPCA, 121, 4379 (2017): B3LYP-D3(BJ) opt+freq + DLPNO-CCSD(T) SP

This validates B3LYP's reliability for getting structures right.

## References

- sobereva.com/557 — This article (when to use B3LYP)
- sobereva.com/272 — DFT functional selection guide
- sobereva.com/413 — When DFT-D3 is needed
- sobereva.com/210 — Using DFT-D
- sobereva.com/83 — DFT-D overview
- sobereva.com/69 — Grid integration in DFT
- sobereva.com/513 — H-bond nature
- sobereva.com/476 — RESP charge script (uses B3LYP-D3(BJ))
- sobereva.com/282 — HF% table for functionals
- sobereva.com/515 — Carbon ring C₁₈
- sobereva.com/265 — Excited state methods
- sobereva.com/284 — Excitation classification
- sobereva.com/434 — Hole-electron analysis
- sobereva.com/550 — Custom range-separated functionals
- sobereva.com/540 — Metal surface cluster models
- bbs.keinsci.com/thread-12773-1-1.html — Consequences of persisting with B3LYP
- bbs.keinsci.com/thread-19495-1-1.html — B3LYP-D3(BJ) for weak interactions
- bbs.keinsci.com/thread-16255-1-1.html — Remdesivir conformational search
- Chem. Rev., 116, 5105 (2016) — DFT for noncovalent interactions
- J. Am. Chem. Soc., 130, 16055 (2008) — Dispersion in DNA
- J. Chem. Theory Comput., 8, 2165 (2012) — Functional benchmark for small molecules
- J. Chem. Theory Comput., 12, 459 (2016) — Functional benchmark for organic molecules
- J. Phys. Chem. Lett., 11, 9957 (2020) — GEO parameter for functional benchmark
- J. Phys. Chem. A, 121, 4379 (2017) — B3LYP-D3(BJ) + DLPNO-CCSD(T) thermochemistry
- J. Chem. Theory Comput., 2, 1282 (2006) — TM complex functional benchmark
- J. Chem. Theory Comput., 13, 5291 (2017) — TM complex functional benchmark
- J. Chem. Theory Comput., 8, 908 (2012) — Metal-metal bonds
- Angew. Chem. Int. Ed., 43, 4200 (2004) — [18]annulene
- Chem. Mater., 29, 477 (2017) — Bredas on B3LYP SIE in conjugated systems
- Carbon, 165, 468 (2020) — Carbon ring C₁₈
- Inorg. Chem., 47, 5485 (2008) — [IF6]-
- J. Chem. Theory Comput., 14, 3715 (2018) — Excited state optimization benchmark
- Chem. Soc. Rev., 42, 845 (2013) — CT state optimization
- Org. Biomol. Chem., 9, 689 (2011) — TS optimization benchmark
- J. Chem. Phys., 128, 034305 (2008) — F+H2 TS at MRCI level
- J. Phys. Chem. A, 123, 10454 (2019) — Boron cluster benchmark
- J. Phys. Chem. A, 121, 2410 (2017) — Gold cluster benchmark
- J. Chem. Phys., 127, 024103 (2007) — Metal lattice constants
