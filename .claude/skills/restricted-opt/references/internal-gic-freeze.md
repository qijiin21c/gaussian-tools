# Internal Variable Freezing, GIC, and No-Gradient Optimization

Detailed guide for freezing internal coordinates, using GIC constraints, and optimizing at methods without analytic gradients, based on Sobereva's article (sobereva.com/404).

## Freezing internal variables in Z-matrix

### Using `opt=z-matrix`

When optimization must respect Z-matrix-defined constraints:

```
#p B3LYP/6-31G** opt=z-matrix

constraint optimization

0 1
 O
 H   1   B1
 H   1   B2   2  A1

B1=0.76533395
B2=0.76533395

A1=80.0
```

**Structure:**
- Coordinates section → Z-matrix with variables
- First blank line → section of variables TO BE OPTIMIZED
- Second blank line → section of variables TO BE FROZEN
- In this example: B1 and B2 are optimized; A1 is frozen at 80°

**Critical:** `opt=z-matrix` is **required**. Without it, Gaussian runs in redundant internal coordinates and Z-matrix freezes won't take effect.

### Numeric vs variable approach

Only variables are optimized; numeric values are implicitly frozen:

```
 O
 H   1   0.9
 H   1   0.9   2  A1

A1=80.0
```

- Bond lengths: numeric (0.9 Å) → **always frozen**
- Bond angle: variable (A1=80.0) → **optimized**
- No second section needed — the distinction is automatic

This approach is useful when you want a minimal constraint specification: simply don't define variables for the coordinates you want frozen.

## Freezing internal variables with `opt=modredundant`

### The most flexible approach

`opt=modredundant` (modify redundant internal coordinate) allows freezing ANY geometric parameter at the end of the input file, after a blank line:

```
# B3LYP/6-31G** opt=modredundant

Title

0 1
 O   0.00000000   0.00000000  -0.11081188
 H   0.00000000   0.58397589   0.44324751
 H   0.00000000  -0.58397589   0.44324751

2 3 F
```

This freezes the H-H distance.

### Freeze directive formats

| Format | Freezes |
|--------|---------|
| `atomno F` | Cartesian coordinates of atom `atomno` |
| `i j F` | Distance between atoms i and j |
| `i j k F` | Angle formed by atoms i-j-k |
| `i j k l F` | Dihedral angle formed by atoms i-j-k-l |

### Multiple simultaneous freezes

```
3 6 F           ! freeze distance 3-6
1 2 12 14 F     ! freeze dihedral 1-2-12-14
55 F            ! freeze atom 55 coordinates
58 F            ! freeze atom 58 coordinates
6 1 7 F         ! freeze angle 6-1-7
```

### Advantage over Cartesian freezing

With `opt=modredundant`:
- Can freeze ANY geometric parameter, not just whole atoms
- Defined variables don't need to exist in the input file's coordinate definition
- Can mix atom freezes with distance/angle/dihedral freezes
- Cartesian coordinates in the input file are fine — Gaussian internally converts to redundant internal coordinates

### Example: water molecule with fixed H-H distance

```
# B3LYP/6-31G** opt=modredundant

Title

0 1
 O   0.00000000   0.00000000  -0.11081188
 H   0.00000000   0.58397589   0.44324751
 H   0.00000000  -0.58397589   0.44324751

2 3 F
```

The H-H distance is frozen while O-H bonds and all angles are free to optimize.

## GIC (Generalized Internal Coordinate) constraints

Available in Gaussian 16+. Allows mathematical expressions as constraints, far more flexible than standard redundant internal coordinate freezes.

### GIC syntax basics

Add `opt=addGIC` to read GIC definitions after coordinates.

GIC supports:
- `R(i,j)` — distance between atoms i and j
- `A(i,j,k)` — angle i-j-k
- `D(i,j,k,l)` — dihedral i-j-k-l
- `XCntr(i-j)`, `YCntr(i-j)`, `ZCntr(i-j)` — geometric center X/Y/Z of atom range i through j
- Mathematical operators: +, -, *, /, ^, sqrt(), sin(), cos(), etc.
- `(freeze)` suffix — freeze the variable at its initial value
- `(inactive)` suffix — variable is not an optimization target, only used in constraint definitions

### Example 1: Constant difference between two O-H bond lengths

```
# B3LYP/6-31g(d) opt=addGIC

test

0 1
 O   0.00000000   0.04716583   0.07081661
 H   0.00000000   0.69230018  -0.40226021
 H   0.00000000  -0.69230018  -0.44220387

b12=R(1,2)
b13=R(1,3)
rcons(freeze)=b12-b13
```

**Effect:** The two O-H bond lengths maintain their initial difference (0.1 Å in this case) throughout optimization. Both bonds can change, but their difference is constant.

### Example 2: Fixed distance between fragment geometric centers

Ammonia-water dimer with constant center-to-center distance:

