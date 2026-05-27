---
name: metal-surface-cluster
description: This skill should be used when the user asks to "metal surface adsorption", "簇模型计算吸附", "cluster model surface", "surface adsorption energy", "metal cluster adsorption", "苯吸附金属表面", "Ag(111) adsorption", "cluster model surface reaction", "surface DFT-D3", "counterpoise surface", "boundary effect cluster", "metal slab cluster model", or mentions using quantum chemistry programs (Gaussian, ORCA) to study metal surface adsorption or surface reactions via cluster models.
version: 0.1.0
---

# Metal Surface Adsorption via Cluster Models

Guidance for studying metal surface adsorption and surface reactions using cluster models with quantum chemistry programs (Gaussian, ORCA), based on Sobereva's article (sobereva.com/540).

## Why cluster models?

Cluster models treat a finite region of the surface as an isolated molecule. This approach complements periodic DFT (VASP, Quantum Espresso, CP2K) with distinct trade-offs:

### Advantages of cluster models
- **Richer theory methods** — double-hybrids, DLPNO-CCSD(T), high-accuracy wavefunction methods unavailable in plane-wave codes
- **Simpler setup** — no k-points, vacuum layers, dipole corrections, or mirror-image interactions to worry about
- **Richer analysis** — Multiwfn wavefunction analysis (NCI, AIM, RDG, CDA, etc.) makes discussion sections much richer
- **Easier keywords** — standard quantum chemistry input format, more visualization tools

### Disadvantages of cluster models
- **Boundary effects** — finite cluster approximation introduces errors; must be managed by cluster size and boundary treatment
- **Higher cost for dense solids** — for close-packed bulk materials, cluster calculations can be more expensive than periodic
- **SCF convergence difficulty** — transition metal clusters often have severe SCF convergence problems and wavefunction instability

### When to use cluster models
- When you need high-accuracy methods (DLPNO-CCSD(T), double-hybrid) on surface problems
- When you need rich wavefunction analysis (NCI, AIM, RDG, excited states)
- When you want to combine periodic optimization with high-accuracy cluster single-point (hybrid approach)
- For enzyme catalysis — extract active site region instead of using ONIOM(QM:MM)

## 1. Cluster model construction

### Cluster size
| Factor | Guideline |
|--------|-----------|
| **Minimum thickness** | At least 3 atomic layers |
| **Lateral size** | Cluster should be noticeably larger than the adsorbate molecule |
| **Shape matching** | Match cluster shape to adsorbate shape (circular for benzene, elongated for rod-shaped molecules) |
| **Cost balance** | Too small → boundary effects dominate; too large → prohibitive cost |

**Example:** For benzene on Ag(111), Ag₅₈ is well-sized — not too large, not too small.

### Boundary treatment
| Material type | Boundary approach |
|---------------|-------------------|
| **Pure metals** | Usually no special treatment needed |
| **Organic systems (graphene, etc.)** | Hydrogen saturation at edges |
| **Inorganic crystals** | Pseudo-hydrogen, capped ECP, or background point charges |

### Atom freezing strategy
- **Freeze edge atoms** — boundary atoms don't feel bulk phase constraints; freeze them to prevent unrealistic relaxation
- **Freeze bottom layers** — deeper layers should be fixed to mimic bulk constraint
- **Allow surface atoms to relax** — atoms directly interacting with adsorbate should be free to optimize

**In Gaussian:** Use `-1` freeze flag or `modredundant` with frozen coordinates.
**In ORCA:** Use `%geom Constraints` block or generate via Multiwfn's `oi` function.

### Closed-shell preference
**Design cluster to be closed-shell whenever possible.** Closed-shell calculations are much faster and more stable than open-shell.
- Even number of metal atoms → closed-shell (for metals bonding via s electrons)
- Odd number → open-shell, significantly harder to converge

## 2. Computational workflow

### Step 1: Build the metal cluster
- Obtain crystal structure from ICSD or literature
- Cut surface facet (e.g., Ag(111)) using VESTA, GaussView, or Avogadro
- Extend to sufficient size, trim to desired shape
- Place adsorbate molecule above surface at reasonable distance (~3 Å for physisorption)

### Step 2: Geometry optimization
- **Functional:** PBE0 (preferred for metals) over B3LYP (known to perform poorly for metals, see JCP 127, 024103, 2007)
- **Dispersion correction:** Essential for physisorption. Use DFT-D3(BJ) — see sobereva.com/413
- **Basis set:** def2-SV(P) or def2-SVP for optimization — geometry is not very basis-set sensitive (see sobereva.com/387)
- **SCF convergence:** Tighten SCF for transition metals. In ORCA, use `tightSCF` for single-point, `scfconv7` for optimization if convergence is difficult
- **Freeze boundary atoms** during optimization

