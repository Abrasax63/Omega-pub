"""Independent external-graph evaluation for one development-selected candidate.

Public datasets are external to Omega, but are NOT blind third-party holdouts.
The candidate is frozen BEFORE this job builds/opens any evaluation graph.
"""
import argparse
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import random
import shutil
import statistics
import subprocess
import tempfile
import time

from gate import digest, evaluate
from model_proposal import validate_source
from reference import walks_exact
from variant_factory import generate

SOURCE_NAMES = ("karate", "davis", "florentine", "lesmis")
MODES = ("bidirectional", "oriented_loops")
HORIZONS = (0, 1, 8, 32, 128, 512)
TIMED_HORIZONS = (8, 32, 128, 512)
ARMS = ("model_candidate", "square-scan", "square-lowbit")
CLASSICAL = ("square-scan", "square-lowbit")
REPEATS = 9
BATCH = 20
SEED = "OMEGA-OPT02-2026-11-15"
IMAGE = "python:3.12-slim"


def canonical_hash(obj):
    return sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":")).encode()).hexdigest()


def get_graphs():
    import networkx as nx
    if nx.__version__ != "3.5":
        raise RuntimeError("NetworkX version changed: require 3.5")
    generators = (
        nx.karate_club_graph,
        nx.davis_southern_women_graph,
        nx.florentine_families_graph,
        nx.les_miserables_graph,
    )
    return list(zip(SOURCE_NAMES, [fn() for fn in generators]))


def rows_from_graph(graph, graph_name, mode):
    nodes = sorted(graph.nodes(), key=str)
    indices = {node: i for i, node in enumerate(nodes)}
    n = len(nodes)
    rows = [0] * n
    for u, v in graph.edges():
        i, j = indices[u], indices[v]
        if mode == "bidirectional":
            rows[i] |= 1 << j
            rows[j] |= 1 << i
        elif mode == "oriented_loops":
            if i == j:
                rows[i] |= 1 << i
            else:
                lo, hi = sorted((i, j))
                bit = int(sha256(f"{SEED}|{graph_name}|{lo}|{hi}".encode()).hexdigest(), 16) & 1
                source, target = (lo, hi) if bit else (hi, lo)
                rows[source] |= 1 << target
        else:
            raise ValueError("unregistered edge mode")
    if mode == "oriented_loops":
        rows = [mask | (1 << i) for i, mask in enumerate(rows)]
    return rows


def build_holdout():
    cases = []
    graph_info = {}
    for name, g in get_graphs():
        graph_info[name] = {"nodes": len(g), "edges": g.number_of_edges()}
        for mode in MODES:
            rows = rows_from_graph(g, name, mode)
            graph_info[name][mode + "_sha256"] = canonical_hash(rows)
            for h in HORIZONS:
                cases.append({"case_id": f"{name}-{mode}-h{h}",
                              "group_id": f"{name}-{mode}",
                              "family": f"{name}-{mode}",
                              "dataset": name, "mode": mode, "n": len(rows),
                              "steps": h, "rows": rows,
                              "timed": h in TIMED_HORIZONS})
    if len(cases) != 48 or sum(x["timed"] for x in cases) != 32:
        raise AssertionError("cohort count changed")
    return cases, graph_info


def compute_inside():
    """Runs inside Docker: all arms use the same CPU and order randomization."""
    source = Path("/work/champion.py").read_text()
    digest_source = sha256(source.encode()).hexdigest()
    expected_source = Path("/work/source-hash.txt").read_text().strip()
    if digest_source != expected_source:
        raise RuntimeError("candidate source changed before execution")
    generated = generate()
    funcs = {}
    namespace = {}
    exec(compile(source, "/work/champion.py", "exec"), namespace)
    funcs["model_candidate"] = namespace["q_power"]
    for name in CLASSICAL:
        namespace = {}
        exec(compile(generated[name]["source"], name, "exec"), namespace)
        funcs[name] = namespace["q_power"]
    cases = json.loads(Path("/work/inputs.json").read_text())
    out = {"source_sha256": digest_source,
           "input_sha256": canonical_hash(cases),
           "classic_sha256": {name: generated[name]["sha256"] for name in CLASSICAL},
           "measure": "process_time_ns inside container, batch=20, nine rounds",
           "results": []}
    rng = random.Random(SEED + "|arm-order")
    for case in cases:
        rows, h = case["rows"], case["steps"]
        answers = {}
        samples = {name: [] for name in ARMS}
        for name in ARMS:
            for _ in range(2):
                answers[name] = funcs[name](rows[:], h)
        for _ in range(REPEATS):
            randomized = list(ARMS)
            rng.shuffle(randomized)
            for name in randomized:
                start = time.process_time_ns()
                for unused in range(BATCH):
                    answer = funcs[name](rows[:], h)
                duration = max(1, time.process_time_ns() - start)
                samples[name].append(duration)
                answers[name] = answer
        out["results"].append({"case_id": case["case_id"],
                               "values": answers, "samples_ns": samples})
    print(json.dumps(out, separators=(",", ":"), sort_keys=True))


