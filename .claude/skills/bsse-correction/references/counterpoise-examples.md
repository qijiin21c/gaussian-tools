# BSSE in Gaussian: Input Examples and Workflows

Practical guide for counterpoise and BSSE calculations in Gaussian, with complete input examples, based on Sobereva's article.

## HF dimer counterpoise example

```
# B3LYP/6-31G(d) counterpoise=2

HF dimer counterpoise calculation

0 1
H 0.00 0.00 0.92 1
F 0.17 0.00 2.73 2
H 0.77 0.00 3.43 2
F 0.00 0.00 0.00 1
```

This computes:
1. E_HF...HF in HF...HF basis
2. E_HF(monomer A) in full dimer basis (DCBS for fragment 1)
3. E_HF(monomer B) in full dimer basis (DCBS for fragment 2)
4. E_HF(monomer A) in monomer A basis only (MCBS)
5. E_HF(monomer B) in monomer B basis only (MCBS)

## Complex with different fragment charges

```
# M062X/def2-TZVP counterpoise=2

Anion-cation complex counterpoise

-1,1,0,1,-1,2
C 0.00 0.00 0.00 1
H 0.00 0.00 1.09 1
H 1.03 0.00 -0.36 1
H -0.51 0.89 -0.36 1
H -0.51 -0.89 -0.36 1
Li -3.00 0.00 0.00 2
```

This specifies:
- Overall: charge=-1, multiplicity=1
- Fragment 1: charge=0, multiplicity=1 (neutral methyl)
- Fragment 2: charge=-1, multiplicity=2 (Li anion)

## Alternative fragment assignment syntax

```
# B2PLYPD3/jul-cc-pVTZ counterpoise=2

Counterpoise with fragment keyword

0 1
H(fragment=1) 0.00 0.00 0.92
F(fragment=2) 0.17 0.00 2.73
H(fragment=2) 0.77 0.00 3.43
F(fragment=1) 0.00 0.00 0.00
```

Equivalent to putting fragment numbers after coordinates.

## Multi-fragment counterpoise (3 fragments)

```
# wB97XD/def2-TZVP counterpoise=3

Water trimer counterpoise

0 1
O 0.00 0.00 0.00 1
H 0.76 0.00 0.52 1
H -0.76 0.00 0.52 1
O 2.80 0.00 0.00 2
H 3.56 0.00 0.52 2
H 2.04 0.00 0.52 2
O 1.40 2.42 0.00 3
H 2.16 2.42 0.52 3
H 0.64 2.42 0.52 3
```

Output order: E_complex, E_1', E_2', E_3', E_1, E_2, E_3

```
E_BSSE = (E_1 - E_1') + (E_2 - E_2') + (E_3 - E_3')
```

## Manual counterpoise with ghost atoms

### Step 1: Complex energy

```
# B3LYP/6-31G(d)

Step 1: E_AB (full complex)

0 1
H 0.00 0.00 0.92
F 0.17 0.00 2.73
H 0.77 0.00 3.43
F 0.00 0.00 0.00
```

### Step 2: Fragment A in dimer basis (DCBS)

```
# B3LYP/6-31G(d) nosymm

Step 2: E_A,bAB (A with B's ghost basis functions)

0 1
H 0.00 0.00 0.92
F-Bq 0.17 0.00 2.73
H-Bq 0.77 0.00 3.43
F 0.00 0.00 0.00
```

`nosymm` is needed because ghost atoms break the original symmetry.

### Step 3: Fragment B in dimer basis (DCBS)

```
# B3LYP/6-31G(d) nosymm

Step 3: E_B,bAB (B with A's ghost basis functions)

0 1
H-Bq 0.00 0.00 0.92
F 0.17 0.00 2.73
H 0.77 0.00 3.43
F-Bq 0.00 0.00 0.00
```

### Step 4: Fragment A alone (MCBS)

```
# B3LYP/6-31G(d)

Step 4: E_A (fragment A isolated)

0 1
H 0.00 0.00 0.92
F 0.00 0.00 0.00
```

### Step 5: Fragment B alone (MCBS)

```
# B3LYP/6-31G(d)

Step 5: E_B (fragment B isolated)

0 1
H 0.77 0.00 0.00
H 0.00 0.00 0.73
```

### Compute BSSE

```
E_BSSE = (E_A - E_A,bAB) + (E_B - E_B,bAB)
E_corrected = E_AB + E_BSSE
E_interaction = E_AB - E_A - E_B + E_BSSE
```

**Advantage:** Preserves symmetry for steps 1, 4, 5 — can be significantly faster for symmetric systems. Gaussian's `counterpoise` keyword disables symmetry for ALL steps.

