# Vibrationally Resolved Electronic Spectra

Detailed guide for computing vibrationally resolved electronic spectra (vibronic spectra) using Gaussian, based on Sobereva's article (sobereva.com/223).

## Why vibronic spectra matter

Electronic spectra (UV-Vis, photoelectron) appear as simple peaks between electronic states. But each electronic state has many vibrational levels. When an electronic transition occurs, the system can transition from the vibrational ground state of the initial electronic state to various vibrational levels of the final electronic state. At higher spectral resolution, a single "electronic" peak resolves into many vibrational sub-peaks.

**To accurately predict absorption/emission spectra** (including dye molecule colors), the entire absorption band must be predicted, not just a few peak positions. This requires considering vibronic coupling — the interaction between vibrational and electronic states.

## Temperature dependence

At 0K, the system is in the vibrational ground state. At finite temperature, vibrationally excited states of the initial electronic state also have Boltzmann population. The observed spectrum is a weighted sum of transitions from all populated initial vibrational states to all final vibrational states. This temperature dependence can be computed theoretically.

## Theory: Transition dipole moment

Under the Born-Oppenheimer approximation, the transition dipole moment between total wavefunctions Ψ (electronic × vibrational) separates:

```
<Ψ'|μ|Ψ''> = <ψ'|μₑ|ψ''>
```

where μₑ = <φ'|μ|φ''> is the electronic transition dipole moment, which depends on nuclear coordinates.

Expanding μₑ in a Taylor series around the excited-state equilibrium geometry leads to three approaches:

### 1. Franck-Condon (FC) approximation
- μₑ takes only the 0th-order term (constant = value at excited-state equilibrium geometry)
- **Sufficient for bright (allowed) states**
- Most commonly used

### 2. Herzberg-Teller (HT) method
- μₑ takes only the 1st-order term (linear function of nuclear coordinates)
- **Rarely used alone** — the 0th-order term is always dominant
- **Use case:** When the electronic transition is symmetry-forbidden (μₑ = 0 at equilibrium), but including nuclear vibration makes the transition weakly allowed
- Essential for studying dark states

### 3. FC + HT (FCHT) method
- Includes both 0th and 1st-order terms
- Broader applicability than FC alone
- **Recommended** when HT effects may be significant

**Note:** Do not confuse:
- **FC principle** — electronic transitions are fast, nuclear coordinates don't change during transition
- **FC factor** — square of overlap integral between initial and final vibrational wavefunctions
- **FC approximation** — treating μₑ as constant in vibronic spectrum calculation

## The computational challenge

A non-linear molecule has 3N-6 normal modes. In the harmonic oscillator model, each mode is independent, and the total vibrational wavefunction is a product of individual mode wavefunctions.

If each mode has vibrational quantum number v=0 → vibrational ground state. If any mode has v>0, or multiple modes have v>0 → vibrationally excited state.

**The number of excited-state vibrational levels is enormous** (v has no upper bound in the harmonic model, plus combinations of excited modes). Computing all transitions is impossible.

**Solution:** Transitions with small FC factors have small transition dipole moments and negligible spectral impact. These can be screened out. Additionally, one can specify an energy range — transitions outside this range need not be computed.

**FCClasses** is a systematic pre-screening method that estimates and classifies transitions, computing only those important for the actual spectrum. The screening threshold maps to computational cost — typically only one parameter (number of integrals to compute) needs adjustment. It is a black-box method.

## Gaussian workflow: Anisole S₀→S₁ example

### Step 1: Excited-state optimization + frequency

```
%chk=anisole_exc.chk
#p cis(root=1)/6-31G* opt freq=saveNM

anisole S1

0 1
[coordinates]
```

Key points:
- `root=1` — compute the 1st excited state (S₁). Change to study S₂, S₃, etc.
- `freq=saveNM` — saves excited-state vibrational information to the .chk file
- Also produces the electronic transition dipole moment at the excited-state equilibrium geometry (needed for FC method)
- Can use TDDFT instead of CIS: `td(root=1)/6-31G*`

**Note:** Only harmonic frequencies are supported for vibronic spectra. Anharmonic requires 3rd+ order derivatives, which TDDFT cannot provide analytically (CIS has 2nd derivatives, TDDFT only has 1st).

### Step 2: Ground-state optimization + FC calculation

```
%chk=anisole.chk
#p hf/6-31G* opt freq=FC nosymm

anisole S0

0 1
[coordinates]

anisole_exc.chk
```

Key points:
- `freq=FC` — uses FC method to compute transitions from S₀ vibrational ground state to S₁ various vibrational states
- Uses the current S₀ Hessian and the S₁ vibrational info from the .chk file
- Computes transition energies, transition dipole moments, and converts to oscillator strengths
- The last line is the path to the excited-state .chk file from Step 1

### Understanding the output

**0-0 transition energy:**
```
Energy of the 0-0 transition:  47860.6879 cm^(-1)
```
This can also be obtained by subtracting ZPE-included energies:
```
Excited state: Sum of electronic and zero-point Energies=  -344.222064
Ground state:  Sum of electronic and zero-point Energies=  -344.440134
ΔE = (-344.222064 + 344.440134) × 219474.6363 = 47860 cm⁻¹
```

**Individual vibronic transitions:**
```
Initial State: <0|
Final State: |15^2>
     DeltaE =  1683.4671 | TDMI**2 = 0.1337E-01, Intensity = 0.4341E-01
```
- Initial: S₀ vibrational ground state
- Final: S₁ with mode 15 at v=2
- DeltaE: relative to 0-0 transition energy (not absolute)
- TDMI**2: squared transition dipole moment
- Intensity: oscillator strength

