---
name: excited-state
description: This skill should be used when the user asks to "TDDFT", "excited state", "激发态", "vertical excitation", "vertical emission", "adiabatic excitation", "oscillator strength", "absorption spectrum", "UV-Vis", "charge transfer excitation", "Rydberg excitation", "local excitation", "CIS", "EOM-CCSD", "CASPT2", "TDA approximation", "vibronic spectrum", "Franck-Condon", "TDDFT functional selection", "range-separated functional", "ghost state TDDFT", "NTO analysis", "hole-electron analysis", "excited state optimization", "conical intersection", or mentions computing electronic excited states, absorption/emission spectra, or excited-state properties.
version: 0.1.0
---

# Excited State Calculation

Guidance for computing electronic excited states, absorption/emission spectra, and excited-state properties, based on Sobereva's articles (sobereva.com/265, sobereva.com/284, sobereva.com/223).

## What excited state calculations compute

| Property | Description | Computational cost |
|----------|-------------|-------------------|
| **Vertical excitation energy** | Excitation at fixed geometry. Most common. Correlates with experimental absorption maximum (typically overestimates by 0.1-0.3 eV). | Lowest |
| **Adiabatic excitation energy** | S₀ minimum → Sₙ minimum. Requires excited-state optimization. Approximates 0-0 transition energy (overestimates by ~0.1 eV due to ZPE difference). | Moderate |
| **Oscillator strength** | Transition intensity. Combined with excitation energies, produces theoretical spectra via broadening. | Same as excitation energy |
| **Excited-state geometry** | How structure changes upon excitation. May involve H-transfer, large conformational changes. | Moderate (needs excited-state opt) |
| **Potential energy surface** | Barriers, conical intersections, avoided crossings. Critical for photochemistry and non-radiative decay (ISC, IC). | High (multireference needed for crossings) |
| **Excited-state properties** | Dipole moment, atomic charges, bonding, aromaticity of excited states. Requires excited-state wavefunction. | Same as excitation energy |

## Quick reference: Method selection

| Method | Accuracy | Cost | Best for |
|--------|----------|------|---------|
| **TDDFT (PBE0)** | ±0.1-0.3 eV for valence LE | Low | **Default for most systems** |
| **TDDFT (CAM-B3LYP/wB97XD)** | ±0.2-0.4 eV for CT/Rydberg | Low | Charge-transfer, Rydberg excitations |
| **TDDFT (TDA)** | Worse for singlets, better for triplets | Slightly lower | Triplet excitations, ORCA hybrid functionals |
| **Double-hybrid TDDFT** | ~30% better than PBE0 | Moderate | High-accuracy valence singlet |
| **EOM-CCSD** | <0.3 eV | High | Benchmark-quality for single-reference |
| **LR-CC3** | <0.1 eV (gold standard) | Very high | Reference values |
| **CASPT2 (MS)** | <0.2 eV | Moderate-high | Multireference, photochemistry, double excitations |
| **CIS** | Overestimates by 1-2 eV | Very low | Qualitative only, excited-state frequency (has analytic 2nd derivative) |
| **ZINDO** | Better than CIS | Very low | Large systems, quick π-π*/n-π* estimate |

## 1. TDDFT — the default method

### Basis set selection

| Excitation type | Minimum | Recommended | Ideal |
|----------------|---------|-------------|-------|
| **Valence (general)** | 6-31G* | 6-311G* | def2-TZVP |
| **Valence (large systems)** | 6-31G* | — | — |
| **Rydberg** | 6-31+G* | aug-cc-pVTZ | d-aug-cc-pVTZ |
| **Anion** | 6-31+G* | aug-cc-pVTZ | — |

**Diffuse functions are essential** for Rydberg excitations and anions. For valence excitations, diffuse functions are not needed.

### Functional selection by excitation type

#### Valence local excitation (singlet)
| Functional | HF% | Error | Notes |
|-----------|-----|-------|-------|
| **PBE0** | 25% | ±0.1-0.3 eV | **First choice** |
| B3LYP | 20% | Slightly worse than PBE0 | Good alternative |
| **Trend:** Higher HF% → higher excitation energy. Pure functionals (0% HF) underestimate severely. BHandHLYP (50%), M06-2X (54%) overestimate. |

