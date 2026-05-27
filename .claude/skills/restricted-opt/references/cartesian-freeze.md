# Cartesian Coordinate Freezing in Gaussian

Detailed guide for freezing atomic Cartesian coordinates during geometry optimization, based on Sobereva's article (sobereva.com/404).

## Why freeze Cartesian coordinates?

### Common scenarios

1. **X-ray crystal structure hydrogen optimization**
   - X-ray diffraction accurately locates heavy atoms but only approximately positions hydrogens
   - Freeze heavy atoms, optimize hydrogens to proper positions
   - Requires sufficiently high-resolution crystal structure

2. **Surface adsorption models**
   - Use 3-4 atomic layers to model solid surface
   - Freeze bottom layer(s) to represent bulk structure
   - Allow adsorbate and top surface layers to relax freely

3. **Enzyme cluster models**
   - Extract active site from enzyme
   - Freeze backbone atoms of boundary amino acid residues
   - Prevent severe deformation/collapse during optimization

## Method 1: 0/-1 flags with `opt=cartesian`

### Basic syntax

```
# B3LYP/6-31G** opt=cartesian

Title Card Required

0 1
 O   0   0.00000000   0.00000000  -0.11081188
 H  -1   0.00000000   0.58397589   0.44324751
 H  -1   0.00000000  -0.58397589   0.44324751
```

- `0` = atom is free to optimize
- `-1` = atom is frozen (all three Cartesian components)
- **Must use `opt=cartesian`** — without it, Gaussian uses redundant internal coordinates

### Why `opt=cartesian` is important

Without `=cartesian`:
- Optimization runs in redundant internal coordinates
- Requires many more optimization steps
- Subtle algorithmic issues in internal-to-Cartesian conversion cause tiny H-H distance changes between initial and final structures

With `=cartesian`:
- Direct Cartesian optimization
- Fewer steps
- Frozen atoms truly stay fixed

### Important: `nosymm` for visualizing frozen atoms

Gaussian automatically reorients the molecule to standard orientation during optimization. This makes frozen atoms appear to move in the trajectory output, even though their relative positions are fixed.

To see frozen atoms truly stationary:
```
# B3LYP/6-31G** opt=cartesian nosymm
```

See sobereva.com/297 for more on `nosymm`.

### Cannot freeze individual components

Gaussian does NOT support freezing just one Cartesian component (e.g., freeze Z but allow X, Y movement). The `-1` flag freezes all three components simultaneously.

## Method 2: GaussView Atom Groups workflow

For large systems where manually writing `-1` for many atoms is tedious:

### Step-by-step example: Carbon nanotube with water molecules

1. Open structure in GaussView
2. Select the carbon nanotube atoms (they turn yellow)
3. Tools → Atom Groups
4. Switch category to **Freeze**
5. Click the `+` button next to "Freeze(Yes)" to add selected atoms to the freeze group
6. The structure now has two groups: frozen (nanotube) and free (water)
7. Save as .gjf → nanotube atoms get `-1`, water atoms get `0`

### Verification

The saved .gjf file will show:
```
 C  -1  x1  y1  z1
 C  -1  x2  y2  z2
 ...
 O   0  x3  y3  z3
 H   0  x4  y4  z4
 H   0  x5  y5  z5
```

Then set appropriate keywords and run.

## Surface adsorption example

Typical slab model for adsorption:

```
# PBE0/def2-SV(P) opt=cartesian nosymm

benzene on Ag(111) slab

0 1
[Ag bottom layer atoms - frozen]
[Ag middle layer atoms - frozen]
[Ag top layer atoms - free]
[benzene atoms - free]

[coordinates with appropriate 0/-1 flags]
```

- Bottom 1-2 layers: frozen (`-1`) to mimic bulk
- Top 1-2 layers: free (`0`) to allow surface relaxation
- Adsorbate: free (`0`)

## X-ray structure hydrogen optimization example

```
# B3LYP/6-31G* opt=cartesian

X-ray structure H optimization

0 1
[all heavy atoms with -1, coordinates from X-ray]
[all hydrogen atoms with 0, approximate initial positions]
```

After optimization, hydrogens are in proper quantum-chemically optimized positions while heavy atoms remain at experimental coordinates.

## Enzyme cluster model example

When extracting an enzyme active site:

```
# B3LYP/6-31G* opt=cartesian

enzyme active site cluster

0 1
[active site residues - free, 0]
[boundary residue backbone atoms - frozen, -1]
[boundary residue side chain atoms - may be free or frozen depending on model]
```

Freezing boundary backbone atoms prevents the cluster from collapsing into an unrealistic conformation during optimization.

## Important notes on computational cost

For methods with analytic gradients, freezing coordinates **does NOT reduce computational cost per step**:
- All atomic gradients are computed normally
- Frozen atom gradients are simply not used for geometry update
- Frozen atom gradients are excluded from convergence criteria
- The gradient calculation is the most expensive part — it proceeds unchanged

The only savings may come from fewer optimization steps if the frozen coordinates represent degrees of freedom that would otherwise require optimization.

## Subspace minima and imaginary frequencies

When coordinates are frozen, optimization converges to a **subspace minimum** — the minimum in the space of unfrozen variables, not the full potential energy surface minimum.

Consequently, frequency calculations on frozen-optimized structures often show imaginary frequencies. This is **normal and expected** — the structure is not at a true minimum in the full coordinate space.

If you need a true minimum for frequency analysis:
1. Do a full (unfrozen) optimization starting from the frozen-optimized structure
2. Or, accept that the frequency calculation will have imaginary frequencies and interpret accordingly

## References

- sobereva.com/404 — This article (restricted optimization)
- sobereva.com/297 — Symmetry and nosymm keyword
- sobereva.com/164 — Helping geometry optimization converge
