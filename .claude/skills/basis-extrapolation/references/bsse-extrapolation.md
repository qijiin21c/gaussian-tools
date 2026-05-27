# BSSE-Aware Basis Set Extrapolation

Detailed guide for extrapolating intermolecular interaction energies to the CBS limit while properly accounting for basis set superposition error (BSSE), based on Sobereva's article (sobereva.com/338).

## Why BSSE matters for extrapolation

Intermolecular interaction energy is computed via the supermolecular approach:
```
E_int = E_AB - E_A - E_B
```

Whether the monomer geometries use the free or complex structure depends on the specific problem and is not discussed here.

To get the CBS-limit interaction energy, one might think to simply extrapolate E_AB, E_A, and E_B separately. However, **BSSE must be considered**, especially for dispersion-dominated interactions where BSSE remains significant even at aug-cc-pVQZ level.

See sobereva.com/46 for detailed BSSE discussion.

## Counterpoise-corrected energy

### Standard counterpoise correction

The BSSE-corrected dimer energy E'_AB is:
```
E'_AB = E_AB + E_BSSE
E_BSSE = (E_A - E_A,bAB) + (E_B - E_B,bAB)
```

Where:
- **E_AB**: Energy of the AB complex computed with basis sets of both A and B
- **E_A,bAB**: Energy of fragment A computed with the full AB basis set (B atoms present as ghost atoms with basis functions but no nuclei/electrons)
- **E_B,bAB**: Energy of fragment B computed with the full AB basis set (A atoms as ghost atoms)
- **E_A**: Energy of fragment A computed with its own basis set only
- **E_B**: Energy of fragment B computed with its own basis set only

### Splitting BSSE for post-HF calculations

For post-HF methods, BSSE affects both the SCF and correlation energy components differently:

```
E_BSSE_HF = (E_A_HF - E_A,bAB_HF) + (E_B_HF - E_B,bAB_HF)
E_BSSE_corr = (E_A_corr - E_A,bAB_corr) + (E_B_corr - E_B,bAB_corr)
```

The BSSE-corrected components are:
```
E'_AB_HF = E_AB_HF + E_BSSE_HF
E'_AB_corr = E_AB_corr + E_BSSE_corr
```

### Extrapolation workflow with BSSE

1. At each basis level (e.g., aug-cc-pVTZ and aug-cc-pVQZ):
   - Compute E_AB_HF, E_A_HF, E_B_HF, E_A,bAB_HF, E_B,bAB_HF
   - Compute E_AB_corr, E_A_corr, E_B_corr, E_A,bAB_corr, E_B,bAB_corr
   - Calculate E_BSSE_HF and E_BSSE_corr
   - Obtain E'_AB_HF and E'_AB_corr

2. Extrapolate E'_AB_HF to CBS using the SCF extrapolation formula

3. Extrapolate E'_AB_corr to CBS using the correlation energy extrapolation formula

4. Sum: `E'_AB(CBS) = E'_AB_HF(CBS) + E'_AB_corr(CBS)`

5. Subtract CBS monomer energies (also BSSE-corrected) to get CBS interaction energy

**This is more rigorous than extrapolating without BSSE correction.**

### When can you skip BSSE in extrapolation?

| Basis level | BSSE magnitude | Skip BSSE? |
|------------|---------------|-----------|
| aug-cc-pVTZ | Moderate | Not recommended for high accuracy |
| aug-cc-pVQZ | Small | May be acceptable, but still noticeable |
| aug-cc-pV5Z | Very small | Probably OK to skip |

**Recommendation:** For high-accuracy work, always include BSSE correction even at QZ level.

## Manual ghost atom approach

### Why not use Gaussian's counterpoise keyword

Gaussian's `counterpoise=N` keyword can compute BSSE-corrected energies in one step. However, for post-HF extrapolation, **manual ghost atom computation is recommended**:

| Issue | Gaussian counterpoise | Manual ghost atoms |
|-------|---------------------|-------------------|
| **Symmetry** | Disables symmetry for ALL calculations | Can keep symmetry for E_AB, E_A, E_B |
| **Data extraction** | Hard to separate E_BSSE_HF from E_BSSE_corr | Clean separation |
| **Confusion risk** | Easy to mix up values in output | Clear, organized |

### Recommended calculation sequence

For each basis set level, compute the following 5 jobs:

**(1) E_AB: Full complex**
```
#p ccsd(T)/aug-cc-pvtz

[all atoms - no ghost atoms]
```
Extract: SCF Done → E_AB_HF, CCSD(T)= → E_AB_total, then E_AB_corr = E_AB_total - E_AB_HF

**(2) E_A: Fragment A alone**
```
#p ccsd(T)/aug-cc-pvtz

[only A atoms]
```
Extract: E_A_HF, E_A_corr

**(3) E_A,bAB: Fragment A with B as ghost atoms**
```
#p ccsd(T)/aug-cc-pvtz nosymm

[A atoms normally]
[B atoms with -Bq suffix, e.g., H-Bq]
```
Extract: E_A,bAB_HF, E_A,bAB_corr

**Note:** `nosymm` is needed because ghost atoms break symmetry.

