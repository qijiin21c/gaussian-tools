# Non-Built-In Methods and Functionals in Gaussian

How to use theoretical methods and functionals not built into Gaussian via IOp settings, based on Sobereva's article (sobereva.com/344).

**CRITICAL WARNING:** For multi-step tasks like `opt freq`, **IOp settings only apply to the first step** and are NOT automatically passed to subsequent steps. When using IOp to define non-built-in methods, **NEVER combine opt and freq in one job** — run them separately.

## Custom DFT functional definition

### The formula

By setting `IOp(3/76=ab)`, `IOp(3/77=cd)`, `IOp(3/78=ef)` (where abcdef are values × 10,000):

```
E_XC = a × [d × E_X_LDA + c × ΔE_X_GGA] + b × E_X_HF + f × E_C_LDA + e × ΔE_C_GGA
```

| Term | Meaning |
|------|---------|
| E_X_LDA | LDA exchange |
| ΔE_X_GGA | GGA exchange gradient correction (includes meta-GGA) |
| E_X_HF | HF exchange (coefficient b = HF% hybridization) |
| E_C_LDA | LDA correlation |
| ΔE_C_GGA | GGA correlation gradient correction |

For both exchange and correlation: E_GGA = ΔE_GGA + E_LDA. For example: E_X_B88 = E_X_LDA + ΔE_X_B88, E_C_LYP = E_C_LDA + ΔE_C_LYP.

### Coefficient rules

| Functional type | a | b (HF%) | c | d | e | f |
|----------------|---|---------|---|---|---|---|
| **a** | Always 1 | — | — | — | — | — |
| **Pure functional** | 1 | 0 | 1 | 1 | 1 | 1 |
| **Single-parameter hybrid** (PBE0, BHandHLYP) | 1 | HF% | 1-HF% | 1-HF% | 1 | 1 |
| **Three-parameter hybrid** (B3LYP) | 1 | varies | varies | varies | varies | varies |
| **HF** | — | 1 | 0 | 0 | 0 | 0 |

### Verifying your definition

With `#P`, Gaussian outputs:
```
IExCor= 402 DFT=T Ex=B+HF Corr=LYP ExCW=0 ScaHFX= 0.200000
ScaDFX= 0.800000 0.720000 1.000000 0.810000
```
- `ScaHFX` = b (HF exchange coefficient)
- `ScaDFX` values = d, c, f, e

## B3LYP and variants

### Standard B3LYP

```
E_XC_B3LYP = (1-a0)×E_X_LDA + a0×E_X_HF + aX×ΔE_X_B88 + E_C_VWN + aC×ΔE_C_LYP
```
where a0=0.20, aX=0.72, aC=0.81.

**Coefficients:** a=1.0, b=0.2, c=0.72, d=0.8, e=0.81, f=1.0

```
# BLYP IOp(3/76=1000002000,3/77=0720008000,3/78=0810010000)
```

### B3LYP with VWN5 (instead of default VWN3)

Gaussian defaults to VWN3 for B3LYP's LDA correlation (slightly better). GAMESS-US defaults to VWN5. To use VWN5:

```
# BV5LYP IOp(3/76=1000002000,3/77=0720008000,3/78=0810010000)
```

### B3LYP* (15% HF for transition metals)

J. Chem. Phys., 117, 4729 (2002): Reduces HF from 20% to 15%, fixing B3LYP's overestimation of high-spin TM complex stability.

**Coefficients:** a=1.0, b=0.15, c=0.72, d=0.85, e=0.81, f=1.0

```
# BLYP IOp(3/76=1000001500,3/77=0720008500,3/78=0810010000)
```

### Tuning HF% for TDDFT

Higher HF% → higher TDDFT excitation energy. You can adjust b (and correspondingly d, keeping b+d=1) to match experimental spectra. (This is data-fitting — scientifically questionable but practically common.)

## PBE0 variants

### Standard PBE0 (PBE1PBE in Gaussian)

25% HF: a=1.0, b=0.25, c=d=0.75, e=f=1.0

```
# PBEPBE IOp(3/76=1000002500,3/77=0750007500)
```

(IOp(3/78) defaults to 1000010000, so can be omitted.)

### PBE0-1/3 (33.3% HF)

J. Chem. Phys., 138, 021104 (2013):

```
# PBEPBE IOp(3/76=1000003333,3/77=0666706667)
```

### PBE38 (37.5% HF)

Defined in DFT-D3 paper. Best for frequency-dependent polarizability.

```
# PBEPBE IOp(3/76=1000003750,3/77=0625006250)
```

## Range-separated functionals: tuning ω

For LC-pure-functional (e.g., LC-BLYP), the range-separation parameter ω controls how much of 1/r₁₂ is treated with HF exchange at long range.

