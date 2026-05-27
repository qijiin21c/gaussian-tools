---
name: diffuse-functions
description: This skill should be used when the user asks to "add diffuse functions", "弥散函数", "when to use diffuse", "aug-cc-pVDZ", "maug-cc-pVTZ", "jul-cc-pVnZ", "月份基组", "6-31+G*", "6-311++G**", "diffuse basis set", "anion basis set", "polarizability basis set", "give hydrogen diffuse", "diffuse functions cause problems", "basis set with diffuse", "reduce diffuse functions", or mentions adding diffuse functions to basis sets for quantum chemistry calculations.
version: 0.1.0
---

# Diffuse Functions and "Month" Basis Sets Guide

Comprehensive guidance on when and how to use diffuse functions in quantum chemistry, based on Sobereva's authoritative article (sobereva.com/119).

**Core principle:** Diffuse functions are NOT universally beneficial. They are essential for some tasks, harmful for others, and add massive computational cost. When in doubt about whether to add diffuse functions — DON'T.

## What are diffuse functions?

Basis functions with very small exponents — they have a wide spatial distribution. Usually uncontracted. Added to describe electrons that are loosely bound or extend far from the nucleus.

## When diffuse functions are essential (MUST add, results unusable without)

| Task | Reason |
|------|--------|
| **Dipole moment, multipole moment** | Diffuse functions describe electron density far from nuclei |
| **Polarizability, hyperpolarizability** | Response properties depend on tail of electron distribution |
| **Rydberg excited states** | Rydberg orbitals are spatially extended |
| **Anion energy, electron affinity** | Extra electron is loosely bound |

**Important notes on anions:**
- "Anion" here means small anions (e.g., nitrate). For larger anions, you only need diffuse on atoms with significant negative charge — much cheaper than all-atom diffuse.
- If your system is neutral or even cationic but has atoms with significant negative charge, add diffuse to those atoms. Use Multiwfn to compute ADCH charges (see sobereva.com/714) — if any atom has charge < -0.5, adding diffuse to that atom is meaningful (more negative = more important).

**Trade-off rule:** When diffuse functions are essential, it's better to drop a zeta level to afford them. For dipole/polarizability: go from 3-zeta to 2-zeta + diffuse rather than 3-zeta without diffuse.

## When diffuse functions are strongly recommended

| Task | Notes |
|------|-------|
| **Weak interaction energy** | If using 4-zeta basis and no anion involved, diffuse is NOT needed |
| **IR, Raman, ROA intensity** | Polarizability derivatives need diffuse |

## When diffuse functions are beneficial (add if resources allow)

| Task | Notes |
|------|-------|
| **Reaction barrier** | Only for 3-zeta and below. def2-TZVP/def2-TZVPP already have slight diffuse character — adding diffuse won't improve barrier results |
| **Optimizing anion or weak interaction structures** | Geometry + frequency |

## When NOT to add diffuse functions

For neutral systems without significant weak interactions or locally negative charge, for tasks NOT mentioned above:

**Do NOT add diffuse for:**
- Atomization energy
- Valence electron excitation
- Bond energy
- Ionization energy
- Geometry optimization (general)
- NMR
- Any task not listed above

**Adding diffuse in these cases:**
- Provides no accuracy improvement
- Adds enormous computational cost
- Causes SCF convergence problems
- Ruins wavefunction analysis (Mulliken charges, Mayer bond orders become garbage)
- May cause structural/symmetry issues

**Adding diffuse functions unnecessarily is self-inflicted harm!**

## Common mistake: Adding diffuse to cations

Cations do NOT have loosely bound electrons. Adding diffuse to cations for ordinary calculations (energy, geometry optimization) is unreasonable. Reviewers immediately recognize this as lack of computational chemistry常识. This mistake often comes from misleading Chinese-language slides that say "add diffuse for ionic systems" without distinguishing cations from anions.

## Hydrogen: When to add diffuse

**Most of the time: DO NOT add diffuse to hydrogen.**