For large conjugated systems (dyes), 25% HF may be too low — consider PBE38 (37.5%) or BMK (42%). See sobereva.com/282 for HF% of common functionals.

#### Valence local excitation (triplet)
- **All methods underestimate** triplet excitation energies (unlike singlets)
- **M06-2X** performs well for triplets
- PBE0/B3LYP are mediocre
- HF% effect is much weaker than for singlets

#### Charge-transfer (CT) and Rydberg excitations
| Functional | Notes |
|-----------|-------|
| **CAM-B3LYP** | Range-separated, recommended |
| **wB97XD** | Range-separated + dispersion, recommended |
| **M06-2X** | High HF% (54%), works but not range-separated |
| **LC-wPBE** | Range-separated, 100% long-range HF |
| **B3LYP/PBE0** | **Do NOT use** — severe underestimation due to wrong long-range behavior |

**Optimize ω parameter** for range-separated functionals before computing. See sobereva.com/346 for the optDFTw tool. System-specific ω tuning gives better accuracy than empirical ω values.

### Ghost states

Low-HF% functionals (GGA, B3LYP) can produce **ghost states** for large conjugated systems:
- Artificially low excitation energy
- CT character with near-zero oscillator strength
- No physical meaning — artifacts of self-interaction error (SIE)
- Waste computation time, may push real states above your state count

**Fix:** Use higher HF% or range-separated functional.

### Tamm-Dancoff Approximation (TDA)

TDA ignores the B matrix in TDDFT, making it formally similar to CIS on DFT orbitals.

| Aspect | Full TDDFT | TDA |
|--------|-----------|-----|
| Singlet accuracy | Better | Slightly worse |
| Triplet accuracy | Worse | **Improved** |
| Oscillator strength | More accurate | Underestimated |
| UV-Vis/ECD spectra | Better | Worse |
| Programming | More complex | Simpler |
| ORCA support | Pure functionals only | All functionals (ORCA 3.x) |

**Recommendation:** Use full TDDFT for absorption/ECD spectra. Consider TDA for triplet-only studies.

### Double-hybrid TDDFT

- ORCA only — computes TDDFT with CIS(D)-style perturbative correction
- B2PLYP is the weakest double-hybrid; **B2GP-PLYP** is better
- ~30% error reduction over PBE0 for valence singlet excitations
- More expensive but still much cheaper than EOM-CCSD

### Solvent effects

**Solvent effects are more important for excited states than ground states.**
- TDDFT + PCM works well — supports non-equilibrium solvation and state-specific calculations
- Implicit solvent shifts absorption peaks (red or blue shift depending on state-solvent interaction)
- For strong solute-solvent interactions, use explicit solvent models
- For protein environments, use QM/MM or background point charges
- **Neither implicit nor explicit solvent captures** spectral broadening or detail loss due to solvent dynamics — requires simulation

### How many states to compute?

| System size | Recommended states |
|-------------|-------------------|
| Small (<20 atoms) | 10-20 |
| Medium (20-50 atoms) | 30-60 |
| Large (50+ atoms) | 80-100+ |

**Tip:** Use sTDA (JCP, 138, 244104) for a quick pre-scan — nearly free, shows roughly how many states are needed to cover your energy range of interest (typically 2-7 eV for UV-Vis). For very large systems needing hundreds of states, use sTDA results directly.

## 2. Other excited state methods

### CIS
- Qualitative only — overestimates by 1-2 eV
- Good for charge-transfer excitations
- Has analytic 2nd derivatives in Gaussian → useful for excited-state frequencies
- Generally obsolete for energy calculations

### Coupled cluster methods
| Method | Accuracy | Notes |
|--------|----------|-------|
| **EOM-CCSD** | <0.3 eV for single excitations | Standard in Gaussian. Fails for multireference and double excitations. |
| **EOM-CCSD(T)** | Better for double excitations | Various implementations, not standardized. |
| **EOM-CCSDT** | <0.05 eV | Only a few atoms. Approx. EOM-CCSDT-3 is cheaper. |
| **LR-CC3** | ~0.1 eV | **Gold standard for excitation energies.** Use as reference. Dalton recommended. |
| **LR-CC2** | Worse than EOM-CCSD | Often used as benchmark but not significantly better than good TDDFT. |

