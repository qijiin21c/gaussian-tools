# Z-Matrix Examples for Symmetric Molecules

Comprehensive Z-matrix examples for common symmetric molecules, dummy atom patterns, and complex multi-group symmetry cases.

## Linear molecules

Linear molecules require dummy atoms. **Old Gaussian rejects 180° bond angles**, so all angles must be 90° (or other non-180° values), with atoms on opposite sides distinguished by dihedral angles.

### CO2 — D∞h

```
C
X 1 1.0
O1 1 RCO 2 90.0
O2 1 RCO 2 90.0 3 180.0

RCO=1.16
```

Dummy atom X is placed first (along Z axis). Both O atoms use X as angle reference with angle=90° (NOT 180°). The two O atoms are distinguished by dihedral: O2-C-X-O1 = 180° places O2 on the opposite side.

### HCN — C∞v

```
C
X 1 1.0
H 1 RCH 2 90.0
N 1 RCN 2 90.0 3 180.0

RCH=1.06
RCN=1.16
```

C at origin, X dummy along Z. H and N both at 90° to X, distinguished by dihedral 180°.

### Acetylene (C2H2) — D∞h

```
C1
C2 1 RCC
X3 1 1.0 2 90.0
H4 1 RCH 2 90.0 3 0.0
H5 2 RCH 1 90.0 3 180.0

RCC=1.20
RCH=1.06
```

C1 at origin, C2 along Z axis. Dummy X3 placed at 90° to define the reference plane. H4 on C1 at 90° with dihedral 0°; H5 on C2 at 90° with dihedral 180° (opposite side). Both H-C-C angles are 180° by construction (the 90° angle is with respect to the dummy X3, not the C-C axis).

### N2O — C∞v

```
N2
X1 1 1.0
N1 1 RNN 2 90.0
O 1 RNO 2 90.0 3 180.0

RNN=1.13
RNO=1.19
```

N2 (central N) at origin, X1 dummy along Z. N1 and O both at 90° to X1, distinguished by dihedral 180°.

## Trigonal planar molecules

### Boron trifluoride (BF3) — D3h

```
B
F 1 RBF
F 1 RBF 2 120.0
F 1 RBF 2 120.0 3 180.0

RBF=1.30
```

All three B-F bonds share `RBF`. The 120° step and 180° dihedral enforce D3h symmetry.

### Formaldehyde (H2CO) — C2v

```
C
O 1 RCO
H 1 RCH 2 AHCO
H 1 RCH 2 AHCO 3 180.0

RCO=1.21
RCH=1.11
AHCO=121.8
```

The two C-H bonds share `RCH`, and the 180° dihedral places them symmetrically about the C=O axis.

## Tetrahedral molecules

### Methane (CH4) — Td

```
C
H 1 R
H 1 R 2 TDA
H 1 R 2 TDA 3 D120
H 1 R 2 TDA 4 -D120

R=1.085
TDA=109.47
D120=120.0
```

The tetrahedral angle TDA = arccos(-1/3) = 109.47°. The last H uses `-D120` to place it on the opposite side of the symmetry plane defined by C, H2, and H3.

### Carbon tetrachloride (CCl4) — Td

```
C
Cl 1 R
Cl 1 R 2 TDA
Cl 1 R 2 TDA 3 D120
Cl 1 R 2 TDA 4 -D120

R=1.77
TDA=109.47
D120=120.0
```

### Ammonium ion (NH4+) — Td

```
N
H 1 R
H 1 R 2 TDA
H 1 R 2 TDA 3 D120
H 1 R 2 TDA 4 -D120

R=1.03
TDA=109.47
D120=120.0
```

## Pyramidal molecules

### Ammonia (NH3) — C3v

With dummy atom on C3 axis:
```
N X 1 1.0
H 2 NH 1 HNX
H 2 NH 1 HNX 3 120.0
H 2 NH 1 HNX 3 120.0 4 180.0

NH=1.01
HNX=107.0
```

Without dummy atom (using H-N-H angle directly):
```
N
H 1 NH
H 1 NH 2 HNH
H 1 NH 2 HNH 3 120.0

NH=1.01
HNH=107.0
```

Note: The version without dummy atom may have convergence issues if the HNH angle approaches problematic values during optimization.

### Phosphine (PH3) — C3v

```
P X 1 1.0
H 2 PH 1 HPX
H 2 PH 1 HPX 3 120.0
H 2 PH 1 HPX 3 120.0 4 180.0

PH=1.42
HPX=93.5
```

## Octahedral molecules

