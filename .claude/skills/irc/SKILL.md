---
name: irc
description: This skill should be used when the user asks to "run IRC", "find IRC path", "IRC calculation", "IRC not converging", "Maximum number of corrector steps exceeded", "IRC stopped early", "IRC same direction both sides", "IRC restart", "LQA vs HPC", "IRC stepsize", "验证过渡态", "IRC报错", or mentions Gaussian Intrinsic Reaction Coordinate calculations including HPC corrector failures, TS verification, and reaction path analysis.
version: 0.1.0
---

# IRC (Intrinsic Reaction Coordinate) Helper

Comprehensive guidance for computing and troubleshooting IRC calculations in Gaussian, based on Sobereva's authoritative article (sobereva.com/63).

IRC is the minimum-energy path connecting two adjacent minima on the potential energy surface in mass-weighted coordinates. It is the most definitive method for verifying that a transition state (TS) connects the correct reactant and product.

## Prerequisites

1. **TS optimization must be completed first** — IRC must start from a transition state structure
2. **IRC and TS must use strictly identical settings** — Any setting that affects the PES must be exactly the same (theory level, basis set, int=ultrafine, scrf settings, etc.). If unsure, compare single-point energies — if they differ, the PES is different.
3. **IRC from TS .chk or TS structure** — Either write the TS structure directly into the IRC input file, or use `geom=check` to read the last frame from the TS optimization's .chk file.

**Typical TS + IRC workflow:**
```
(a) Build TS guess in GaussView → TS.gjf
(b) # B3LYP/6-31G* opt(calcfc,noeigen,TS) → run TS optimization
(c) Open TS output, save as IRC.gjf
(d) # B3LYP/6-31G* IRC=calcfc → run IRC
```

## Key parameters

### Maxpoints (steps per direction)
- Default: 10 per direction
- Total points = 1 (TS) + 2 × Maxpoints (both directions)
- If a PES minimum is detected, that direction stops early
- Larger = longer IRC but higher cost

### Stepsize (IRC step length)
- Default: 10 (means 0.10 Bohr in Cartesian, automatically converted to amu^1/2 Bohr in mass-weighted coordinates)
- Positive value: unit = 0.01 Bohr
- Negative value: unit = 0.01 amu^1/2 Bohr
- Smaller stepsize → more accurate, smoother curve, less oscillation, fewer HPC corrector failures
- Larger stepsize → less accurate, possible kinks, HPC corrector more likely to fail

### Recommended settings by purpose

| Purpose | Maxpoints | Stepsize | Additional keywords |
|---------|-----------|----------|---------------------|
| Verify TS is correct | default (10) | 15-20 | LQA (avoid HPC failures) |
| Get approximate reactant/product structures | 50+ | 15-20 | LQA |
| High-quality, complete IRC curve (for publication) | 200 | 5 | calcall or recalc=3/5 if HPC fails |

## IRC algorithms in Gaussian

### HPC (Hessian-based Predictor-Corrector) — G09/G16 default
- Uses LQA as predictor, modified Bulirsch-Stoer as corrector
- More accurate than LQA alone
- **Main problem:** Corrector step often fails to converge, causing the most common IRC error
- Error: "Maximum number of corrector steps exceeded"

### LQA (Local Quadratic Approximation)
- Traditional algorithm (1988), requires Hessian at every step
- Less accurate than HPC but never fails due to corrector non-convergence
- Use when HPC fails: `IRC(calcfc,LQA)`

### GS2 (Gonzalez-Schlegel 2)
- G03 default algorithm
- Each step is essentially a constrained optimization
- Much more expensive than HPC but more accurate than LQA
- Completely avoids HPC corrector failures: `IRC(calcfc,GS2)`

### DVV, EulerPC
- Available but rarely used
- `IRC(gradientonly,euler)` for methods without analytic Hessian (e.g., CCSD)

## Hessian computation during IRC

- **IRC=calcfc** — Compute exact Hessian at the first step (required for IRC). Subsequent steps use Bofill approximate updates.
- **IRC=calcall** — Compute exact Hessian at every step. Much more accurate but 10x+ more expensive.
- **IRC=recalc=N** — Recompute exact Hessian every N steps. N=1 = calcall. Recommended N=3~5 for balancing cost and accuracy.
- **IRC=rcfc** — Read Hessian from .chk file (if a freq calculation was already done on the TS). Saves the cost of calcfc.

## Coordinate system

- **Default (mass-weighted coordinates)** — IRC is defined in mass-weighted coordinates, results affected by isotope mass settings
- **IRC=Cartesian** — Executes in Cartesian coordinates; technically this is MEP (Minimum Energy Path), not IRC. Don't use unless you know what this means.

## Direction control

- **IRC=Forward** — Only follow IRC in the forward direction
- **IRC=Reverse** — Only follow IRC in the reverse direction
- **IRC=Phase=(i,j)** — Define which direction is "forward" by specifying that atom i moving toward atom j defines the positive direction

**Note:** Gaussian only knows "two directions" — it doesn't know which is reactant and which is product. Only the researcher knows this.

## Troubleshooting: How to check IRC progress

1. **GaussView** — Open the output file with "Read intermediate geometries" enabled. Switch frames to watch the IRC trajectory, or play the animation.
2. **Results → IRC/Path** — View "Energy vs Reaction Coordinate" plot. Also check "Force vs Reaction Coordinate" below — if forces at both ends are close to zero, the IRC is nearly complete.
3. **During calculation** — Can open the output file mid-calculation to check progress. Don't panic if an intermediate point appears to "drop down" — this is an artifact of viewing incomplete output.

