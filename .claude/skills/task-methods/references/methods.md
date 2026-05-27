# Theoretical Methods in Computational Chemistry

Detailed description of every common theoretical method, based on Sobereva's article (sobereva.com/723).

## Overview

All tasks described in `references/task-types.md` require computing the system's energy (and often derivatives) at different structures. **How** you compute energy and its derivatives is the domain of theoretical methods.

## Non-quantum methods

### Molecular force field (MM)

**Also known as:** Classical force field, molecular mechanics (MM), empirical potential function

**Idea:** Simple model for the system (typically one atom = one particle, electrons and nuclei not separated). Simple mathematical functions (potentials) describe interatomic interactions. Example: electrostatic interaction modeled by assigning point charges to atomic positions and computing via Coulomb's law.

**Advantages:**
- Extremely low computational cost

**Key limitations:**
1. **Cannot describe chemical reactions** — bonding relationships are fixed from the start (exceptions: reactive force fields, which are much more expensive and supported by fewer programs)
2. **Heavily parameter-dependent** — affects both accuracy and applicable systems; finding/building appropriate parameters is not easy

**Note:** Despite "molecular" in the name, not limited to molecular systems — inorganic solids, metal clusters, etc. are also simulated.

### Machine learning potential

**Idea:** Use machine learning to construct abstract relationships between atom-coordinate-dependent molecular descriptors (distance matrix, energy matrix, etc.) and energy. More complex than traditional force field potentials.

**Cost:** Low to medium (some complex ML potentials now match semi-empirical cost)

**Accuracy:** Depends on training data quality

### Reactive force field

**Idea:** Force field that can describe bond breaking/formation.

**Cost:** Much higher than standard force fields

**Support:** Fewer programs support reactive force fields

## Quantum chemistry methods

### Density Functional Theory (DFT)

**Status:** Most widely used method in quantum chemistry / first-principles calculations.

**Why:** Excellent cost-performance ratio. With appropriate exchange-correlation functional choice, can achieve very good results sufficient for most research needs. Significantly more accurate than force fields (unless the force field is specifically trained for a particular system). Much more universal.

**Cost:** Higher than force field by many orders of magnitude (larger systems = larger gap)

**Key factors:** Exchange-correlation functional choice is the decisive factor for DFT accuracy.

**Common functionals:** B3LYP, ωB97XD, PBE0, TPSS, etc. See popularity rankings at sobereva.com/706. Functional selection guidance: sobereva.com/272.

**Dispersion:** Many functionals (e.g., B3LYP) describe dispersion poorly or fail entirely. Can be fixed with dispersion corrections — see sobereva.com/413 and sobereva.com/210.

**Two forms:**
- **KS-DFT (Kohn-Sham DFT):** The absolute mainstream. Involves orbital wavefunctions. This is what people mean by "DFT" in practice.
- **Orbital-free DFT:** Non-mainstream. No orbitals involved. Very limited applicability. Supported by few programs.

### Hartree-Fock (HF)

**Status:** Widely used before DFT's rise. Now completely obsolete.

**Why obsolete:** Cost is not significantly lower than DFT (DFT with RI technology can actually be noticeably faster), while accuracy is much worse.

### Post-HF methods

**What:** A family of methods (CCSD(T), MP2, CISD, etc.) that build on HF to additionally account for electron dynamic correlation.

**HF's problem:** Accounts for neither dynamic nor static correlation → poor accuracy.

**Post-HF fix:** Accounts for dynamic correlation to varying degrees, at the cost of much higher computational expense.

**Examples:**
- MP2 — lowest-cost post-HF, moderate improvement
- CCSD — higher accuracy, much more expensive
- CCSD(T) — "gold standard," very expensive

### MCSCF (Multi-Configuration Self-Consistent Field)

**What:** Primarily addresses HF's lack of static correlation consideration.

**Limitation:** Little or no dynamic correlation → results are not great either.

**Most common implementation:** CASSCF

**Use case:** Systems where static correlation is the dominant concern (bond breaking, near-degeneracy, transition metals, excited states).

### Multireference methods

**What:** Build on MCSCF to additionally account for dynamic correlation.

**Accuracy:** Overall excellent, highly universal.

**Drawbacks:** Complex to use, expensive.

**Typical implementations:** CASPT2, NEVPT2, MRCI

### Semi-empirical methods

**What:** A family of methods that simplify HF to dramatically reduce cost.

**Cost:** Tiny fraction of HF cost

**Accuracy:** Significantly reduced overall

**Limitation:** Introduce element-dependent parameters → can only be used for limited elements.

**Typical examples:** AM1, PM3, PM6

**Note:** Some complex ML potentials now match semi-empirical cost.

### GFN-xTB

**What:** Semi-empirical-level method incorporating some DFT ideas.

**Versions:** GFN1-xTB, GFN2-xTB (commonly used)

**Cost:** Similar to semi-empirical methods

**Accuracy:** >= mainstream semi-empirical methods, but still far from DFT

**History:** Developed since 2017. Highly similar to the earlier DFTB method.

## Ab initio vs empirical

**Ab initio methods:** No empirical parameters introduced (with rare exceptions like CASPT2 shift parameter). Parameters depend only on physical constants.
- Includes: HF, post-HF, MCSCF, multireference methods

**Empirical methods:** Introduce significant empirical parameters.
- Includes: Force fields, semi-empirical, GFN-xTB

**DFT:** Ambiguous. The theoretically exact functional has no parameters, but all practical functionals contain some empirical parameters (varying amounts). The debate over whether DFT is ab initio is pointless — it's just terminology.