### Sulfur hexafluoride (SF6) — Oh

```
S
X1 1 1.0
X2 1 1.0 2 90.0
F 1 RSF 2 90.0 3 0.0
F 1 RSF 2 90.0 3 180.0
F 1 RSF 2 90.0 4 90.0
F 1 RSF 2 90.0 4 270.0
F 1 RSF 2 0.0
F 1 RSF 2 180.0

RSF=1.56
```

Two dummy atoms (X1, X2) define the coordinate axes. Six F atoms placed at equal distance along ±X, ±Y, ±Z.

## Planar ring systems

### Cyclopropane (C3H6) — D3h

```
X1
X2 1 1.0
C3 1 RCC 2 90.0
C4 1 RCC 2 90.0 3 120.0
C5 1 RCC 2 90.0 4 120.0
H6 3 RCH 2 ACH 4 180.0
H7 3 RCH 2 ACH2 5 0.0
H8 4 RCH 3 ACH 6 180.0
H9 4 RCH 3 ACH2 5 0.0
H10 5 RCH 4 ACH 8 180.0
H11 5 RCH 4 ACH2 3 0.0

RCC=1.51
RCH=1.08
ACH=115.0
ACH2=115.0
```

### Cyclopentadienyl anion (C5H5-) — D5h

```
X1
X2 1 1.0
C3 1 RCC 2 90.0
C4 1 RCC 2 90.0 3 72.0
C5 1 RCC 2 90.0 4 72.0
C6 1 RCC 2 90.0 5 72.0
C7 1 RCC 2 90.0 6 72.0
H8  3 RCH 1 180.0 2 0.0
H9  4 RCH 1 180.0 3 0.0
H10 5 RCH 1 180.0 4 0.0
H11 6 RCH 1 180.0 5 0.0
H12 7 RCH 1 180.0 6 0.0

RCC=1.42
RCH=1.08
```

All carbons at same `RCC` from center, 72° apart (360°/5). All H atoms use X1 (ring center, atom 1) as angle reference with angle=180° for radial outward placement.

### Pyridine (C5H5N) — C2v

```
N1
C2 1 RNC
C3 2 RCC 1 ACCN
C4 3 RCC 2 ACC 1 0.0
C5 4 RCC 3 ACC 2 0.0
C6 5 RCC 4 ACC 3 0.0
C6 1 RNC 5 ACCN 4 0.0
H7 2 RCH 1 AHCC 3 180.0
H8 3 RCH 2 AHCC 4 180.0
H9 4 RCH 3 AHCC 5 180.0
H10 5 RCH 4 AHCC 6 180.0
H11 6 RCH 1 AHCC 5 180.0

RNC=1.34
RCC=1.39
RCH=1.08
ACCN=123.7
ACC=118.3
AHCC=120.0
```

Note: Pyridine has C2v symmetry (mirror plane through N and para-C). The two ortho-C positions share variables, the two meta-C positions share variables.

## Fused ring systems

### Naphthalene (C10H8) — D2h

```
C1
C2 1 RCCa
C3 2 RCCb 1 ACC1
C4 3 RCCa 2 ACC2 1 0.0
C5 4 RCCb 3 ACC1 2 0.0
C6 5 RCCa 4 ACC2 3 0.0
C7 1 RCCb 6 ACC1 2 0.0
C8 7 RCCa 1 ACC2 6 0.0
C9 8 RCCb 7 ACC1 1 0.0
C10 9 RCCa 8 ACC2 7 0.0
C10 3 RCCb 9 ACC1 4 0.0
H11 2 RCH 1 AHCC 3 180.0
H12 3 RCH 4 AHCC 2 0.0
H13 5 RCH 4 AHCC 6 0.0
H14 6 RCH 5 AHCC 7 0.0
H15 8 RCH 7 AHCC 9 0.0
H16 9 RCH 8 AHCC 10 0.0
H17 10 RCH 9 AHCC 3 0.0
H18 4 RCH 3 AHCC 5 0.0

RCCa=1.37
RCCb=1.42
RCH=1.08
ACC1=120.0
ACC2=120.0
AHCC=120.0
```

Two types of C-C bonds (RCCa for outer ring bonds, RCCb for fusion bond).

## Clusters and complexes

### P4 (white phosphorus) — Td

```
P1
P2 1 RPP
P3 1 RPP 2 PPP
P4 1 RPP 2 PPP 3 120.0

RPP=2.21
PPP=60.0
```

The P-P-P angle in the tetrahedral P4 cage is 60°.

### B12H12(2-) — Ih (icosahedral, simplified)

