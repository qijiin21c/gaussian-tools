# Pseudopotential Theory and Function Forms

Detailed explanation of pseudopotential theory, function forms, and construction methods. Based on Sobereva's article (sobereva.com/188).

## What pseudopotentials do

1. **Replace core electrons:** Describe chemically uninteresting inner electrons with an effective potential field, eliminating the need to explicitly represent them — dramatically reduces computational cost
2. **Incorporate relativistic effects:** Implicitly represent scalar relativistic effects. From the 4th period onwards, relativistic effects begin to appear (ignorable but not critical). From the 5th period onwards, relativistic effects are **不可忽视** — ignoring them can lead to qualitatively wrong results

## Pseudo-orbitals

After applying pseudopotentials, the resulting orbitals are called **pseudo-orbitals**:

- The lowest batch of pseudo-orbitals have energies close to or exactly matching the valence orbital energies from all-electron calculations
- **Inner region (r < rc):** Pseudo-orbitals have no nodes (smoothed out), unlike real valence orbitals
- **Valence and outer region (r > rc):** Pseudo-orbitals closely match or exactly match real orbital shapes

With properly designed pseudopotentials, pseudo-orbitals can reasonably reproduce the properties exhibited by real valence orbitals: bonding patterns, valence-region electron density distribution, etc.

## Pseudopotential properties

- Defined per **element**, sometimes with different versions for specific valence states, relativistic treatment methods, or number of core electrons replaced
- For molecular systems, the total pseudopotential is the **sum** of pseudopotentials for each atom
- Requires good **transferability** — must work in different chemical environments
- **Angular momentum dependent** (depends on quantum number l)
- Dependence on principal quantum number n and magnetic quantum number m is generally not considered
- (2-component and 4-component relativistic pseudopotentials also depend on total angular momentum j — not covered here)

## Construction methods

### Shape-consistent pseudopotentials (Los Alamos / Lanl type)

Construction steps:
1. For the target atom, select which orbitals are core and which are valence, and select the atomic configuration
2. Perform numerical Hartree-Fock all-electron calculation to obtain valence orbital wavefunctions
3. Remove nodes from the r < rc portion of valence orbital wavefunctions, replacing with smooth functions (expressed as polynomials); leave r > rc region unchanged → creates pseudo-orbitals
4. For each angular momentum's pseudo-orbital, back-derive a potential function (numerically tabulated) such that the pseudo-orbital is exactly an eigenfunction of the HF equation plus this potential, with eigenvalue equal to the real valence orbital energy
5. Fit the numerically described potential function with Gaussian functions (easy because the potential is smooth)
6. Select a number of primitive Gaussian functions (GTFs) and optimize their exponents and contraction coefficients to best represent the pseudo-orbital → defines the pseudopotential basis set

### Energy-consistent pseudopotentials (Stuttgart / SDD type)

Construction approach differs significantly from shape-consistent:
- Target data: total valence electron energies of hundreds/thousands of electronic states of the atom and its ions (NOT individual valence orbital energies)
- Continuously adjust pseudopotential parameters to minimize the average difference between pseudopotential and relativistic all-electron calculations for these states' total valence electron energies
- Though not strictly requiring pseudo-orbitals to match real orbitals for r > rc, the results are very close in practice

## Pseudopotential and basis set pairing

**Using pseudopotentials requires valence-electron basis sets.** Each pseudopotential comes with standard matched basis sets. The same pseudopotential may have multiple basis sets of different quality or from different researchers.

| Pseudopotential | Matched basis sets |
|----------------|-------------------|
| Los Alamos | Lanl2DZ, Lanl2DZdp, Lanl08, LANL2TZ, LAV/LACV series |
| Stuttgart/Dresden | Standard SDD basis, (aug)-cc-pVnZ-PP series, def2 series for heavy elements |
| SBKJC/CEP | SBKJC, LFK (modified for polarizability) |

**Warning:** Do NOT use valence basis sets not specifically optimized for a given pseudopotential without experience. Different pseudopotentials' basis sets should NOT be freely interchanged. This is because pseudo-orbitals from different pseudopotentials have different radial shapes in the core region — using mismatched basis sets will fail to properly represent this region.

## The Hamiltonian with pseudopotentials

System Hamiltonian:
```
H = Σ[i] h'_i + ΣΣ[i>j] 1/r_ij
```

First term: sum of valence electron effective one-electron Hamiltonians
Second term: electrostatic interaction between valence electrons

Effective one-electron Hamiltonian:
```
h' = h + Σ[a] U_a
```

Where h is the standard one-electron Hamiltonian (kinetic energy + nuclear attraction), and U_a is the pseudopotential for atom a.

For HF (or DFT):
- The HF equation considers only valence electrons
- The Fock operator contains Coulomb and exchange terms built only from valence electrons, plus Σ[a] U_a and nuclear attraction
- Solving the HF equation yields pseudo-valence orbitals

