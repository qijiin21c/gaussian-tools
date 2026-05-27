---
name: opt-convergence
description: This skill should be used when the user asks to "help geometry optimization converge", "fix optimization oscillation", "Optimization stopped", "Lnk1e in l9999", "opt=calcall", "opt=gdiis", "优化不收敛", "优化震荡", "when to use B3LYP optimization", "B3LYP geometry optimization appropriate", "B3LYP-D3", "B3LYP transition metal", "B3LYP conjugated system", "B3LYP weak interaction", "B3LYP excited state", "B3LYP cluster", "basis set for optimization", "optimization basis set", "频率计算需要大基组吗", "opt need large basis set", or mentions Gaussian geometry optimization convergence issues, basis set selection for opt/freq, or asks about whether B3LYP is appropriate for optimizing a particular type of system.
version: 0.1.0
---

# Geometry Optimization Convergence Helper

Comprehensive guidance for diagnosing and resolving geometry optimization convergence failures in Gaussian, based on Sobereva's authoritative article (sobereva.com/62).

**Important:** Blindly increasing the optimization step limit is the most commonly misused approach and almost never works. Non-convergence is almost always caused by oscillation, not insufficient steps. The solution requires examining actual convergence trends and trying systematic methods.

## Pre-check: Verify the root cause

When optimization fails, first determine what actually happened:

1. **Read the error message** — "Error termination request processed by link 9999" with "Number of steps exceeded" means step limit exceeded without convergence
2. **Check for oscillation** — Use GaussView with "Read intermediate geometries" enabled:
   - Play the optimization animation to visually inspect oscillation
   - Go to Results → Optimization to view energy, force, and displacement curves
   - If curves oscillate up and down without an overall decreasing trend toward flatness, oscillation is occurring
3. **Check for SCF failure mid-optimization** — Sometimes optimization fails because a single-point energy calculation failed (often due to SCF non-convergence). See the scf-convergence skill for that case.
4. **Check for unreasonable setup** — Wrong theory level, basis set, electronic state, or calculation model can cause optimization to head in obviously wrong directions. These are input problems, not optimization algorithm problems.

## Understanding convergence criteria

Gaussian uses four convergence criteria (default settings):

| Criterion | Default limit |
|-----------|--------------|
| Maximum force | < 0.00045 |
| RMS force | < 0.00030 |
| Maximum displacement | < 0.00180 |
| RMS displacement | < 0.00120 |

All four must be met for convergence. Additionally, if all forces are below the convergence limit × 100, even if displacements haven't converged, it is considered converged. This accounts for very large flexible molecules where the potential energy surface is extremely flat.

## Recommended order to try (for most cases)

For most oscillation problems, try these methods in this order:

1. **DFT: increase grid accuracy** — `int=ultrafine` (G09 only; G16 default is already ultrafine). If using SMD solvent, switch to IEFPCM
2. **Small system: exact Hessian** — `opt=calcall`. For large slow systems, try `opt=recalc=3` or `opt=recalc=5` instead
3. **Try GDIIS** — `opt=GDIIS`
4. **GDIIS with reduced step** — `opt(GDIIS,maxstep=x,noTrust)` where x = 3~5
5. **Last resort: loose convergence** — `opt=loose` (but frequency analysis afterward may show imaginary frequencies)

## Detailed resolution methods

### 1. Try different optimization methods

Three methods available in Gaussian:

- **opt=RFO** — Rational Function Optimization.改良 of Newton-Raphson. Default in G03 (Berny method). Good general-purpose method.
- **opt=GDIIS** — Geometric DIIS. Combined with RFO. Default for semi-empirical in G03. Generally faster than RFO for large systems with flat potential energy surfaces (characterized by small forces but large displacements each step).
- **opt=GEDIIS** — Generalized EDIIS. Default in G09. Claimed to be the most efficient, but in practice often not better than the others.

**Personal strong recommendation:** For weak interaction systems and large flexible systems experiencing non-convergence, try `opt=GDIIS` first.

**Note:** When using GDIIS, even if `cartesian` is specified, Gaussian still optimizes in redundant internal coordinates.