For icosahedral symmetry, the Z-matrix becomes very complex. Use the following approach:
1. Define 12 boron atoms at vertices of icosahedron
2. Use dummy atoms at center and along symmetry axes
3. All B-B bonds share one variable, all B-H bonds share another

For such high symmetry, consider using `Opt=Cartesian` with `Symm=(Follow,PG=Ih)` instead of Z-matrix.

## Multi-group symmetry

### trans-1,2-dichloroethylene (C2H2Cl2) — C2h

```
C1
C2 1 RCC
Cl3 1 RCCl 2 ACCCl
Cl4 2 RCCl 1 ACCCl 3 180.0
H5 1 RCH 2 ACCH 3 180.0
H6 2 RCH 1 ACCH 4 180.0

RCC=1.33
RCCl=1.72
RCH=1.08
ACCCl=122.3
ACCH=118.5
```

The 180° dihedrals enforce the trans (C2h) geometry.

### Ferrocene (Fe(C5H5)2) — D5d (staggered) or D5h (eclipsed)

For staggered (D5d) conformation:
```
Fe
X1 1 1.0
X2 1 1.0 2 90.0
C3 1 RFeC 2 90.0
C4 1 RFeC 2 90.0 3 72.0
C5 1 RFeC 2 90.0 4 72.0
C6 1 RFeC 2 90.0 5 72.0
C7 1 RFeC 2 90.0 6 72.0
H8  3 RCH 1 180.0 2 0.0
H9  4 RCH 1 180.0 3 0.0
H10 5 RCH 1 180.0 4 0.0
H11 6 RCH 1 180.0 5 0.0
H12 7 RCH 1 180.0 6 0.0
C13 1 RFeC 2 90.0 3 36.0
C14 1 RFeC 2 90.0 4 36.0
C15 1 RFeC 2 90.0 5 36.0
C16 1 RFeC 2 90.0 6 36.0
C17 1 RFeC 2 90.0 7 36.0
H18 13 RCH 1 180.0 2 0.0
H19 14 RCH 1 180.0 3 0.0
H20 15 RCH 1 180.0 4 0.0
H21 16 RCH 1 180.0 5 0.0
H22 17 RCH 1 180.0 6 0.0

RFeC=2.04
RCH=1.08
```

The second Cp ring is offset by 36° (72°/2) for staggered D5d conformation. For eclipsed D5h, use 0° offset instead. Fe serves as ring center — all H atoms use Fe (atom 1) as angle reference with angle=180°.

## Hydrogen-bonded complexes

### Water dimer — Cs

```
O1
H2 1 ROH1
H3 1 ROH1 2 AHOH1
O4 1 ROO 3 AOOH 2 180.0
H5 4 ROH2 1 AOOH2 3 0.0
H6 4 ROH2 1 AHOH2 2 0.0

ROH1=0.96
AHOH1=104.5
ROO=2.98
AOOH=120.0
ROH2=0.96
AHOH2=104.5
```

### Formic acid dimer — C2h

```
O1
C2 1 ROC
O3 2 RCO 1 AOCO
H4 2 RCH 1 ACHC 3 180.0
O5 2 RCOH 1 ACOH 3 0.0
H6 5 ROHH 2 AOH 3 180.0
O7 1 ROC 2 AOCO 6 180.0
C8 7 ROC 1 AOCO 2 180.0
O9 8 RCO 7 AOCO 1 180.0
H10 8 RCH 7 ACHC 9 0.0
O11 8 RCOH 7 ACOH 1 0.0
H12 11 ROHH 8 AOH 9 0.0

ROC=1.34
RCO=1.20
RCH=1.08
RCOH=1.34
ROHH=0.97
AOCO=123.0
ACHC=117.0
ACOH=112.0
AOH=107.0
```

Both monomers share all variables (C2h symmetry: the two monomers are equivalent and related by inversion).

## Tips for building complex Z-matrices

1. **Start from the center:** Place the most symmetric atom first, build outward
2. **Use dummy atoms liberally:** They cost nothing and prevent linear-angle errors
3. **Number systematically:** Number symmetry-equivalent atoms consecutively
4. **Test with fixed geometry first:** Run a single-point calculation before optimization
5. **Verify symmetry:** After the calculation starts, check Gaussian's point group detection in the output
6. **For very high symmetry (Ih, Oh):** Consider Cartesian + `Symm=(Follow,PG=group)` instead of Z-matrix
7. **For flexible molecules:** Use Z-matrix for the rigid symmetric core, Cartesian for flexible side chains