## The pseudopotential function form in detail

Since pseudopotentials are spherically averaged, only the radial coordinate needs to be considered. All pseudopotentials follow this general form:

```
U(r) = U_L(r) + Σ[l=0 to L-1] [U_l(r) - U_L(r)] × P_l
```

Where:
- **L** is typically the highest angular momentum in core orbitals + 1
- **P_l = |l><l|** is the angular momentum projection operator for quantum number l
- P_l can be further written as a sum over magnetic angular momentum projection operators: P_l = Σ[m=-l to l] P_{l,m}

### Understanding the projection operator

- P_2 projects out d components (l=2)
- Applied to a p orbital (l=1): result is 0
- Applied to a d orbital: orbital remains unchanged
- Applied to a complex orbital: yields R(r) × Σ c_lm × Y_lm(θ,φ), where R is the radial part, Y_lm are spherical harmonics, and c_lm are the coefficients of each Y_lm component

### Physical meaning of the formula

- **All orbital components** receive the U_L potential
- **Components with l in [0, L-1]** receive additional correction potentials U_l - U_L
- In other words: components with l >= L all feel the same U_L; components with l < L each feel their own U_l potential

### Why pseudopotentials depend on angular momentum

For valence orbital angular momentum components l = 0, 1, 2, ..., t (where t is the highest angular momentum in core orbitals), each must have its own separately defined pseudopotential. This is because the interaction between core orbitals of a given angular momentum and the corresponding angular momentum component of valence orbitals differs significantly (specifically: orthogonality and exchange potential).

For l > t, as l increases, the difference between U_l and U_{l+1} quickly becomes negligible. This is why pseudopotentials choose a cutoff L and use U_L for all l >= L rather than defining separate potentials for each.

### Typical L values

| System | L | Reasoning |
|--------|---|-----------|
| 1st row transition metals | 3 (f) | Hay & Wadt found d vs f potential difference is significant, but f vs g is negligible. So L=3, with separate s, p, d potentials |
| 3rd row transition metals | 4-5 (g-h) | Higher angular momentum needs explicit consideration. Lanl: L=4 (g); Stuttgart: L=5 (h) |

### Pseudopotential L vs basis set max angular momentum

The pseudopotential's L does NOT need to match the basis set's highest angular momentum. Typically L >= basis set max angular momentum + 1.

**Example:** For Cu, Lanl ECP has L=3 (f), but Lanl2DZ basis set's highest angular momentum is d (for valence d electrons).

**Why define >= f potential when the basis set has no f functions?** Because we calculate molecular systems, not isolated atoms. The pseudopotential acts on pseudo-orbitals, not directly on the atom's own basis functions. Basis functions from other atoms also contribute to the pseudo-orbitals, making them complex. Projection operators can extract >= f components from these pseudo-orbitals, which must also feel the pseudopotential. So the pseudopotential cannot be defined only for s, p, d.

**Exception:** If calculating only an isolated Cu atom, the pseudo-orbital (which is just the nodeless atomic orbital) has maximum angular momentum d — no f or higher components can be projected. In this case, only s, p, d potentials are needed. Defining f and above would be unused.

## Gaussian fitting form

For practical solving, numerically described pseudopotentials are fitted to analytical expressions using polynomial × Gaussian products:

```
r² × U(r) = Σ[k] d_k × r^(n_k) × exp(-ζ_k × r²)
```

Equivalently:

```
U(r) = Σ[k] d_k × r^(n_k - 2) × exp(-ζ_k × r²)
```

Where:
- r = radial coordinate
- d_k = expansion coefficient
- n_k = 0, 1, or 2
- ζ_k = Gaussian exponent

Because the actual pseudopotential expression follows the same unified convention as Gaussian-type basis sets, all pseudopotentials can原则上 be used in all quantum chemistry programs that support pseudopotentials.

**Fitting procedure:**
1. First fit U_L(r) using the above form → obtain d, n, ζ data for l >= L components
2. For l < L components, separately fit U_l(r) - U_L(r) (the correction to U_L) using the same form

## Program angular momentum limitations

When a quantum chemistry program uses a pseudopotential, it must be able to compute integrals up to L angular momentum basis functions.

**Example:** GAMESS-US integral code supports basis functions up to g only. For Hg, Stuttgart pseudopotential has L=5 (h). Even though the pseudopotential basis set's highest angular momentum is only d, it cannot be used in GAMESS-US.

**Note:** The highest angular momentum in the output wavefunction is unrelated to the pseudopotential's L. Standard .wfn files can only record up to f angular momentum Gaussian functions. For Hg with Stuttgart pseudopotential, since the pseudopotential basis set itself has no higher-than-f basis functions, and if other atoms' basis sets also have no higher-than-f functions, the .wfn file can record the system's wavefunction normally.

**Wavefunction analysis programs:** Multiwfn supports up to h angular momentum Gaussian functions, so analysis of such systems is completely fine.
