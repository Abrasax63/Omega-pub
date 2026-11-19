"""Real dependency version probe: output and manifest are separate evidence."""
import json
import tempfile
from pathlib import Path
from tools.repro_scientific_pilot import run_pinned_script

root = Path(__file__).resolve().parents[1]
script = "02_MATHEMATIQUES/observabilite_temporelle/sources/verification_specialisation_unaire.py"
with tempfile.TemporaryDirectory() as d:
    path, manifest, result = run_pinned_script(root, script, d)
    assert result["returncode"] == 0, result["stderr"]
    assert result["stdout"].strip()
    print(json.dumps({"dependency_version": manifest["dependencies"]["sympy"],
                      "manifest_fingerprint": json.loads(path.read_text())["fingerprint"],
                      "output": result["stdout"]}, sort_keys=True))
