# Month Basis Sets — Usage Guide

Step-by-step guide for using "month" basis sets (jul-, jun-, may-, apr-, maug-cc-pVnZ) in Gaussian, based on Sobereva's article (sobereva.com/119).

## What are month basis sets?

The "month" series systematically removes high-angular-momentum diffuse functions from aug-cc-pVnZ to reduce cost while maintaining most of the accuracy:

| Basis | Heavy atom diffuse | Hydrogen diffuse |
|-------|-------------------|------------------|
| **aug-** (august) | All angular momentum | All |
| **jul-** | All angular momentum | None |
| **jun-** | Remove highest-l | None |
| **may-** | Remove 2 highest-l | None |
| **apr-** | Remove 3 highest-l | None |
| **maug-** | s+p only | None |

### Naming logic

aug- = august. Then go backward through months, each removing the highest angular momentum diffuse function:
- jul(y): remove hydrogen diffuse only
- jun(e): remove highest-l heavy atom diffuse
- may: remove 2 highest-l
- apr(il): remove 3 highest-l
- mar(ch): remove 4 highest-l (= maug)
- ...and so on

The lower bound depends on the base basis set's maximum angular momentum.

### Example: aug-cc-pVQZ for carbon

Highest angular momentum in aug-cc-pVQZ for C is g:
- **jul-cc-pVQZ:** Keep all heavy atom diffuse (s,p,d,f,g), remove all H diffuse
- **jun-cc-pVQZ:** Remove g diffuse from heavy atoms (keep s,p,d,f)
- **may-cc-pVQZ:** Remove f,g diffuse (keep s,p,d)
- **apr-cc-pVQZ:** Remove d,f,g diffuse (keep s,p) = maug-cc-pVQZ

Since apr- = maug- at QZ level, there is no mar-cc-pVQZ.

For aug-cc-pV5Z (highest angular momentum increased by 1), the lower bound drops one month to mar-.

### Construction note

Month basis sets are created by simply **deleting functions** from aug-cc-pVnZ. The remaining functions' exponents and contraction coefficients are NOT re-optimized.

## Recommended month basis sets by method

### HF / KS-DFT

HF/KS-DFT don't require high-angular-momentum basis functions. When diffuse is needed:

| Accuracy | Recommended basis |
|----------|-------------------|
| Large systems | maug-cc-pVDZ |
| Higher accuracy | maug-cc-pVTZ (= may-cc-pVTZ) |

aug- level's high-angular-momentum diffuse functions are wasteful for HF/DFT.

### Post-HF methods

Post-HF is much more sensitive to high-angular-momentum functions than HF/DFT. maug- level is too small.

| Accuracy | Recommended basis |
|----------|-------------------|
| Medium-low | jul-cc-pVDZ |
| Medium | may-cc-pVTZ |
| Medium-high | jul-cc-pVTZ |
| High | jun-cc-pVQZ |

**Why lower month with higher zeta:** As zeta number increases, the outermost cc-pVnZ functions become more diffuse-like, partially serving as diffuse functions. At the same zeta, different month levels have smaller accuracy differences.

**Key insight:** For tasks that absolutely need diffuse, adding even maug-level diffuse to cc-pVnZ improves results more dramatically than increasing zeta number without diffuse. **Diffuse must be present when needed, but doesn't need high angular momentum.**

**With proper use of month basis sets, there's no need to use aug-cc-pVnZ anymore.**

## Gaussian usage

### Gaussian 09 D.01 and later

Direct support — simply write the basis set name:

```
# wB97XD/may-cc-pVTZ opt
```

or

```
# B3LYP/jul-cc-pVQZ SP
```

Also supported: `spAug-cc-pV*Z` = maug-cc-pV*Z + s diffuse on hydrogen.

### Older Gaussian versions (custom basis set)

Must define via `gen` keyword and custom basis set input.

**Example:** Using may-cc-pVTZ for CH₄ in an old Gaussian version.

#### Step 1: Get aug-cc-pVTZ definition from BSE

Go to https://www.basissetexchange.org:
1. Click carbon in the periodic table
2. Select `aug-cc-pVTZ` from the left list
3. Set Format to `Gaussian94`
4. Click "Get Basis Set"