## Standard interaction energy workflow

### Step 1: Optimize complex (NO counterpoise)

```
# B3LYP-D3(BJ)/def2-TZVP opt

Optimize HF dimer

0 1
H 0.00 0.00 0.92
F 0.17 0.00 2.73
H 0.77 0.00 3.43
F 0.00 0.00 0.00
```

### Step 2: Frequency check (NO counterpoise)

```
# B3LYP-D3(BJ)/def2-TZVP freq

Frequency check

0 1
H 0.00 0.00 0.92
F 0.17 0.00 2.73
H 0.77 0.00 3.43
F 0.00 0.00 0.00
```

### Step 3: Counterpoise single-point at optimized geometry

```
# B3LYP-D3(BJ)/def2-TZVP counterpoise=2

Counterpoise at optimized geometry

0 1
H 0.00 0.00 0.92 1
F 0.17 0.00 2.73 2
H 0.77 0.00 3.43 2
F 0.00 0.00 0.00 1
```

Read output:
```
Counterpoise corrected energy =    -200.665576
BSSE energy =       0.001682
sum of monomers =    -200.659550
complexation energy =      -4.84 kcal/mole (raw)
complexation energy =      -3.78 kcal/mole (corrected)
```

## Solvent model + BSSE workflow

### Gas phase counterpoise

```
# B3LYP-D3(BJ)/def2-TZVP counterpoise=2

Gas phase CP for BSSE

0 1
H 0.00 0.00 0.92 1
F 0.17 0.00 2.73 2
H 0.77 0.00 3.43 2
F 0.00 0.00 0.00 1
```

Read E_BSSE from output.

### Solvent phase normal calculation

```
# B3LYP-D3(BJ)/def2-TZVP SCRF=IEFPCM

Solvent phase single-point

0 1
H 0.00 0.00 0.92
F 0.17 0.00 2.73
H 0.77 0.00 3.43
F 0.00 0.00 0.00
```

Get E_AB(solvent), E_A(solvent), E_B(solvent) from separate calculations.

### Combine

```
E_interaction(solvent) ≈ E_AB(solvent) - E_A(solvent) - E_B(solvent) + E_BSSE(gas)
```

## When NOT to use counterpoise

### Chemical bond energy calculation

```
! WRONG — computing bond dissociation energy with counterpoise
# CCSD(T)/cc-pVQZ counterpoise=2

0,2  0,1 0,2
C 0.00 0.00 0.00 1
H 0.00 0.00 1.09 1
H 1.03 0.00 -0.36 1
H -0.51 0.89 -0.36 1
H -0.51 -0.89 -0.36 1
C 0.00 0.00 1.54 2
...
```

**This is wrong.** For chemical bonds, use a large basis set instead (cc-pVQZ or def2-QZVP). See sobereva.com/381.

### Correct approach for bond energy

```
# CCSD(T)/cc-pVQZ

Bond dissociation — large basis, no CP

0 1
... full molecule ...
```

Compute fragments separately at the same level and take the difference. With cc-pVQZ, BSSE is negligible.

## Intramolecular BSSE workaround

For a molecule with intramolecular weak interaction (e.g., folded vs. extended conformation):

### Approach: Molecular cutting

Original molecule: HO-(CH₂)₁₀-OH (folded into C-shape)

1. Cut at the middle C-C bond
2. Cap with H atoms
3. Separate the cut ends

```
# B3LYP/6-311+G(d,p) counterpoise=2

Intramolecular BSSE workaround

0,2 0,1 0,1
H 0.00 0.00 0.00 1
O 0.00 0.00 1.00 1
C 0.00 0.00 2.20 1
... 5 CH₂ units ...
H-Bq 0.00 0.00 8.00 1    ← cut point capped (far from interaction region)
H-Bq 0.00 0.00 -1.00 2   ← cut point capped (far from interaction region)
... 5 CH₂ units ...
C 3.00 0.00 8.00 2
O 4.00 0.00 9.00 2
H 4.00 0.00 10.00 2
```

Keep the interacting ends at original positions; move the cut ends far apart.

### Better approach: Diffuse functions or gCP

Instead of cutting:
- Use basis set with diffuse functions: `6-311++G(d,p)` or `aug-cc-pVDZ`
- Or use gCP in ORCA with non-diffuse basis: `def2-TZVP + gCP`

## References

- sobereva.com/381 — Counterpoise is wrong for bond energies
- sobereva.com/214 — gCP approach
- sobereva.com/685 — sobEDA with BSSE discussion
- sobereva.com/542 — ORCA counterpoise via Multiwfn