def score(cases, graph_info, raw, source_sha, gen_report, image_digest):
    if raw.get("source_sha256") != source_sha:
        raise ValueError("changed candidate source SHA")
    if gen_report.get("winner_source_sha256") != source_sha:
        raise ValueError("candidate differs from development-selected champion")
    if gen_report.get("model_attempts") != 3 or gen_report.get("external_corpus_opened") is not False:
        raise ValueError("incomplete model generation provenance")
    input_rows = [{k:v for k,v in row.items() if k != "timed"} for row in cases]
    if raw.get("input_sha256") != canonical_hash(input_rows):
        raise ValueError("evaluation input SHA mismatch")
    result_rows = raw.get("results")
    if not isinstance(result_rows, list) or len(result_rows) != len(cases):
        raise ValueError("incomplete result set")
    ids = [r.get("case_id") for r in result_rows]
    canonical_ids = [r["case_id"] for r in cases]
    if ids != canonical_ids or len(set(ids)) != len(ids):
        raise ValueError("missing, reordered or duplicate cases")
    errors = []
    speeds = []
    external_manifest = []
    case_arms = {name: [] for name in ARMS}
    raw_cases = []
    for case, result in zip(cases, result_rows):
        answers, samples = result["values"], result["samples_ns"]
        if set(answers) != set(ARMS) or set(samples) != set(ARMS):
            raise ValueError("missing arm")
        gold = walks_exact(case["rows"], case["steps"])
        median_ns = {}
        for name in ARMS:
            if answers[name] != gold:
                errors.append({"case_id": case["case_id"], "arm": name,
                               "expected_hash": canonical_hash(gold),
                               "actual_hash": canonical_hash(answers[name])})
            vals = samples[name]
            if len(vals) != REPEATS or any(type(x) is not int or x <= 0 for x in vals):
                raise ValueError("missing/invalid CPU samples")
            median_ns[name] = statistics.median(vals)
        if case["timed"]:
            best_classic = min(median_ns[name] for name in CLASSICAL)
            ratio = best_classic / median_ns["model_candidate"]
            speeds.append({"family": case["family"], "case_id": case["case_id"],
                           "speedup_vs_best_classic": ratio,
                           "median_ns": median_ns})
            external_manifest.append({"case_id":case["case_id"], "group_id":case["group_id"],
                                      "domain":case["family"], "expected":digest(gold)})
            for name in ARMS:
                case_arms[name].append({"case_id":case["case_id"],"prediction":digest(answers[name]),
                                        "cost": max(1,math.ceil(median_ns[name]/1000))})
        raw_cases.append({"case_id": case["case_id"], "output_sha256": canonical_hash(gold),
                          "median_cpu_ns": median_ns,
                          "sample_count_per_arm": REPEATS})
    medians = {family: statistics.median(r["speedup_vs_best_classic"]
               for r in speeds if r["family"] == family)
               for family in sorted({r["family"] for r in speeds})}
    geometric = math.exp(sum(math.log(r["speedup_vs_best_classic"]) for r in speeds) / len(speeds))
    positive = sum(x > 1 for x in medians.values())
    binomial_p = sum(math.comb(8, k) for k in range(positive, 9)) / 256
    manifest = {"experiment_id":"OMEGA-OPT02-2026-11-15",
                "cost_unit":"median_container_CPU_microseconds_for_20_calls",
                "cost_policy":"no_increase", "max_cost_per_case":1_000_000_000,
                "max_total_cost": len(speeds)*1_000_000_000,
                "training_case_ids":[str(x) for x in (207,401,607,809,1009,1229)],
                "training_group_ids":[f"dev-{x}" for x in (207,401,607,809,1009,1229)],
                "previous_holdout_group_ids":["OMEGA-TRANSFER-01-PR93"],
                "required_domains":sorted(medians), "holdout":external_manifest}
    gate_results = {}
    for name in CLASSICAL:
        observations={"experiment_id":manifest["experiment_id"],
                      "arms":{
                         "baseline":{"source_commit":raw["classic_sha256"][name],
                                     "run_url":"UNATTESTED-GITHUB-CI",
                                     "results":case_arms[name]},
                         "candidate":{"source_commit":source_sha,
                                      "run_url":"UNATTESTED-GITHUB-CI",
                                      "results":case_arms["model_candidate"]}}}
        gate_results[name]=evaluate(manifest, observations, digest(manifest))
    prereg_pass = (not errors and geometric >= 1.10
                   and all(x>=1.03 for x in medians.values())
                   and positive >= 7 and binomial_p <= .05
                   and all(x["candidate_for_independent_review"] for x in gate_results.values()))
    return {
        "status":"REVIEW_REQUIRED" if prereg_pass else "NO_DEMONSTRATED_ADVANTAGE",
        "source_generated_with_real_model":True,
        "source_sha256":source_sha,
        "model":"Qwen2.5-Coder-3B-Instruct Q4_K_M",
        "model_calls_budgeted":3,
        "generation_sha256":canonical_hash(gen_report),
        "external_package_version":"networkx==3.5",
        "external_graph_info":graph_info,
        "external_group_count":len(medians), "total_cases":len(cases),
        "timed_cases":len(speeds), "repetitions":REPEATS,"batch":BATCH,
        "correctness_errors":errors,
        "geometric_mean_speedup":geometric,
        "family_median_speedup":medians,
        "positive_families":positive,
        "family_sign_test_p":binomial_p,
        "classical_gates":gate_results,
        "image_digest":image_digest,
        "git_commit":os.environ.get("GITHUB_SHA","local"),
        "input_sha256":raw["input_sha256"],
        "per_case":raw_cases,
        "limitations":[
            "External public NetworkX graphs; NOT third-party blind escrow.",
            "Graph transforms are specified in the preregistration; adaptation after this result is forbidden.",
            "CPU measures from a single shared runner with noisy performance.",
            "Docker network isolation is not a high-assurance hostile-code sandbox.",
            "Correct known algorithms are not evidence of original discovery."],
    }


