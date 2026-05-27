# Optimization Precision and Imaginary Frequencies

Detailed explanation of why imaginary frequencies appear after converged optimization and how to eliminate them through improved precision. Based on Sobereva's article (sobereva.com/608).

## Why optimization and frequency use different convergence checks

### Newton method vs quasi-Newton method

**Newton method:**
- Computes exact Hessian matrix (second derivatives of energy w.r.t. geometry) at each step
- Efficient for finding stationary points
- For high-level calculations or large systems, computing Hessian once is very expensive
- Many methods lack analytical second derivatives in Gaussian (CCSD, MP4, etc.)
- Computing Hessian for large systems at these levels is extremely expensive or impossible

**Quasi-Newton method (Gaussian default):**
- Does NOT compute exact Hessian at each step
- Only computes forces (gradients)
- Uses forces and previous step's Hessian to approximate current Hessian
- Each step is much cheaper (e.g., 10 quasi-Newton steps may cost only 1-2 Newton steps)
- Overall much cheaper than Newton method
- Requires more steps to converge, but each step is so much cheaper that total cost is far lower

**Optimization convergence criteria (4 checks):**
1. Maximum Force < 0.000450
2. RMS Force < 0.000300
3. Maximum Displacement < 0.00180
4. RMS Displacement < 0.001200

When all four are YES, optimization stops.

### The mismatch

**During optimization:** Quasi-Newton uses approximate Hessian → displacement criteria checked against approximate displacement
**During frequency:** Exact Hessian is computed → displacement criteria re-checked using exact Hessian → may differ

**Force criteria:** Consistent between opt and freq (both use actual forces)
**Displacement criteria:** May differ (opt uses approximate, freq uses exact)

### Typical example

```
Opt output:
 Maximum Force            0.000401     0.000450     YES
 RMS     Force            0.000197     0.000300     YES
 Maximum Displacement     0.001791     0.001800     YES
 RMS     Displacement     0.000951     0.001200     YES

Freq output:
 Maximum Force            0.000401     0.000400     YES
 RMS     Force            0.000197     0.000300     YES
 Maximum Displacement     0.002231     0.001800     NO
 RMS     Displacement     0.001325     0.001200     NO
```

The force values are identical, but displacement values differ because freq uses the exact Hessian.

### When is this acceptable?

If the NO values exceed the threshold by not much (less than 2x) AND no imaginary frequencies appear — generally acceptable.

If you need high structural/frequency accuracy OR imaginary frequencies appear — perform more precise optimization.

## Method 1: Tighter convergence criteria

**`opt=tight`:** Tightens all four convergence limits by an order of magnitude or more.

**Effect:** More precisely located minimum → much lower chance of imaginary frequencies.

**Cost:**
- Much harder to reach convergence
- Many more steps needed
- Significantly higher total time
- Increased probability of oscillation (never reaching the tighter limits)

**Note about `opt=tight freq`:** When both are specified, freq also uses tight criteria for its convergence check. In reality, freq only needs to meet default criteria — the tight check is unnecessarily strict for the frequency step.

**Special case — very flat PES:** For very flexible large molecules or molecular clusters, Gaussian auto-accepts convergence if forces are less than 100x the convergence limit, even if displacements haven't converged. This is because for such systems, the structural precision at the default limit may not be meaningful relative to the system's scale. In these cases, even opt shows NO, and freq will also show NO. Tighten convergence if structural precision is important.

## Method 2: Improve DFT integration grid

### What is DFT integration grid?

DFT calculations require numerical integration of the exchange-correlation functional on a grid. Grid quality directly affects force and Hessian accuracy. See sobereva.com/69 for detailed explanation.

### Grid levels in Gaussian

| Grid | Description | When to use |
|------|-------------|-------------|
| `int=fine` | Default (Gaussian 09) | — |
| `int=ultrafine` | Higher precision | Gaussian 09 users; Minnesota functionals |
| `int=superfine` | Very high precision | Stubborn tiny imaginary frequencies |

**Gaussian 16:** `int=ultrafine` is now the default.

### When grid quality causes imaginary frequencies

If integration grid quality is insufficient:
- Force accuracy is compromised
- Hessian accuracy is compromised
- This often causes imaginary frequencies
- Using `tight` alone won't fix this — may make convergence/oscillation worse

### Functional-specific grid requirements

**B3LYP, PBE0, TPSS, etc.:** Standard grid quality usually sufficient

**Minnesota functionals (M06-2X, etc.):**
- Require much higher grid quality than common functionals
- `int=ultrafine` may still produce tiny imaginary frequencies
- Try `int=superfine` if this happens (very expensive)
- Note: Not ALL Minnesota functionals have this requirement

**Rare case — dispersion-dominated weak interactions:**
- Sometimes need `int=superfine` even for non-Minnesota functionals
- Example: ωB97XD/def2-TZVP(-f) C30 nested structure had persistent ~2 cm⁻¹ imaginary frequencies — resolved only by `int=superfine` (without even tightening convergence)
- Extremely rare — don't treat as general case
- Worth trying when tiny imaginary frequencies persist despite other methods

## Method 3: Use exact Hessian during optimization

### `opt=calcall`

**What:** Compute exact Hessian at EVERY optimization step.

**Effect:**
- Optimization is as accurate as frequency analysis
- Opt and freq use the same Hessian → convergence check results are identical
- If opt ends with YES, freq will also end with YES
- Usually ensures no imaginary frequencies
- **Automatically performs frequency analysis after optimization** — no need for separate `freq` keyword

**Cost:** Very expensive — every step requires full Hessian computation.

### `opt=calcfc`

**What:** Compute exact Hessian at the FIRST step only, then approximate for subsequent steps.

**When to use:** Restart from the last structure of a default optimization.

**Effect:** Often avoids NO and imaginary frequencies after freq.

**Limitation:** If the initial structure is far from the true minimum, by the time convergence is reached, the Hessian may have drifted significantly from the exact value.

### `opt=recalc=N` (Gaussian 16+)

**What:** Compute exact Hessian at the first step, then every N steps.

**Effect and cost:** Between calcfc and calcall.

**Recommended N values:**
- N=3~5: When Hessian computation cost is not too high
- N=5~10: When Hessian computation cost is high
- Adjust based on your situation

### Cost comparison

| Method | Hessian computation | Relative cost | Accuracy |
|--------|--------------------|---------------|----------|
| Default | First step only (approximate) | Lowest | Moderate |
| calcfc | First step only (exact) | Low | Good |
| recalc=N | Every N steps (exact) | Medium | Good-Very Good |
| calcall | Every step (exact) | Highest | Best |

## Combined approach for stubborn cases

```
# For general DFT:
# B3LYP/6-31G(d) opt(calcfc,tight) int=ultrafine

# For Minnesota functionals:
# M06-2X/6-31G(d) opt(calcfc,tight) int=superfine

# For maximum precision:
# B3LYP/6-31G(d) opt(calcall,tight) int=ultrafine
```

## Transition state optimization

All the above discussion applies equally to TS optimization (`opt=TS`). The only difference: for TS, one imaginary frequency is expected (the reaction mode). Only eliminate EXTRA imaginary frequencies beyond the expected one. Use vibration animation to identify which mode corresponds to the reaction coordinate.
