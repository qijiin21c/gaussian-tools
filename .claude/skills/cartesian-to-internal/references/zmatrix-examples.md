# Z-Matrix Examples for Symmetric Molecules

Comprehensive Z-matrix examples for common symmetric molecules, dummy atom patterns, and complex multi-group symmetry cases.

## Linear molecules

Linear molecules require dummy atoms because the dihedral angle is undefined when the bond angle is exactly 180°.

### CO2 — D∞h

```
C
O 1 RCO
O 1 RCO 2 180.0
X 1 1.0 2 90.0 3 90.0

RCO=1.16
```

The dummy atom X is placed at 90° from both the C-O bond and the O-C-O axis, providing a reference for the dihedral angle definition. Both C=O bonds share `RCO`.

### HCN — C∞v

```
H
C 1 RHC
N 1 RCN 2 180.0
X 1 1.0 2 90.0 3 90.0

RHC=1.06
RCN=1.16
```

### Acetylene (C2H2) — D∞h

```
C1
C2 1 RCC
H3 1 RCH 2 180.0
H4 2 RCH 1 180.0
X5 1 1.0 2 90.0 3 0.0
X6 2 1.0 1 90.0 4 0.0

RCC=1.20
RCH=1.06
```

Two dummy atoms (X5, X6) placed on opposite sides of the axis to define the molecular plane.

### N2O — C∞v

```
N1
N2 1 RNN
O 1 RNO 2 180.0
X 1 1.0 2 90.0 3 90.0

RNN=1.13
RNO=1.19
```

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
H8 3 RCH 2 ACH 4 180.0
H9 4 RCH 3 ACH 5 180.0
H10 5 RCH 4 ACH 6 180.0
H11 6 RCH 5 ACH 7 180.0
H12 7 RCH 6 ACH 3 180.0

RCC=1.42
RCH=1.08
ACH=108.0
```

All carbons at same `RCC` from center, 72° apart (360°/5).

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
H8 3 RCH 2 ACH 4 180.0
H9 4 RCH 3 ACH 5 180.0
H10 5 RCH 4 ACH 6 180.0
H11 6 RCH 5 ACH 7 180.0
H12 7 RCH 6 ACH 3 180.0
C13 1 RFeC 2 90.0 3 36.0
C14 1 RFeC 2 90.0 4 36.0
C15 1 RFeC 2 90.0 5 36.0
C16 1 RFeC 2 90.0 6 36.0
C17 1 RFeC 2 90.0 7 36.0
H18 13 RCH 2 ACH 14 180.0
H19 14 RCH 3 ACH 15 180.0
H20 15 RCH 4 ACH 16 180.0
H21 16 RCH 5 ACH 17 180.0
H22 17 RCH 6 ACH 13 180.0

RFeC=2.04
RCH=1.08
ACH=126.0
```

The second Cp ring is offset by 36° (72°/2) for staggered D5d conformation. For eclipsed D5h, use 0° offset instead.

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
