"""Independently check aggregates in the published diagnostic reports."""
from hashlib import sha256
import json
import math
from pathlib import Path
from zipfile import ZipFile

EXPECTED = {
    28: "cdc74f5f60176ed3ca4b811964f6ffcf631f33eb82af784dba3398d0bf3f2fde",
    29: "988c5f04a1f09cb73bffb99daa5f56f3791d5ede966f9be0540e2f704199fd35",
    30: "05f6492a164d672c0f48da0388f6407c8f90b0db2a803d432a80f9dc93dba71e",
}


def read(run, *names):
    f = Path(f"a{run}.zip")
    assert sha256(f.read_bytes()).hexdigest() == EXPECTED[run]
    with ZipFile(f) as archive:
        assert set(archive.namelist()) == set(names)
        return [json.loads(archive.read(name)) for name in names]


def main():
    cont, = read(28, "continuity28.json")
    a, b, num = read(29, "historical_loader.json", "low_memory.json", "numerics29.json")
    grad, = read(30, "gradient30.json")
    assert cont["same_next_loss_parameters_optimizer_rng"] and cont["rollback_exact"]
    assert not cont["historical_128_checkpoint_reproduced"] and not cont["semantic_skill_tested"]
    assert a["start"] == b["start"] and a["trace"] == b["trace"]
    assert a["environment"] == b["environment"] and a["source_sha"] == b["source_sha"]
    assert a["historical_stats"] == b["historical_stats"]
    delta = [{k: row["stats"][k]-expected[k] for k in expected}
             for row, expected in zip(a["trace"], a["historical_stats"], strict=True)]
    assert all(delta == num["historical_delta"][label] for label in ("historical_loader", "low_memory"))
    tensors = grad["gradient_tensors_detail"]
    assert len(tensors) == len({row["parameter"] for row in tensors}) == grad["gradient_tensors"]
    assert sum(row["elements"] for row in tensors) == grad["gradient_elements"]
    l2 = math.sqrt(math.fsum(row["norm64"] ** 2 for row in tensors))
    assert math.isclose(l2, grad["python_fsum_norm64"], rel_tol=1e-12)
    clipped = {v["clipped_gradient_sha"] for v in grad["norm_variants"]}
    norms = sorted({v["norm"] for v in grad["norm_variants"]})
    assert len(clipped) == 1 and norms == grad["distinct_norms"]
    assert grad["historical_first_step"] == a["historical_stats"][0]
    assert not grad["historical_raw_gradients_available"] and grad["optimizer_updates"] == 0
    historical = grad["historical_first_step"]
    forward_delta = {k: v-historical[k] for k, v in grad["forward_metrics"].items()}
    print(json.dumps(dict(continuity_updates=cont["total_test_optimizer_updates"],
                          continuation_seconds=cont["new_process_seconds"],
                          loader_delta=delta, gradient_elements=grad["gradient_elements"],
                          norm_variants=len(grad["norm_variants"]), variants_distinct=len(norms),
                          historical_norm=historical["grad_norm"], current_norm=norms[0],
                          recomputed_norm64=l2, gradient_forward_delta=forward_delta),indent=2))


if __name__ == "__main__":
    main()
