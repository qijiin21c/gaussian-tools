# IRC Keyword Reference

Based on Sobereva (sobereva.com/63). Every keyword Gaussian supports for IRC calculations.

## IRC Algorithm Keywords

### HPC (default in G09/G16)
- Hessian-based Predictor-Corrector
- Uses LQA as predictor, modified Bulirsch-Stoer as corrector
- More accurate than LQA alone with modest extra cost
- **Main problem:** Corrector step frequently fails to converge → "Maximum number of corrector steps exceeded"

### LQA
- Local Quadratic Approximation (1988)
- Requires Hessian at every step
- Less accurate than HPC but never fails due to corrector issues
- Use: `IRC(calcfc,LQA)`

### GS2
- Gonzalez-Schlegel 2 (1989), default in G03
- Each step is essentially a constrained optimization
- Much more expensive than HPC
- Completely avoids HPC corrector failures
- Use: `IRC(calcfc,GS2)`

### DVV
- Default for gradientonly mode
- Poor quality, strongly oscillatory — not recommended

### Euler
- Better than DVV for gradientonly mode
- Use: `IRC(gradientonly,euler)` for methods without analytic Hessian (e.g., CCSD)

### gradientonly
- Uses only gradient information for IRC
- For methods without analytic Hessian
- Combined with euler: `IRC(gradientonly,euler)`

## Hessian Computation Keywords

### calcfc
- Compute exact Hessian at the first step
- Required for IRC tasks
- Subsequent steps use Bofill approximate Hessian updates

### calcall
- Compute exact Hessian at every step
- Much more accurate but 10x+ more expensive
- Use for high-quality IRC curves or when HPC fails repeatedly

### recalc=N
- Recompute exact Hessian every N steps
- N=1 = calcall
- Recommended: N=3~5 for balancing cost and accuracy

### rcfc
- Read Hessian from .chk file
- Use when a freq calculation was already done on the TS
- Avoids the cost of calcfc
- Use instead of calcfc when Hessian is already available

## Step Control Keywords

### maxpoints=N
- Maximum steps per direction (default: 10)
- Total points = 1 (TS) + 2×N (both directions)
- If PES minimum detected, that direction stops early
- Larger = longer IRC, higher cost

### stepsize=N
- IRC step length
- Positive N: unit = 0.01 Bohr
- Negative N: unit = 0.01 amu^1/2 Bohr
- Default: 10 (0.10 Bohr)
- Smaller → more accurate, smoother, fewer failures
- Larger → less accurate, possible kinks, HPC more likely to fail

**Recommended settings by purpose:**
- Verify TS: maxpoints=default, stepsize=15-20, add LQA
- Approximate reactant/product: maxpoints=50+, stepsize=15-20, add LQA
- Publication-quality IRC: maxpoints=200, stepsize=5, add calcall or recalc=3/5

## Direction Control Keywords

### Forward
- Only follow IRC in the forward direction

### Reverse
- Only follow IRC in the reverse direction

### Phase=(i,j)
- Define positive direction: atom i moving toward atom j is "forward"
- Gaussian only knows "two directions" — it doesn't know which is reactant/product

## Restart Keywords

### restart
- Restart an interrupted or extend a completed IRC
- Must use same .chk file as the original IRC job
- Example: `IRC(restart,maxpoints=20)`
- GaussView must open .chk/.fch file (not .out/.log) to see full restarted trajectory

## Other Keywords

### Cartesian
- Execute IRC in Cartesian coordinates
- Technically this is MEP (Minimum Energy Path), not IRC
- Don't use unless you specifically want MEP

### ReCorrect=never
- Disables HPC corrector step entirely
- Same cost as LQA but worse accuracy
- **Strongly not recommended**

### tight
- Tightens corrector convergence criterion
- Increases chance of HPC corrector failure
- **Do not use** — makes non-convergence more likely

### maxcyc=N
- Increases HPC corrector iteration limit (default: 20)
- **Most misused approach** — almost never solves corrector failure
- Do not use — "increase iteration limit" is a common beginner mistake

---

## Important Notes

1. **IRC and TS must use strictly identical settings** — Any setting affecting the PES (theory, basis, int, scrf, etc.) must be exactly the same
2. **IRC stepsize and maxpoints jointly determine maximum IRC length** — each side's maximum length = maxpoints × stepsize
3. **IRC endpoints are NOT true minima** — Must optimize IRC endpoints to get accurate reactant/product structures
4. **IRC results are isotope-dependent** — Mass-weighted coordinates mean isotope settings affect the path
5. **Gaussian's reaction coordinate zero is the TS** — Negative = one direction, Positive = the other (which is reactant/product depends on the system)
