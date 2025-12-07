# tools/test_lightdock_dfire.py
"""
LightDock DFIRE/DFIRE2/fastDFIRE 
usage：
    conda activate lightdock
    python tools/test_lightdock_dfire.py
"""

import importlib
import inspect
import sys
from typing import Tuple, Optional

MODS = [
    ("dfire2",  "lightdock.scoring.dfire2.potential"),
    ("dfire",   "lightdock.scoring.dfire.potential"),
    ("fastdfire","lightdock.scoring.fastdfire.potential"),
]

def _find_scorer_and_method(module) -> Tuple[object, str]:
  """
Find an instantiable class inside the module (preferably one whose name contains 'DFIRE'),
and return (instance, callable_method_name). The priority order for selecting the method is:

compute_score > score > evaluate > energy > __call__
"""
# First, pick classes whose names contain 'DFIRE'

    classes = [getattr(module, n) for n in dir(module)
               if isinstance(getattr(module, n), type)]
    classes.sort(key=lambda c: (("DFIRE" not in c.__name__.upper()), c.__name__))  # DFIRE 优先

    if not classes:
        raise RuntimeError("模块中未发现可实例化的类")

    # try each class
    for cls in classes:
        try:
            inst = cls()
        except Exception:
            continue
        for m in ("compute_score", "score", "evaluate", "energy", "__call__"):
            if hasattr(inst, m):
                return inst, m

    # If no suitable method exists in the class, fall back to checking module-level functions

    for m in ("compute_score", "score", "evaluate", "energy"):
        if hasattr(module, m) and inspect.isfunction(getattr(module, m)):
            return module, m

    raise RuntimeError("No method found.")

def _toy_coords():
    """minimize smoke test：2 3-d coord (N,3)"""
    import numpy as np
    
    rec = np.array([[0.,0.,0.],
                    [8.,0.,0.],
                    [0.,8.,0.]], dtype=float)
    lig = np.array([[2.,2.,2.],
                    [9.,1.,0.],
                    [1.,9.,0.]], dtype=float)
    return rec, lig

def test_one(mod_name: str, full_import: str) -> None:
    print(f"\n===== test {mod_name}  ({full_import}) =====")
    try:
        module = importlib.import_module(full_import)
        print("Successful import：", module.__name__)
    except Exception as e:
        print("Unsuccessful import：", e)
        return

    
    public = [n for n in dir(module) if not n.startswith("_")]
    print("mod：", public if public else "（none）")

    # scorer
    try:
        scorer, entry = _find_scorer_and_method(module)
        print(f"🔎 使用入口：{scorer.__class__.__name__ if not inspect.ismodule(scorer) else module.__name__}.{entry}")
    except Exception as e:
        print("⚠️ 未找到可用评分入口：", e)
        return

    # try
    rec, lig = _toy_coords()
    try:
        fn = getattr(scorer, entry) if not inspect.ismodule(scorer) else getattr(module, entry)
        score = fn(rec, lig)
        # scalar
        try:
            score = float(score)
        except Exception:
            pass
        print(f"🎯 评分成功：score = {score}")
    except Exception as e:
        print("⚠️ 评分调用失败：", repr(e))
        print("   可能原因：该实现需要全原子/更多参数。此时仅表示入口存在，非致命。")

def main():
    
    try:
        import lightdock, lightdock.scoring as scoring
        print("✅ LightDock 路径：", lightdock.__file__)
        print("✅ scoring  路径：", scoring.__path__)
    except Exception as e:
        print("❌ 无法导入 LightDock：", e)
        sys.exit(1)

    for name, mod in MODS:
        test_one(name, mod)

    print("\n✅ 自检结束")

if __name__ == "__main__":
    main()
