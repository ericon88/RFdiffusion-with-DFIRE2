#!/usr/bin/env python3
# count_residues.py
# Usage:
#   python count_residues.py structure.pdb
#   python count_residues.py structure.pdb --include-hetatm
#   python count_residues.py structure.pdb --keep-water
#   python count_residues.py structure.pdb --include-hetatm --keep-water

import argparse
from collections import defaultdict

def parse_args():
    p = argparse.ArgumentParser(description="Count residues in a PDB file.")
    p.add_argument("pdb", help="Path to PDB file")
    p.add_argument("--include-hetatm", action="store_true",
                   help="Include HETATM residues (ligands, ions, etc.)")
    p.add_argument("--keep-water", action="store_true",
                   help="Keep waters (HOH/ WAT/ H2O). Default: exclude")
    p.add_argument("--model", type=int, default=None,
                   help="If provided, only count residues within this MODEL number (1-based).")
    return p.parse_args()

# common water residue names seen in PDBs
WATER_NAMES = {"HOH", "H2O", "WAT"}

def is_water(resname: str) -> bool:
    return resname.strip() in WATER_NAMES

def count_residues(pdb_path, include_hetatm=False, keep_water=False, model=None):
    """
    Count unique residues by (chainID, resSeq, iCode, resName).
    By default:
      - Use only ATOM records (protein/nucleic acid).
      - Exclude waters.
    Options allow including HETATM and keeping waters.
    """
    residues = set()
    per_chain = defaultdict(set)

    current_model = 1
    model_filter_on = model is not None

    with open(pdb_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            rec = line[0:6].strip()

            # Handle MODEL/ENDMDL blocks (1-based indexing)
            if rec == "MODEL":
                try:
                    current_model = int(line[10:14].strip())
                except ValueError:
                    current_model += 1  # fallback increment if missing number
                continue
            if rec == "ENDMDL":
                continue

            if model_filter_on and current_model != model:
                continue

            if rec not in ("ATOM", "HETATM"):
                continue
            if rec == "HETATM" and not include_hetatm:
                continue

            # Parse minimal fields per PDB format v3.3+
            # columns are 1-indexed in spec; here using 0-indexed python slices
            resname = line[17:20].strip()
            chain_id = line[21:22]  # can be space
            resseq = line[22:26].strip()  # residue sequence number
            icode  = line[26:27]  # insertion code (may be space)

            if not keep_water and is_water(resname):
                continue

            # Use a robust residue key (chain, seq, icode, name)
            key = (chain_id, resseq, icode, resname)
            residues.add(key)
            per_chain[chain_id].add(key)

    total = len(residues)
    per_chain_counts = {k if k.strip() else "(blank)": len(v) for k, v in per_chain.items()}
    return total, dict(sorted(per_chain_counts.items(), key=lambda x: x[0]))

def main():
    args = parse_args()
    total, per_chain = count_residues(
        args.pdb,
        include_hetatm=args.include_hetatm,
        keep_water=args.keep_water,
        model=args.model,
    )

    print(f"PDB file: {args.pdb}")
    if args.model:
        print(f"Counted only MODEL {args.model}")
    print(f"Include HETATM: {'Yes' if args.include_hetatm else 'No'} | Keep water: {'Yes' if args.keep_water else 'No'}")
    print(f"\nTotal residues: {total}")
    print("Per-chain counts:")
    if per_chain:
        for chain, n in per_chain.items():
            print(f"  Chain {chain}: {n}")
    else:
        print("  (none)")

if __name__ == "__main__":
    main()