Why:
- Hydrogen has only one electron and low electronegativity
- In molecular environments, hydrogen usually loses electron density
- Organic systems have many hydrogens — diffuse on all of them adds significant cost
- Heavy atom diffuse functions already extend into hydrogen regions, partially serving the same role
- Extensive testing confirms: diffuse on hydrogen has negligible effect for ordinary calculations
- Even for H-bond energy calculations, diffuse on hydrogen has minimal impact

**Recommended:** When diffuse is needed, use `6-311+G**` (diffuse on heavy atoms only) rather than `6-311++G**` (diffuse on hydrogen too).

**Exceptions — when hydrogen DOES need diffuse:**
- (Hyper)polarizability calculations
- Hydrogen carries significant negative charge (e.g., LiH)
- These are rare cases

## Problems caused by diffuse functions

1. **Explosive cost increase** — especially for cc-pVnZ series, going from cc-pVTZ to aug-cc-pVTZ may make the calculation impossible
2. **SCF convergence difficulty** — often much harder to converge with diffuse
3. **Ruins Hilbert-space wavefunction analysis** — Mulliken charges become terrible, Mayer bond orders unreliable. Reason: diffuse functions from atom A extend into atom B's space, so B's electrons get assigned to A
4. **Virtual orbital meaning degrades** — especially under HF with diffuse, virtual orbitals become extremely spatially extended, making frontier orbital theory inapplicable
5. **Linear dependency problems** — programs usually auto-detect and remove problematic functions
6. **Symmetry degradation** — optimized structures may lose point group symmetry due to numerical precision issues from diffuse
7. **Intramolecular BSSE** — if the original basis is incomplete but you add too many diffuse functions, effects that should be described by valence functions get described by diffuse instead. Example: MP2 with 6-31++G** gives bent benzene (planar should be stable) because diffuse s/p functions try to compensate for missing f polarization

## Partial diffuse: Only add where needed

If only part of the system has significant negative charge or is easily polarized, or if weak interactions only involve part of the system — and you can't afford diffuse on all atoms — add diffuse only to those specific regions. This dramatically reduces cost.

## Common diffuse-containing basis sets

### Pople series
- `6-31+G*` — diffuse on heavy atoms only (one layer of s+p with same exponent)
- `6-311++G(2df,2p)` — diffuse on heavy atoms AND hydrogen (one layer of s on H, s+p on heavy)
- All Pople basis sets share the same diffuse exponents (not separately optimized)
- **Important:** `6-311G*` is cheaper AND better than `6-31+G*` for problems where diffuse isn't critical. Many people use `6-31+G*` unnecessarily.

### Dunning cc-pVnZ series
- `aug-cc-pVnZ` — adds one layer of diffuse for EACH angular momentum present
  - Example: cc-pVTZ for C is 4s,3p,2d,1f → aug- adds s, p, d, f diffuse
  - Example: cc-pVDZ for H is 2s,1p → aug- adds s, p diffuse
