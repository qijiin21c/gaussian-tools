---
name: cartesian-to-internal
description: This skill should be used when the user asks to "convert Cartesian to internal coordinates", "直角坐标转内坐标", "build Z-matrix", "Z-矩阵", "internal coordinate symmetry", "内坐标对称性", "maintain symmetry in Gaussian", "保持对称性 内坐标", "Z-matrix benzene", "Z-matrix dummy atom", "dummy atom X Gaussian", "Opt=Z-Matrix", "ModRedundant freeze Z-matrix", "symmetry-constrained optimization", "对称性约束优化", or mentions converting Cartesian coordinates to Z-matrix/internal coordinates in Gaussian while preserving or enforcing molecular symmetry.
version: 0.2.0
---

# Cartesian to Internal Coordinate Conversion with Symmetry

Convert Cartesian coordinates to Z-matrix (internal coordinates) in Gaussian, with symmetry detection and preservation. Z-matrix with shared symbolic variables is the most reliable way to enforce molecular symmetry during optimization in Gaussian.

## Core concept: Why Z-matrix for symmetry

Gaussian does NOT maintain point-group symmetry by default during geometry optimization. Even if Gaussian detects high symmetry at the starting geometry, tiny numerical noise (floating-point precision, SCF convergence thresholds, DFT integration grids) breaks symmetry as optimization proceeds.

**Z-matrix enforces symmetry mathematically:** all symmetry-equivalent bond lengths/angles/dihedrals share the same symbolic variable. During optimization, only independent variables change — symmetry is guaranteed because all equivalent parameters change together.

## Automated symmetry detection with libmsym

The `libmsym` Python library is installed and can automatically detect molecular point group symmetry from Cartesian coordinates.

**Usage:**

```bash
# From command line with explicit atoms
python scripts/detect_symmetry.py --atoms "C,0,0,0 H,1,0,0 H,0,1,0 H,0,0,1"

# From a .gjf file
python scripts/detect_symmetry.py --gjf jobs/molecule.gjf

# From XYZ file
python scripts/detect_symmetry.py molecule.xyz

# Tight/loose tolerance
python scripts/detect_symmetry.py --tight molecule.xyz   # threshold 1e-5
python scripts/detect_symmetry.py --loose molecule.xyz   # threshold 1e-2
```

**Example output:**
```
Analyzing 12 atoms...
Point group: D6h
Order: 24
Symmetry operations:
  C2: 7
  C3: 2
  C6: 2
  E: 1
  S3: 2
  S6: 2
  i: 1
  sigma_d: 3
  sigma_h: 1
  sigma_v: 3
```

**In Python:**
```python
from scripts.detect_symmetry import detect_symmetry, format_symmetry

atoms = [('C', 0.0, 0.0, 0.0), ('H', 1.0, 1.0, 0.0), ...]
ctx = detect_symmetry(atoms, threshold=1e-3)
print(format_symmetry(ctx))
```

**Threshold guide:**
- `--tight` (1e-5): Only very precise symmetry is detected. Use for optimized structures.
- Default (1e-3): Standard tolerance. Works for most cases.
- `--loose` (1e-2): Detects approximate symmetry. Use for experimental or rough coordinates.

## Pre-check: Do you need Z-matrix?

| Your goal | Use |
|-----------|-----|
| Quick optimization, symmetry not critical | Default `Opt` (redundant internal coords) |
| Enforce specific symmetry | `Opt=Z-Matrix` with shared variables |
| Freeze specific coordinates | `Opt=ModRedundant` (Cartesian or Z-matrix input) |
| PES scan along one coordinate | `Opt=ModRedundant` with scan spec |
| Symmetric ring/cage molecule | `Opt=Z-Matrix` or `Opt=(Z-Matrix,CalcFC)` |
| Optimization with Cartesian input fails | Switch to `Opt=Z-Matrix` or `Opt=Cartesian` |

## Symmetry detection from Cartesian coordinates

Before building a Z-matrix, examine the Cartesian coordinates to identify the molecule's approximate point group:

