# Practical ECP Usage in Gaussian

Practical guidance for defining, modifying, and using pseudopotentials (ECPs) in Gaussian. Based on Sobereva's article (sobereva.com/188).

## Gaussian ECP definition format

### General structure

```
ElementName    0                    // Element name or atom number. 0 is mandatory.
Name-ECP    L    core_electrons     // ECP name; L value; number of core electrons replaced
L-ul potential                      // Block name (can be anything) — defines U_L
  N_terms                           // Number of expansion terms for U_L
n_1    ζ_1    d_1                   // Each line: n, ζ (exponent), d (coefficient)
n_2    ζ_2    d_2
...
s-ul potential                      // Block name (can be anything) — defines U_0 - U_L
  N_terms
n_1    ζ_1    d_1
...
p-ul potential                      // Block name (can be anything) — defines U_1 - U_L
  N_terms
...
```

### Critical rules

1. **Block names are arbitrary** — "d-ul", "d and up", "s-d", "Mio_akiyama" — all work equally well
2. **Block ORDER is critical and cannot be wrong:**
   - First: U_L block (potential for l >= L)
   - Then: U_0 - U_L (s correction), U_1 - U_L (p correction), ..., U_{L-1} - U_L
   - Must be in ascending angular momentum order
3. First line after element name must end with `0`
4. The `-ECP` suffix is conventional but not required

### Understanding each field

**Element line:**
- `ZN     0` — defines pseudopotential for element Zn (by name)
- Can also use atom number to define for a specific atom only

**ECP header line:**
- `ZN-ECP` — name (arbitrary)
- `3` — L value (f and above use the same potential U_L)
- `18` — number of core electrons replaced by the pseudopotential

**Each term line:**
- `n` — power of r (0, 1, or 2)
- `ζ` — Gaussian exponent
- `d` — expansion coefficient

## Example: Zn Los Alamos ECP

```
ZN     0
ZN-ECP     3     18
f-ul potential
  5
1    386.7379660            -18.0000000
2     72.8587359           -124.3527403
2     15.9066170            -30.6601822
2      4.3502340            -10.6358989
2      1.2842199             -0.7683623
s-ul potential
  5
0     19.0867858              3.0000000
1      5.0231080             22.5234225
2      1.2701744             48.4465942
2      1.0671287            -44.5560119
2      0.9264190             12.9983958
p-ul potential
  5
0     43.4927750              5.0000000
1     20.8692669             20.7435589
2     21.7118378             90.3027158
2      6.3616915             74.6610316
2      1.2291195              9.8894424
d-ul potential
  3
2     13.5851800             -4.8490359
2      9.8373050              3.6913379
2      0.8373113             -0.5037319
```

**Breakdown:**
- L = 3 (f): f and above all feel U_L; s, p, d each have their own correction
- 18 core electrons replaced: Zn has 30 electrons; 18 replaced → 12 valence electrons (3d¹⁰ 4s²)
- U_L (f-ul): 5 terms, with n values 1, 2, 2, 2, 2
- U_0 - U_L (s-ul): 5 terms, corrections for s component
- U_1 - U_L (p-ul): 5 terms, corrections for p component
- U_2 - U_L (d-ul): 3 terms, corrections for d component

## Example: Pt Stuttgart ECP

```
PT     0
PT-ECP     5     60
h-ul potential
  1
2      1.000000000            0.000000000
s-ul potential
  2
2     13.428651000          579.223861000
2      6.714326000           29.669491000
p-ul potential
  2
2     10.365944000          280.860774000
2      5.182972000           26.745382000
d-ul potential
  2
2      7.600479000          120.396444000
2      3.800240000           15.810921000
f-ul potential
  1
2      3.309569000           24.314376000
g-ul potential
  1
2      5.277289000          -24.218675000
```

**Note:** The h-ul block has only 1 term with d=0. This means >=h components actually receive no pseudopotential — it's just a formality. This is because defining >=h pseudopotential has negligible effect on the atom's various configuration total valence electron energies, so Stuttgart didn't bother.