```
#p PM7 opt(gdiis,maxcyc=100,addgic)

Title

0 1
 N   -1.51786076   -1.12768292    2.39707540
 H   -1.11590788   -2.26462122    2.39707540
 H   -1.18452166   -0.65628274    3.21357213
 H   -1.18452166   -0.65628274    1.58057866
 O   -1.16213343   -0.15012738    6.00166916
 H   -0.20213343   -0.15012738    6.00166916
 H   -1.48258801    0.75480845    6.00166916

XC1=XCntr(1-4)
YC1=YCntr(1-4)
ZC1=ZCntr(1-4)
XC2=XCntr(5-7)
YC2=YCntr(5-7)
ZC2=ZCntr(5-7)
F1F2(freeze)=sqrt[(XC1-XC2)^2+(YC1-YC2)^2+(ZC1-ZC2)^2]*0.529177
```

**What this does:**
- Defines geometric center of NH₃ (atoms 1-4) as (XC1, YC1, ZC1)
- Defines geometric center of H₂O (atoms 5-7) as (XC2, YC2, ZC2)
- Computes Euclidean distance between centers
- Multiplies by 0.529177 to convert Bohr to Ångstrom
- Freezes this distance at its initial value

**Result:** Only monomer internal structures change during optimization; the center-to-center distance remains constant.

### GIC variables in output

GIC variable values are printed in the output file during optimization. Note that GIC defaults to atomic units (Bohr), so multiply by 0.529177 for Ångstrom output.

### GIC stability warning

- GIC with too many constraints or overly complex expressions often crashes mid-optimization
- G16 A.03 GIC code is known to be somewhat unstable
- Start with simple constraints and build up complexity gradually
- May improve in future Gaussian versions

## Optimization with methods that have no analytic gradients

### The problem

Methods like CCSD(T) in Gaussian lack analytic gradients. Geometry optimization must use the EF (Eigenvector Following) algorithm with finite-difference gradients.

**Consequences:**
- Each step requires multiple energy calculations (one per variable, via finite differences)
- Cost per step is proportional to the number of optimized variables
- **Program requires explicit variable definitions** — it cannot auto-determine what to optimize
- Maximum 50 variables

### Required syntax

```
#p CCSD(T)/def2TZVP opt nosymm

Title

0 1
O   0.00000000   0.00000000   0.11930801
H   0.00000000   0.75895306   Z2
H   0.00000000  -0.75895306   Z3

Z2=-0.43723204
Z3=-0.40723204
```

**Key points:**
- Only coordinates expressed as variables are optimized
- Numeric coordinates → treated as frozen
- Z-matrix or Cartesian with variables both work
- `nosymm` recommended for stability

### What happens without variables

If all coordinates are numeric (no variables defined):
```
ERROR IN INITNF. NUMBER OF VARIABLES (  0)
  INCORRECT (SHOULD BE BETWEEN 1 AND 50)
```

This error also reveals the **50-variable maximum** for EF optimization.

### Practical considerations

CCSD(T) optimization is extremely expensive:
- Each step requires N+1 CCSD(T) energy calculations (N = number of variables)
- For a 10-variable optimization: 11 CCSD(T) calculations per step
- Typically 20-50+ steps needed
- Use only for very small systems

**Alternative approach:**
1. Optimize at cheaper level (DFT, MP2)
2. Single-point CCSD(T) at optimized geometry

## Convergence tips for constrained optimization

When constrained optimization has convergence difficulties:

| Strategy | When to use |
|----------|-------------|
| `opt=gdiis` | Standard convergence acceleration |
| `opt=calcfc` | Compute force constants at first step |
| `opt=(gdiis,calcfc)` | Combined approach |
| `maxcyc=NNN` | Increase maximum cycles (default often insufficient for constrained cases) |
| `opt=loose` | Relax convergence criteria for rough exploration |
| `recalc=N` | Recompute Hessian every N steps |
| `opt=modredundant` | Switch to redundant internal coordinates (often better than Cartesian) |
| Reduce number of frozen atoms | Over-constraining can cause convergence failure |

See sobereva.com/164 for comprehensive optimization convergence help.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Using Z-matrix freezes without `opt=z-matrix` | Keyword is required |
| `opt=readopt` + `cartesian` | Incompatible — readopt always uses redundant internal coords |
| Expecting Z-matrix-style freezes in modredundant | modredundant uses atom-pair/triple/quadruple format, not variable names |
| Too many complex GIC constraints | G16 GIC crashes — simplify |
| CCSD(T) optimization without variables | Must define variables; EF needs explicit variable count |
| Freezing individual Cartesian components | Not supported in Gaussian — `-1` freezes all three |
| Numeric values in Z-matrix expecting them to be optimized | Only variables are optimized; numerics are frozen |

## References

- sobereva.com/404 — This article (restricted optimization)
- sobereva.com/164 — Helping geometry optimization converge
- sobereva.com/297 — Symmetry and nosymm keyword
- gaussian.com/opt — GIC Info page (official Gaussian documentation)
