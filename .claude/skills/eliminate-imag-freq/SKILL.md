---
name: eliminate-imag-freq
description: This skill should be used when the user asks to "eliminate imaginary frequency", "消虚频", "remove imaginary freq", "opt converged but freq has imaginary", "tight convergence", "calcalc", "calcfc", "recalc", "int=superfine", "SMD imaginary frequency", "symmetry imaginary freq", "distort along imaginary mode", "optimization converged but NO in freq", or mentions Gaussian geometry optimization convergence followed by frequency analysis showing imaginary frequencies or NO convergence criteria.
version: 0.1.0
---

# Imaginary Frequency Elimination Guide

Comprehensive guidance for diagnosing and eliminating imaginary frequencies that appear after geometry optimization convergence in Gaussian, based on Sobereva's authoritative article (sobereva.com/608).

**Core principle: There is NO such thing as an uneliminable imaginary frequency.** Every case can be resolved by properly applying the methods below. If it doesn't work, you haven't tried hard enough or made a basic error (like not optimizing before freq, or using different levels for opt and freq).

**Important distinction from small-imag-freq skill:** This skill is about **eliminating** imaginary frequencies (making them go away by improving optimization). The small-imag-freq skill is about **tolerating** small imaginary frequencies when you can't afford to eliminate them. These are complementary approaches.

## Why imaginary frequencies appear after converged optimization

Gaussian's default geometry optimization uses **quasi-Newton method** (approximate Hessian updated each step), while frequency analysis uses the **exact Hessian**. This mismatch causes:

- Force criteria (Max, RMS): consistent between opt and freq
- Displacement criteria (Max, RMS): may differ because opt uses approximate Hessian

**Typical scenario:**
```
Opt output:    All four criteria = YES
Freq output:   Force = YES, Displacement = NO (and imaginary frequencies appear)
```

**When is it acceptable?** If the NO values exceed the default threshold by less than 2x, and no imaginary frequencies appear — generally acceptable.

**If you need high accuracy or imaginary frequencies exist:** Perform more precise optimization.

## Pre-check: Verify basics

1. **Frequency was done at the same level as optimization** — identical theory, basis set, int, scrf, etc.
2. **Geometry optimization was actually performed** before frequency analysis
3. **Not a transition state issue** — for TS, the imaginary frequency of interest is the reaction mode. Only eliminate EXTRA imaginary frequencies beyond the one expected TS mode.

## Recommended approach (try in order)

### Step 1: Improve Hessian quality

| Method | When to use | Cost |
|--------|------------|------|
| `opt=calcfc` | Restart from last structure of a default optimization | Low |
| `opt=recalc=3~5` | Hessian computation is not too expensive | Medium |
| `opt=recalc=5~10` | Hessian computation is expensive | Medium |
| `opt=calcall` | Maximum precision needed | High |

**`opt=calcfc`:** Compute exact Hessian only at the first step. Take the last structure from your default optimization and restart with calcfc. Often avoids NO and imaginary frequencies. **Limitation:** If the initial structure is far from the true minimum, the Hessian may drift away from exact by convergence time.

**`opt=recalc=N`:** Compute exact Hessian at first step, then every N steps. Effect and cost between calcfc and calcall. N=3~5 for cheap Hessian, N=5~10 for expensive Hessian. **Available from Gaussian 16 onwards.**

**`opt=calcall`:** Compute exact Hessian at every step. Most accurate. **Automatically performs frequency analysis after optimization** — no need to separately add `freq` keyword. If opt ends with YES, freq will also end with YES. **Limitation:** Very expensive.

### Step 2: Tighten convergence criteria

`opt=tight` — Tightens optimization convergence limits by an order of magnitude or more. More precisely located minimum → much lower chance of imaginary frequencies.

**Trade-off:** Much harder to reach convergence → more steps needed → higher cost → increased probability of oscillation.

**Note:** If you write `opt=tight freq`, the freq convergence check also uses tight criteria. In reality, freq only needs to meet default criteria, not tight. The tight check is unnecessarily strict.

### Step 3: Improve DFT integration grid (for DFT calculations)

If integration grid quality is insufficient, forces and Hessian accuracy are compromised — often the cause of imaginary frequencies. Using `tight` alone won't fix this and may cause convergence/oscillation problems.

| Grid level | When to use |
|------------|------------|
| `int=ultrafine` | Gaussian 09 users; Minnesota functionals (M06-2X, etc.) |
| `int=superfine` | Persistent tiny imaginary frequencies; dispersion-dominated weak interactions; M06-2X even with ultrafine |

**Gaussian 16:** `int=ultrafine` is the default — no need to specify manually.

