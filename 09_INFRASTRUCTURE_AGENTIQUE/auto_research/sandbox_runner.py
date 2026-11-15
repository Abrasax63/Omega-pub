"""Execute candidate Python in an ephemeral, read-only, network-disabled Docker container.

Only a fixed-function protocol is exposed. This mitigates rather than eliminates
code-execution risk: Docker shares the host kernel and is not a proof sandbox.
"""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

from model_proposal import validate_source
from variant_factory import generate

IMAGE = "python:3.12-slim"
HARNESS = r'''
import json
import sys
from pathlib import Path

namespace = {}
src = Path("/work/candidate.py").read_text(encoding="utf-8")
exec(compile(src, "/work/candidate.py", "exec"), namespace)
fn = namespace["q_power"]
job = json.load(sys.stdin)
rows, steps, repeats = job["rows"], job["steps"], job["repeats"]
result = None
for _ in range(repeats):
    result = fn(rows[:], steps)
print(json.dumps(result, separators=(",", ":")))
'''


def docker_available():
    try:
        result = subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL, timeout=8)
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def execute(source, rows, steps, repeats=12, timeout=12):
    # Only hashes of the four repository-defined programs can bypass the
    # one-function model proposal validator; their code is audited separately.
    if source not in {v["source"] for v in generate().values()}:
        validate_source(source)
    if not docker_available():
        raise RuntimeError("Docker unavailable: fail closed")
    if type(steps) is not int or not 0 <= steps <= 100000 or not 1 <= len(rows) <= 64:
        raise ValueError("bad job dimensions")
    if type(repeats) is not int or not 1 <= repeats <= 200:
        raise ValueError("bad repeats")
    if any(type(v) is not int or not 0 <= v < (1 << len(rows)) for v in rows):
        raise ValueError("invalid bitmask")
    job = json.dumps({"rows": rows, "steps": steps, "repeats": repeats})
    with tempfile.TemporaryDirectory(prefix="omega-model-sandbox-") as path:
        folder = Path(path)
        candidate = folder / "candidate.py"
        harness = folder / "harness.py"
        cid = folder / "container-id"
        candidate.write_text(source, encoding="utf-8")
        harness.write_text(HARNESS, encoding="utf-8")
        os.chmod(candidate, 0o644)
        os.chmod(harness, 0o644)
        cmd = [
            "docker", "run", "--rm", "-i", "--cidfile", str(cid),
            "--network", "none", "--read-only", "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges", "--pids-limit", "32",
            "--memory", "256m", "--memory-swap", "256m", "--cpus", "1",
            "--user", "65534:65534", "--tmpfs", "/tmp:rw,noexec,nosuid,nodev,size=16m",
            "--mount", "type=bind,src=" + str(candidate) + ",dst=/work/candidate.py,readonly",
            "--mount", "type=bind,src=" + str(harness) + ",dst=/work/harness.py,readonly",
            IMAGE, "python", "-I", "-B", "/work/harness.py",
        ]
        start = time.perf_counter_ns()
        try:
            proc = subprocess.run(cmd, input=job, text=True, capture_output=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            if cid.is_file():
                container_id = cid.read_text(encoding="ascii").strip()
                if container_id:
                    subprocess.run(["docker", "rm", "-f", container_id],
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL, timeout=10)
            raise RuntimeError("sandbox timeout")
        duration_us = (time.perf_counter_ns() - start) // 1000
    if proc.returncode:
        raise RuntimeError("sandbox nonzero exit: " + proc.stderr[-300:])
    if len(proc.stdout) > 8192:
        raise ValueError("sandbox output too large")
    try:
        outcome = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError("invalid sandbox JSON") from exc
    if not isinstance(outcome, list) or len(outcome) != len(rows):
        raise ValueError("wrong output dimensions")
    if any(type(v) is not int or not 0 <= v < (1 << len(rows)) for v in outcome):
        raise ValueError("invalid result bits")
    return outcome, max(1, duration_us)
