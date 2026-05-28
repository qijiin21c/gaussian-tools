"""
detect_symmetry.py - Use libmsym to detect molecular point group symmetry from Cartesian coordinates.

Usage:
  python detect_symmetry.py < xyz_file.xyz
  python detect_symmetry.py --atoms C,0,0,0 H,1,0,0 H,0,1,0 H,0,0,1
  python detect_symmetry.py --gjf jobs/molecule.gjf
"""

import sys
import os
from libmsym import Element
import libmsym


def make_element(symbol, x, y, z):
    """Create a libmsym Element from symbol and coordinates."""
    masses = {
        'H': 1.008, 'He': 4.003, 'Li': 6.941, 'Be': 9.012,
        'B': 10.81, 'C': 12.011, 'N': 14.007, 'O': 15.999,
        'F': 18.998, 'Ne': 20.180, 'Na': 22.990, 'Mg': 24.305,
        'Al': 26.982, 'Si': 28.086, 'P': 30.974, 'S': 32.06,
        'Cl': 35.45, 'Ar': 39.948, 'K': 39.098, 'Ca': 40.078,
        'Fe': 55.845, 'Cu': 63.546, 'Zn': 65.38, 'Br': 79.904,
        'I': 126.90, 'Pt': 195.08, 'Au': 196.97,
    }
    e = Element()
    e.mass = masses.get(symbol, 1.0)
    e._v = (x, y, z)
    e._name = symbol.encode('ascii')[:3]
    return e


def parse_xyz(text):
    """Parse XYZ format string. Returns list of (symbol, x, y, z)."""
    lines = text.strip().split('\n')
    # Skip comment line (line 1) and natoms line (line 0)
    start = 0
    try:
        natoms = int(lines[0].strip())
        start = 2
    except ValueError:
        start = 0
        natoms = 0

    atoms = []
    for line in lines[start:]:
        parts = line.split()
        if len(parts) >= 4:
            symbol = parts[0]
            x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
            atoms.append((symbol, x, y, z))
    return atoms


def parse_gjf(text):
    """Parse Gaussian .gjf/.com file for Cartesian coordinates."""
    lines = text.strip().split('\n')
    atoms = []
    in_geom = False
    found_blank_after_geom = False

    for line in lines:
        stripped = line.strip()
        if not stripped and in_geom and not found_blank_after_geom:
            found_blank_after_geom = True
            break
        if in_geom:
            parts = stripped.split()
            if len(parts) >= 4:
                # Could be: Symbol X Y Z or Symbol Z-matrix line
                try:
                    float(parts[1])
                    symbol = parts[0]
                    if symbol.lower() not in ('x', 'bq'):
                        x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                        atoms.append((symbol, x, y, z))
                except ValueError:
                    pass
            continue
        if 'coord' in stripped.lower() or 'z-matrix' in stripped.lower():
            continue
        # Detect geometry start: after charge/multiplicity line
        if len(parts := stripped.split()) == 2:
            try:
                int(parts[0])
                int(parts[1])
                in_geom = True
            except ValueError:
                pass

    return atoms


def detect_symmetry(atoms, threshold=1e-3):
    """Detect molecular symmetry from list of (symbol, x, y, z) tuples."""
    elements = [make_element(s, x, y, z) for s, x, y, z in atoms]

    ctx = libmsym.Context()
    ctx.elements = elements
    ctx.find_symmetry()

    return ctx


def format_symmetry(ctx):
    """Format symmetry results for display."""
    result = []
    result.append(f"Point group: {ctx.point_group}")

    # Classify operations
    from collections import Counter
    types = Counter()
    for op in ctx.symmetry_operations:
        if op.type == 0:
            types['E'] += 1
        elif op.type == 1:
            types[f'C{op.order}'] += 1
        elif op.type == 2:
            types[f'S{op.order}'] += 1
        elif op.type == 3:
            if op.orientation == 1:
                types['sigma_h'] += 1
            elif op.orientation == 2:
                types['sigma_v'] += 1
            else:
                types['sigma_d'] += 1
        elif op.type == 4:
            types['i'] += 1

    result.append(f"Order: {len(ctx.symmetry_operations)}")
    result.append("Symmetry operations:")
    for k, v in sorted(types.items()):
        result.append(f"  {k}: {v}")

    return '\n'.join(result)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Detect molecular point group symmetry using libmsym')
    parser.add_argument('file', nargs='?', help='XYZ or GJF file to analyze')
    parser.add_argument('--atoms', help='Comma-separated atoms: Symbol,x,y,z Symbol,x,y,z ...')
    parser.add_argument('--gjf', help='Gaussian .gjf/.com file')
    parser.add_argument('--threshold', type=float, default=1e-3, help='Symmetry detection threshold (default: 1e-3)')
    parser.add_argument('--loose', action='store_true', help='Use loose threshold (1e-2)')
    parser.add_argument('--tight', action='store_true', help='Use tight threshold (1e-5)')

    args = parser.parse_args()

    threshold = args.threshold
    if args.loose:
        threshold = 1e-2
    if args.tight:
        threshold = 1e-5

    atoms = []

    if args.atoms:
        for part in args.atoms.split():
            parts = part.split(',')
            symbol = parts[0]
            x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
            atoms.append((symbol, x, y, z))
    elif args.gjf:
        with open(args.gjf, 'r') as f:
            atoms = parse_gjf(f.read())
    elif args.file:
        with open(args.file, 'r') as f:
            text = f.read()
        if args.file.endswith(('.gjf', '.com')):
            atoms = parse_gjf(text)
        else:
            atoms = parse_xyz(text)
    else:
        # Read from stdin
        text = sys.stdin.read()
        atoms = parse_xyz(text)

    if not atoms:
        print("Error: No atoms found.", file=sys.stderr)
        sys.exit(1)

    print(f"Analyzing {len(atoms)} atoms...")
    ctx = detect_symmetry(atoms, threshold)
    print(format_symmetry(ctx))


if __name__ == '__main__':
    main()