```
# B3LYP/6-31G(d) opt=GDIIS
```

### 2. Use better Hessian matrix

The Hessian (force constant matrix in mass-weighted coordinates) is needed by RFO, GDIIS, and GEDIIS for step determination. Computing the exact Hessian is expensive, so Gaussian by default approximates it using a valence force field, then updates it with gradients at each step. This means the Hessian used throughout optimization is only approximate (which is why a subsequent Freq often shows the structure hasn't fully converged — Freq uses the exact Hessian).

When the approximate Hessian deviates significantly from the exact value, convergence becomes slow or fails entirely.

- **opt=calcfc** — Compute exact Hessian at the first step only. Subsequent steps use gradient-updated approximate Hessian. Good balance of cost and reliability.
- **opt=calcall** — Compute exact Hessian at every step. Solves many optimization failures, typically reduces required steps, guarantees accurate final result. But each step is much more expensive.
- **opt=recalc=N** — (G16 only) Recompute exact Hessian every N steps. N=1 corresponds to calcall. Recommended N = 3~5 for balancing cost and convergence help.
- **opt=readfc** — Read initial Hessian from a lower-level freq calculation's .chk file. Useful when even calcfc is too expensive at the target level.

```
# Step 1: get Hessian at lower level
# HF/3-21G Freq
# Step 2: use Hessian for high-level optimization
# B3LYP/6-31G(d) opt=readfc
```

### 3. Increase step limit: opt=maxcyc=N

**This is the most commonly misused approach by beginners.** In most cases, if convergence hasn't been reached within the default steps, oscillation has already occurred and increasing the limit is pointless — it wastes resources.

**Only increase step limit when:**
- The initial structure is far from the final structure
- The system is small (default step limit is lower)
- Force and displacement curves from GaussView show an overall decreasing trend

Note: Pre-G16 Gaussian has an internal step limit (related to the number of coordinate variables, shown as "maximum allowed number of steps" in the output). Even if N is set huge, it will be capped at this internal limit.

```
# Only when convergence trend is clear
# B3LYP/6-31G(d) opt=maxcyc=200
```

### 4. Use different coordinate systems

The choice of coordinate system significantly affects convergence speed and even whether convergence is achievable. A good coordinate system minimizes coupling between geometric variables.

**(1) Cartesian coordinates: opt=Cartesian**

- Usually slower than redundant internal coordinates for most systems
- Suitable for cluster systems with many molecules
- Use when redundant internal coordinate optimization fails due to coordinate definition issues (e.g., four atoms defining a dihedral become colinear during optimization)
- Note: GDIIS ignores cartesian and still uses redundant internal coordinates

**(2) Internal coordinates: opt=Z-Matrix**

- For single-molecule systems, convergence is usually faster than Cartesian (bond lengths that are far apart have minimal coupling)
- Not suitable for cluster systems (how to link monomers/atoms is often unclear)
- Particularly unsuitable for ring systems (the ring is defined from one atom going around; head and tail atoms are geometrically close but not connected in internal coordinates, causing strong coupling)
- Very useful for high-symmetry systems — cleverly designed internal coordinates with dummy atoms can significantly reduce the number of variables to optimize

**(3) Redundant internal coordinates (default)**

- Based on internal coordinates with additional geometric variables (total > 3N-6)
- Automatically constructed by Gaussian — nearby atoms get bond length terms (and possibly angle, dihedral terms)
- Usually easier to converge than both internal and Cartesian for single-molecule systems
- Especially good for ring systems (head-tail atoms are close, so redundant coordinates include bond/angle/dihedral terms for them)
- Hydrogen bonds are usually recognized as bonded in automatic redundant coordinates

**For weak interactions:** Weak hydrogen bonds (or halogen bonds, van der Waals interactions) between distant atoms may not get automatic bond length terms. Add them manually:

```
# In the route section:
# B3LYP/6-31G(d) opt=modredundant
# Then after molecular coordinates, add a blank line and:
3 7
12 14
8 22
```

This adds R(3,7), R(12,14), R(8,22) bond length terms to the redundant internal coordinates.

**For molecular clusters (e.g., water clusters):** If oscillation occurs, add bond length terms for all H···O hydrogen bonds. Adding O···O terms may also help.

### 5. Adjust step size upper limit: opt=maxstep=N

Sets the step size upper limit (also called trust radius) to 0.01N Bohr or radians. Default is 30.

When the optimization method determines the next step's geometric variable change exceeds this value, the actual change is adjusted to exactly equal this limit.

**When to reduce step size:** If optimization oscillates and each step has moderate displacement but large forces, the process may be stuck in a deep, narrow potential well. Reduce step size to N=5 or even N=3 to avoid overshooting the minimum each step.

**When NOT to reduce step size:** Don't reduce too early in the optimization — it slows things down and increases total steps. Also, when using calcall, reducing step size may actually hinder convergence (since the exact Hessian already gives accurate steps).

**opt=notrust** — By default, maxstep only sets the initial step limit; the trust radius is dynamically adjusted. Adding notrust keeps your setting fixed throughout. Recommended to use together with maxstep for cases of repeated small oscillations.

```
# Reduce step size for oscillation
# B3LYP/6-31G(d) opt(maxstep=5,noTrust)
```

### 6. Adjust symmetry

**High initial symmetry maintained throughout:** If the initial structure has high symmetry, optimization usually maintains it. If the actual PES minimum doesn't have that symmetry, optimization may fail to converge, and even if it does, there will be imaginary frequencies. **Fix:** Manually perturb the initial structure slightly (e.g., twist a dihedral angle a bit to break symmetry).

**System becoming symmetric but not converging:** If the system is gradually becoming more symmetric during optimization but still not converging, extract the structure, use GaussView's Edit → Point Group tool with lower tolerance to identify the highest possible point group, click Symmetrize, then re-optimize. This:
- Greatly reduces computation time for energy and derivatives
- Gives more precise structure (without symmetry, numerical micro-deviations prevent exact symmetry)
- Significantly reduces degrees of freedom to optimize

If Gaussian doesn't recognize the point group (especially high-order groups like Ih for C60), try:
- Using internal coordinates instead of Cartesian in the input
- `symm=loose` to relax point group recognition criteria

### 7. Increase DFT integration grid accuracy

DFT exchange-correlation functionals use numerical grid integration (not analytical). More grid points → more accurate energy, forces, and Hessian. Insufficient integration accuracy can cause both optimization convergence difficulties and imprecise final results.

- `int=ultrafine` — (99,590) grid
- **Note:** From G16 onward, this is the default. Only needed for G09.
- Particularly important for Minnesota functionals (M06-2X, M06, M06L).

```
# G09 only
# M06-2X/6-31G(d) int=ultrafine opt
```

### 8. Change convergence criteria

This is a last-resort approach.

- **opt=loose** — Relaxed convergence criteria. Use when the structure doesn't need high precision (e.g., rough structure for dynamics initialization), and the structure is oscillating very close to the convergence limit. **Warning:** Frequency analysis afterward is more likely to show imaginary frequencies.
- **opt=tight / opt=verytight** — Tighter convergence. Use for systems with very weak interactions (e.g., H2 dimer) or when accurate vibrational frequencies are needed.

### 9. Try different initial structure

If a dihedral angle oscillates between two values during optimization, try setting it to the average of those two angles as the initial structure (ideally combined with calcfc). This occasionally works by chance.

If optimization is heading in an unreasonable or unexpected direction, the initial structure is likely clearly wrong and needs to be rebuilt.

### 10. Try different theory level and basis set

If one level doesn't converge, try a similar basis set or theory method (e.g., B3LYP → B3PW91). If it converges, use the resulting structure (and optionally wavefunction and Hessian) as the starting point for the target level.

The theory/basis should not differ too much from the target level, or the PES minimum position may be significantly different.

**For saving total computation time:** Pre-optimize at a lower level (or with a good semi-empirical method, or appropriate molecular mechanics) with `opt=loose`. But this may not solve the non-convergence problem at the target level, since low-level and high-level PES minima often differ noticeably. The lower level must be meaningful — e.g., pre-optimizing a van der Waals complex with B3LYP (which poorly describes dispersion) wastes time and may produce a structure further from the minimum than the starting structure.

### 11. Solvent model considerations

- **SMD solvent model:** Geometry optimization with SMD may be more difficult and can introduce imaginary frequencies in subsequent frequency analysis, likely due to numerical noise in the SMD surface. **Not recommended for opt+freq tasks.**
- **IEFPCM (default of scrf):** Does not have this significant issue.
- If IEFPCM also fails and solvent is not absolutely necessary, try optimization in vacuum.
- Optimization and single-point calculations do NOT need to use the same solvent model. It is fine to optimize with IEFPCM (or vacuum) and then compute single-point energy with SMD.

## Basis set selection for optimization and frequency

**Core principle:** Geometry optimization and frequency results are much LESS sensitive to basis set size than energy calculations. Using a large basis set for opt/freq wastes significant time with minimal accuracy gain.

### Evidence: HF molecule basis set sensitivity

| Basis set | Bond length (Å) | Error | Frequency (cm⁻¹) | Error | Energy (Hartree) | Error |
|-----------|----------------|-------|-------------------|-------|------------------|-------|
| def2-SVP | 1.3940 | **0.3%** | 1057.0 | **0.13%** | -199.46122 | **26.4 kJ/mol (4.5%)** |
| def2-TZVP | 1.3896 | 0.02% | 1055.3 | 0.03% | -199.51145 | 0.4 kJ/mol (0.07%) |
| def2-TZVPP | 1.3894 | 0.01% | 1055.4 | 0.02% | -199.51351 | 0.2 kJ/mol (0.03%) |
| def2-QZVP | 1.3893 | — | 1055.6 | — | -199.51457 | — |

Bond length and frequency errors at def2-SVP level are negligible. Energy error is 26.4 kJ/mol — but the energy is computed at the same level as the geometry, not used as a high-accuracy single-point.

### Recommendation

**def2-SVP or 6-31G\*\* (double-zeta with polarization) is sufficient for opt+freq for >95% of organic systems.**

The improvement in geometry and frequency from def2-SVP to def2-QZVP is far smaller than the intrinsic error of the DFT functional itself. JCTC 2023 systematic test (DOI: 10.1021/acs.jctc.3c00388) confirms: basis set size has minimal impact on geometry accuracy compared to functional choice.

### What NOT to go below

| Basis set | Acceptable for opt? | Why |
|-----------|-------------------|-----|
| def2-SV(P) | Barely — borderline | Only H has polarization; heavy atoms don't. Noticeably worse than def2-SVP |
| 6-31G (no polarization) | **NO** | Completely inadequate — no polarization on any atom |
| STO-3G | **Absolutely not** | Qualitatively wrong geometries |

**Hydrogen polarization is important:** def2-SV(P) vs def2-SVP shows noticeable degradation. Never use 6-31G without any polarization for opt/freq.

### Exceptions: when larger basis IS needed for opt

| Case | Minimum basis for opt | Reason |
|------|---------------------|--------|
| **Transition metal complexes (coordination bonds)** | def2-TZVP or def2-TZVPP | def2-SVP vs def2-TZVP difference in metal-ligand bond length is significant |
| **Large conjugated systems with delocalization** | 6-311G\* or def-TZVP | 18-carbon ring (sobereva.com/515): def2-SVP gives wrong bond alternation pattern |
| **High-precision vibrational frequencies** | def2-TZVP | When frequency accuracy is critical (e.g., isotope effect studies) |
| **Raman/ROA intensity calculation** | def2-TZVP + diffuse | See two-step approach below |

### Raman/ROA two-step approach

For Raman and ROA calculations where polarizability derivatives are sensitive to basis set:

1. **Optimization + frequency (no diffuse):** B3LYP-D3(BJ)/def2-SVP — get structure and thermochemistry
2. **Polarizability derivative (with diffuse):** B3LYP-D3(BJ)/def2-TZVP + diffuse — compute Raman/ROA intensities

This separates the geometry task (insensitive to basis) from the property task (sensitive to basis).

### CCSD(T) energy + DFT opt/freq pairing

A common and well-justified pattern:
- **Optimization + frequency:** DFT/def2-SVP (e.g., B3LYP-D3(BJ)/def2-SVP)
- **Single-point energy:** CCSD(T)/def2-TZVP or larger

**Justification:** Comput. Theor. Chem., 1200, 113249 (2021) tested DFT geometry + CCSD(T) energy across multiple systems. DFT-optimized geometries are close enough to CCSD(T) geometries that the energy difference from using DFT vs CCSD(T) geometry is negligible compared to the overall accuracy gain of CCSD(T) over DFT energy.

### Frequency thermodynamics: quasi-RRHO matters more than basis set

For low-frequency modes (<100 cm⁻¹), the harmonic oscillator approximation breaks down. Quasi-RRHO corrections (treating low-frequency modes as hindered rotors) can change free energy by several kcal/mol — far more than basis set effects on frequency. See the small-imag-freq skill for handling this.

## Transition state optimization

Transition state (TS) optimization is also a geometry optimization process, but toward a first-order saddle point rather than a minimum.

**Typical keyword:** `opt(calcfc,noeigen,TS)`

All methods for minimum optimization apply to TS optimization as well. However:

1. **TS optimization is much more sensitive to initial structure** — Non-convergence is often because the guessed TS structure is not close enough to the actual TS, causing optimization to head toward a chemically meaningless structure. Use GaussView to check if the structure evolution makes chemical sense.
2. **Hessian quality is much more critical for TS** — Prioritize `calcall` or `recalc=3`. For small systems where Hessian computation is not too expensive, always use `calcall` or `recalc` for difficult TS searches to reduce repeated attempts.
3. **QST2 method** — Generates TS guess from reactant and product structures via interpolation. The guess is often unreasonable — worse than what a chemically intuitive user can manually build. Generally not recommended. If QST2 heads in a wrong direction, immediately abandon it and use `opt=TS`.

## When to use B3LYP for geometry optimization

B3LYP (1994) is obsolete for single-point energy calculations — but it remains practical for geometry optimization due to:
1. **Fastest among hybrid functionals** in Gaussian — simple functional form vs. complex M06-2X or range-separated functionals
2. **Low grid sensitivity** — converges on coarse grids; `int=fine` (cheaper than `ultrafine`) often suffices. Modern meta-hybrids (especially M06-2X) require `ultrafine` or higher.
3. **Massive literature precedent** — widely accepted, rarely challenged by reviewers.

**Strong recommendation:** Always add DFT-D3 dispersion correction: `B3LYP-D3(BJ)`. It's free (no extra cost), improves accuracy universally, and eliminates reviewer criticism. See sobereva.com/413 on when D3 is needed.

### B3LYP appropriateness by system type

| System / Task | Use B3LYP? | Recommendation |
|---------------|-----------|---------------|
| **Organic molecules (no weak interactions, no large conjugation)** | Yes | `B3LYP-D3(BJ)/def2-SVP` — safe and well-validated |
| **Weak interaction systems** | Only with D3 | `B3LYP-D3(BJ)` — essential; bare B3LYP fails completely for dispersion |
| **Transition metal complexes (general)** | Acceptable but not optimal | TPSSh often outperforms for metal-ligand bond lengths |
| **Transition metal complexes (metal-metal bonds)** | **NO** | Use pure functionals (BP86, TPSS, PBE) — B3LYP gives qualitatively wrong bond lengths |
| **Large π-conjugated systems** | **NO** | B3LYP self-interaction error overdelocalizes, forces planarity, equalizes bond lengths. Use wB97XD or M06-2X |
| **Excited state optimization** | Not recommended | PBE0 or wB97XD perform better. B3LYP fails for CT state optimization |
| **Transition state (organic reactions)** | Acceptable | wB97XD or M06-2X more accurate, but B3LYP is fine if structure looks reasonable |
| **Transition state (radical reactions)** | Caution | B3LYP may give qualitatively wrong TS geometry (e.g., F+H₂→HF+H) |
| **Carbon clusters** | Yes | B3LYP works well for carbon clusters |
| **Boron clusters** | Probably not | PBE0 or TPSSh likely better |
| **Gold/metal clusters** | **NO** | TPSSh best; PBE0 acceptable; B3LYP very poor |
| **d-block metal clusters** | **NO** | Use pure functionals (BP86, TPSS, SCAN) |
| **Metal lattice constants** | **NO** | PBE0 or HSE much better |
| **High-precision thermochemistry** | Yes | Used in G4, G3//B3LYP, CBS-QB3 composite methods |
| **Conformational search** | Only with D3 | `B3LYP-D3(BJ)` recommended as final optimization level |

### Key details

#### Weak interaction systems
- B3LYP describes dispersion **completely incorrectly** — Ar₂ dimer has no minimum with B3LYP
- Electrostatic-dominated weak interactions (e.g., water dimer H-bonds): B3LYP is qualitatively correct but quantitatively improved with D3
- π-π stacking (e.g., DNA base pairs): B3LYP fails without D3 —碱基间距完全错乱
- **Conclusion:** Never use bare B3LYP for any system where dispersion could affect structure. `B3LYP-D3(BJ)` is the standard.

#### Large π-conjugated systems
B3LYP's self-interaction error (SIE) causes:
- **Overdelocalization** — forces fully coplanar conformations
- **Bond length equalization** — makes all bonds in conjugation path equal

Examples where B3LYP fails:
- [18]annulene: B3LYP gives planar D6h with equal C-C bonds; wB97XD gives D3h with alternating bonds (matches CCSD and experiment)
- Carbon ring (C₁₈): B3LYP gives equal C-C bonds; wB97XD gives alternating bonds (matches CCSD and AFM experiment)
- [IF6]⁻: B3LYP gives Oh minimum; true structure is C3v (lone pair on iodine). wB97XD correctly gives C3v

**Fix:** Use wB97XD or other high-HF% / range-separated functionals (CAM-B3LYP). See sobereva.com/282 for HF% table.

#### Transition metal complexes
- B3LYP is widely used but **mediocre** for metal-ligand bond lengths in benchmarks
- TPSSh consistently outperforms in metal-ligand bond length tests
- For metal-metal bonds (e.g., V₂ in [V(Cp)]₂Pn): B3LYP gives 2.994 Å vs. experimental 2.538 Å; BP86 gives 2.568 Å
- If you only care about ligand chemistry (not metal coordination), B3LYP is fine

#### Excited state optimization
- Ground-state and excited-state optimization performance are uncorrelated
- B3LYP fails for charge-transfer (CT) excited state optimization — gives qualitatively wrong geometries
- **For CT or Rydberg states:** Must use range-separated hybrids (CAM-B3LYP, wB97X-D)
- PBE0 and wB97XD generally perform well for excited states across the board

#### Practical recommendation
When recommending an optimization level to others or writing input templates, **default to `B3LYP-D3(BJ)`** rather than bare B3LYP. This adds universality — you don't need to know whether the user's system has weak interactions, and reviewers won't question it.

## Additional Resources

For detailed keyword reference and failure patterns, consult:

- **`references/opt-strategies.md`** — Detailed explanation of every optimization keyword
- **`references/common-failures.md`** — Common failure patterns with before/after examples
- **`references/b3lyp-appropriateness.md`** — When to use B3LYP for optimization: weak interactions, organic molecules, transition metals, large conjugated systems, excited states, transition states, clusters, and special cases ([IF6]-, annulenes, carbon ring). DFT-D3 necessity and benefits. B3LYP-D3(BJ) as universal default recommendation. Based on sobereva.com/557
- **`references/basis-for-opt-freq.md`** — Why opt/freq don't need large basis sets: HF molecule sensitivity data, hydrogen polarization importance, exceptions (TM coordination bonds, conjugated systems), Raman/ROA two-step approach, CCSD(T)+DFT pairing justification. Based on sobereva.com/387