### Step 3: Single-point energy
- **Basis set:** def2-QZVP or def2-TZVP for accurate energy
- **Functional:** PBE0-D3(BJ) or higher-level methods
- **Integration grid:** Use finer grid (`grid4 gridx4` in ORCA, `int=ultrafine` in Gaussian) for dense atomic packing
- **BSSE treatment:** See Section 3 below

### Step 4: Calculate binding energy
```
E_bind = E(cluster + adsorbate) - E(cluster) - E(adsorbate)
```
Use fragment energies calculated at the complex geometry (BSSE-minimized approach).

### Step 5: Wavefunction analysis (optional)
- NCI/RDG analysis for visualization of weak interactions
- AIM topology for metal-adsorbate bond characterization
- Charge decomposition analysis (CDA)
- See Multiwfn analysis guides: sobereva.com/68, sobereva.com/252, sobereva.com/471

## 3. BSSE treatment for surface adsorption

| Approach | Pros | Cons |
|----------|------|------|
| **Counterpoise correction** | Rigorous | Requires 2× more calculations |
| **gCP correction** | Free, approximate | Parameters only fitted up to 4th period; unreliable for heavy metals |
| **Add diffuse functions** | Reduces BSSE | Increases SCF difficulty dramatically; causes linear dependency for dense packing |
| **Larger basis set (def2-QZVP)** | BSSE negligible at QZVP level; reaches basis set limit for DFT | Expensive but manageable with RIJCOSX |

**Recommendation:** For heavy metal clusters, use def2-QZVP single-point. BSSE is negligible at this level. See sobereva.com/46 for BSSE discussion.

## 4. SCF convergence tips for metal clusters

| Difficulty ranking (easiest → hardest) | Main group < ds-block < d-block < lanthanide |
|----------------------------------------|---------------------------------------------|

**Common strategies:**
- Start with hybrid functional (PBE0) rather than pure functional (PBE) — hybrid often converges easier for transition metals
- Use `DirectResetFreq=1` in ORCA to disable incremental Fock acceleration if SCF oscillates
- Place adsorbate at reasonable distance (~3 Å) — too close makes electronic structure much more complex
- Reduce SCF convergence threshold for optimization (`scfconv7` in ORCA) if `tightSCF` won't converge
- After optimization, re-optimize with tighter SCF to ensure structural accuracy
- For very difficult systems, pre-optimize with xTB (see sobereva.com/421)
- If Gaussian: exploit symmetry (e.g., C₃v) for faster convergence
- **Be patient** — 30-50+ SCF cycles is normal for these systems

## 5. DFT-D3 three-body correction

For systems with many densely packed atoms, the DFT-D3 three-body (ABC) term can be significant (~2 kcal/mol for Ag₅₅ + benzene).

**Recommendation:**
- Include `ABC` keyword in ORCA for single-point calculations (no cost increase)
- Or use standalone `dftd3` program: `dftd3 mol.xyz -func pbe0 -bj -abc`
- Three-body correction has no analytic Hessian — skip for optimization/frequency

## 6. Common pitfalls

| Pitfall | Consequence | Fix |
|---------|-------------|-----|
| Cluster too small | Large boundary errors | Use ≥3 layers, extend laterally |
| No atom freezing | Unphysical boundary relaxation | Freeze edge/bottom atoms |
| B3LYP for metals | Poor metal description | Use PBE0 instead |
| No dispersion correction | Wrong physics for physisorption | Always add DFT-D3(BJ) |
| Adsorbate too close to surface | SCF nightmare | Start at ~3 Å distance |
| Open-shell cluster design | Much harder SCF | Design for even metal atom count |
| Default integration grid | Poor accuracy for dense packing | Use fine/superfine grid |
| Ignoring D3 three-body term | ~2 kcal/mol error for large clusters | Add ABC keyword |

## Recommended quick-reference setup

### ORCA optimization
```
! PBE0 D3BJ def2-SV(P) def2/J RIJCOSX tightSCF
%geom
  Constraints
    {C 1-11 14 17 19-23 26 29 32 34-38 41 44 46-50 52 54-58 F}
  end
end
```

### ORCA single-point
```
! PBE0 D3BJ ABC grid4 gridx4 def2-QZVP def2/J RIJCOSX noautostart
%scf DirectResetFreq=1 end
```

### Gaussian optimization (using symmetry)
```
#p PBE1PBE/def2svp empirical=dispersion opt=modredundant

[coordinates]

-1 1-11 14 17 19-23 26 29 32 34-38 41 44 46-50 52 54-58
```

## Additional Resources

For detailed methodology and comprehensive coverage, consult:

- **`references/benzene-ag111-example.md`** — Step-by-step benzene on Ag(111) workflow: cluster construction, optimization, single-point, binding energy calculation, D3 three-body correction, NCI analysis
- **`references/cluster-best-practices.md`** — Detailed discussion of boundary effects, SCF convergence troubleshooting, BSSE treatment comparison, Multiwfn analysis workflow, enzyme active site cluster models
