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
X1
C2 1 1.0
C3 2 RCC 1 90.0
X4 3 1.0 2 90.0 1 90.0
H5 2 RCH 1 90.0 3 180.0
H6 3 RCH 4 90.0 2 180.0

RCC=1.20
RCH=1.06
```

X1 at origin, C2 along Z axis. C3 at 90° to X1 (molecular axis along X at z=1). Second dummy X4 at 90° to C3 for H6 angle reference. Both H atoms use 90° angles with dihedral 180°, placing them collinear with the carbons (H-C-C = 180°).

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

RBF=1.31
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
AHCO=121.5
```

The two C-H bonds share `RCH`, and the 180° dihedral places them symmetrically about the C=O axis.

## Tetrahedral molecules

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

H at origin, C at RCH distance. The other three H atoms defined relative to C with tetrahedral angle AHCH=109.5°, last two use dihedral DA=120°.

### Carbon tetrachloride (CCl4) — Td

```
Cl
C 1 RCCl
Cl 2 RCCl 1 ACClC
Cl 2 RCCl 1 ACClC 3 DA
Cl 2 RCCl 1 ACClC 4 DA

RCCl=1.77
ACClC=109.5
DA=120.0
```

### Ammonium ion (NH4+) — Td

```
H
N 1 RNH
H 2 RNH 1 AHNH
H 2 RNH 1 AHNH 3 DA
H 2 RNH 1 AHNH 4 DA

RNH=1.03
AHNH=109.5
DA=120.0
```

## Pyramidal molecules

### Ammonia (NH3) — C3v

```
N
H 1 RNH
H 1 RNH 2 HNH
H 1 RNH 2 HNH 3 120.0

RNH=1.01
HNH=107.0
```

N at origin, H at RNH. Two remaining H atoms relative to N with HNH=107°, dihedral steps of 120°.

### Phosphine (PH3) — C3v

```
P
H 1 RPH
H 1 RPH 2 HPH
H 1 RPH 2 HPH 3 dHPHH

RPH=1.42
HPH=93.5
dHPPH = 93.7 
```

## Octahedral molecules

### Sulfur hexafluoride (SF6) — Oh

```
F
S 1 RSF
F 2 RSF 1 180.0
F 2 RSF 1 90.0 3 0.0
F 2 RSF 1 90.0 3 90.0
F 2 RSF 1 90.0 3 180.0
F 2 RSF 1 90.0 3 270.0

RSF=1.56
```

S at RSF from F1. F3 opposite F1 (180°). F4-F7 in equatorial plane at 90° with 90° dihedral steps.

## Planar ring systems

### Cyclopropane (C3H6) — D3h

```
C1
C2 1 RCC
C3 1 RCC 2 ACC
H4 1 RCH 2 ACH 3 DA
H5 1 RCH 2 ACH 3 -DA
H6 2 RCH 1 ACH 3 DA
H7 2 RCH 1 ACH 3 -DA
H8 3 RCH 1 ACH 2 DA
H9 3 RCH 1 ACH 2 -DA

RCC=1.51
RCH=1.08
ACC=60.0
ACH=117.82
DA=107.74
```

C1 at origin, C2 along X axis, C3 in XZ plane (Gaussian Z-matrix convention). All H atoms use adjacent C as angle reference with ACH=122.6° (gives H-C-H=114.8°). **Critical: dihedrals must be 180° apart (DA=107.7 and DB=287.7) to place H atoms on opposite sides of the ring plane.** C1's H pair: DA/DB, C2's H pair: DB/DA (alternating), C3's H pair: DA/DB. This gives 3H above and 3H below the carbon plane, D3h staggered symmetry.

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

RCC=1.38
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

**Critical: fused rings require one ring-closing atom per ring.** C6 closes to C1 (left ring) and C10 closes to C9 (right ring closure through C3). C9 uses C8 for distance with D1=0° to keep planarity; C10 uses C9 for distance with A2 (closing angle) and D2=180°.

```
C1
C2 1 R1
C3 2 R1 1 A1
C4 3 R1 2 A1 1 D1
C5 4 R2 3 A1 2 D1
C6 1 R2 5 A2 4 D2
C7 2 R1 1 A1 3 D2
C8 7 R2 2 A1 1 D2
C9 8 R1 7 A1 2 D1
C10 9 R2 3 A2 8 D2
H11 1 RCH 6 -AH 2 D1
H12 7 RCH 2 AH 1 D1
H13 8 RCH 7 -AH 2 D1
H14 9 RCH 8 -AH 7 D1
H15 10 RCH 3 -AH 9 D1
H16 4 RCH 3 -AH 2 D1
H17 5 RCH 4 -AH 3 D1
H18 6 RCH 1 -AH 5 D1

R1=1.4
R2=1.37
A1=120.0
A2=30.0
RCH=1.1
AH=120.0
D1=0.0
D2=180.0
```