**(4) E_B: Fragment B alone**
```
#p ccsd(T)/aug-cc-pvtz

[only B atoms]
```
Extract: E_B_HF, E_B_corr

**(5) E_B,bAB: Fragment B with A as ghost atoms**
```
#p ccsd(T)/aug-cc-pvtz nosymm

[A atoms with -Bq suffix, e.g., N-Bq]
[B atoms normally]
```
Extract: E_B,bAB_HF, E_B,bAB_corr

### Extracting energies from Gaussian output

| Energy | Where to find |
|--------|--------------|
| **HF energy** | `SCF Done:` line |
| **CCSD(T) total energy** | Search for `CCSD(T)=` |
| **MP2 total energy** | Search for `EUMP2 =` |
| **Correlation energy** | E_total - E_HF |

## Worked example: H₂-N₂ dimer

Parallel H₂-N₂ dimer, CCSD(T)/aug-cc-pVDZ/TZ extrapolation, from J. Mol. Model. 19, 5387.

### Geometry
```
N   0.00000000    0.55705000   -0.42673900
N   0.00000000   -0.55705000   -0.42673900
H   0.00000000   -0.36881700    2.98717200
H   0.00000000    0.36881700    2.98717200
```

### aug-cc-pVTZ results

**Five calculations at aug-cc-pVTZ level:**

| Quantity | HF energy | CCSD(T) total | Correlation |
|----------|----------|---------------|-------------|
| E_AB | -110.11354966 | -110.55353809 | -0.43998843 |
| E_A | -108.98075536 | -109.38058553 | -0.39983017 |
| E_A,bAB | -108.98078589 | -109.38068579 | -0.39989990 |
| E_B | -1.13304859 | -1.17261651 | -0.03956792 |
| E_B,bAB | -1.13305499 | -1.17262921 | -0.03957422 |

**BSSE calculation:**
```
E_BSSE_HF = (-108.98075536 - (-108.98078589)) + (-1.13304859 - (-1.13305499))
          = 0.00003053 + 0.00000640
          = 0.00003692

E_BSSE_corr = (-0.39983017 - (-0.39989990)) + (-0.03956792 - (-0.03957422))
            = 0.00006973 + 0.00000630
            = 0.00007603
```

**BSSE-corrected energies:**
```
E'_AB_HF = -110.11354966 + 0.00003692 = -110.11351274
E'_AB_corr = -0.43998843 + 0.00007603 = -0.43991240
```

### aug-cc-pVQZ results

| Quantity | HF energy | CCSD(T) total | Correlation |
|----------|----------|---------------|-------------|
| E_AB | [computed] | [computed] | [computed] |
| E_A | [computed] | [computed] | [computed] |
| E_A,bAB | [computed] | [computed] | [computed] |
| E_B | [computed] | [computed] | [computed] |
| E_B,bAB | [computed] | [computed] | [computed] |

**Results:**
```
E_BSSE_HF = 0.00001463   (much smaller than VTZ's 0.00003692)
E_BSSE_corr = 0.00003224  (much smaller than VTZ's 0.00007603)
E'_AB_HF = -110.12069678
E'_AB_corr = -0.46017610
```

BSSE at QZ level is clearly much smaller than at TZ level.

### CBS extrapolation

**SCF energy:** No aug-cc-pVnZ-specific α parameters available. Use aug-cc-pVQZ HF energy directly as CBS approximation:
```
E'_AB_HF(CBS) ≈ -110.12069678
```

Alternatively, approximate with cc-pVnZ α = 5.46 (L=3/4) — the difference from ideal aug-cc-pVnZ α is small.

**Correlation energy:** Klopper-Helgaker with L=3/4 (N=3, M=4):
```
E'_AB_corr(CBS) = [E'_corr(QZ)×4³ - E'_corr(TZ)×3³] / (4³ - 3³)
                = [-0.46017610×64 - (-0.43991240)×27] / (64 - 27)
                = [-29.45127040 + 11.87763480] / 37
                = -0.47496313
```

**Total CBS energy:**
```
E'_AB(CBS) = -110.12069678 + (-0.47496313) = -110.59565991
```

**Interaction energy:** Subtract CBS monomer energies (computed separately with same extrapolation protocol).

## Symmetry considerations

When using manual ghost atom approach:
- **E_AB, E_A, E_B:** Can use symmetry if the system has it — saves time
- **E_A,bAB, E_B,bAB:** Must use `nosymm` — ghost atoms break symmetry

Gaussian's `counterpoise` keyword disables symmetry for ALL calculations, losing this efficiency benefit.

## Consistency rules for relative energies

**Critical:** When computing interaction energies or other relative energies:
1. **All systems** (all complexes and all monomers) must be extrapolated using the **same basis pair**
2. **All systems** must use the **same BSSE correction protocol**
3. Never mix extrapolated and non-extrapolated energies — the error is massive

## References

- sobereva.com/338 — This article (basis set extrapolation including BSSE)
- sobereva.com/46 — BSSE and counterpoise correction
- J. Mol. Model. 19, 5387 — H₂-N₂ dimer study using this protocol
