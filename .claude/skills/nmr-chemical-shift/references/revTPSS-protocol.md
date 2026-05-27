# revTPSS/pcSseg-1 Protocol for NMR

Detailed testing and validation of the revTPSS/pcSseg-1 method for NMR chemical shift calculations, based on Sobereva's article (sobereva.com/565 context, published 2021-Oct-24).

## Background

A JCTC article (doi.org/10.1021/acs.jctc.1c00604) found that the revTPSS functional (meta-GGA) performs excellently for ¹H NMR chemical shifts, outperforming all standard functionals and even matching the empirical scaling method accuracy. This article validates and extends those findings.

## Test molecules

Three representative organic small molecules tested in chloroform:
1. **Oxetane** (恶丁环) — saturated 4-membered ring with oxygen
2. **Isoxazole** (异恶唑) — 5-membered aromatic heterocycle
3. **Pyridine** (吡啶) — 6-membered aromatic heterocycle

Experimental ¹H and ¹³C chemical shifts measured in chloroform.

## Methods tested

| Method | Program | Notes |
|--------|---------|-------|
| **revTPSS/pcSseg-1** | Gaussian 16 | IEFPCM chloroform |
| **revTPSS/pcSseg-2** | Gaussian 16 | Larger basis set test |
| **revTPSS/def2-SVP** | Gaussian 16 | General-purpose small basis |
| **revTPSS/def2-TZVPP** | Gaussian 16 | General-purpose large basis |
| **B97-2/pcSseg-1** | Gaussian 16 | Standard NMR functional |
| **B3LYP/def2-TZVPP** | Gaussian 16 | Common combination |
| **MP2/def2-TZVPP** | Gaussian 16 | Post-HF reference |
| **DSD-PBEP86/def2-TZVPP** | ORCA 5.0.1 | Double-hybrid, vacuum and CPCM |
| **DSD-PBEP86/pcSseg-3** | ORCA 5.0.1 | Near-CBS limit |
| **KT1/def2-TZVPP** | ORCA 5.0.1 | Magnetic property functional, vacuum and CPCM |
| **KT2/def2-TZVPP** | ORCA 5.0.1 | Magnetic property functional, vacuum |
| **Scaling (B3LYP/6-31G*)** | Gaussian 09 | Empirical reference |

All Gaussian calculations used IEFPCM chloroform for NMR (unless noted vacuum). Structures optimized at B3LYP/def2-TZVPP in gas phase (unless noted).

## Results summary

### ¹H NMR accuracy (MAE vs experiment in chloroform)

| Method | MAE (ppm) | Ranking |
|--------|-----------|---------|
| **revTPSS/pcSseg-1** | **Lowest** | ★★★ Best |
| **Scaling (B3LYP/6-31G*)** | **Equivalent to revTPSS** | ★★★ Best |
| KT2/def2-TZVPP (vacuum) | Comparable to revTPSS | ★★ Good |
| DSD-PBEP86/def2-TZVPP (vacuum) | Good | ★★ Good |
| B97-2/pcSseg-1 | Moderate | ★ Mediocre |
| B3LYP/def2-TZVPP | Moderate | ★ Mediocre |
| MP2/def2-TZVPP | Surprisingly poor | ✗ Disappointing |
| WP04/6-311+G(2d,p) | Similar to B97-2 | ★ Mediocre |

### ¹³C NMR accuracy (MAE vs experiment in chloroform)

| Method | MAE (ppm) | Ranking |
|--------|-----------|---------|
| **Scaling (B3LYP/6-31G*)** | **Best** | ★★★ Best |
| **revTPSS/pcSseg-1** | **Slightly worse than scaling, but better than others** | ★★ Good |
| DSD-PBEP86/def2-TZVPP (vacuum) | Moderate | ★ Mediocre |
| B97-2/pcSseg-1 | Moderate | ★ Mediocre |
| MP2/def2-TZVPP | Poor | ✗ Disappointing |
| WC04/6-311+G(2d,p) | Poor | ✗ Bad |
| KT1, KT2/def2-TZVPP | Poor for ¹³C | ✗ Bad |

### Key findings

