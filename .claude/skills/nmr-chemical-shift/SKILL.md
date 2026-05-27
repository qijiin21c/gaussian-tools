---
name: nmr-chemical-shift
description: This skill should be used when the user asks to "calculate NMR", "NMR chemical shift", "核磁化学位移", "GIAO", "NMR shielding", "scaling factor NMR", "标度法 NMR", "revTPSS NMR", "pcSseg", "pcSseg-1", "TMS reference", "13C NMR", "1H NMR", "predict NMR spectrum", "绘制NMR谱", "WP04 WC04", "B97-2 NMR", "KT2 NMR", or mentions computing NMR chemical shifts, magnetic shielding tensors, or predicting NMR spectra for organic molecules.
version: 0.1.0
---

# NMR Chemical Shift Calculation

Guidance for computing ¹H and ¹³C NMR chemical shifts efficiently and accurately, based on Sobereva's articles (sobereva.com/354, sobereva.com/565).

**Core principle:** Standard NMR calculation (compute TMS reference → compute molecule → subtract) has systematic errors. Two approaches dramatically improve accuracy at low cost: the **scaling method** (标度法, empirical, cheapest) and **revTPSS/pcSseg-1** (non-empirical, similarly cheap). Use both to cross-validate.

## Quick reference: Recommended protocols

| Priority | Protocol | Best for | Notes |
|----------|----------|---------|-------|
| **1st choice** | Scaling: B3LYP/6-31G* opt(gas) → B3LYP/6-31G* NMR(SMD, chloroform) + scaling parameters | ¹H and ¹³C, organic molecules in CDCl₃ | Cheapest, very accurate, empirical |
| **1st choice (non-empirical)** | B3LYP/6-31G* opt(gas) → revTPSS/pcSseg-1 NMR(IEFPCM, chloroform) - TMS reference | ¹H and ¹³C | Same cost as scaling, less empirical |
| **Alternative** | M06-2X/6-31G* opt(gas) → mPW1PW91/6-31G* NMR(SMD, chloroform) + scaling parameters | When weak interactions matter | Slightly more expensive, two functionals |
| **Fallback** | B3LYP/6-31G* opt(gas) → B97-2/pcSseg-1 NMR(SMD, chloroform) - TMS reference | When scaling parameters unavailable | Standard method, less accurate |

## 1. Before computing: Five factors

| Factor | Recommendation |
|--------|---------------|
| **Geometry optimization** | B3LYP/6-31G* in gas phase is sufficient. No need for larger basis sets. If already optimized at another reasonable level, can use that structure directly. |
| **Method for NMR** | Scaling method (B3LYP/6-31G*) or revTPSS/pcSseg-1. Avoid MP2 (too expensive, no accuracy gain in practice). |
| **Basis set** | pcSseg-1 (designed for NMR, ≈6-31G** size but def2-TZVP/cc-pVTZ accuracy for NMR). Or 6-31G* for scaling. |
| **Solvent model** | Use implicit solvent (SMD or IEFPCM) for chloroform. Chloroform is weakly polar so solvent effect is modest, but include for rigor. |
| **Diffuse functions** | **Do NOT use** — meaningless for NMR, dramatically increases cost with zero accuracy improvement. |

## 2. What quantum chemistry programs compute

Programs compute the **magnetic shielding tensor** σ (3×3 matrix, in ppm) for each nucleus:
```
11  H    Isotropic =    31.8273   Anisotropy =    10.7602
XX=    30.2103   YX=     2.1740   ZX=    -2.1740
XY=     2.2346   YY=    32.6358   ZY=    -5.2595
XZ=    -2.2346   YZ=    -5.2595   ZZ=    32.6358
```

The **isotropic shielding** σ_iso = average of diagonal elements = 31.8273 ppm. This is what matters for solution NMR (molecules tumble randomly).

**GIAO** (Gauge-Including Atomic Orbital) is the default and recommended method in Gaussian. Writing `NMR=GIAO` is redundant — GIAO is already the default.

