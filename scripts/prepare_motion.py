"""Run the existing PMS example and export its result for Blender playback."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pms-root", type=Path, default=Path(os.environ.get(
        "PRACTICAL_MECHANICAL_SIMULATION_ROOT", str(ROOT.parent / "PracticalMechanicalSimulation"))))
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs/motion")
    parser.add_argument("--reuse-result", action="store_true",
                        help="Export an existing result without rerunning simulation")
    args = parser.parse_args()
    pms_root = args.pms_root.resolve()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(pms_root / "python/src"))
    from practical_mechanical_simulation import Sim3D

    source = pms_root / "examples/spatial/python_api_double_pendulum.py"
    model = runpy.run_path(str(source))["build_model"]()
    model.source_directory = output
    result = output / "double-pendulum.simp"
    if not args.reuse_result:
        run = Sim3D.run(model, output=result, model_path=output / "double-pendulum.toml",
                        overwrite=True)
        print(run.stdout, end="")
        print(run.stderr, end="", file=sys.stderr)
    if not result.is_file():
        parser.error(f"Missing result: {result}")
    julia = shutil.which("julia")
    if julia is None:
        parser.error("Julia must be on PATH")
    subprocess.run([julia, f"--project={pms_root}", str(ROOT / "scripts/export_motion.jl"),
                    str(pms_root), str(result), str(output / "double-pendulum.motion.json")],
                   check=True)
    # Source document comes from the same saved result, not a potentially edited
    # model builder. The CLI extraction preserves the exact simulated model.
    extract = subprocess.run([str(pms_root / "bin/simpExtract"), str(result), "-"],
                             text=True, capture_output=True, check=True)
    import tomllib
    document = tomllib.loads(extract.stdout)
    (output / "double-pendulum.model.json").write_text(json.dumps(document, indent=2) + "\n")
    (output / "provenance.json").write_text(json.dumps({
        "source_example": str(source), "result": str(result),
        "result_sha256": hashlib.sha256(result.read_bytes()).hexdigest(),
        "pms_version": tomllib.loads((pms_root / "Project.toml").read_text())["version"],
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