## Modifying pseudopotential definitions

### Case 1: Simplifying for single-atom calculation

For an isolated Pt atom, valence orbitals are described only by the atom's own s, p, d basis functions — no f or higher components. The ECP can be simplified:

```
PT     0
PT-ECP     3     60
f-ul potential
  0
s-ul potential
  2
2     13.428651000          579.223861000
2      6.714326000           29.669491000
p-ul potential
  2
2     10.365944000          280.860774000
2      5.182972000           26.745382000
d-ul potential
  2
2      7.600479000          120.396444000
2      3.800240000           15.810921000
```

Changes:
- L reduced from 5 to 3
- f-ul block: 0 terms (no potential for >= f)
- Removed g-ul and h-ul blocks
- Kept s, p, d corrections unchanged

**Result for single Pt atom:** Identical.
**Result for Pt-containing molecules:** Will differ — pseudo-orbitals are more complex than atomic orbitals and can project out >= f components. Removing these potentials affects the calculation.

### Case 2: Merging U_L into corrections

You can eliminate U_L (set it to 0 terms) and merge U_L terms directly into each correction block:

```
ZN     0
ZN-ECP     3     18
f-ul potential
  0
s-ul potential
  10
[5 terms from original U_L + 5 terms from original U_0-U_L]
p-ul potential
  10
[5 terms from original U_L + 5 terms from original U_1-U_L]
d-ul potential
  8
[5 terms from original U_L + 3 terms from original U_2-U_L]
```

**Result for single Zn atom:** Identical (s, p, d components feel the same total potential).
**Result for molecules:** Different — pseudo-orbitals have f and higher components that now feel no potential (original U_L was non-zero).

### Case 3: Truncating for program angular momentum limits

Some programs have maximum angular momentum limits in their integral code. For example, GAMESS-US supports basis functions only up to g. Stuttgart Hg has L=5 (h), which GAMESS-US cannot handle.

**Workaround:** Manually truncate the angular momentum definition:
- Keep only >= g, s, p, d, f definitions
- Set >= g part to receive no pseudopotential (0 terms)

**Warning:** This affects molecular calculations. Must note in publications that a truncated pseudopotential was used.

**Alternative:** Use a different pseudopotential with lower L. For Pt, Los Alamos and SBKJC have L=4 (one order lower than Stuttgart's L=5), so they work in GAMESS-US.

## Mixed basis sets with pseudopotentials in Gaussian

For a system with light atoms (all-electron) and heavy atoms (pseudopotential):

```
# B3LYP/gen opt

[molecular coordinates]

H C N O 0
6-31G*
****
Fe Cu Zn 0
Lanl2DZ
****

Fe Cu Zn 0
Lanl2DZ
```

The first section defines basis sets for light atoms. After `****`, the second section defines basis sets for heavy atoms. After another `****`, the ECP definitions for heavy atoms.

See sobereva.com/60 for detailed Gaussian mixed basis/ECP input format.

## Pseudopotential and wavefunction analysis

- **Must use small-core pseudopotentials** for wavefunction analysis
- Large-core pseudopotentials remove too many electrons
- See sobereva.com/156 for detailed discussion

## Pseudopotential and all-electron relativistic calculations

- **All-electron relativistic calculations** (DKH, ZORA, X2C) must use all-electron basis sets
- **NEVER use pseudopotentials with DKH or similar relativistic Hamiltonians** — the results are completely wrong
- Pseudopotentials already incorporate scalar relativistic effects — using them with DKH is redundant and incorrect
- **Exception:** If only considering spin-orbit coupling (not scalar relativistic effects), ordinary basis sets and pseudopotentials can be used normally

## References

- sobereva.com/188 — This article (pseudopotential function form and definition)
- sobereva.com/373 — Pseudopotential basis set selection guide
- sobereva.com/156 — Wavefunction analysis with pseudopotentials
- sobereva.com/60 — Gaussian mixed/custom/pseudopotential basis input
- sobereva.com/344 — Non-built-in methods/functionals in Gaussian
