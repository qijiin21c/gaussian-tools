# DFT-D in Gaussian: Usage Guide

Practical guide for enabling and using DFT-D dispersion corrections across different Gaussian versions, based on Sobereva's article (sobereva.com/83).

## Gaussian version capabilities

### G03
- **No DFT-D support at all**
- Best option: `M052X` (only available in later G03 versions)
- Workaround: Not practical — upgrade if possible

### G09 A/B/C (before D.01)
- **No DFT-D3 support**
- Built-in dispersion-corrected functionals available:
  - `wB97XD` — good for most weak interactions
  - `M062X` — slightly better than wB97XD for some systems
  - `B2PLYPD` — double-hybrid, higher accuracy
- Speed comparison: wB97XD and M062X are much slower than B3LYP

**Heavy atom error:** When computing heavy atoms with B97D, wB97XD, B2PLYPD, you may see:
```
R6DR0: No vdW radius available for IA= xx
```
This means the element (atomic number xx) has no DFT-D2 parameter. **Fix:** Upgrade to G09 D.01+ for DFT-D3, or use a different method.

### G09 D.01 and later (including G16)
- **Full DFT-D3 support** — this is what you should be using

## Gaussian 16 / G09 D.01+ usage

### Basic syntax

```
# B3LYP/6-31G(d) EmpiricalDispersion=GD3BJ opt
# B3LYP/6-31G(d) em=GD3BJ opt    ← shorthand
```

**Keyword options:**
| Keyword | Damping | Full name |
|---------|---------|-----------|
| `em=GD3` or `EmpiricalDispersion=GD3` | Zero-damping | DFT-D3(0) |
| `em=GD3BJ` or `EmpiricalDispersion=GD3BJ` | BJ-damping | DFT-D3(BJ) |
| `em=GD2` or `EmpiricalDispersion=GD2` | D2 | DFT-D2 |

### Built-in corrected functionals

These work directly without `EmpiricalDispersion`:

| Keyword | Built-in correction |
|---------|-------------------|
| `B2PLYPD3` | DFT-D3(BJ) |
| `B97D3` | DFT-D3(BJ) |
| `mPW2PLYPD` | DFT-D2 |
| `B97D` | DFT-D2 |
| `wB97XD` | DFT-D2 |
| `B2PLYPD` | DFT-D2 |

### PM6 semi-empirical
```
# PM6D3    ← PM6 with DFT-D3 correction
```

### Output interpretation

With `#P`, DFT-D enabled calculations show:
```
R6Disp:  Grimme-D3(BJ) Dispersion energy=       -0.0018363766 Hartrees.
Nuclear repulsion after empirical dispersion term =       41.9082499513 Hartrees.
```

Gaussian adds the DFT-D correction energy to the nuclear repulsion term. The total energy output is the DFT-D corrected energy.

## G09 D.01 D3(BJ) frequency bug

**Bug:** In G09 D.01, the D3(BJ) frequency calculation **omits the r⁻⁸ term**, making the dispersion contribution to force constants incomplete.

**Impact:**
- Hard vibrational modes: negligible effect
- Soft vibrational modes: can cause **false imaginary frequencies** even when the structure is at a true minimum

**Fixes:**
1. Upgrade to G09 E.01 or later (bug fixed)
2. Use D3(0) (`em=GD3`) instead of D3(BJ) for opt+freq in G09 D.01
3. Separate opt and freq: optimize with D3(BJ), then compute freq at D3(0) level (not ideal)

**Zero-damping does NOT have this problem.**

## Custom DFT-D3 parameters

### When needed