### Quick symmetry identification checklist

1. **C1** — No symmetry elements (asymmetric molecule)
2. **Cs** — One mirror plane (e.g., formamide, planar molecules with unequal sides)
3. **Ci** — Center of inversion only (e.g., staggered ethane with equal substituents)
4. **Cn** — Single n-fold rotation axis
5. **Cnv** — n-fold rotation axis + n vertical mirror planes (e.g., H2O = C2v, NH3 = C3v, benzene planar = D6h but monosubstituted = C2v)
6. **Cnh** — n-fold rotation axis + horizontal mirror plane
7. **Dn** — n-fold principal axis + n perpendicular 2-fold axes
8. **Dnh** — Dn + horizontal mirror plane (e.g., ethylene = D2h, benzene = D6h, CO2 = D∞h)
9. **Dnd** — Dn + diagonal mirror planes (e.g., allene = D2d, staggered ethane = D3d)
10. **Td** — Tetrahedral (e.g., CH4, CCl4)
11. **Oh** — Octahedral (e.g., SF6)
12. **Ih** — Icosahedral (e.g., C60)

### Practical approach

1. Look at the Cartesian coordinates
2. Identify symmetry elements: rotation axes, mirror planes, inversion center
3. Determine point group
4. Build Z-matrix that encodes this symmetry through variable sharing

## Z-matrix variable sharing for symmetry

The key principle: **symmetry-equivalent geometric parameters must share the same variable name**.

| Symmetry operation | How to encode in Z-matrix |
|-------------------|--------------------------|
| Equivalent bonds | Same R variable (e.g., `RCC` for all C-C bonds) |
| Equivalent angles | Same A variable (e.g., `ACC` for all angles) |
| Symmetric dihedrals | `D` and `-D` for atoms related by mirror plane |
| Rotation symmetry | Same angle step (e.g., all 120° for C3) |

## Dummy atoms for symmetry construction

Dummy atoms (symbol `X`, atomic number 0) have no basis functions and don't contribute to energy — they exist purely as geometric reference points.

### When to use dummy atoms

| Situation | Dummy atom solution |
|-----------|-------------------|
| Linear atom sequence (180° bond angle) | Place dummy atom off-axis at 90° |
| Center of symmetric ring | Place dummy atom at ring center |
| Multiple rotation axes | Use multiple dummy atoms at intersection |
| Tetrahedral center | Use dummy atom to define tetrahedral angle reference |

### Dummy atom rules

- Symbol: `X` (or `Bq` for ghost atom)
- Bond length to dummy: arbitrary (typically 1.0 Å)
- Angle to dummy: typically 90° to place it off-axis
- Dihedral involving dummy: defines the symmetry plane/axis

## Standard Z-matrix templates for common symmetric molecules

### Water (H2O) — C2v

```
O
H 1 ROH
H 1 ROH 2 AHOH

ROH=0.96
AHOH=104.5
```

Key: both O-H bonds share `ROH`, ensuring C2 symmetry.

### Ammonia (NH3) — C3v

```
H
N 1 RNH
H 2 RNH 1 HNH
H 2 RNH 1 HNH 3 120.0
H 2 RNH 1 HNH 3 120.0 4 180.0

RNH=1.01
HNH=107.0
```

Key: H at origin, N at RNH distance. The other three H atoms are defined relative to N (atom 2) with H-N-H angle=107°. Dihedral steps of 120° enforce C3v symmetry, with 180° placing the last H on the opposite side.

### Methane (CH4) — Td

```
H
C 1 RCH
H 2 RCH 1 AHCH
H 2 RCH 1 AHCH 3 DA
H 2 RCH 1 AHCH 4 DA

RCH=1.087
AHCH=109.5
DA=120.0
```

Key: H at origin, C placed at RCH distance. The other three H atoms are defined relative to C (atom 2) with the tetrahedral angle AHCH=109.5°. The last two H atoms use dihedral DA=120° to place them at the correct tetrahedral positions.

### Ethylene (C2H4) — D2h