**Minnesota functionals (M06-2X, etc.):** Require higher grid quality than B3LYP, PBE0, TPSS, etc. Sometimes even `int=ultrafine` produces tiny imaginary frequencies — try `int=superfine` (very expensive).

**Rare case:** For some dispersion-dominated weak interaction systems, even non-Minnesota functionals may need `int=superfine` to eliminate stubborn tiny imaginary frequencies. This is extremely rare but worth trying when nothing else works.

### Combined approach (recommended for stubborn cases)

```
# B3LYP/6-31G(d) opt(calcfc,tight) int=ultrafine
```

Or for Minnesota functionals:
```
# M06-2X/6-31G(d) opt(calcfc,tight) int=superfine
```

## Other causes and solutions

### Symmetry too high in initial structure

**Symptom:** Initial structure has higher symmetry than the true minimum. Optimization maintains this symmetry throughout, leading to imaginary frequency corresponding to symmetry-breaking distortion.

**Example:** Biphenyl is actually twisted in the ground state, but starting from a planar structure keeps it planar → imaginary frequency for torsional mode.

**Solution:**
1. Open the optimized structure in GaussView
2. Go to the imaginary frequency vibration mode view
3. Select **Manual Displacement** and drag the slider to distort along the imaginary mode
4. Click **Save Structure** to get the new distorted structure
5. Re-optimize and re-run frequency on the new structure

**Limitations:**
- Works well for symmetry-related single imaginary frequencies
- Less effective for other causes
- Unlikely to eliminate multiple imaginary frequencies at once
- **Do NOT default to this approach** — try the optimization improvement methods (Steps 1-3) first!

**Common beginner mistake:** Seeing any imaginary frequency and immediately trying to distort along the mode. This is wrong — the optimization precision methods should be tried first.

### SMD implicit solvent model

**Problem:** SMD introduces significant numerical noise → false imaginary frequencies and optimization convergence difficulty.

**Solution:** Use **IEFPCM** (Gaussian's default scrf model) for optimization and frequency:
```
# B3LYP/6-31G(d) opt SCRF=(IEFPCM,Solvent=water)
# B3LYP/6-31G(d) freq SCRF=(IEFPCM,Solvent=water)
```

Then compute single-point energy with SMD afterward:
```
# B3LYP/6-31G(d) SCRF=(SMD,Solvent=water) SP Guess=Read Geom=Check
```

**Why this works:** SMD vs IEFPCM makes no structural difference — SMD's advantage is accounting for non-polar solvent contributions, which are important for energy but have negligible effect on geometry. See sobereva.com/327.

### IOp-defined custom functionals

**Problem:** When using IOp to define custom functionals (sobereva.com/344, sobereva.com/550), IOp settings do NOT carry over to the next task. With `opt freq`, IOp applies only to opt, not to freq → different functional definitions → different PES → imaginary frequencies.

**Solution:** Run opt and freq as **separate jobs** when using custom functionals via IOp.

### Program bug (Gaussian 09 D.01)

**Bug:** Gaussian 09 D.01 has a bug in DFT-D3(BJ) analytical second derivatives. Even with perfectly converged optimization, freq with DFT-D3(BJ) may show imaginary frequencies.

**Solutions:**
1. Upgrade to Gaussian 09 E.01 or later
2. Use DFT-D3(0) (zero-damping) instead of DFT-D3(BJ) for both opt and freq

## Why calcall freq criteria might still differ from opt

If you used `opt=calcall` but freq still shows different criteria or NO:

1. **Level mismatch:** freq uses different theory/basis/grid settings than opt
2. **Numerical precision from GaussView:** Reading opt output in GaussView and saving as freq input loses decimal precision → numerical error
3. **GDIIS effect:** opt uses GDIIS (or GEDIIS with GDIIS component) which references previous steps for displacement prediction → differs from freq's Newton-method-based displacement check
4. **Different wavefunction:** freq converged to a different wavefunction than opt's last step. Compare single-point energies — if different, the higher-energy one is the unstable wavefunction. Fix: use `Guess=Read` in freq to read opt's .chk file.

## When small imaginary frequencies are tolerable

If the imaginary frequency is very small (typically < 50 cm⁻¹), it may not be necessary to eliminate it at all costs. See the small-imag-freq skill and sobereva.com/699 for detailed discussion on when small imaginary frequencies can be tolerated for energy-related calculations.

## Additional Resources

For detailed methodology and comprehensive coverage, consult:

- **`references/optimization-precision.md`** — Detailed explanation of quasi-Newton vs Newton methods, convergence criteria, Hessian strategies
- **`references/special-cases.md`** — Special cases: symmetry distortion, SMD issues, custom functionals, program bugs, wavefunction consistency