## 3. Standard method (reference subtraction)

The traditional approach:
1. Compute σ_iso for TMS (tetramethylsilane) reference at the same computational level
2. Compute σ_iso for target molecule
3. δ = σ_iso(TMS) - σ_iso(molecule)

**Problems:** Even with good methods and large basis sets, results often differ significantly from experiment due to systematic errors.

## 4. Scaling method (标度法) — recommended

The scaling method corrects systematic errors using pre-fitted parameters:

```
δ = (intercept - σ_iso) / (-slope)
```

Parameters are fitted by comparing calculated chemical shifts to experimental values for a large set of organic molecules.

### Recommended scaling parameters (Gaussian 09, chloroform, SMD)

**For ¹H NMR** — B3LYP/6-31G* level:
- Intercept: 32.2109
- Slope: -1.0157
- δ_H = (32.2109 - σ_iso) / 1.0157

**For ¹³C NMR** — B3LYP/6-31G* level:
- See http://cheshirenmr.info for the latest parameters (Scaling Factors table)

### Scaling method workflow
1. **Optimize** at B3LYP/6-31G* in gas phase
2. **Compute NMR** at B3LYP/6-31G* with `scrf(SMD,solvent=chloroform)`
3. **Apply formula** δ = (intercept - σ_iso) / (-slope)
4. No TMS calculation needed!

**Advantages:**
- Very cheap (6-31G* basis set)
- Very accurate (RMSD lower than many larger basis sets)
- No TMS reference calculation needed
- More accurate than "standard" B97-2/pcSseg-1 or even MP2

**Important:** Do NOT blindly use larger basis sets with scaling — larger basis sets often give worse results because the scaling parameters are fitted specifically for small basis sets. Error cancellation is part of the accuracy.

### Where to find scaling parameters
- http://cheshirenmr.info — comprehensive database
- Click "Scaling Factors" on the left sidebar
- Find the table matching your program, solvent, and method

## 5. revTPSS/pcSseg-1 — non-empirical alternative

The revTPSS functional (meta-GGA) with pcSseg-1 basis set is excellent for NMR, particularly for ¹H:

### Protocol
1. **Optimize** at B3LYP/6-31G* in gas phase
2. **Compute NMR** at revTPSS/pcSseg-1 with IEFPCM chloroform
3. **Subtract TMS reference** computed at the same level

### Performance
- **¹H NMR:** Accuracy comparable to scaling method, inter-weaving wins
- **¹³C NMR:** Slightly worse than scaling, but better than standard DFT functionals with larger basis sets
- **Cost:** Similar to scaling method

### Cross-validation strategy
Use both methods. If they agree → high confidence. If one disagrees significantly with experiment → try the other.

## 6. Basis set comparison for NMR

| Basis set | Size | NMR accuracy | Notes |
|-----------|------|-------------|-------|
| **3-21G** | Tiny | Poor | Too small |
| **6-31G\*\*** | Small | Moderate | Too rough for standard method |
| **pcSseg-0** | ≈3-21G | Surprisingly decent | Better than 6-31G** overall, but not great |
| **pcSseg-1** | ≈6-31G** | ≈def2-TZVP, ≈cc-pVTZ | **Best cost-performance** for NMR |
| **def2-SVP** | Small | Poor for NMR | Not designed for magnetic properties |
| **def2-TZVP** | Medium | Good | Reasonable but more expensive than pcSseg-1 |
| **pcSseg-2** | Large | Marginal improvement over pcSseg-1 | Not worth the extra cost |
| **def2-QZVP / cc-pVQZ** | Large | Excellent | Overkill, CBS limit approached |
| **pcSseg-3** | Very large | ≈CBS | Not worth it for routine NMR |

**Key finding:** pcSseg-1 (≈6-31G** size) gives NMR accuracy comparable to def2-TZVP/cc-pVTZ. This is the best cost-performance choice for standard-method NMR.

## 7. Methods to avoid for NMR