1. **revTPSS/pcSseg-1 for ¹H:** Excellent accuracy, ties with scaling method
2. **revTPSS/pcSseg-1 for ¹³C:** Good accuracy, second only to scaling method, better than all other standard methods
3. **MP2 is disappointing:** Both ¹H and ¹³C accuracy is worse than expected, especially for ¹³C. Not worth the computational cost.
4. **Double-hybrids have no clear advantage:** DSD-PBEP86/def2-TZVPP is not better than revTPSS/pcSseg-1 despite being much more expensive
5. **KT2 is good for ¹H but bad for ¹³C:** Not recommended as a general NMR method
6. **Scaling remains best for ¹³C:** revTPSS/pcSseg-1 is close but scaling still wins

## Basis set effects on revTPSS

### revTPSS with different basis sets

| Basis set | Size | ¹H accuracy | ¹³C accuracy | Notes |
|-----------|------|------------|-------------|-------|
| **pcSseg-1** | ≈6-31G** | **Best** | **Good** | Optimal choice |
| **pcSseg-2** | Much larger | **Worse than pcSseg-1** | **Worse** | Error cancellation broken |
| **def2-SVP** | ≈pcSseg-1 | Poor | Poor | Too small, not NMR-optimized |
| **def2-TZVPP** | Large | Good | Moderate | Good but much more expensive |

### Why pcSseg-1 > pcSseg-2?

