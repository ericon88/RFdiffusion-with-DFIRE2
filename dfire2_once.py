# tools/dfire2_once.py
import sys
from types import SimpleNamespace
from lightdock.scoring.dfire2.driver import DFIRE2, DFIRE2Adapter
from lightdock.pdbutil.PDBIO import parse_complex_from_file
from lightdock.structure.space import SpacePoints  

def load_molecule_from_pdb(pdb_path):
    atoms, residues, chains = parse_complex_from_file(pdb_path)
    return SimpleNamespace(residues=residues, n_modes=None)

def to_dm_coords_via_adapter(adapter, molecule):
    """return (DockingModel, SpacePoints)"""
  
    dm = adapter._get_docking_model(molecule, restraints=None)

    coords = dm.coordinates
    if not hasattr(coords, "coordinates"):
        coords = SpacePoints(coords)
    return dm, coords

def main():
    if len(sys.argv) < 3:
        print("USAGE: python tools/dfire2_once.py <receptor.pdb> <ligand.pdb>")
        sys.exit(2)

    rec_pdb, lig_pdb = sys.argv[1], sys.argv[2]
    rec_mol = load_molecule_from_pdb(rec_pdb)
    lig_mol = load_molecule_from_pdb(lig_pdb)
    adapter = DFIRE2Adapter(rec_mol, lig_mol)
    rec_model, rec_coords = to_dm_coords_via_adapter(adapter, rec_mol)
    lig_model, lig_coords = to_dm_coords_via_adapter(adapter, lig_mol)
    scorer = DFIRE2(weight=1.0)
    score = scorer(rec_model, rec_coords, lig_model, lig_coords)
    print(f"DFIRE2 score = {float(score):.4f}")

if __name__ == "__main__":
    main()
