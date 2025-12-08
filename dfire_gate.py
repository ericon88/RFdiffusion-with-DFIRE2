# rfdiffusion/external/dfire_gate.py
import subprocess
from pathlib import Path
from typing import Optional


def dfire2_normalize(score: float, total_residues: int) -> float:
    """Normalize the DFIRE2 raw score by system size into [0,1], where higher is better."""
    lower = -1.971 * total_residues
    norm = (-score) / (-lower)
    return max(0.0, min(1.0, norm))

class DFIREGate:
    def __init__(self, script_path: str, total_residues: int,
                 target: float = 0.9, max_mult: float = 3.0, min_scale: float = 0.1,
                 cmd_prefix: Optional[str] = None):
        """
        script_path : The single-shot scoring script you use (e.g. tools/dfire2_once.py)
        total_residues : The “total number of residues” used for normalization (you will pass this in after preprocessing)
        target : Normalization threshold; scores below this threshold trigger a penalty
        max_mult : Maximum amplification factor when penalizing (applied to the strength of the differentiable guiding potential)
        min_scale : Minimum guiding strength after the target is reached (not recommended to use 0; keep a small amount of guidance)
        cmd_prefix : If you need to call it in another environment, you can add a prefix such as `conda run -n lightdock`
        """
        self.script = str(script_path)
        self.total_res = int(total_residues)
        self.target = float(target)
        self.max_mult = float(max_mult)
        self.min_scale = float(min_scale)
        self.cmd_prefix = cmd_prefix

    def score(self, receptor_pdb: str, ligand_pdb: str) -> float:
        """Call the external script and return the DFIRE2 raw score (float, usually negative)."""
        if self.cmd_prefix:
            cmd = self.cmd_prefix.split() + ["python", self.script, receptor_pdb, ligand_pdb]
        else:
            cmd = ["python", self.script, receptor_pdb, ligand_pdb]
        out = subprocess.check_output(cmd, text=True).strip()
        try:
            return float(out.split()[-1])
        except Exception:
            return float(out)

    def scale_from_norm(self, norm: float) -> float:
        """
        Map the normalized score to the external scaling factor `external_scale` for the differentiable guiding potential:
            - norm >= target → immediately reduce to min_scale (slow down and keep it until the end)
            - norm <  target → linearly increase up to at most max_mult
        """
        if norm >= self.target:
            return self.min_scale
        k = (self.target - norm) / self.target    # ∈ (0,1]
        return 1.0 + k * (self.max_mult - 1.0)