| Functional | Default ω |
|-----------|----------|
| LC-BLYP, LC-PBE, etc. | 0.47 |
| wB97X | 0.3 |
| LC-wPBE | 0.4 |

To tune ω, set both IOp(3/107) and IOp(3/108) to MMMMM00000 (ω = MMMMM/10000):

```
# LC-wPBE IOp(3/107=0300000000,3/108=0300000000)
```

For full range-separated functional customization (α, β, ω parameters), see sobereva.com/550.

## QTP17 functional

QTP17 + aug-cc-pVTZ gives orbital energies that satisfy Koopmans' theorem — orbital energy negatives ≈ photoelectron spectrum ionization energies (valence, core, inner). No correction needed for Multiwfn photoelectron spectrum plotting.

**Trained on aug-cc-pVTZ — accuracy drops with other basis sets.**

```
# SLYP/aug-cc-pVTZ IOp(3/76=1000006200,3/77=0000003800,3/78=0800010000)
```

## Perturbation-correlated methods

### SCS-MP2

J. Chem. Phys., 118, 9095 (2003): Spin-component-scaled MP2. Same-spin (parallel) × 1/3, opposite-spin (antiparallel) × 6/5.

**Performance:** Much improved reaction energies (reaches QCISD level), slightly better geometries. Slightly worse barriers. Significantly worse weak interactions. Overall inferior to modern double-hybrids.

```
# MP2 IOp(3/125=0333312000)
```

IOp(3/125=MMMMMNNNNN): parallel spin coefficient = MMMMM/10000, antiparallel = NNNNN/10000.

**Verification from output:**
```
MP2:     alpha-alpha T2 E2= -0.0473  → SCS-MP2: E2= -0.0158  (× 1/3)
         alpha-beta  T2 E2= -0.3005  → SCS-MP2: E2= -0.3606  (× 6/5)
```

### SOS-MP2

J. Chem. Phys., 121, 9793 (2004): Ignores same-spin contribution, antiparallel × 1.3. Worse than MP2, especially for weak interactions. Claims O(N⁴) scaling but Gaussian doesn't optimize it — no speedup. **Not recommended.**

```
# MP2 IOp(3/125=0000013000)
```

### SCSN-MP2

J. Chem. Theory Comput., 3, 80 (2007): Ignores antiparallel, parallel × 1.76. Fitted for nucleobase pair interactions. Weak interaction accuracy 2-3× better than MP2. **Useful for weak interactions.**

```
# MP2 IOp(3/125=1760000000)
```

Note: For weak interactions, the scaling direction is opposite to SCS-MP2 — reduce antiparallel, increase parallel.

### MP2.5

ChemPhysChem, 10, 282 (2009): MP2 + 0.5 × MP3 third-order perturbation. Same cost as MP3.

**Usage:** Run MP3, then manually compute:
```
E(MP2.5) = EUMP2 + E3 × 0.5
```

From MP3 output:
```
E2 =    -0.3951023394D+00  EUMP2= -0.11430702788798D+03
E3=       -0.48480932D-02  EUMP3= -0.11431187598D+03
```
E(MP2.5) = -114.30702788798 + (-0.0048480932) × 0.5 = -114.3094519

**Cannot be used for optimization/frequency** — only for single-point energy (must be computed manually from MP3 output).

### MP2.X

Phys. Chem. Chem. Phys., 13, 21121 (2011): MP2 + X × MP3, where X is fitted per basis set from S66 test set. Makes small basis sets (even 6-31G*) give weak interaction energies comparable to MP2.5/aug-cc-pVTZ. Reliability on broader systems still needs verification.

### SCS-MP3

J. Comput. Chem., 24, 1529 (2003): SCS-MP2 + 0.25 × E3. Thermochemistry much better than SCS-MP2 (approaches QCISD(T)). Weak interaction accuracy mediocre.

```
# MP3 IOp(3/125=0333312000)
```
Then: E(SCS-MP3) = EUMP2 + E3 × 0.25

### SCS-CCSD / SCS-MI-CCSD

Not implementable in Gaussian — program doesn't output CCSD same-spin and opposite-spin contributions separately.

## Double-hybrid functionals

### Old-style double-hybrids

General form:
```
E_XC = (1-c1)×E_X_GGA + c1×E_X_HF + (1-c2)×E_C_GGA + c2×E2
```

**B2PLYP** (J. Chem. Phys., 124, 034108, 2006):
```
E_XC = 0.47×E_X_B88 + 0.53×E_X_HF + 0.73×E_C_LYP + 0.27×E2
```
Built into Gaussian 09. No SCS scaling, no dispersion.

