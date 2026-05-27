---
name: opt-convergence
description: This skill should be used when the user asks to "help geometry optimization converge", "fix optimization oscillation", "Optimization stopped", "Lnk1e in l9999", "opt=calcall", "opt=gdiis", "优化不收敛", "优化震荡", or mentions Gaussian geometry optimization convergence issues including oscillation, exceeding step limits, and transition state optimization failures.
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

## Transition state optimization

Transition state (TS) optimization is also a geometry optimization process, but toward a first-order saddle point rather than a minimum.

**Typical keyword:** `opt(calcfc,noeigen,TS)`

All methods for minimum optimization apply to TS optimization as well. However:

1. **TS optimization is much more sensitive to initial structure** — Non-convergence is often because the guessed TS structure is not close enough to the actual TS, causing optimization to head toward a chemically meaningless structure. Use GaussView to check if the structure evolution makes chemical sense.
2. **Hessian quality is much more critical for TS** — Prioritize `calcall` or `recalc=3`. For small systems where Hessian computation is not too expensive, always use `calcall` or `recalc` for difficult TS searches to reduce repeated attempts.
3. **QST2 method** — Generates TS guess from reactant and product structures via interpolation. The guess is often unreasonable — worse than what a chemically intuitive user can manually build. Generally not recommended. If QST2 heads in a wrong direction, immediately abandon it and use `opt=TS`.

## Additional Resources

For detailed keyword reference and failure patterns, consult:

- **`references/opt-strategies.md`** — Detailed explanation of every optimization keyword
- **`references/common-failures.md`** — Common failure patterns with before/after examples
