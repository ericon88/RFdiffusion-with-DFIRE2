from pathlib import Path
from typing import Union
import torch

def write_pdb_from_xyz_ca(xyz_ca, seq, out_path: Path, chain_id="A"):
    """Write a PDB file from CA coordinates and sequence."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        for i, (aa, pos) in enumerate(zip(seq, xyz_ca), start=1):
            x, y, z = map(float, pos)
            f.write(f"ATOM  {i:5d}  CA  {aa:>3s} {chain_id}{i:4d}    "
                    f"{x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00\n")
        f.write("END\n")

def export_for_lightdock(xyz, seq, binderlen, t, out_root: Union[str, Path]):
    """Export receptor.pdb and ligand.pdb into the subdirectory for DFIRE2/LightDock scoring."""
    out_root = Path(out_root)
    eval_dir = out_root / f"ld_eval_t{t}"
    eval_dir.mkdir(parents=True, exist_ok=True)
    with torch.no_grad():
        ca = xyz[:, 1, :].detach().cpu().numpy()  # xyz: [L,27,3] index1  CA
    lig_ca = ca[:binderlen]
    rec_ca = ca[binderlen:]
    lig_seq = seq[:binderlen]
    rec_seq = seq[binderlen:]
    write_pdb_from_xyz_ca(rec_ca, rec_seq, eval_dir / "receptor.pdb", chain_id="A")
    write_pdb_from_xyz_ca(lig_ca, lig_seq, eval_dir / "ligand.pdb", chain_id="B")
    return eval_dir