The output shows:
```
****
C     0
[standard s,p basis functions...]
S   1   1.00
      0.0440200              1.0000000        ← s diffuse (smallest s exponent)
P   1   1.00
      0.0356900              1.0000000        ← p diffuse (smallest p exponent)
D   1   1.00
      0.1000000              1.0000000        ← d diffuse (smallest d exponent) ← REMOVE
F   1   1.00
      0.2680000              1.0000000        ← f diffuse (smallest f exponent) ← REMOVE
****
```

#### Step 2: Remove highest-l diffuse for may-

may- removes the 2 highest angular momentum diffuse functions. For cc-pVTZ (max l=f), remove d and f diffuse:

Remove these blocks:
```
D   1   1.00
      0.1000000              1.0000000
F   1   1.00
      0.2680000              1.0000000
```

Keep the s diffuse and p diffuse blocks.

#### Step 3: Create the input file

```
#P wb97xd/gen

Divokej Bill

0 1
 C                 -2.32704417   -0.72320845   -0.00946732
 H                 -1.97038974   -1.73201845   -0.00946732
 H                 -1.97037133   -0.21881026    0.86418419
 H                 -1.97037133   -0.21881026   -0.88311882
 H                 -3.39704417   -0.72319527   -0.00946732

C     0
[full cc-pVTZ s,p basis...]
S   1   1.00
      0.0440200              1.0000000        ← keep (s diffuse)
P   1   1.00
      0.0356900              1.0000000        ← keep (p diffuse)
D   1   1.00
      1.0970000              1.0000000        ← keep (d polarization, NOT diffuse)
D   1   1.00
      0.3180000              1.0000000        ← keep (d polarization, NOT diffuse)
F   1   1.00
      0.7610000              1.0000000        ← keep (f polarization, NOT diffuse)
****
H 0
cc-pVTZ
****
```

**Note on hydrogen:** Month basis sets remove ALL hydrogen diffuse, making them equivalent to cc-pVnZ for hydrogen. So we use `cc-pVTZ` for H.

### BSE now has month basis sets

The Basis Set Exchange (BSE) now includes month basis set definitions directly. Simply search for `may-cc-pV(T+d)Z` etc. and download in Gaussian format.

## When is removing hydrogen diffuse OK?

Many worry that removing all hydrogen diffuse is too aggressive. It's fine because:
- Hydrogen has low electronegativity — electrons are not diffuse
- Nearby heavy atom diffuse functions already supplement hydrogen
- The S66 weak interaction benchmark set removes hydrogen diffuse for CBS extrapolation
- **Exception:** LiH (Li has very low electronegativity → H carries large negative charge → H needs diffuse)

## Cost savings

### Pople series

Many people use `6-311++G**` when `6-311+G**` is sufficient. Removing hydrogen diffuse:
- Saves significant time (organic systems have many hydrogens)
- No accuracy loss for most properties

### Dunning series

MP2 in Gaussian, aug-cc-pVnZ vs cc-pVnZ:
| n | Basis function increase | Time increase |
|---|------------------------|---------------|
| D | >50% | 2.4x |
| T | >50% | 5.0x |
| Q | >50% | 6.3x |

Using may-cc-pVTZ instead of aug-cc-pVTZ:
- Removes d and f diffuse from heavy atoms, all H diffuse
- Significant cost reduction
- Minimal accuracy loss for HF/DFT
- Good for medium-accuracy post-HF

## Even-tempered diffuse construction

If no diffuse version exists for your basis set:

1. **Even-tempered approach:** Build diffuse functions systematically from existing exponents
2. **Divide by 3:** Take the smallest s and p exponents and divide by 3 (JCTC,7,3027)

These exponents may not be as good as specifically optimized ones for particular problems, but could perform better for broader problem types not considered during optimization.

See sobereva.com/340 for detailed discussion of adding diffuse to def2- and other basis sets.

## References

- sobereva.com/119 — This article (diffuse functions and month basis sets)
- sobereva.com/340 — Adding diffuse to def2- series
- sobereva.com/336 — Basis set selection guide
- sobereva.com/347 — adddiffuse tool for even-tempered diffuse
- sobereva.com/60 — Gaussian mixed/custom basis input
- JCTC,7,10 — Truhlar month basis sets paper
- JCTC,7,3027 — Extended month basis sets and diffuse construction methods
- JCTC,7,3027 — "Divide by 3" rule for diffuse exponents