**WFT (Wavefunction Theory):** Sometimes used to collectively refer to HF, post-HF, MCSCF, multireference — methods with physics fully based on wavefunctions. When "WFT" is used, DFT is not confused with these methods.

## First-principles vs quantum chemistry

**"First-principles calculation":** Mainstream usage refers to quantum chemistry methods for **periodic systems**. Includes DFT (most commonly used) and strict ab initio methods. DFTB is often counted as first-principles for periodic systems despite its empirical parameters.

**"Quantum chemistry calculation":** Usually refers to **isolated (non-periodic) systems** — molecules, clusters.

**Program classification:**
- **Quantum chemistry programs:** Gaussian, ORCA, GAMESS-US (primarily isolated systems)
- **First-principles programs:** CP2K, Quantum ESPRESSO (primarily periodic systems)

**Note:** "Quantum computing" is NOT the same as "quantum chemistry calculation." Quantum computing emphasizes quantum algorithms implemented on quantum computers — can but is not limited to quantum chemistry research.

## Composite methods

### QM/MM

**Idea:** Use quantum chemistry (QM) to describe one part of the system, molecular mechanics (MM) to describe another part, with proper coupling between the two.

**Advantage:** Much cheaper than treating everything with QM (MM part cost is "nine cows, one hair" compared to QM part).

**Cost:** MM region accuracy is worse than QM region. Most force fields cannot describe bond breaking/formation in the MM region.

**Critical requirement:** Proper QM/MM partitioning — reaction center and atoms requiring accurate description must be in QM region;次要 "environment" atoms can be in MM region.

**Warning:** Many beginners see QM/MM in papers, think it sounds impressive, and want to use it without understanding its limitations. This is naive — blind use of QM/MM is self-inflicted suffering.

### ONIOM

**Idea:** Partition into different regions, combine any two theoretical methods for different parts.

**ONIOM(QM:MM):** Specifically refers to combining quantum chemistry with force field. Similar purpose to QM/MM but implemented differently.

**Important:** ONIOM and QM/MM are NOT the same. Do not confuse them.

See sobereva.com/597 for guidance on cluster models vs ONIOM for protein-ligand interactions.

## Excited state methods

Ground state methods (semi-empirical, HF, post-HF, DFT) can compute excited states via delta-SCF but this is not general-purpose.

**Dedicated excited state methods:**
- **TDDFT** — Most common, good cost-performance
- **CIS** — Obsolete, poor accuracy
- **EOM-CCSD** — High precision, very expensive

See sobereva.com/265 for excited state calculation guidance.

**Force fields for excited states:** Most force fields describe ground state electronic states. However, if force field parameters are specifically fitted to excited state PES, they can describe excited states — but existing such force fields are for extremely specific systems and are not general-purpose. ML potentials same situation.

**QM/MM for excited states:** Can describe excited states only if electronic excitation occurs entirely within the QM region.

**Excited state dynamics:**
- Simply computing forces on an excited state PES at each MD step is NOT the full picture
- Often requires internal conversion, intersystem crossing rates
- Nonadiabatic dynamics (surface hopping, etc.) is more complex — specialized programs: Newton-X, SHARC
- Supporting excited state theory + MD in a program ≠ being able to rigorously study excited state dynamics

## Method comparison summary

| Method | Cost | Dynamic corr. | Static corr. | Reactions? | Ab initio? | Empirical? |
|--------|------|--------------|--------------|------------|------------|------------|
| Force field | ~ | N/A | N/A | No | No | Heavy |
| ML potential | ~- | N/A | N/A | Usually no | No | ML-trained |
| Reactive FF | ~- | N/A | N/A | Yes | No | Heavy |
| Semi-empirical | - | No | No | Yes | No | Heavy |
| GFN-xTB | - | Approx. | No | Yes | No | Moderate |
| HF | -- | No | No | Yes | Yes | None |
| DFT | -- | Approx. | No | Yes | Debated | Some |
| MP2 | --- | Yes | No | Yes | Yes | None |
| CCSD | ---- | Yes | No | Yes | Yes | None |
| CASSCF | ---- | Limited | Yes | Yes | Yes | None |
| CCSD(T) | ----- | Yes | No | Yes | Yes | None |
| CASPT2 | ----- | Yes | Yes | Yes | Yes | Shift only |
| NEVPT2 | ----- | Yes | Yes | Yes | Yes | None |
| MRCI | ------ | Yes | Yes | Yes | Yes | None |

Cost scale: ~ (force field) < - (semi-empirical/xTB) < -- (HF/DFT) < --- (MP2) < ---- (CCSD/CASSCF) < ----- (CCSD(T)/CASPT2) < ------ (MRCI)

## Basis functions and basis sets

All methods based on quantum theory (everything except force fields and ML potentials) use molecular orbitals in numerical solving. Most programs expand molecular orbitals as linear combinations of basis functions.

**Two common basis function types:**
1. **Atom-centered basis functions** (Gaussian-type orbitals, GTO): Centered at atomic nuclei. Used by Gaussian and most quantum chemistry programs, and some first-principles programs like CP2K.
2. **Plane wave basis functions:** Cover the entire unit cell. Used by most first-principles programs for periodic systems.

**Basis set:** For atom-centered basis functions, defines how many and what parameters of basis functions to use for each element. Examples: 6-31G*, def2-TZVP, cc-pVDZ.

**Quality rule:** Better basis set → results closer to complete basis set limit → method's inherent accuracy is better utilized. But cost increases.
- Good method + bad basis set = bad results
- Bad method + good basis set = bad results
- Good method + good basis set = good results

**Semi-empirical / GFN-xTB:** Basis functions are built into the method definition — you do NOT and CANNOT specify basis sets for these methods.