Gaussian has built-in D3 parameters for many functionals (see manual's DFT section). For functionals NOT built-in, you must define parameters manually.

**Commonly needed custom parameters:**
- TPSSh — not built-in until very recent versions
- MN15 — may not have D3 parameters in older G16
- MN15L — same issue
- BHandHLYP — not built-in

### IOp method (Gaussian 16 C.01+)

**Parameter encoding:** Multiply the actual parameter value by 1,000,000 and use as integer.

| IOp | Parameter | Applies to |
|-----|-----------|-----------|
| IOp(3/174) | S6 | Both |
| IOp(3/175) | S8 | Both |
| IOp(3/176) | SR6 | Zero-damping only |
| IOp(3/177) | A1 | BJ-damping only |
| IOp(3/178) | A2 | BJ-damping only |

**Parameter sources:** GMTKN55 benchmark paper (Phys. Chem. Chem. Phys., 19, 32184, 2017), Supplementary Material Tables S3 and S4.

### Complete worked examples

**TPSSh-D3(BJ):**
Parameters: S6=1.0, S8=2.2382, a1=0.4529, a2=4.655
```
# TPSSh/def2-TZVP em=GD3BJ IOp(3/174=1000000,3/175=2238200,3/177=452900,3/178=4655000)
```

**MN15L-D3(0):**
Parameters: S6=1.0, S8=0.0, sr6=3.3388
```
# MN15L/def2-TZVP em=GD3 IOp(3/174=1000000,3/175=0,3/176=3338800)
```

**MN15-D3(BJ):**
Parameters: S6=1.0, S8=0.7862, a1=2.0971, a2=7.5923
```
# MN15/def2-TZVP em=GD3BJ IOp(3/174=1000000,3/175=786200,3/177=2097100,3/178=7592300)
```

**BHandHLYP-D3(BJ):**
Parameters: S6=1.0, S8=1.0354, a1=0.2793, a2=4.9615
```
# BHandHLYP/def2-TZVP em=GD3BJ IOp(3/174=1000000,3/175=1035400,3/177=279300,3/178=4961500)
```

**BHandHLYP-D3(0):**
Parameters: S6=1.0, S8=1.442, sr6=1.37
```
# BHandHLYP/def2-TZVP em=GD3 IOp(3/174=1000000,3/175=1442000,3/176=1370000)
```

### CRITICAL: IOp multi-step warning

**When Gaussian runs multi-step tasks, IOp settings only apply to the FIRST step.**

```
# BAD — freq will NOT receive custom D3 parameters!
# TPSSh/def2-TZVP em=GD3BJ IOp(...) opt freq
```

This causes freq to use built-in (or default) D3 parameters instead of your custom ones, creating a method mismatch between opt and freq — a serious problem since opt+freq+IRC must match.

**Correct approach: Separate opt and freq into two jobs.**

```
Job 1: # TPSSh/def2-TZVP em=GD3BJ IOp(...) opt
Job 2: # TPSSh/def2-TZVP em=GD3BJ IOp(...) freq
```

### Environment variable method (G09/16 B.01 and earlier)

For older versions, use environment variables instead of IOp:

| Variable | Parameter |
|----------|-----------|
| `GAUSS_DFTD3_S6` | S6 |
| `GAUSS_DFTD3_S8` | S8 |
| `GAUSS_DFTD3_SR6` | SR6 (zero-damping) |
| `GAUSS_DFTD3_ABJ1` | A1 (BJ-damping) |
| `GAUSS_DFTD3_ABJ2` | A2 (BJ-damping) |

Value = parameter × 1,000,000.

```bash
# Linux (Bash) — set before running Gaussian
export GAUSS_DFTD3_S6=1000000
export GAUSS_DFTD3_S8=786200
export GAUSS_DFTD3_ABJ1=2097100
export GAUSS_DFTD3_ABJ2=7592300
```

Then use: `# MN15/6-311+G(d,p) em=GD3BJ`

### wB97X-D3 limitation

The wB97X-D3 functional (wB97X with D3 instead of D2) provides improved weak interaction accuracy in ORCA. It cannot be used in Gaussian via custom parameters because its sr,8 = 1.094, while Gaussian only allows sr,8 = 1.0 via environment variables.

## External keyword workflow (G09 before D.01)

For G09 versions before D.01, you CAN combine external optimization with DFT-D3 using the `external` keyword:

```
# B3LYP/6-31G(d) external='./dftdopt.sh' opt
```

The script `dftdopt.sh` must:
1. Read coordinates passed by Gaussian
2. Call another Gaussian job with `force` keyword to get energy and gradients
3. Call DFT-D3 program to get dispersion gradients
4. Add dispersion gradients to DFT gradients
5. Return combined gradients to Gaussian

This is complex to implement. Reference articles:
- sobereva.com/421 — Gaussian + xTB coupling
- sobereva.com/422 — Gaussian + ORCA coupling
- post-G program scripts (http://faculty1.ucmerced.edu/ejohnson29/2.cfm?pm=432&lvl=2&menuid=618) — XDM correction coupling example

## Recommended combination for weak interactions

**B3LYP-D3(BJ)** is the recommended functional for weak interaction studies:
- Good accuracy — among the best hybrid functionals for this purpose
- Reliable — well-tested across many system types
- Fast — faster than M06-2X and wB97XD
- Universal — works for all element types

For absolute interaction energy accuracy: `M06-2X-D3(0)` is slightly better than `B3LYP-D3(BJ)`.

See Phys. Chem. Chem. Phys., 19, 32184 (2017) Supplementary Material Table 20 for comprehensive comparison.

## APF-D dispersion

G09 D.01+ also supports APF-D (Austin-Petersson-Frisch, JCTC, 8, 4989):
- Built-in: `APFD`
- Applied to other functionals: `EmpiricalDispersion=PFD`

**Not recommended** — reliability is questionable compared to D3.

## References

- sobereva.com/83 — This article (DFT-D usage in programs)
- sobereva.com/344 — Non-built-in methods in Gaussian
- sobereva.com/421 — Gaussian + xTB coupling
- sobereva.com/422 — Gaussian + ORCA coupling
- Phys. Chem. Chem. Phys., 19, 32184 (2017) — GMTKN55 benchmark
- J. Chem. Theory Comput., 8, 4989 — APF-D