```
C1
C2 1 RCC
H3 1 RCH 2 AHCC
H4 1 RCH 2 AHCC 3 180.0
H5 2 RCH 1 AHCC 3 0.0
H6 2 RCH 1 AHCC 4 0.0

RCC=1.34
RCH=1.09
AHCC=121.5
```

Key: symmetry encoded through shared `RCH` and `AHCC`. Dihedrals at 0° and 180° place H atoms in the molecular plane.

### Benzene (C6H6) — D6h (with dummy atom at ring center)

```
X1
X2 1 1.0
C3 1 RCC 2 90.0
C4 1 RCC 2 90.0 3 60.0
C5 1 RCC 2 90.0 4 60.0
C6 1 RCC 2 90.0 5 60.0
C7 1 RCC 2 90.0 6 60.0
C8 1 RCC 2 90.0 7 60.0
H9  3 RCH 1 180.0 2 90.0
H10 4 RCH 1 180.0 3 90.0
H11 5 RCH 1 180.0 4 90.0
H12 6 RCH 1 180.0 5 90.0
H13 7 RCH 1 180.0 6 90.0
H14 8 RCH 1 180.0 7 90.0

RCC=1.39
RCH=1.08
```

Key: dummy atom X1 at ring center, X2 along the C6 axis. All carbons at same `RCC` from center, 60° apart. **All H atoms use X1 (atom 1, ring center) as angle reference with angle=180°** — this places each H on the radial extension of C→center, pointing outward. Angle reference is NOT X2 (that would give wrong position).

### Acetylene (C2H2) — D∞h

```
H1
C2 1 RCH
C3 2 RCC 1 180.0
H4 3 RCH 2 180.0

RCC=1.20
RCH=1.06
```

Key: simple linear chain H-C-C-H. The two H-C-C angles are 180°, which is allowed for newer Gaussian versions. If you get a "Linear angle" error, use the dummy atom approach with two dummies placed off-axis.

### CO2 (linear) — D∞h (with dummy atom)

```
C
X 1 1.0
O1 1 RCO 2 90.0
O2 1 RCO 2 90.0 3 180.0

RCO=1.16
```

Key: dummy atom X is placed first (along Z axis from C). Both O atoms use X as angle reference with angle=90° (NOT 180° — old Gaussian rejects linear angles). The two O atoms are distinguished by dihedral: O2-C-X-O1 = 180° places O2 on the opposite side of C from O1. All bond angles are 90°, avoiding the forbidden 180° angle issue.

### Water dimer ((H2O)2) — Cs

```
O1
H2 1 ROH1
H3 1 ROH1 2 AHOH1
O4 1 ROO 3 AOOH 2 D1
H5 4 ROH2 1 AOOH2 3 D2
H6 4 ROH2 1 AHOH2 2 -D2

ROH1=0.96
AHOH1=104.5
ROO=2.98
AOOH=120.0
ROH2=0.96
AHOH2=104.5
D1=180.0
D2=0.0
```

Key: the two monomers have different variables (donor vs. acceptor are NOT symmetry-equivalent). Within each monomer, equivalent bonds share variables.

## Complete Gaussian input example

### Optimization with symmetry enforcement

```
%chk=benzene_opt.chk
# B3LYP/6-31G* Opt=Z-Matrix

Benzene optimization with D6h symmetry enforced via Z-matrix

0 1
X1
X2 1 1.0
C3 1 RCC 2 90.0
C4 1 RCC 2 90.0 3 60.0
C5 1 RCC 2 90.0 4 60.0
C6 1 RCC 2 90.0 5 60.0
C7 1 RCC 2 90.0 6 60.0
C8 1 RCC 2 90.0 7 60.0
H9  3 RCH 1 180.0 2 90.0
H10 4 RCH 1 180.0 3 90.0
H11 5 RCH 1 180.0 4 90.0
H12 6 RCH 1 180.0 5 90.0
H13 7 RCH 1 180.0 6 90.0
H14 8 RCH 1 180.0 7 90.0

RCC 1.39
RCH 1.08
```

### Optimization with initial force constant calculation