### CASPT2
- **Most popular high-accuracy method for small molecules**
- Error <0.2 eV, much cheaper than CC3
- **Best for:** Multireference ground states, double-excitation character, photochemistry (conical intersections)
- **Requires experience** in active space selection — not black-box
- Use **MS-CASPT2** (multi-state) over SA-CASPT2 for conical intersections and valence-Rydberg mixing
- Molpro/Molcas are the main programs; Molpro supports analytic gradient
- Watch for intruder states — fix with level shift

### MCSCF/CASSCF
- Not for accurate excitation energies — provides reference wavefunction with static correlation for CASPT2/MRCI
- **Only method** that correctly describes conical intersections (equally treats both crossing states)
- S₀-T₁ intersection: DFT also works

### ΔSCF
- Adjust initial guess to excite an electron from occupied to virtual orbital of different irreducible representation
- Same cost as ground-state calculation
- **Limitations:** Requires symmetry, hard to compute multiple states, no oscillator strength

### Spin multiplicity change (for triplets)
- To study T₁ (lowest triplet): simply change multiplicity to 3 in the input
- Same cost as ground state, gives excited-state orbitals and spin density
- **Only works for lowest state of given multiplicity** (T₂, T₃ need TDDFT)

### Semi-empirical methods
| Method | Notes |
|--------|-------|
| **ZINDO/S** | Best semi-empirical for excitation. Good for π-π*/n-π* of organics and some transition metals. Bad for CT, Rydberg, anions, double excitations. |
| **INDO/X** | Re-parameterized ZINDO. Half the error of ZINDO. CHON only. Not publicly available. |
| **OM3** | Thiel's method. ~2× TDDFT error. Not publicly available. |

## 3. Excitation type identification

### Classification hierarchy

```
Electronic excitation
├── Valence excitation (electron → valence orbital)
│   ├── Local excitation (LE) — electron distribution unchanged
│   └── Charge-transfer (CT) — electron distribution shifts significantly
│       ├── Intramolecular CT
│       └── Intermolecular CT
│
└── Rydberg excitation (electron → diffuse Rydberg orbital)
```

### Valence excitation by orbital character
- **π→π*** — most common for conjugated systems
- **n→π*** — heteroatom lone pair → π* (low energy, often forbidden)
- **σ→π*** — higher energy
- **n→σ*** — higher energy
- **σ→σ*** — highest energy (saturated systems)
- **d→d, d→p** — transition metals
- **MLCT, LMCT, LLCT, MMCT** — transition metal complexes

### How to identify excitation type

1. **Dominant orbital pair (>75% contribution):** Look at the two orbitals directly
2. **Multiple orbital pairs:** Use Multiwfn electron-hole analysis or NTO analysis
3. **Multiwfn tools (sobereva.com/437):**
   - Electron-hole distribution (sobereva.com/434)
   - NTO analysis (sobereva.com/377, sobereva.com/91)
   - Transition density matrix
   - Charge transfer analysis
   - Δr index for CT distance

### Key rule for CT and Rydberg excitations
Both involve large changes in electron distribution (small electron-hole overlap). **Must use range-separated functional (wB97XD, CAM-B3LYP) or at least high-HF% functional (M06-2X).** Standard B3LYP/PBE0 will give wrong results.

## 4. HF% tuning guide

If your computed excitation energies are systematically:
- **Blue-shifted (too high):** Use a functional with lower HF%
- **Red-shifted (too low):** Use a functional with higher HF%

See sobereva.com/282 for HF% of common functionals.

## Additional Resources

For detailed methodology and comprehensive coverage, consult:

- **`references/tdfft-guide.md`** — Comprehensive TDDFT guide: functional selection by excitation type, basis set recommendations, TDA analysis, double-hybrid TDDFT, solvent models, ghost states, state count estimation, sTDA pre-scan
- **`references/vibronic-spectra.md`** — Vibrationally resolved electronic spectra: Franck-Condon, Herzberg-Teller, FCHT methods, Gaussian freq=FC workflow, parameter tuning (MaxInt, MaxOvr, SpecHwHm), Duschinsky rotation, emission spectra, frequency scaling approximation
