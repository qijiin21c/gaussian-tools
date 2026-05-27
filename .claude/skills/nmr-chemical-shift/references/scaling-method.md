# Scaling Method for NMR Chemical Shifts

Detailed guide to the scaling method (标度法) for computing NMR chemical shifts, based on Sobereva's article (sobereva.com/354).

## Why the scaling method works

Even with good computational methods and large basis sets, standard NMR calculations (TMS reference subtraction) often disagree significantly with experiment. Two main reasons:
1. **Conformational effects** — not covered here, relevant for large flexible molecules
2. **Systematic theoretical errors** — can be corrected by empirical scaling, similar to vibrational frequency scaling factors (sobereva.com/221)

The scaling method fits linear parameters to minimize the difference between calculated and experimental chemical shifts for a large training set of organic molecules.

## The scaling formula

```
δ = (intercept - σ_iso) / (-slope)
```

Where:
- δ = chemical shift (ppm)
- σ_iso = calculated isotropic magnetic shielding (ppm)
- intercept and slope = pre-fitted parameters for a specific computational level

## Finding scaling parameters

### The Cheshire NMR database
- **URL:** http://cheshirenmr.info
- Navigate to "Scaling Factors" in the left sidebar
- Tables are organized by: data source (#1, #2, ...), program, solvent, computational level

### Recommended table for Gaussian 09
**Table #1b** (may be updated on the website) — covers:
- Gas-phase optimized structures
- SMD solvent model for chloroform
- Various functionals and basis sets

### How to select the best level from the table
1. Look at **RMSD** (root-mean-square deviation from experiment)
2. Look at **basis set size**
3. Choose the level with low RMSD and small basis set

### Surprising finding: small basis sets win
B3LYP/6-31G* has lower RMSD than many larger basis sets. This is because:
- Scaling parameters are specifically fitted for each basis set
- Error cancellation between basis set incompleteness and functional errors is captured in the fit
- Using a larger basis set with parameters fitted for a smaller one breaks this cancellation

**Do NOT blindly use larger basis sets with scaling!**

## Recommended scaling parameters

### Protocol 1: B3LYP/6-31G* (primary recommendation)

**Workflow:**
1. Optimize at B3LYP/6-31G* in gas phase
2. Compute NMR at B3LYP/6-31G* with `scrf(SMD,solvent=chloroform)`
3. Apply scaling parameters

**For ¹H NMR:**
- Intercept: 32.2109
- Slope: -1.0157
- δ_H = (32.2109 - σ_iso) / 1.0157

**For ¹³C NMR:**
- See the Cheshire NMR database for carbon parameters at the same level

### Protocol 2: M06-2X/mPW1PW91 (for systems with significant weak interactions)

**Workflow:**
1. Optimize at M06-2X/6-31G* in gas phase
2. Compute NMR at mPW1PW91/6-31G* with `scrf(SMD,solvent=chloroform)`
3. Apply scaling parameters for this level

**When to use:** When weak interactions (dispersion) may significantly affect the molecular structure. M06-2X describes dispersion much better than B3LYP.

**Trade-off:** Slightly more expensive; requires two different functionals.

### Comparison of the two protocols
| Aspect | Protocol 1 (B3LYP/B3LYP) | Protocol 2 (M06-2X/mPW1PW91) |
|--------|--------------------------|-------------------------------|
| Cost | Lower | Higher (M06-2X optimization) |
| ¹H RMSD | Very low | Comparable |
| ¹³C RMSD | Very low | Comparable |
| Structure quality | Good | Better for weak interactions |
| Complexity | Single functional | Two functionals |

**Recommendation:** Use Protocol 1 by default. Use Protocol 2 if the system has significant intramolecular dispersion or weak intermolecular interactions affecting the structure.

## Basis set analysis for NMR

### pcSseg series — designed for NMR

Jensen's pcS series (JCTC, 4, 719, 2008) and pcSseg series (JCTC, 11, 132, 2015):
- Specifically designed for magnetic shielding calculations
- pcSseg = decontracted version of pcS, much faster in mainstream programs
- Available on EMSL Basis Set Exchange

| Basis | Size comparison | NMR accuracy | Cost |
|-------|----------------|-------------|------|
| **pcSseg-0** | ≈3-21G | Better than 6-31G** | Very cheap |
| **pcSseg-1** | ≈6-31G** | ≈def2-TZVP, ≈cc-pVTZ | Cheap |
| **pcSseg-2** | Much larger than pcSseg-1 | Marginal improvement | Not cost-effective |

**pcSseg-1 is the sweet spot** — def2-TZVP accuracy at 6-31G** cost.

### Diffuse functions for NMR

**Diffuse functions are completely useless for NMR calculations.**
- No accuracy improvement
- Dramatically increases computational cost
- Causes SCF convergence problems
- Scaling method results confirm: adding diffuse doesn't improve RMSD

**Do not follow the bad practice of adding diffuse functions for NMR!**

## WC04 and WP04 functionals

WC04 and WP04 (JCTC, 2, 1085, 2006, Cramer et al.) are specialized functionals for chloroform NMR:
- **WC04** — for ¹³C (C = carbon)
- **WP04** — for ¹H (P = proton)
- Based on B3LYP with re-optimized parameters
- Fitted with 6-311+G(2d,p) + IEFPCM chloroform

### Gaussian usage
```
WC04: BLYP IOp(3/76=1000007400,3/77=0999900001,3/78=0000109999)
WP04: BLYP IOp(3/76=1000001189,3/77=0961409999,3/78=0000109999)
```

### Why they are no longer recommended
1. **Require diffuse functions** — parameters were fit with 6-311+G(2d,p); must use diffuse even though it's unnecessary for NMR
2. **Accuracy inferior to scaling** — even though they outperform other standard functionals, they don't match scaling method accuracy
3. **Expensive** — 6-311+G(2d,p) is much more costly than 6-31G*
4. **Need separate TMS calculations** — unlike scaling, which eliminates this step

## Worked examples

### Test molecule 1: Oxetane (恶丁环)

Experimental ¹³C and ¹H chemical shifts in chloroform known. Comparison of methods:

| Method | ¹³C MAE | ¹H MAE | Notes |
|--------|---------|--------|-------|
| **MP2/pcSseg-1** | Poor | Moderate | Very expensive, disappointing accuracy |
| **MP2/def2-TZVP** | Poor | Moderate | Even more expensive, similar accuracy |
| **B97-2/pcSseg-1** | Moderate | Moderate | Mediocre |
| **Scaling (B3LYP/6-31G*)** | **Excellent** (<1 ppm) | **Excellent** (<0.21 ppm) | Cheap and accurate |
| **Scaling (M06-2X//mPW1PW91)** | Good | Moderate | Slightly worse than B3LYP scaling |
| **WP04/6-311+G(2d,p)** | Poor | Moderate | Specialized for ¹H but unimpressive |
| **WC04/6-311+G(2d,p)** | Moderate | Poor | Specialized for ¹³C but worse than scaling |

### Test molecule 2: Isoxazole (异恶唑)

| Method | ¹³C MAE | ¹H MAE | Notes |
|--------|---------|--------|-------|
| **MP2/pcSseg-1** | Poor | Moderate | Same pattern as oxetane |
| **B97-2/pcSseg-1** | Moderate | Moderate | Consistent with oxetane |
| **Scaling (B3LYP/6-31G*)** | **Excellent** | **Excellent** | Best overall |
| **Scaling (M06-2X//mPW1PW91)** | Very good for ¹³C | Less good for ¹H | Mixed results |
| **WP04/WC04** | Poor/Moderate | Moderate | Not competitive |

### Key conclusions from examples
1. **MP2 is disappointing** — despite theoretical superiority, practical accuracy is worse than expected, especially for ¹³C. Not worth the extra cost.
2. **pcSseg-1 often beats def2-TZVP** — smaller basis, sometimes more accurate
3. **Scaling method dominates** — cheapest and most accurate
4. **WP04/WC04 don't compete** — specialized functionals can't match the empirical scaling approach

## Method accuracy ranking (theory vs practice)

### Theoretical accuracy (using CCSD(T) as reference, equilibrium geometry)
```
CCSD(T) > CCSD > MP2 > DFT ≥ HF
```
Within DFT: KT2 (Dalton only) > B97-2 > others

### Practical accuracy (compared to experiment, with real molecules)
```
Scaling method ≈ revTPSS/pcSseg-1 > B97-2 > MP2 > standard B3LYP
```

The practical ranking differs dramatically because:
- Vibrational corrections are neglected (affects all methods differently)
- Solvent effects are approximated
- Geometry is not at the true equilibrium
- Error cancellation plays a significant role

## Gaussian input examples

### Step 1: Geometry optimization (gas phase)
```
#p B3LYP/6-31G* opt

Oxetane - gas phase optimization

0 1
 C    0.000000    0.000000    0.000000
 ...
```

### Step 2: NMR calculation (SMD chloroform)
```
#p B3LYP/6-31G* NMR scrf(SMD,solvent=chloroform)

Oxetane - NMR with SMD chloroform

0 1
 C    [coordinates from optimization]
 ...
```

### Step 3: Apply scaling formula
Extract σ_iso values from the Gaussian output, then:
```
δ_H = (32.2109 - σ_iso_H) / 1.0157
δ_C = (intercept_C - σ_iso_C) / (-slope_C)  [from Cheshire NMR]
```

## References

- sobereva.com/354 — This article (scaling method for NMR)
- sobereva.com/565 — Plotting NMR spectra with Multiwfn
- sobereva.com/221 — Vibrational frequency scaling factors
- sobereva.com/60 — Gaussian mixed/custom basis input
- http://cheshirenmr.info — Scaling factors database
- JCTC, 10, 572 (2014) — NMR method benchmark against CCSD(T)
- JCP, 138, 024111 (2013) — NMR method benchmark
- JCTC, 4, 719 (2008) — pcS basis sets
- JCTC, 11, 132 (2015) — pcSseg basis sets
- JCTC, 2, 1085 (2006) — WC04/WP04 functionals
- J. Chem. Phys., 132, 154104 (2010) — DFT-D3 paper (benzene on Ag(111))