The fact that the larger pcSseg-2 basis set gives worse results reveals that revTPSS/pcSseg-1's excellent performance is partly due to **favorable error cancellation** between the functional and basis set. This is not a coincidence — it's a common pattern observed across multiple test sets (also seen in the JCTC article's Figure 3).

However, revTPSS also performs well with general-purpose large basis sets (def2-TZVPP), showing that the functional itself is genuinely good for NMR, not entirely dependent on error cancellation.

## Geometry optimization level effects

Tested B3LYP optimization with different basis sets, followed by revTPSS/pcSseg-1 NMR:

| Optimization level | NMR accuracy | Notes |
|-------------------|-------------|-------|
| **B3LYP/6-31G*** | **Excellent** | Sufficient, cheapest |
| **B3LYP/def2-SVP** | Comparable | No significant improvement |
| **B3LYP/def2-TZVPP** | Comparable | No significant improvement, much more expensive |

**Conclusion:** B3LYP/6-31G* gas-phase optimization is fully sufficient for subsequent revTPSS/pcSseg-1 NMR calculation. Using a larger basis set for optimization provides no meaningful improvement.

**Practical implication:** If you've already optimized a structure at any reasonable level (B3LYP, PBE0, etc. with at least a modest basis set), you can use it directly for NMR calculation — no need to re-optimize specifically for NMR.

## Solvent model effects

### Does implicit solvent improve NMR accuracy?

| Method | Vacuum | IEFPCM/CPCM chloroform | Better? |
|--------|--------|------------------------|---------|
| **revTPSS/pcSseg-1** | Comparable | Comparable | **No clear preference** |
| **KT1/def2-TZVPP** | Better | Worse | Vacuum is better |
| **DSD-PBEP86/def2-TZVPP** | **Better** | **Worse** | Vacuum significantly better |

**For revTPSS/pcSseg-1:** Results with and without solvent model are comparable, with no systematic preference. **Recommendation:** Use IEFPCM chloroform because it's more rigorous in principle, and the extra cost is minimal.

**For double-hybrids in ORCA:** Vacuum results are clearly better. The CPCM solvent model may not be properly implemented for NMR in ORCA 5.0.1. If using DSD-PBEP86, compute in vacuum (assuming experiment is in chloroform — the weak polarity of chloroform means this approximation is reasonable).

## Double-hybrid NMR: Is it worth it?

### DSD-PBEP86 testing

| Basis set | ¹H accuracy | ¹³C accuracy | Cost |
|-----------|------------|-------------|------|
| **def2-TZVPP** | Good, no advantage over revTPSS | Moderate | Much higher |
| **pcSseg-3 (≈CBS)** | Slight ¹H improvement | **Significant ¹³C degradation** | Extremely high |

**Key finding:** Even at the near-CBS limit (pcSseg-3), DSD-PBEP86 does not outperform revTPSS/pcSseg-1. The ¹H improvement with larger basis is marginal, while ¹³C accuracy actually gets worse. This confirms the limitation is at the functional level, not the basis set.

**When to consider double-hybrids:**
- Only when both scaling and revTPSS/pcSseg-1 disagree significantly with experiment
- Possibly useful for other elements (not ¹H/¹³C) or other types of systems
- Use ORCA with RI approximation for reasonable speed
- Compute in vacuum (not with solvent model) for chloroform systems

### Computational cost comparison

| Method | Relative cost (pyridine NMR) | Hardware |
|--------|-----------------------------|----------|
| B3LYP/6-31G* | ~1 minute | 36-core server |
| revTPSS/pcSseg-1 | ~1 minute | 36-core server |
| MP2/def2-TZVPP | ~6 minutes | 36-core server (Gaussian) |
| DSD-PBEP86/def2-TZVPP | ~1.5 minutes | 8-core laptop (ORCA, RI) |
| DSD-PBEP86/pcSseg-3 | Very high | 36-core server |

**Note:** MP2 in Gaussian is extremely expensive for NMR. ORCA with RI approximation makes MP2 and double-hybrids much faster.

## KT1/KT2 functionals

KT series functionals (KT1, KT2, KT3) are among the few functionals specifically designed for magnetic properties:

| Functional | ¹H accuracy | ¹³C accuracy | Availability |
|-----------|------------|-------------|--------------|
| **KT2** | Excellent (ties with revTPSS) | Poor | ORCA via libxc only |
| **KT1** | Good but worse than KT2 | Poor | ORCA via libxc only |

- KT2 is often cited as the best DFT functional for NMR in benchmark studies
- However, KT2 is poorly supported (not in Gaussian, requires libxc in ORCA)
- KT2 is only good for ¹H, not for ¹³C
- With revTPSS/pcSseg-1 available in Gaussian, KT functionals are no longer necessary

## Recommended protocols

### Protocol A: revTPSS/pcSseg-1 (primary non-empirical choice)

```
Step 1: B3LYP/6-31G* opt (gas phase)
Step 2: revTPSS/pcSseg-1 NMR IEFPCM(solvent=chloroform)
Step 3: Subtract TMS reference (computed at same level)
```

**TMS reference values:** Built into Multiwfn (since 2021-Oct-23 update). In NMR plotting interface: option 7 → option 1 → select revTPSS/pcSseg-1.

### Protocol B: Scaling method (primary empirical choice)

```
Step 1: B3LYP/6-31G* opt (gas phase)
Step 2: B3LYP/6-31G* NMR scrf(SMD,solvent=chloroform)
Step 3: Apply scaling parameters (δ = (intercept - σ_iso)/(-slope))
```

### Cross-validation
Use both Protocol A and Protocol B. Agreement → high confidence. Disagreement → investigate further.

## Gaussian usage details

### revTPSS keyword
```
#p revTPSSrevTPSS/gen NMR IEFPCM(solvent=chloroform)
```
`revTPSSrevTPSS` means both exchange and correlation use the revTPSS definition.

### pcSseg-1 basis set
pcSseg-1 is NOT built into Gaussian (as of C.01). Must copy definition from BSE database:
1. Go to https://www.basissetexchange.org
2. Select elements needed
3. Choose pcSseg-1
4. Format: Gaussian94
5. Use with `gen` keyword

See sobereva.com/60 for Gaussian mixed/custom basis input format.

### B97-2 keyword
In Gaussian, B97-2 is written as `B972`.

## Conformational effects

For flexible large molecules, the conformational distribution significantly affects chemical shifts. This article does not address conformational averaging — consider Boltzmann-weighted averaging over conformers for such systems.

## Vibrational corrections

For high-precision NMR that can be directly compared to experiment, vibrational corrections are non-negligible. However:
- Extremely expensive even for medium-size systems
- Not directly supported in Gaussian
- ORCA 5.0+ supports VPT2 anharmonic vibrational corrections
- The accuracy conclusions in this article reflect error cancellation with neglected vibrational corrections

This is appropriate for practical research since vibrational corrections are typically ignored in computational NMR studies.

## References

- sobereva.com/565 context (2021-Oct-24 article) — This article (revTPSS/pcSseg-1 testing)
- sobereva.com/354 — Scaling method for NMR
- sobereva.com/565 — Plotting NMR spectra with Multiwfn
- sobereva.com/60 — Gaussian mixed/custom basis input
- sobereva.com/557 — When B3LYP optimization is appropriate
- doi.org/10.1021/acs.jctc.1c00604 — JCTC article on revTPSS for NMR
- JCTC, 10, 572 (2014) — MP2 vs DFT NMR benchmark (CCSD(T) reference)
- JCTC, 14, 4756 (2018) — DSD-PBEP86 NMR benchmark (CCSD(T) reference)
- JCTC, 4, 719 (2008) — pcS basis sets
- JCTC, 11, 132 (2015) — pcSseg basis sets