| Method | Why avoid |
|--------|-----------|
| **MP2** | Extremely expensive for NMR (much more than for single-point); accuracy worse than expected in practice; no advantage over revTPSS/pcSseg-1 |
| **Double-hybrids (DSD-PBEP86)** | Much more expensive; no clear advantage over revTPSS/pcSseg-1 for ¹H/¹³C in chloroform; solvent model can even make results worse |
| **B3LYP (standard method)** | Worse than scaling and revTPSS |
| **B97-2** | Mediocre results; only use if nothing else available |
| **WC04/WP04** | Specialized functionals for NMR but require 6-311+G(2d,p) with diffuse (expensive); accuracy inferior to scaling method |
| **Diffuse functions** | Zero benefit for NMR; dramatically increases cost and SCF difficulty |
| **Large basis sets with scaling** | Scaling parameters are fitted for specific basis sets; larger basis ≠ better results with scaling |

## 8. Solvent model considerations

- **Geometry optimization:** Gas phase is fine — chloroform barely changes structure vs gas phase
- **NMR calculation:** Include implicit solvent (SMD or IEFPCM) for rigor
- **Chloroform is weakly polar** — solvent effect is modest, and error cancellation may make gas-phase results accidentally better
- **For double-hybrids in ORCA:** Compute NMR in vacuum (not with solvent model) — solvent model actually degrades results, possibly due to incomplete implementation

## 9. Recommended Gaussian input templates

### Scaling method — optimization
```
#p B3LYP/6-31G* opt

Molecule name - gas phase optimization

0 1
[coordinates]
```

### Scaling method — NMR calculation
```
#p B3LYP/6-31G* NMR scrf(SMD,solvent=chloroform)

Molecule name - NMR with SMD chloroform

0 1
[coordinates from optimization]
```

### revTPSS/pcSseg-1 — NMR calculation
```
#p revTPSSrevTPSS/gen NMR IEFPCM(solvent=chloroform)

Molecule name - revTPSS/pcSseg-1 NMR

0 1
[coordinates from optimization]

[pcSseg-1 basis set definition from BSE]
****
```

Note: `revTPSSrevTPSS` means both exchange and correlation use revTPSS definition. pcSseg-1 is not built into Gaussian — must copy from BSE database (sobereva.com/60).

## 10. Plotting NMR spectra

Use Multiwfn (sobereva.com/565) for professional NMR spectrum plotting:
- Easy, flexible, powerful, free
- Built-in scaling method support — can directly convert σ_iso to δ
- Built-in TMS reference values for revTPSS/pcSseg-1 level (since 2021-Oct-23 update)
- In the NMR plotting interface: option 7 "Set how to determine chemical shifts" → option 1 "Set reference shielding value" → select the appropriate level

## 11. Conformational effects

For flexible large molecules, conformational distribution affects chemical shifts. This article does not cover this topic — consider Boltzmann-weighted averaging over conformers for flexible systems.

## 12. Vibrational corrections

Vibrational corrections to NMR chemical shifts are non-negligible for high-precision work. However:
- Extremely expensive for even medium-size systems
- Not directly supported in Gaussian
- ORCA 5.0+ supports VPT2 anharmonic vibrational corrections
- The recommended protocols above implicitly absorb vibrational errors into the empirical calibration

The accuracy conclusions reflect the error cancellation with neglected vibrational corrections — this is appropriate for practical research where vibrational corrections are typically ignored.

## Additional Resources

For detailed methodology and comprehensive coverage, consult:

- **`references/scaling-method.md`** — Detailed scaling method explanation: parameter sources, basis set analysis, WC04/WP04 functionals, comparison with MP2/B97-2, worked examples (oxetane, isoxazole)
- **`references/revTPSS-protocol.md`** — revTPSS/pcSseg-1 detailed testing: ¹H and ¹³C accuracy comparison, basis set effects, geometry optimization level effects, double-hybrid comparison, KT1/KT2 testing, solvent model effects