- Always adds diffuse to hydrogen (unlike Pople's +/++ distinction)
- `d-aug-cc-pVnZ`, `t-aug-cc-pVnZ` — two or three layers of diffuse per angular momentum (extremely expensive, for Rydberg states, hyperpolarizability)
- aug- versions also exist for: cc-pCVnZ, cc-pwCVnZ, cc-pVnZ-DK, cc-pV(n+d)Z, cc-pVnZ-PP

### def2- series
- No official diffuse versions
- See sobereva.com/340 for ways to add diffuse to def2- basis sets
- def2-SVPD, TZVPD, TZVPPD, QZVPD, QZVPPD — proposed in JCP,133,134105

### pc-n (Jensen polarization-consistent)
- Jensen proposed method to add diffuse to pc-n series (JCP,117,9234)
- Adding s+p diffuse greatly improves DFT electron affinity accuracy
- Response properties need higher-angular-momentum diffuse too

### Response-property-optimized diffuse basis sets
| Basis | Size | Accuracy | Notes |
|-------|------|----------|-------|
| **Sadlej POL** | ~cc-pVTZ | Polarizability ≈ aug-cc-pVTZ | Much cheaper than aug-cc-pVTZ |
| **Sadlej ZPOL** | ~6-311+G* | Polarizability > 6-311++G(2df,2p) | Great for large systems |
| **Sadlej LPol-ds** | > POL | Hyperpolarizability ≈ d-aug-cc-pVTZ | Cheapest at this accuracy. C,H,O,N,F only |
| **LFK pseudopotential** | SBKJC + diffuse/polarization | Polarizability ≈ Sadlej all-electron | For pseudopotential calculations |

## "Month" basis sets: Reducing diffuse cost

The "month" series systematically removes high-angular-momentum diffuse functions from aug-cc-pVnZ:

| Basis | Heavy atoms | Hydrogen |
|-------|-------------|----------|
| **aug-cc-pVnZ** | All angular momentum diffuse | All diffuse |
| **jul-cc-pVnZ** | All angular momentum diffuse | NO diffuse |
| **jun-cc-pVnZ** | Remove highest-l diffuse | NO diffuse |
| **may-cc-pVnZ** | Remove 2 highest-l diffuse | NO diffuse |
| **apr-cc-pVnZ** | Remove 3 highest-l diffuse | NO diffuse |
| **maug-cc-pVnZ** | s+p diffuse only | NO diffuse |

**Naming:** aug- = august, then months go backward removing highest angular momentum.

**Why removing hydrogen diffuse is OK:**
- Hydrogen has low electronegativity, electrons are not diffuse
- Nearby heavy atom diffuse functions already supplement hydrogen
- Even the S66 weak interaction benchmark set removes hydrogen diffuse for CBS extrapolation
- **Exception:** LiH (Li has very low electronegativity → H carries large negative charge → H needs diffuse)

### Cost comparison

For MP2 in Gaussian, aug-cc-pVnZ vs cc-pVnZ:
- n=D: 2.4x slower
- n=T: 5x slower
- n=Q: 6.3x slower

aug-cc-pVnZ has >50% more basis functions than cc-pVnZ.

### Recommended month basis sets

**For HF/DFT** (don't need high-angular-momentum diffuse):
- Large systems: maug-cc-pVDZ
- Higher accuracy: maug-cc-pVTZ (= may-cc-pVTZ)

**For post-HF** (sensitive to high-angular-momentum functions):
- Medium-low accuracy: jul-cc-pVDZ
- Medium accuracy: may-cc-pVTZ
- Medium-high accuracy: jul-cc-pVTZ
- High accuracy: jun-cc-pVQZ

**Key insight:** As zeta number increases, the outermost cc-pVnZ functions become more diffuse-like, partially serving as diffuse functions. At the same zeta, different month levels have smaller accuracy differences.

**Critical rule:** For tasks that absolutely need diffuse, adding even maug-level diffuse to cc-pVnZ improves results more than increasing zeta number without diffuse. Diffuse must be present when needed, but doesn't need high angular momentum.

**With proper use of month basis sets, there's no need to use aug-cc-pVnZ anymore.**

## Gaussian usage

**Gaussian 09 D.01+:** Directly supported — write `may-cc-pVTZ`, `jul-cc-pVQZ`, etc.
- Also supports `spAug-cc-pV*Z` = maug-cc-pV*Z + s diffuse on hydrogen

**Older Gaussian:** Use custom basis set via BSE (https://www.basissetexchange.org):
1. Select element, choose aug-cc-pVnZ, format Gaussian94
2. Remove highest-l diffuse terms (lowest-exponent function for each l)
3. Use with `gen` keyword

See "Using month basis sets in Gaussian" example in references for detailed instructions.

## Additional Resources

For detailed methodology and comprehensive coverage, consult:

- **`references/diffuse-details.md`** — Detailed discussion of all diffuse-containing basis sets, response-property-optimized basis sets, month basis set recommendations by method and accuracy
- **`references/month-basis-usage.md`** — Step-by-step Gaussian usage of month basis sets, BSE workflow, custom basis set construction, even-tempered diffuse generation
