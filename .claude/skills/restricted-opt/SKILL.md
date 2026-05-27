---
name: restricted-opt
description: This skill should be used when the user asks to "restricted optimization", "限制性优化", "freeze atoms", "frozen optimization", "constraint optimization", "冻结原子", "冻结坐标", "opt=cartesian freeze", "opt=modredundant freeze", "opt=readopt", "opt=z-matrix freeze", "opt=addGIC", "GIC freeze", "frozen surface adsorption", "enzyme cluster optimization", "X-ray hydrogen optimization", "geometric center constraint", "distance constraint optimization", "bond length constraint", or mentions freezing geometric variables during geometry optimization in Gaussian.
version: 0.1.0
---

# Restricted (Constrained) Optimization in Gaussian

Guide to freezing atoms, coordinates, and internal variables during geometry optimization in Gaussian, based on Sobereva's article (sobereva.com/404).

**Core concept:** A restricted (constrained) optimization freezes selected geometric variables while optimizing the rest. The result is a **subspace minimum**, not a global minimum — imaginary frequencies in subsequent frequency calculations are normal and expected.

**Pre-check: When NOT to freeze blindly**
- Freezing arbitrary coordinates can cause convergence failures or unphysical results
- Always have a clear purpose before freezing
- Restricted optimization does NOT reduce computational cost per step (all gradients still computed — frozen ones are just not used for geometry update or convergence judgment)

## Quick reference: Freezing method by purpose

| Goal | Method | Syntax |
|------|--------|--------|
| Freeze atom Cartesian coordinates | `opt=cartesian` + `-1` flag | `H  -1  x y z` |
| Freeze by element/atom number | `opt=readopt` | `notatoms=C,O` |
| Freeze atom coordinates in redundant internal coords | `opt=modredundant` | `atomno F` |
| Freeze internal variable (Z-matrix) | `opt=z-matrix` | Put frozen vars in separate section |
| Freeze any distance/angle/dihedral | `opt=modredundant` | `i j F` or `i j k F` or `i j k l F` |
| Complex constraints (distances between centers, difference constraints) | `opt=addGIC` | GIC expressions |
| No-analytic-gradient methods (CCSD(T)) | Z-matrix with variables | Only variables are optimized |

## Method 1: Cartesian coordinate freezing (0/-1 flags)

```
# B3LYP/6-31G** opt=cartesian

Title

0 1
 O   0   0.00000000   0.00000000  -0.11081188
 H  -1   0.00000000   0.58397589   0.44324751
 H  -1   0.00000000  -0.58397589   0.44324751
```

- `0` = free to optimize
- `-1` = frozen
- Always use `opt=cartesian` with this method — without it, Gaussian uses redundant internal coordinates and takes many more steps
- Cannot freeze individual Cartesian components (x, y, or z only) — freezes the entire atom
- **Add `nosymm`** to see frozen atoms truly stationary in the trajectory (otherwise Gaussian reorients the molecule)

### GaussView shortcut for large systems
1. Select atoms to freeze (they turn yellow)
2. Tools → Atom Groups → Freeze category → Add selected to freeze group
3. Save → frozen atoms get `-1`, free atoms get `0`

### Common use cases
- **X-ray structures:** Freeze heavy atoms, optimize hydrogens
- **Surface adsorption:** Freeze bottom layer(s) of slab, optimize adsorbate + surface layers
- **Enzyme clusters:** Freeze backbone atoms of boundary residues

## Method 2: `opt=readopt` (element/atom number filtering)

```
# PM6 opt=readopt

Title

0 1
 C   0.00000000   0.00000000  -0.56221066
 H   0.00000000  -0.92444767  -1.10110537
 H  -0.00000000   0.92444767  -1.10110537
 O   0.00000000   0.00000000   0.69618930

notatoms=C,O
```

- Optimizes all atoms EXCEPT those specified
- Can mix element names and atom numbers: `notatoms=C,4` or `notatoms=1,4`
- **GaussView shortcut:** Select region → Tools → Atom Selection → copy atom numbers → paste into `notatoms=`

### Advanced `readopt` commands
| Command | Effect |
|---------|--------|
| `noatoms` | Clear the optimization list (nothing optimized) |
| `atoms=1,5-70` | Add atoms 1,5-70 to optimization list |
| `notatoms=N,O` | Remove N and O elements from optimization list |

**Combination example:** `noatoms atoms=1,5-70 notatoms=N,O` → clear list, add atoms 1,5-70, remove N/O from those → optimize only non-N/O atoms in range 1,5-70.

**Note:** `opt=readopt` always runs in redundant internal coordinates. Cannot use `cartesian` with it — will error at start.

## Method 3: `opt=modredundant` (redundant internal coordinate freezing)

