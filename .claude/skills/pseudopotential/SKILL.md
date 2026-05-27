---
name: pseudopotential
description: This skill should be used when the user asks to "define pseudopotential", "ECP format", "赝势", "Lanl2DZ", "SDD", "Stuttgart pseudopotential", "custom ECP", "pseudopotential L value", "how to write ECP in Gaussian", "modify pseudopotential", "pseudo potential function form", "Los Alamos ECP", "赝势基组", "relativistic pseudopotential", or mentions pseudopotential definitions, effective core potentials, or custom ECP input in Gaussian.
version: 0.1.0
---

# Pseudopotential (ECP) Guide

Comprehensive guidance for understanding and defining pseudopotentials (effective core potentials, ECPs) in quantum chemistry programs, based on Sobereva's authoritative article (sobereva.com/188).

## When to use pseudopotentials

1. **Replace core electrons** with an effective potential — dramatically reduces computational cost
2. **Incorporate scalar relativistic effects** implicitly — essential for 5th period and beyond (不可忽视), recommended from 4th period onwards

## Pseudopotential types

| Type | Examples | Construction approach |
|------|----------|----------------------|
| **Shape-consistent** | Los Alamos (Lanl), SBKJC/CEP | Match pseudo-orbital shape to all-electron valence orbital (r > rc identical, r < rc smooth without nodes) |
| **Energy-consistent** | Stuttgart/Dresden (SDD) | Fit to hundreds/thousands of atomic/ionic state total valence electron energies |

**Important:** Do NOT mix pseudopotentials with basis sets not specifically optimized for them. Different pseudopotentials produce pseudo-orbitals with different radial shapes in the core region.

## Common pseudopotentials and their matched basis sets

| Pseudopotential | Matched basis sets |
|----------------|-------------------|
| **Los Alamos (Lanl)** | Lanl2DZ, Lanl2DZdp, Lanl08, LANL2TZ, LAV/LACV series |
| **Stuttgart/Dresden (SDD)** | SDD标配, (aug)-cc-pVnZ-PP series, def2 series for heavy elements |
| **SBKJC/CEP** | SBKJC, LFK (modified SBKJC for polarizability) |

## Pseudopotential function form

The pseudopotential is angular-momentum-dependent and spherically averaged:

```
U(r) = U_L(r) + Σ[l=0 to L-1] [U_l(r) - U_L(r)] × P_l
```

Where:
- **L** = highest angular momentum in core orbitals + 1
- **P_l** = angular momentum projection operator for quantum number l
- **U_L(r)** = potential applied to all angular momentum components >= L
- **U_l(r) - U_L(r)** = correction potential for angular momentum l < L

**Physical meaning:**
- All orbital components with l >= L feel the same U_L potential
- Components with l < L each feel their own U_l potential (U_L + correction)

### Why L is chosen this way

For l > t (t = highest angular momentum in core orbitals), the difference between U_l and U_{l+1} becomes negligible very quickly. So a cutoff L is chosen, and all l >= L components share U_L.

| System | Typical L | Example |
|--------|-----------|---------|
| 1st row transition metals | L=3 (f) | Cu: Lanl2DZ has max basis function d, but ECP defines >=f potential too |
| 3rd row transition metals | L=4-5 (g-h) | Hg: Stuttgart ECP L=5 (h) |

**Note:** The pseudopotential's L is independent of the basis set's highest angular momentum. L is typically >= basis set max angular momentum + 1. This is because in molecules, pseudo-orbitals are complex and projection operators can extract components with l >= basis set max.

### Gaussian expansion form

Pseudopotentials are fitted to polynomial × Gaussian products:

```
r² × U(r) = Σ[k] d_k × r^(n_k) × exp(-ζ_k × r²)
```

Equivalently:

```
U(r) = Σ[k] d_k × r^(n_k - 2) × exp(-ζ_k × r²)
```

Where n_k can be 0, 1, or 2; d_k is the expansion coefficient; ζ_k is the Gaussian exponent.

## Gaussian ECP definition format

### Structure

```
ElementName    0                    // Element name (or atom number). 0 is required.
Name-ECP    L    core_electrons     // ECP name; L value; number of core electrons
L-ul potential                      // Block for U_L (l >= L potential)
  N_terms                           // Number of expansion terms
n_1    ζ_1    d_1                   // Each term: n, ζ, d
n_2    ζ_2    d_2
...
s-ul potential                      // Block for U_0 - U_L (s correction)
  N_terms
n_1    ζ_1    d_1
...
p-ul potential                      // Block for U_1 - U_L (p correction)
  N_terms
...
```

**Critical rules:**
1. Block names can be anything (e.g., "d-ul", "Mio_akiyama" — doesn't matter)
2. **Block ORDER cannot be wrong:** First U_L (l >= L), then U_0 - U_L (s), U_1 - U_L (p), ..., U_{L-1} - U_L, in ascending angular momentum order
3. The first line after element name must have `0`
4. The `-ECP` suffix in the name is conventional but not required

### Example: Zn Los Alamos ECP

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

## Modifying pseudopotential definitions

### Truncating angular momentum (for program limitations)

Some programs have maximum angular momentum limits for integral code (e.g., GAMESS-US only supports up to g). If a pseudopotential's L exceeds this (e.g., Stuttgart Hg with L=5/h), you must truncate:

1. Reduce L to the program's limit
2. Set the >= new_L block to have 0 terms (no potential)
3. Keep corrections for s, p, d, ... up to new_L - 1

**Warning:** This affects molecular calculations (pseudo-orbitals can project out >= truncated_l components) but has no effect on single-atom calculations. Note this modification in publications.

### Simplifying for single-atom calculations

For isolated atom calculations, pseudo-orbitals only have components up to the basis set's max angular momentum. Higher-L components can be safely removed.

### Combining U_L with corrections

You can merge U_L terms directly into each U_l block and set U_L to 0 terms:
- For single atoms: results are identical
- For molecules: results will differ because pseudo-orbitals have >= L components that now feel no potential (original U_L was non-zero)

## Practical usage in Gaussian

### Using built-in pseudopotentials

```
# B3LYP/Lanl2DZ opt freq
```

### Using mixed basis sets (light atoms: all-electron; heavy atoms: pseudopotential)

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

See sobereva.com/60 for detailed Gaussian mixed basis/ECP input format.

## Pseudopotential and wavefunction analysis

- Must use **small-core pseudopotentials** for wavefunction analysis
- Large-core pseudopotentials remove too many electrons, making analysis unreliable
- See sobereva.com/156 for detailed discussion

## Pseudopotential and relativistic calculations

- **All-electron relativistic calculations** (DKH, ZORA, X2C) must use all-electron basis sets — NEVER pseudopotentials
- Pseudopotentials already incorporate scalar relativistic effects — using them with DKH is completely wrong
- **Exception:** If only considering spin-orbit coupling (not scalar relativistic effects), ordinary basis sets and pseudopotentials can be used normally

## Key references

- sobereva.com/188 — This article (pseudopotential function form and definition)
- sobereva.com/373 — Pseudopotential basis set selection guide
- sobereva.com/156 — Wavefunction analysis with pseudopotentials
- sobereva.com/60 — Gaussian mixed/custom/pseudopotential basis input
- sobereva.com/344 — Non-built-in methods/functionals in Gaussian (includes custom ECP)
