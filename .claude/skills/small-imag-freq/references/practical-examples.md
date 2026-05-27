# Practical Examples with Shermo

Workflow examples for computing thermodynamic quantities using Shermo when small imaginary frequencies are present.

## Getting frequency data from Gaussian output

Shermo reads frequency data from Gaussian output files (.log or .out). The frequency section in Gaussian output looks like:

```
 Harmonic frequencies (cm**-1), IR intensities (KM/Mole), Raman scattering
 activities (pm**4/AMU), depolarization ratios (300K after 50 degrees)
                        1       2       3       4       5       6       7
 Frequencies --       127.4   289.3   412.7   558.9   723.1   891.2  1024.5
 ...
```

Imaginary frequencies appear with a negative sign or "i" notation.

## Shermo input file (thermo.inp)

Basic Shermo input file format:

```
# Basic settings
T 298.15          ! Temperature in Kelvin
P 1.0             ! Pressure in atm

# Frequency data source
freqfile gaussian_output.log    ! Gaussian output file containing frequencies

# QRRHO model selection
ilowfreq 2         ! 0=RRHO, 1=QRRHO(Truhlar), 2=QRRHO(Grimme), 3=QRRHO(Minenkov)

# Imaginary frequency treatment
imagreal 0         ! 0=ignore imag freq (default), N=treat |imag|<N as real

# Output options
prtvib 1           ! Print each mode's contribution to thermodynamic quantities
```

## Example 1: Single small imaginary frequency (~20i cm⁻¹)

Scenario: B3LYP/6-31G(d) Opt+Freq of a large flexible molecule shows one imaginary frequency at -18.7i cm⁻¹. Computational resources don't allow re-optimization.

### Computing electronic energy + ZPE + U(0)

```
# thermo.inp
T 298.15
P 1.0
freqfile molecule.log
ilowfreq 2           ! QRRHO(Grimme) — good practice even if not strictly needed for ZPE
imagreal 0           ! Ignore the imaginary frequency
prtvib 1
```

Run:
```
Shermo thermo.inp
```

Output will show ZPE and U(0) — the imag freq contribution is automatically skipped.

### Computing entropy and Gibbs free energy

```
# thermo.inp
T 298.15
P 1.0
freqfile molecule.log
ilowfreq 2           ! QRRHO(Grimme) — essential for entropy with low-freq modes
imagreal 0           ! Do NOT treat imag as real (Sobereva's recommendation)
prtvib 1
```

**Interpretation:** The free energy will have an error of approximately 5-6 kJ/mol compared to the true minimum. This is borderline acceptable for room-temperature calculations.

## Example 2: Multiple small imaginary frequencies

Scenario: A weakly bound complex has three imaginary frequencies: -12.3i, -27.8i, -45.1i cm⁻¹.

**Recommendation: Eliminate the imaginary frequencies if possible.** If not:

```
# thermo.inp
T 298.15
P 1.0
freqfile complex.log
ilowfreq 3           ! QRRHO(Minenkov) — preferred for multiple imag freq
imagreal 50          ! Treat all imag freq with |imag| < 50 as real
prtvib 1
```

**Warning:** Results with multiple imaginary frequencies have large uncertainties. Use only as a rough estimate.

## Example 3: Comparing RRHO vs QRRHO

To see the difference between models, run Shermo with different `ilowfreq` settings:

```bash
# RRHO (traditional)
echo "T 298.15
freqfile molecule.log
ilowfreq 0
prtvib 1" > rrho.inp
Shermo rrho.inp > rrho.out

# QRRHO(Grimme)
echo "T 298.15
freqfile molecule.log
ilowfreq 2
prtvib 1" > grimme.inp
Shermo grimme.inp > grimme.out

# QRRHO(Truhlar)
echo "T 298.15
freqfile molecule.log
ilowfreq 1
prtvib 1" > truhlar.inp
Shermo truhlar.inp > truhlar.out

# QRRHO(Minenkov)
echo "T 298.15
freqfile molecule.log
ilowfreq 3
prtvib 1" > minenkov.inp
Shermo minenkov.inp > minenkov.out
```

Compare the entropy and free energy values across the four outputs. The RRHO result will typically show much larger entropy (and thus different free energy) for systems with low-frequency modes.

## Example 4: High-temperature calculation

Scenario: Computing thermodynamics at 500 K for a system with one small imaginary frequency.

```
# thermo.inp
T 500.0            ! High temperature
P 1.0
freqfile molecule.log
ilowfreq 3           ! QRRHO(Minenkov) — preferred at high T
imagreal 0
prtvib 1
```

**Note:** At higher temperatures, the -T×S term is larger, so entropy errors cause larger free energy errors. High-T calculations are more sensitive to the presence of imaginary frequencies.

## Example 5: "Imaginary as real" approach (for comparison)

To compare the effect of treating small imaginary frequencies as real:

```bash
# Without imagreal
echo "T 298.15
freqfile molecule.log
ilowfreq 2
prtvib 1" > normal.inp
Shermo normal.inp > normal.out

# With imagreal=50 (treat all |imag| < 50 as real)
echo "T 298.15
freqfile molecule.log
ilowfreq 2
imagreal 50
prtvib 1" > imagreal.inp
Shermo imagreal.inp > imagreal.out
```

Compare the two outputs. The difference shows the impact of the "imaginary as real" treatment. Sobereva generally recommends against this approach, but it can be informative to see the magnitude of the difference.

## Interpreting prtvib=1 output

With `prtvib 1`, Shermo outputs each vibrational mode's individual contribution to thermodynamic quantities. This is useful for:

1. **Identifying which modes contribute most to entropy** — typically the lowest-frequency real modes
2. **Understanding the impact of missing an imaginary mode** — compare its expected contribution (if it were real at similar frequency) with the total
3. **Diagnosing problematic systems** — if many modes are below 50 cm⁻¹, the system is very flexible and small imag freq treatment matters less relative to the overall low-frequency spectrum

## Shermo download and documentation

- Manual and download: sobereva.com/552
- Shermo supports output from Gaussian, ORCA, GAMESS, and other programs
- Supports single-point thermodynamics, reaction thermodynamics, and isotope effects