```
# B3LYP/6-31G** opt=modredundant

Title

0 1
 O   0.00000000   0.00000000  -0.11081188
 H   0.00000000   0.58397589   0.44324751
 H   0.00000000  -0.58397589   0.44324751

2 F
3 F
```

After a blank line following coordinates, add freeze directives:

| Format | Freezes |
|--------|---------|
| `atomno F` | Cartesian coordinates of atom |
| `i j F` | Distance between atoms i and j |
| `i j k F` | Angle i-j-k |
| `i j k l F` | Dihedral i-j-k-l |

Can add unlimited freeze lines. Multiple types can be mixed:

```
3 6 F         ! freeze distance 3-6
1 2 12 14 F   ! freeze dihedral 1-2-12-14
55 F          ! freeze atom 55
6 1 7 F       ! freeze angle 6-1-7
```

**Advantage over Cartesian freezing:** Can freeze ANY geometric parameter, not just whole atoms. Defined variables don't need to exist in the input file's coordinate definition.

## Method 4: `opt=z-matrix` (Z-matrix internal variable freezing)

### Variable-based approach
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

- Blank line after variables → section of variables TO BE OPTIMIZED
- Second blank line → section of variables TO BE FROZEN
- `opt=z-matrix` is **required** — otherwise optimization runs in redundant internal coordinates and Z-matrix freezes won't take effect

### Numeric vs variable approach
```
 O
 H   1   0.9
 H   1   0.9   2  A1

A1=80.0
```

- Numeric values → always frozen
- Variable names → optimized
- In this example: bond lengths fixed at 0.9 Å, bond angle optimized

## Method 5: GIC (Generalized Internal Coordinate) constraints

Gaussian 16+ feature. Most flexible constraint system — can define mathematical expressions as constraints.

### Example 1: Constant difference between two bond lengths
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

Two O-H bonds maintain their initial difference (0.1 Å) throughout optimization.

### Example 2: Fixed distance between fragment geometric centers
```
#p PM7 opt(gdiis,maxcyc=100,addgic)

Title

0 1
[coordinates]

XC1=XCntr(1-4)
YC1=YCntr(1-4)
ZC1=ZCntr(1-4)
XC2=XCntr(5-7)
YC2=YCntr(5-7)
ZC2=ZCntr(5-7)
F1F2(freeze)=sqrt[(XC1-XC2)^2+(YC1-YC2)^2+(ZC1-ZC2)^2]*0.529177
```

- `XCntr`, `YCntr`, `ZCntr`: geometric center of specified atom range
- `0.529177`: Bohr-to-Ångstrom conversion
- Only monomer internal structures change; center-to-center distance is constant

**Warning:** GIC can be unstable with complex or numerous constraints — may crash mid-optimization.

## Method 6: No-analytic-gradient methods (CCSD(T), etc.)

Methods without analytic gradients (CCSD(T) in Gaussian) use EF algorithm via finite-difference gradients. The program **requires** explicit variable definitions and has a **50-variable maximum**.

```
#p CCSD(T)/def2TZVP opt nosymm

Title

0 1
O  0.00000000   0.00000000   0.11930801
H  0.00000000   0.75895306   Z2
H  0.00000000  -0.75895306   Z3

Z2=-0.43723204
Z3=-0.40723204
```

- Only coordinates expressed as variables are optimized
- If ALL coordinates are numeric (no variables): ERROR "NUMBER OF VARIABLES (0) INCORRECT"
- Maximum 50 variables
- Cartesian coordinates with numeric values → treated as frozen

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Forgetting `opt=cartesian` with -1/0 flags | Gaussian defaults to redundant internal coords → slow convergence |
| Expecting no imaginary frequencies after frozen optimization | Subspace minimum → imaginary frequencies are normal |
| Freezing without a clear purpose | Results may be unphysical or hard to converge |
| Using `opt=z-matrix` freeze without `opt=z-matrix` keyword | Keyword is required; otherwise runs in redundant internal coords |
| CCSD(T) optimization with all-numeric coordinates | Must use variables; EF needs explicit variable count |
| Too many/complex GIC constraints | G16 GIC code is unstable — simplify constraints |
| Trying to freeze only one Cartesian component (e.g., just Z) | Not supported — `-1` freezes all three components |

## Additional Resources

- **`references/cartesian-freeze.md`** — Detailed Cartesian freezing: X-ray structure H-optimization, surface adsorption slab models, enzyme cluster boundary freezing, GaussView Atom Groups workflow
- **`references/internal-gic-freeze.md`** — Internal variable freezing (Z-matrix, modredundant), GIC constraints (difference constraints, geometric center distances), no-analytic-gradient optimization (CCSD(T) EF algorithm), convergence tips for constrained optimization