**Combination bands:**
```
Initial State: <0|
Final State: |26^1;17^1>
```
- S₁ with mode 26 at v=1 AND mode 17 at v=1 simultaneously

**Final spectrum data:**
Gaussian outputs energy-intensity pairs ready for plotting:
```
Axis X = Energy (in cm^-1)
Axis Y = Intensity
...
       47476.6879        0.247451D-02
       47484.6879        0.311828D-02
       47492.6879        0.391045D-02
...
```
Plot these two columns in Origin (or any plotting software) to get the vibronic spectrum.

## Additional parameters

Use `freq=(FC,ReadFCHT)` to read control parameters. Place them in the input file after coordinates (with blank lines as separators):

```
[coordinates]

MaxInt=200 SpecHwHm=1 MaxOvr=100...

[excited-state chk path]
```

### Important parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| **MaxOvr** | 20 | Maximum vibrational quantum number for excited state. For transitions with large geometry changes (wide spectral range), increase this value. Otherwise spectrum will be incomplete. |
| **MaxInt** | 100 (×10⁶) | Number of integrals per transition class, in millions. Default = 10⁸. **This is the main cost determinant** — not system size, basis set, or method. Higher = more accurate spectrum but more expensive. |
| **SpecHwHm** | 135 cm⁻¹ | Half-width at half-maximum for Gaussian broadening in the simulated spectrum. Larger = smoother curve, less vibrational detail. Very large = single broad peak (not "vibrationally resolved" anymore). |
| **PrtInt** | 0.01 | Minimum intensity ratio to 0-0 transition for output. If a transition's oscillator strength > 1% of 0-0, it is printed. |
| **DoTemp** | Off | Include temperature effects. Default = 0K (only vibrational ground state of initial state). **Note:** This keyword exists in Gaussian but does NOT actually work. |
| **SPECMIN/SPECMAX** | — | `NORELI00 SPECMIN=37900 SPECMAX=42000` — compute only transitions in this energy range (cm⁻¹). |
| **SPECRES** | 8 cm⁻¹ | Spectral resolution. Output energy points are spaced by this value. Smaller = higher resolution but more expensive. |
| **PrtMat** | 0 | 1 = print Duschinsky matrix J; 2 = print displacement vector K. |

### Duschinsky rotation

The Duschinsky effect describes how normal modes mix (rotate) upon electronic transition:

```
Q'' = J × Q' + K
```

- Q''ᵢ = normal coordinate of mode i in excited state
- Q'ᵢ = normal coordinate of mode i in ground state
- J = Duschinsky matrix (rotation/mixing)
- K = displacement vector

If J = identity matrix → no mode mixing. Significant deviation from identity means excited-state modes are significant linear combinations of ground-state modes.

### Saving computation with readfc

When re-computing with different parameters, use `readfc` to read the existing Hessian from the .chk file:

```
%chk=anisole.chk
#p hf/6-31G* geom=check guess=read freq=(readfc,FC,readFCHT) nosymm

anisole S0

0 1

SPECHWHM=10

anisole_exc.chk
```

This avoids re-computing the Hessian, saving significant time.

### Forcing calculation when FC factor is too small

For systems with large geometry change between ground and excited states:
```
ERROR: The Franck-Condon factor corresponding to the overlap integral between both vibrational ground states is too small: |<0'|0">|² = x
```

Default threshold: x < 10⁻⁴ → abort.

**Fix:** Use `readFCHT` with `ForceFCCalc` keyword to force calculation. The FC method is fundamentally less suitable for large geometry changes, so results should be interpreted with caution.

## Frequency scaling approximation

Harmonic frequencies differ from anharmonic frequencies. Frequency scaling factors (sobereva.com/221) correct harmonic frequencies.

To approximate anharmonic vibronic spectra:
1. Compute anharmonic frequencies for ground state (Gaussian 09 supports PT2 anharmonic)
2. Divide anharmonic by harmonic for each mode → scaling factors
3. Use `SclVec` keyword to apply these scaling factors
4. The program mixes the scaling factors via the Duschinsky matrix to estimate excited-state scaling factors

**Limitation:** Direct anharmonic calculation for excited states would require high-order derivatives — not feasible. This indirect approach through ground-state scaling is an approximation.

See `vibronic_spectra_G09-A02.pdf` (idea.sns.it/files/idea/docs/vibronic_spectra_G09-A02.pdf) for examples.

## Emission spectra

Gaussian can also compute vibrationally resolved **emission** spectra:
- Same input as absorption
- In Step 2 (ground-state calculation), use `freq(FC,emission)`
- **Does not support HT or FCHT** for emission — FC only

## Ionization spectra

Vibrationally resolved photoelectron spectra (ionization):
- Same as absorption workflow
- Replace excited-state calculation with cation calculation
- Ground-state calculation remains the same

## Method limitations

| Method | FC | HT | FCHT | Notes |
|--------|----|----|----|-------|
| **CIS** | ✓ | ✓ | ✓ | Requires `freq=numer` for HT (needs transition dipole derivative) |
| **TDDFT** | ✓ | ✗ | ✗ | Only FC supported (no analytic 2nd derivative) |

## References

- sobereva.com/223 — This article (vibronic spectra calculation)
- sobereva.com/224 — Plotting spectra with Multiwfn
- sobereva.com/221 — Vibrational frequency scaling factors
- FCClasses program: village.pi.iccom.cnr.it/Software
- vibronic_spectra_G09-A02.pdf: idea.sns.it/files/idea/docs/vibronic_spectra_G09-A02.pdf