For complex symmetric molecules, compute initial Hessian to guide optimization:

```
# B3LYP/6-31G* Opt=(Z-Matrix,CalcFC)
```

## User-requested symmetry enforcement

When the user specifies that a particular group of atoms should maintain a certain symmetry, construct the Z-matrix as follows:

### Workflow

1. Identify the atoms in the group and the target symmetry
2. Determine the symmetry elements (rotation axis, mirror plane, etc.)
3. Build the Z-matrix with:
   - Shared variables for all symmetry-equivalent parameters
   - Appropriate dihedral values (D and -D for mirror pairs)
   - Dummy atoms if needed for linear sequences or rotation axes
4. Use `Opt=Z-Matrix` in the route section
5. Optionally add `Symm=(Follow,PG=group)` to help Gaussian recognize the symmetry

### Example: User requests "the phenyl ring (atoms 1-6) should maintain C2v symmetry"

Construct Z-matrix where:
- C1-C2 and C1-C6 share the same bond length variable
- C3-C4 and C5-C4 share the same bond length variable
- Corresponding angles are shared
- Mirror plane defined by C1-C4 axis, with dihedrals as D and -D

## Common mistakes and fixes

| Mistake | Error | Fix |
|---------|-------|-----|
| Not sharing variables for equivalent parameters | Symmetry breaks during optimization | Use same variable name for all equivalent bonds/angles |
| 180° bond angle without dummy atom | "Bend failed" / "Linear angle" error | Add dummy atom at 90° off the linear axis |
| Referencing undefined atoms | Parse error | Each atom must reference only previously defined atoms |
| Missing blank line before variables | Gaussian misinterprets input | Always include blank line between geometry and variables |
| Using `Opt=ModRedundant` freeze with Z-matrix but no `Opt=Z-Matrix` | Freezes are ignored | Add `Opt=Z-Matrix` to route section |
| DFT grid noise breaking symmetry | Tiny imaginary frequencies after opt | Use `Int=UltraFine` with tight optimization |
| Over-constrained system | "NVar < NDOF" error | Reduce fixed variables; need NVar = 3N-6 (or 3N-5 for linear) |

## Z-matrix structure validation

Before outputting a Z-matrix, verify each atom has the correct number of parameters:

| Atom # | Required parameters | Format |
|--------|--------------------|--------|
| 1 | None | `Atom1` |
| 2 | Bond length only | `Atom2 1 R` |
| 3 | Bond length + angle | `Atom3 2 R 1 A` |
| 4+ | Bond length + angle + dihedral | `Atom4 3 R 2 A 1 D` |

This is a hard constraint: the Nth atom can reference at most N-1 previously defined atoms, so it can have at most 3 internal coordinates (R, A, D). A Z-matrix that gives a dihedral to atom 2 or 3, or omits a dihedral from atom 4+, is invalid and will be rejected by Gaussian.

## Converting existing Cartesian coordinates

When given Cartesian coordinates and asked to convert to internal coordinates:

1. **Manual conversion:** Identify bonds, angles, and dihedrals from Cartesian positions, then build Z-matrix with variable sharing for symmetry-equivalent parameters
2. **Gaussian `newzmat` utility:** `newzmat -icart -rebuildzmat input.gjf output.zmat` — converts Cartesian to Z-matrix format
3. **GaussView:** Open the .gjf file, then Save — in the dialog, uncheck "Write Cartesians" to output Z-matrix format
4. **Multiwfn:** Can convert between coordinate formats (sobereva.com/490)

After automatic conversion, manually review and consolidate variables to enforce the desired symmetry.

## Additional resources

- **`references/zmatrix-examples.md`** — Comprehensive Z-matrix examples for 20+ symmetric molecules, dummy atom patterns, linear molecule handling, ring systems, multi-group symmetry
- **`references/symmetry-detection.md`** — Detailed symmetry identification guide, point group determination flowchart, Gaussian symmetry keyword options (Symm=Loose/Tight/Follow, PG=, NoSymm), symmetry-breaking causes and fixes