**B2GP-PLYP** (J. Phys. Chem. A, 112, 12868, 2008):
c1=0.65, c2=0.36. Better than B2PLYP but still inferior to SCS-scaled double-hybrids.

```
# B2PLYP/cc-pVTZ IOp(3/125=0360003600,3/76=1000006500,3/77=0350003500,3/78=0640006400)
```

Here `B2PLYP` is kept to trigger double-hybrid computation, but all parameters are overridden. IOp(3/125) sets E2 parallel/antiparallel coefficients.

### Modern SCS-scaled double-hybrids with D3

General form:
```
E_XC = (1-cX)×E_X_GGA + cX×E_X_HF + cC×E_C_GGA + cO×E2_OS + cS×E2_SS + E_D
```

Where E2_OS = opposite-spin E2, E2_SS = same-spin E2, E_D = DFT-D3(BJ) dispersion.

**DSD-PBEP86-D3(BJ)** (J. Comput. Chem., 34, 2327, 2013):
cX=0.69, cC=0.44, cO=0.52, cS=0.22, D3(BJ): s6=0.48, a2=5.6

**For Gaussian 09** (requires environment variables for D3):

```bash
# Linux bash — set before running Gaussian
export GAUSS_DFTD3_S6=480000
export GAUSS_DFTD3_SR6=0
export GAUSS_DFTD3_S8=0
export GAUSS_DFTD3_ABJ1=0
export GAUSS_DFTD3_ABJ2=5600000
```

```
# B2PLYP/cc-pVTZ IOp(3/125=0220005200,3/76=1000006900,3/77=0310003100,3/78=0440004400,3/74=1004) empiricaldispersion=GD3BJ
```

IOp(3/74=1004) sets X_GGA=PBE, C_GGA=P86.

**DSD-PBEP86 (without D3):**
cX=0.72, cC=0.44, cO=0.51, cS=0.36

```
# B2PLYP/cc-pVTZ IOp(3/125=0360005100,3/76=1000007200,3/77=0280002800,3/78=0440004400,3/74=1004)
```

**revDSD-PBEP86-D3(BJ)** (J. Phys. Chem. A, 123, 5129, 2019):

For Gaussian 16:
```
# DSDPBEP86/basis IOp(3/125=0079905785,3/78=0429604296,3/76=0310006900,3/74=1004) em=gd3bj IOp(3/174=0437700,3/175=-1,3/176=0,3/177=-1,3/178=5500000)
```

### RSX-QIDH (range-separated double-hybrid)

For carbon ring bond alternation energy differences (PCCP, 2022, DOI: 10.1039/d1cp04996h). Gaussian 16:

```
# PBEQIDH IOp(3/74=1001009,3/78=0666606666,3/107=0270000000,3/108=0270000000,3/119=0310000000,3/120=0310000000,3/125=0333403334,3/130=06900,3/131=06900)
```

## Old Minnesota functionals

MPW1K, PBE1KCIS, etc. — not recommended. Pre-M05 Minnesota functionals are superseded by better alternatives. If you must use them, see http://comp.chem.umn.edu/info/DFT.htm for Gaussian implementations. Some require modified Gaussian source code.

## References

- sobereva.com/344 — This article (non-built-in methods)
- sobereva.com/550 — Custom range-separated functionals in Gaussian
- sobereva.com/543 — QTP functionals and Koopmans' theorem
- sobereva.com/478 — Photoelectron spectrum plotting with Multiwfn
- Chem. Phys. Lett., 268, 345 (1997) — VWN3 vs VWN5 for B3LYP
- J. Chem. Phys., 117, 4729 (2002) — B3LYP*
- J. Chem. Phys., 118, 9095 (2003) — SCS-MP2
- J. Chem. Phys., 121, 9793 (2004) — SOS-MP2
- J. Chem. Theory Comput., 3, 80 (2007) — SCSN-MP2
- ChemPhysChem, 10, 282 (2009) — MP2.5
- Phys. Chem. Chem. Phys., 13, 21121 (2011) — MP2.X
- J. Comput. Chem., 24, 1529 (2003) — SCS-MP3
- J. Chem. Phys., 124, 034108 (2006) — B2PLYP
- J. Phys. Chem. A, 112, 12868 (2008) — B2GP-PLYP
- J. Comput. Chem., 34, 2327 (2013) — DSD-PBEP86-D3(BJ)
- J. Phys. Chem. A, 123, 5129 (2019) — revDSD-PBEP86-D3(BJ)
- PCCP, 2022, DOI: 10.1039/d1cp04996h — RSX-QIDH for carbon rings
- Phys. Chem. Chem. Phys., 12, 9611 (2010) — SCS-MI-CCSD
