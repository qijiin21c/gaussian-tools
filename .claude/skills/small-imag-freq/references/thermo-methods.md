# RRHO and QRRHO Model Reference

Detailed explanation of rigid-rotor harmonic oscillator (RRHO) and quasi-RRHO (QRRHO) models for computing thermodynamic quantities from quantum chemistry frequency calculations.

## RRHO Model (Traditional)

The standard approach used by Gaussian and most quantum chemistry programs. Treats all vibrational modes as harmonic oscillators.

### Vibrational contribution to partition function

For each vibrational mode with frequency ν:

```
q_vib = 1 / [1 - exp(-hν/kT)]
```

### Zero-point energy (ZPE)

```
ZPE = Σ (1/2) hν_i
```

Sum over all real vibrational modes. Imaginary frequencies are excluded by default.

### Thermal correction to internal energy

```
U_vib(0→T) = Σ [hν_i / (exp(hν_i/kT) - 1)]
```

### Vibrational entropy

```
S_vib = k Σ [x_i/(exp(x_i)-1) - ln(1-exp(-x_i))]
```

where x_i = hν_i/kT

### The low-frequency problem

As ν → 0:
- The term ln(1-exp(-x_i)) → -∞, causing S_vib → ∞
- This leads to severe overestimation of entropy for low-frequency modes
- Under RRHO, a 10 cm⁻¹ mode contributes ~60 J/mol/K to entropy, while a 3000 cm⁻¹ mode contributes only ~0.002 J/mol/K
- The divergence is unphysical — in reality, very low-frequency modes correspond to hindered internal rotations (free rotors), not harmonic oscillators

## QRRHO Models

Quasi-RRHO models interpolate between the harmonic oscillator limit (high frequency) and free rotor limit (low frequency), giving physically reasonable entropy for low-frequency modes.

### QRRHO(Grimme)

Proposed by Grimme. Interpolates between free rotor and harmonic oscillator based on frequency value.

**Key idea:** Frequency closer to 0 → larger free rotor weight. Frequency much higher → approaches harmonic oscillator.

**Advantages:**
- Much less sensitive to exact frequency values than RRHO
- Smooth transition between limits
- Physically motivated

**When imag freq is present (e.g., 18i → would be 20 cm⁻¹ real):**
- Missing this mode causes entropy error of ~-18 J/mol/K at 298.15 K
- Free energy error: ~5.4 kJ/mol (>1 kcal/mol) — significant

### QRRHO(Truhlar)

Proposed by Truhlar. Raises all frequencies below a threshold to that threshold before computing thermodynamic contributions.

**Typical threshold:** 100 cm⁻¹

**Procedure:**
1. For each vibrational mode, if ν < 100 cm⁻¹, set ν = 100 cm⁻¹
2. Compute thermodynamic quantities using standard RRHO formulas with modified frequencies

**Advantages:**
- Simple to implement
- Eliminates the low-frequency divergence problem

**Disadvantages:**
- Less physically motivated than Grimme
- Creates artificial discontinuity at the threshold
- Performs poorly for cluster reaction free energies

### QRRHO(Minenkov)

Same entropy treatment as Grimme, but also applies the interpolation to U_corr (thermal correction to internal energy).

**Key difference from Grimme:**
- Grimme: QRRHO only for entropy, RRHO for U_corr
- Minenkov: QRRHO for both entropy and U_corr

**Advantages:**
- More internally consistent — both entropy and energy use the same model
- Cannot compute ZPE separately (since the model is unified)
- Slightly better in practice for most cases

**Disadvantage:**
- ZPE cannot be extracted separately from the calculation

## Error Analysis

### ZPE error with small imaginary frequencies

- Each wavenumber contributes only 5.98 J/mol to ZPE
- A 30 cm⁻¹ mode contributes only 0.18 kJ/mol (0.04 kcal/mol)
- After eliminating imag freq, other real frequencies shift by several to ~10 cm⁻¹
- For large flexible systems, ZPE difference before/after eliminating imag freq is typically at most 1-2 kJ/mol
- **Conclusion: ZPE is generally safe with small imaginary frequencies**

### U(T) error with small imaginary frequencies

- Low-frequency modes contribute more to U_vib(0→T) than high-frequency modes
- In the small tens of wavenumbers range: frequency value's effect on U_vib(0→T) is noticeable but not huge — within 2.0-2.4 kJ/mol range
- Missing one small imag freq (not counting one low real mode) → underestimation of ~2.2 kJ/mol for U_vib(0→298.15K)
- **Conclusion: U(T) with one imag freq → ~0.5 kcal/mol underestimation, borderline acceptable**

### Entropy error with small imaginary frequencies

- Low-frequency modes contribute much more to entropy than high-frequency modes
- Under RRHO: as frequency → 0, entropy contribution diverges sharply
- Under QRRHO(Grimme), 298.15 K: missing one mode (that would be 20 cm⁻¹ real) → entropy error ~-18 J/mol/K
- Free energy error: ~-298.15 × (-18) / 1000 = 5.4 kJ/mol
- **Entropy error cancellation:** structures with small imag freq tend to have other low-freq modes slightly underestimated, which overestimates their entropy contribution → partially cancels the missing-mode underestimation
- **Conclusion: always use QRRHO, never RRHO, for systems with small imaginary frequencies**

### Temperature dependence

- T越大, -T×S越大, entropy errors cause larger free energy errors
- High-temperature calculations are more sensitive to frequency model choice
- For calculations at T >> 298.15 K, eliminating imaginary frequencies becomes more important

## The "Treat Imaginary as Real" Approach

Some researchers (e.g., Grimme, Angew. Chem. Int. Ed. 2022) suggest: under QRRHO, treat small imaginary frequencies as real (e.g., 18i → 18 cm⁻¹).

**Rationale:** After elimination, you'd get a real mode with similar low frequency anyway, so treating it as real "makes up" for the missing contribution.

**Why Sobereva does NOT recommend this as general practice:**

1. The difference between "with imag" and "without imag" structures is not just one mode changing from imag to real — many other low-frequency modes also shift, often systematically increasing. Without the conversion, the "entropy error cancellation" helps; with the conversion, the missing-mode underestimation is resolved but the low-frequency overestimation has nothing to cancel against.

2. If the system has many modes around 10 cm⁻¹, even QRRHO models are sensitive to frequency values in this range.

3. This approach is non-mainstream, overly subjective and optimistic, and lacks systematic validation.

**When it may help:**
- For computing U_corr, treating imag as real can reduce the difference between "with" and "without" imag freq cases
- Combined with QRRHO(Truhlar), this gives entropy close to the no-imaginary-freq case (because all low frequencies are raised to 100 cm⁻¹ anyway), but QRRHO(Truhlar) performs poorly for cluster reaction free energies