Key D2h symmetry features:
- **Only 2 C-C bond types**: R1 (most bonds) and R2 (closing + alternating bonds). All equivalent bonds share the same variable.
- **Only 2 angles**: A1=120° for all regular C-C-C angles, A2=30° for both ring-closing atoms (C6 and C10).
- **Mirror plane dihedrals**: -AH and AH for H atoms related by the horizontal mirror plane (atoms on opposite sides of the molecular plane don't exist here since it's planar, but -AH/AH distinguishes H atoms on opposite sides of the C-C bond axis within the plane).
- **D2 alternation**: D2=180° for atoms placed on the opposite side of the molecular plane (C6, C7, C8, C10), keeping all atoms planar.

## Clusters and complexes

### P4 (white phosphorus) — Td

```
P1
P2 1 RPP
P3 1 RPP 2 PPP
P4 1 RPP 2 PPP 3 DA

RPP=2.21
PPP=60.0
DA=70.5288
```

All four P atoms at vertices of a regular tetrahedron. Each P-P-P angle is 60° (each face is equilateral). The dihedral for P4 is `arcsin(1/3) ≈ 19.471°`, NOT 120° — this is the angle that places P4 at the correct tetrahedral position equidistant from P1, P2, and P3.

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

**Critical: the two Cp rings must be on opposite sides of Fe.** All carbons use Fe as bond reference and X1 as angle reference. Upper ring uses angle A1 = 180 - θ (places ring at z < 0), lower ring uses angle A2 = θ (places ring at z > 0). For staggered D5d, lower ring dihedrals are offset by 36°; for eclipsed D5h, use 0° offset. θ is computed from geometry: θ = arcsin(RCC/(2·sin(36°)·RFeC)) ≈ 35.72°.

**All lower ring dihedrals reference C2 (atom 3)** — not successive upper ring atoms — to ensure correct 72° spacing around the ring.

**H atoms must be coplanar with their Cp rings** (same z as their C atoms, pointing radially outward). H atoms use Fe as angle reference and X1 as dihedral reference. All H atoms share the same angle AH = 90 + θ ≈ 125.72°. Upper ring H: D = 0°; lower ring H: D = 180°.

For staggered (D5d) conformation:
```
Fe
X1 1 1.0
C2 1 RFeC 2 A1
C3 1 RFeC 2 A1 3 72.0
C4 1 RFeC 2 A1 4 72.0
C5 1 RFeC 2 A1 5 72.0
C6 1 RFeC 2 A1 6 72.0
H7  3 RCH 1 AH 2 0.0
H8  4 RCH 1 AH 2 0.0
H9  5 RCH 1 AH 2 0.0
H10 6 RCH 1 AH 2 0.0
H11 7 RCH 1 AH 2 0.0
C12 1 RFeC 2 A2 3 36.0
C13 1 RFeC 2 A2 3 108.0
C14 1 RFeC 2 A2 3 180.0
C15 1 RFeC 2 A2 3 252.0
C16 1 RFeC 2 A2 3 324.0
H17 13 RCH 1 AH 2 180.0
H18 14 RCH 1 AH 2 180.0
H19 15 RCH 1 AH 2 180.0
H20 16 RCH 1 AH 2 180.0
H21 17 RCH 1 AH 2 180.0

RFeC=2.04
RCH=1.08
A1=144.28
A2=35.72
AH=125.72
```

For eclipsed (D5h) conformation, change the lower ring dihedrals from 36/108/180/252/324 to 0/72/144/216/288. The upper ring C2-C6 and lower ring C12-C16 each form regular pentagons (C-C = 1.40 Å) with Fe-C = 2.04 Å. Ring separation = 2 × RFeC × cos(θ) ≈ 3.31 Å. All H atoms are coplanar with their respective Cp rings (same z as their parent C).

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
C2 1 RCO
O3 2 RCOH 1 AOCO
H4 2 RCH 1 AHC 3 DHC
H5 3 ROH 2 ACOH 1 0.0
O6 1 ROO 2 AOO 3 0.0
C7 6 RCO 1 AOO 2 180.0
O8 7 RCOH 6 AOCO 1 0.0
H9 7 RCH 6 AHC 8 180.0
H10 8 ROH 7 ACOH 6 0.0

RCO=1.20
RCOH=1.34
RCH=1.08
ROH=0.97
ROO=3.1763
AOCO=123.0
AHC=117.0
ACOH=107.0
AOO=86.1446
DHC=-180.0
```

Both monomers share all internal variables (C2h symmetry: the two monomers are equivalent and related by inversion through the center point). The H-bond geometry: H5···O6 = 1.70 Å, H10···O1 = 1.70 Å, O3···O6 = 2.67 Å, O3-H5···O6 = 180°, O8-H10···O1 = 180°. ROO and AOO are derived from the H-bond geometry rather than being independent parameters.

## Tips for building complex Z-matrices

1. **Start from the center:** Place the most symmetric atom first, build outward
2. **Use dummy atoms liberally:** They cost nothing and prevent linear-angle errors
3. **Number systematically:** Number symmetry-equivalent atoms consecutively
4. **Test with fixed geometry first:** Run a single-point calculation before optimization
5. **Verify symmetry:** After the calculation starts, check Gaussian's point group detection in the output
6. **For very high symmetry (Ih, Oh):** Consider Cartesian + `Symm=(Follow,PG=group)` instead of Z-matrix
7. **For flexible molecules:** Use Z-matrix for the rigid symmetric core, Cartesian for flexible side chains