def run_host(champion_path, generation_json, output_path):
    source=champion_path.read_text(encoding="utf-8")
    validate_source(source)
    source_sha=sha256(source.encode()).hexdigest()
    generation=json.loads(generation_json.read_text(encoding="utf-8"))
    if generation.get("winner_source_sha256") != source_sha:
        raise ValueError("generation and frozen candidate mismatch")
    cases, graph_info=build_holdout()
    inputs=[{k:v for k,v in row.items() if k != "timed"} for row in cases]
    docker=subprocess.run(["docker","info"],capture_output=True,timeout=10)
    if docker.returncode:
        raise RuntimeError("Docker unavailable: fail closed")
    inspect=subprocess.run(["docker","image","inspect",IMAGE,"--format",
                            "{{index .RepoDigests 0}}"],capture_output=True,text=True,timeout=10)
    img=inspect.stdout.strip() if inspect.returncode == 0 else "IMAGE_DIGEST_UNAVAILABLE"
    root=Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(prefix="omega-opt02-final-") as td:
        stage=Path(td)
        os.chmod(stage,0o755)
        files={"opt02_evaluator.py":root/"opt02_evaluator.py",
               "variant_factory.py":root/"variant_factory.py",
               "champion.py":champion_path}
        for dest,from_path in files.items():
            shutil.copyfile(from_path,stage/dest)
            os.chmod(stage/dest,0o644)
        (stage/"inputs.json").write_text(json.dumps(inputs))
        (stage/"source-hash.txt").write_text(source_sha)
        for name in ("inputs.json","source-hash.txt"):
            os.chmod(stage/name,0o644)
        cmd=["docker","run","--rm","--network","none","--read-only","--cap-drop","ALL",
             "--security-opt","no-new-privileges","--user","65534:65534",
             "--memory","512m","--memory-swap","512m","--pids-limit","32","--cpus","1",
             "--mount",f"type=bind,src={stage},dst=/work,readonly",
             IMAGE,"python","-I","-B","/work/opt02_evaluator.py","--inside"]
        completed=subprocess.run(cmd,capture_output=True,text=True,timeout=900)
        if completed.returncode:
            raise RuntimeError("isolated final evaluation failed: "+completed.stderr[-800:])
        if len(completed.stdout) > 3_000_000:
            raise ValueError("oversized evaluation output")
        raw=json.loads(completed.stdout)
    result=score(cases,graph_info,raw,source_sha,generation,img)
    output_path.write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k not in ("per_case","classical_gates")},indent=2))


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--inside",action="store_true")
    p.add_argument("--champion",type=Path)
    p.add_argument("--generation-report",type=Path)
    p.add_argument("--output",type=Path,default=Path("opt02-result.json"))
    args=p.parse_args()
    if args.inside:
        compute_inside()
    else:
        if not args.champion or not args.generation_report:
            p.error("champion and generation-report required")
        run_host(args.champion,args.generation_report,args.output)


if __name__=="__main__":
    main()
