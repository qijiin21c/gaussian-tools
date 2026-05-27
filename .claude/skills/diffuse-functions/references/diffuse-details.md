# Diffuse Function Basis Sets — Detailed Reference

Comprehensive discussion of all common basis sets with diffuse functions, based on Sobereva's article (sobereva.com/119).

## Diffuse function characteristics

For each angular momentum type, the diffuse function's exponent is several times smaller than the smallest exponent of other functions with the same angular momentum in the basis set. Diffuse functions are generally uncontracted. Different basis sets have different numbers of diffuse functions and involve different angular momenta.

## Pople series diffuse basis sets

### Notation
- `6-31+G*` — one layer of s+p diffuse on heavy atoms only (same exponent for s and p)
- `6-311++G(2df,2p)` — diffuse on heavy atoms AND hydrogen (s on H, s+p on heavy)

### Key points
- All Pople basis sets share the same diffuse exponents — they are NOT separately optimized for each basis set
- The `+` adds heavy atom diffuse; `++` adds hydrogen diffuse too
- **Important cost comparison:** `6-311G*` is cheaper than `6-31+G*` AND gives better results for problems where diffuse isn't critical. Countless people use `6-31+G*` when `6-311G*` would be much more appropriate and cost-effective.

### Why the 6-311G* > 6-31+G* rule

When diffuse functions are NOT essential:
- 3-zeta (6-311G*) provides much better valence electron description than 2-zeta + diffuse (6-31+G*)
- Increasing zeta level gives more benefit than adding diffuse for most properties
- This is confirmed by extensive benchmark testing

## Dunning cc-pVnZ series diffuse basis sets

### aug-cc-pVnZ (augmented)

Adds one layer of same-angular-momentum diffuse to EACH angular momentum present in the base basis set.

**Examples:**
- cc-pVTZ for C: 4s, 3p, 2d, 1f → aug-cc-pVTZ adds: s diffuse, p diffuse, d diffuse, f diffuse
- cc-pVDZ for H: 2s, 1p → aug-cc-pVDZ adds: s diffuse, p diffuse

**Always adds diffuse to hydrogen** — unlike Pople series which distinguishes + vs ++.

### aug- variants

The same diffuse functions are added to related basis sets:
- **aug-cc-pCVnZ**, **aug-cc-pwCVnZ** — core-valence correlation basis sets + diffuse
- **aug-cc-pVnZ-DK** — DKH relativistic basis sets + diffuse
- **aug-cc-pV(n+d)Z** — cc-pVnZ with extra tight d function + diffuse (d diffuse exponent re-optimized)
- **aug-cc-pVnZ-PP** — pseudopotential basis sets + diffuse (diffuse types/quantities same as aug-cc-pVnZ, exponents re-optimized)

### Multiple diffuse layers

- **d-aug-cc-pVnZ** — two layers of diffuse per angular momentum
- **t-aug-cc-pVnZ** — three layers of diffuse per angular momentum
- Extremely expensive — used for precise Rydberg state calculations, hyperpolarizability

## def2- series diffuse basis sets

No official diffuse versions exist (a regrettable omission). Options:

1. **See sobereva.com/340** for ways to add diffuse to def2- basis sets
2. **def2-SVPD, TZVPD, TZVPPD, QZVPD, QZVPPD** — proposed in JCP,133,134105. Added to def2-SVP, TZVP, TZVPP, QZVP, QZVPP respectively. Diffuse exponents optimized from atomic HF polarizability.
3. **Borrow diffuse** from similarly-sized basis sets
4. **Even-tempered construction** based on existing basis sets
5. **Divide smallest s,p exponent by 3** (JCTC,7,3027) — not as good as optimized exponents for specific problems, but may perform better for broader, unconsidered problem types

## Jensen pc-n series diffuse basis sets

Jensen proposed method to add diffuse to pc-n series (JCP,117,9234). The angular momentum level of diffuse can be chosen as needed:
- Adding s+p diffuse greatly improves DFT electron affinity accuracy
- Further improvement of response properties needs higher-angular-momentum diffuse too

## Lanl pseudopotential diffuse basis sets

- **LANL2DZdp** (JPCA,105,8111) — Lanl2DZ + d polarization + p diffuse for main group elements. Greatly improves electron affinity, vibrational frequency, bond length accuracy vs Lanl2DZ.
- **LANL2TZ+**, **LANL08+** — Added one layer of diffuse for 1st row transition metals on LANL2TZ and LANL08 respectively. d-shell-filled 1st row transition metals are sometimes easily polarized.

## Response-property-optimized diffuse basis sets

These basis sets (or their diffuse functions, or entire basis sets) are optimized for response properties (polarizability, hyperpolarizability) rather than energy, achieving better accuracy/cost ratios.

### Sadlej POL

- Also called Sadlej pVTZ
- Proposed starting from 1988
- Parameters optimized for polarizability calculation
- Size ≈ cc-pVTZ
- Polarizability accuracy ≈ aug-cc-pVTZ (much more expensive)

### Sadlej ZPOL

- Proposed starting from 2004
- Simplified version of POL
- Suitable for large system dipole moment and polarizability
- Cost ≈ 6-311+G*
- Polarizability accuracy better than 6-311++G(2df,2p)

### Sadlej LPol series

- Proposed 2009
- Series: LPol-ds < LPol-dl < LPol-fs < LPol-fl (increasing size)
- **LPol-ds:** Smallest in series, but much larger than POL
  - First hyperpolarizability accuracy ≈ d-aug-cc-pVTZ
  - Lowest cost at this accuracy level
  - Defined only for C, H, O, N, F

### LFK pseudopotential basis sets

- Based on SBKJC pseudopotential
- Added diffuse and polarization functions for 39 main group elements
- Goal: achieve all-electron Sadlej-level polarizability accuracy at pseudopotential cost
- Exponents and contraction coefficients obtained by fitting experimental atomic polarizabilities or high-level relativistic calculations

## When to use which diffuse basis set

### For polarizability (cheapest to most expensive, best cost-performance first)
1. ZPOL
2. jul-cc-pVDZ
3. aug-cc-pVDZ
4. POL
5. aug-cc-pVTZ(-f,-d)
6. LPol-ds

### For hyperpolarizability (cheapest to most expensive)
1. aug-cc-pVDZ
2. POL
3. aug-cc-pVTZ(-f,-d)
4. LPol-ds
5. LPol-fs

### For very high precision hyperpolarizability on small systems
- t-aug-cc-pVTZ or aug-pcseg-3 (similar size, ~2x basis functions of LPol-ds)
- Use adddiffuse tool (sobereva.com/347) to generate even-tempered diffuse

## Borrowing diffuse between basis sets

If a basis set doesn't have an official diffuse version:
1. Borrow diffuse from a similarly-sized basis set
2. Use even-tempered construction
3. Divide the smallest s and p exponents by 3 (JCTC,7,3027)

These approaches produce exponents that may not be optimal for specific problems, but could perform better for broader problem types not considered during the optimization process. See sobereva.com/340 for detailed discussion.