## Common problems and solutions

### Problem 1: "Maximum number of corrector steps exceeded" (HPC failure)

**Most common IRC error.** HPC corrector step fails to converge.

**Solutions (try in order):**
1. `IRC(calcfc,LQA)` — 100% solves the problem but sacrifices some accuracy
2. Reduce stepsize: `IRC(calcfc,stepsize=5)` — smaller stepsize = higher chance of avoiding the error
3. Add calcall: `IRC(calcfc,calcall)` — or recalc=3/5 for lower cost
4. Use GS2: `IRC(calcfc,GS2)` — completely avoids this error, more expensive than LQA but more accurate
5. `IRC(calcfc,ReCorrect=never)` — disables corrector step entirely. Same cost as LQA but worse accuracy — **strongly not recommended**
6. **Do NOT** use `maxcyc=N` to increase corrector iteration limit — this almost never works and is a common beginner mistake

### Problem 2: IRC stops after only a few steps, or both sides produce the same curve

**Cause:** TS optimization was not accurate enough. The TS structure is slightly offset from the true saddle point, so when going "left," the program detects energy increasing and thinks it has reached a minimum.

**Solutions:**
1. Verify: IRC is using the exact TS structure from the optimization, and both TS and IRC use strictly identical settings
2. Improve TS accuracy:
   - Use `opt(...,tight)` for TS optimization
   - For DFT, also use `int=ultrafine` (must also be in IRC)
   - Use `calcall` or `recalc=3` during TS optimization
3. If (2) doesn't work or is too expensive, increase IRC stepsize to 20 or 30 — this may allow the IRC to "jump over" the offset TS and continue normally
4. **Wavefunction mismatch:** If the SCF in IRC converges to a different wavefunction than the TS optimization, the PES is effectively different. Check if the first SCF Done energy in IRC differs from the last SCF Done in TS optimization. Fix: use `Guess=Read` in IRC to read the converged wavefunction from the TS .chk file. Also consider using `Forward` and `Reverse` as two separate jobs.
5. **SMD solvent model:** Numerical noise from SMD can cause early termination. Switch both TS optimization and IRC to IEFPCM.

### Problem 3: L502 error during IRC (SCF non-convergence)

**Cause:** SCF fails to converge at one of the IRC points.

**Solutions:**
- Apply SCF convergence methods (see scf-convergence skill)
- If first SCF in IRC fails: add `Guess=Read` to read wavefunction from TS .chk
- If mid-IRC SCF fails: reduce stepsize — smaller steps mean the previous point's wavefunction is a better guess for the current point

### Problem 4: IRC curve is sharp/spiky at the TS position

**Cause:** TS position not accurately located, or PES settings differ between TS and IRC.

**Solutions:**
1. Verify TS structure is from optimization, not a guess
2. Verify all PES-affecting settings are identical between TS and IRC
3. Increase TS accuracy: `tight`, `calcall`/`recalc=x`, `int=ultrafine`
4. Try GS2 algorithm or calcall for IRC
5. Ensure first SCF in IRC converges to the same wavefunction as last step of TS optimization

### Problem 5: IRC ends with structures that are not the true reactant/product

**Note:** This is expected behavior. IRC uses fixed step sizes, so it will never land exactly on a minimum. **Must optimize the endpoints** of the IRC to get the true reactant and product structures.

If endpoint optimization gives wrong minima:
1. The TS may connect to different minima than expected (run IRC longer to verify)
2. Optimization may have jumped to a neighboring minimum — use smaller stepsize with `maxstep` + `notrust`, or `calcall`/`recalc`, or run IRC longer to get endpoints closer to minima first

### Problem 6: IRC curve has a "bump" or shoulder on one side

**This is normal.** As long as the calculation flow is correct, trajectory looks normal, and TS position is smooth, there's no problem. Shoulders often indicate complex electronic structure changes — the reaction may have two stages despite being a single step. Analyze with bond order, ELF, density difference, or atomic charge changes along the path (e.g., using Multiwfn).

## IRC restart and extension

### Restart interrupted IRC
```
%chk=same_as_before.chk
# B3LYP/6-31G(d) IRC(restart,maxpoints=15)
```

### Extend completed IRC
If IRC finished with maxpoints=15 and you want 5 more points per direction:
```
%chk=same_as_before.chk
# B3LYP/6-31G(d) IRC(restart,maxpoints=20)
```

**Note:** GaussView must open the .chk/.fch file (not the .out/.log) to see the full restarted IRC trajectory.

## Methods without analytic Hessian (e.g., CCSD)

### Finding TS without analytic Hessian:
1. **Gradient-only methods:** `CCSD/cc-pVDZ opt(TS,modRedundant,noeigen)` or `opt(TS,gediis,noeigen)` or QST2/3
2. **Semi-numerical Hessian:** 
   - Compute Hessian: `# CCSD/cc-pVDZ freq` (expensive)
   - Read Hessian for TS: `# CCSD/cc-pVDZ opt(TS,noeigen,readfc)`

### Running IRC without analytic Hessian:
```
# CCSD/cc-pVDZ IRC(gradientonly,euler)
```
`gradientonly` uses gradient-only IRC algorithm (default DVV, but Euler is better). Quality is poor — often very oscillatory.

## Additional Resources

For detailed keyword reference and common failure patterns, consult:

- **`references/irc-strategies.md`** — Detailed explanation of every IRC keyword and parameter
- **`references/common-failures.md`** — Common IRC failure patterns with before/after examples
