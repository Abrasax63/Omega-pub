"""PROTECT24: bounded 32-step protected/ordinary exploratory learning pilot.
Exact PILOT14 reconstruction required; identical batches and auxiliary work.
No deployment, independent qualification, or publication of unvalidated weights.
"""
import argparse
import copy
import json
import random
import tempfile
import time
from pathlib import Path

import numpy as np
import curriculum06 as c
import trainer07 as t
import runner11 as r
import pilot14 as p
import cumulative18 as a
import retention15 as n
import retention16 as b
import transfer13 as x
import protect21 as k
import route23 as route

STEPS = 32
SEED = 2026112524


def need(ok, message):
    if not ok:
        raise ValueError(message)


def plan():
    old, new = b.datasets()
    og, ng = b.pairs(old), b.pairs(new)
    rng = random.Random(SEED)
    chosen = rng.sample(sorted(ng), STEPS)
    pools = {s: sorted(q for q, z in og.items() if z[0]["kind"] == s) for s in c.KINDS}
    anchors = [{s: rng.choice(pools[s]) for s in c.KINDS} for _ in chosen]
    return old, new, og, ng, chosen, anchors


def projected_step(model, opt, params, batch, anchors, protected):
    """Identical training/gradient/projection work, different applied displacement.
    AdamW moments follow the proposed ordinary step in both arms. This is an
    explicit optimizer design choice, not a guarantee about later updates.
    """
    import torch
    before = [w.detach().clone() for w in params]

    def vector(values):
        return np.concatenate([v.detach().cpu().reshape(-1).numpy().astype(np.float64) for v in values])

    model.train()
    gradients = []
    for anchor in anchors:
        out = model(input_ids=anchor["input_ids"], attention_mask=anchor["attention_mask"], use_cache=False)
        loss, _, _ = t.loss_parts(out.logits, anchor["labels"], "adaptive")
        gradients.append(vector(torch.autograd.grad(loss, params)))
        del out, loss
    gradients = np.stack(gradients)
    stats = t.optimizer_step(model, opt, params, batch, "adaptive")
    ordinary_parameters = [w.detach().clone() for w in params]
    displacement = vector([w.detach() - v for w, v in zip(params, before)])
    need(np.isfinite(displacement).all(), "NONFINITE_UPDATE")
    projected, meta = k.protect(displacement, gradients)

    def assign(v):
        offset = 0
        with torch.no_grad():
            for w, original in zip(params, before):
                size = w.numel()
                chunk = torch.from_numpy(v[offset:offset + size].copy()).reshape(w.shape)
                w.copy_((original.double() + chunk).to(w.dtype))
                offset += size
        need(offset == len(v), "DIMENSION")

    # Also exercise assignment and rounding in the ordinary control.
    assign(projected)
    realized = vector([w.detach() - v for w, v in zip(params, before)])
    norms = np.linalg.norm(gradients, axis=1)
    unit = gradients[norms > 0] / norms[norms > 0, None]
    tolerance = 1e-6 * float(np.linalg.norm(displacement))
    rounded_fallback = bool(np.any(unit @ realized > tolerance))
    if rounded_fallback:
        assign(np.zeros_like(displacement))
        realized = vector([w.detach() - v for w, v in zip(params, before)])
    need(np.all(unit @ realized <= tolerance), "REALIZED_INFEASIBLE")
    if not protected:
        # Keep the actual proposal exactly, including entries crossing zero.
        with torch.no_grad():
            for w, proposed in zip(params, ordinary_parameters):
                w.copy_(proposed)
        need(all(torch.equal(w, proposed) for w, proposed in zip(params, ordinary_parameters)), "ORDINARY_ROUNDTRIP")
    need(all(bool(torch.isfinite(w).all()) for w in params), "NONFINITE_PARAMETER")
    return dict(optimizer=stats, projection=meta, rounding_fallback=rounded_fallback,
                proposed_norm=float(np.linalg.norm(displacement)),
                protected_norm=float(np.linalg.norm(realized)),
                applied="protected" if protected else "ordinary",
                auxiliary_anchor_gradients=len(anchors),
                adam_moments="ordinary proposed step retained")


def selftest():
    k.selftest()
    old, new, og, ng, selected, anchors = plan()
    need(plan() == (old, new, og, ng, selected, anchors), "DETERMINISM")
    need(len(selected) == len(set(selected)) == STEPS, "STEP_BUDGET")
    need(all(set(z) == set(c.KINDS) and all(z[s] in og for s in c.KINDS) for z in anchors), "TRAIN_ANCHORS")
    eval_old = x.make(SEED, "protect24-old")
    eval_new = n.build("fixture", SEED + 1)
    consumed = x.make(p.PILOT_SEED, p.FORM) + x.make(a.OLD_SEED, "retention18-old")
    used = {z["prompt"] for z in old + new + consumed}
    need(not used & {z["prompt"] for z in eval_old + eval_new}, "EVAL_OVERLAP")
    need(not {z["prompt"] for z in eval_new} & {z["prompt"] for z in n.build("fixture", a.NEW_SEED)}, "NEW_EVAL_OVERLAP")
    good = [dict(id=z["id"], prompt_sha=r.digest(z["prompt"]), raw=z["gold"]) for z in eval_new]
    perfect = n.score(eval_new, good, "fixture")
    base = {s: dict(correct=32, both_pairs=12) for s in c.KINDS}
    need(n.retention(base, base, perfect)["exploratory_pass"], "POSITIVE_GATE")
    bad = copy.deepcopy(base)
    bad["copy"]["correct"] -= 1
    need(not n.retention(base, bad, perfect)["exploratory_pass"], "REGRESSION_REJECTED")
    # Original score rejects missing/duplicated or altered prompt traces.
    for altered in (good[:-1], good + [good[0]], [dict(good[0], prompt_sha="bad")] + good[1:]):
        try:
            n.score(eval_new, altered, "fixture")
        except ValueError:
            pass
        else:
            raise AssertionError("CORRUPT_TRACE_ACCEPTED")
    print("PROTECT24_OFFLINE_OK: paired training, train-only anchors, fresh development cohorts and regression rejection")


def toytest():
    """Exercise the actual training/projection path without pretrained weights."""
    import torch
    from types import SimpleNamespace

    class Toy(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.emb = torch.nn.Embedding(3, 4)
            self.head = torch.nn.Linear(4, 3)

        def forward(self, input_ids, attention_mask, use_cache=False):
            return SimpleNamespace(logits=self.head(self.emb(input_ids)))

    torch.manual_seed(24)
    model = Toy()
    params = list(model.parameters())
    state = copy.deepcopy(model.state_dict())
    labels = torch.tensor([[-100, 1], [-100, 2], [-100, 2], [-100, 1]])
    batch = dict(input_ids=torch.tensor([[0, 1], [0, 2], [2, 2], [2, 1]]),
                 attention_mask=torch.ones(4, 2, dtype=torch.long), labels=labels)
    opt = torch.optim.AdamW(params, lr=.001, weight_decay=0.)
    initial = r.tensor_hash(list(model.named_parameters()))
    projected_step(model, opt, params, batch, [batch] * 4, False)
    ordinary = r.tensor_hash(list(model.named_parameters()))
    ordinary_state = copy.deepcopy(model.state_dict())
    model.load_state_dict(state)
    opt = torch.optim.AdamW(params, lr=.001, weight_decay=0.)
    projected_step(model, opt, params, batch, [batch] * 4, True)
    need(r.tensor_hash(list(model.named_parameters())) != initial and ordinary != initial, "ACTUAL_UPDATE")
    # No conflict on the same training loss: both paths should agree closely.
    need(all(torch.allclose(v, ordinary_state[name], atol=1e-7, rtol=1e-5) for name, v in model.state_dict().items()), "NO_CONFLICT_CONTROL")
    model.load_state_dict(state)
    need(r.tensor_hash(list(model.named_parameters())) == initial, "TOY_ROLLBACK")
    print("PROTECT24_REAL_STEP_TOY_OK: both updates, no-conflict control, exact restoration")


def run(budgetfile, original, resultfile, probefile, out):
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from peft import get_peft_model

    started = time.monotonic()
    out = Path(out)
    out.mkdir(exist_ok=False)
    decision = route.decide(a.load(probefile))
    need(decision["recommended_next_experiment"] == "PROTECTED_VS_ORDINARY_BLOCK", "PROSPECTIVE_ROUTE")
    original = Path(original)
    manifest = a.check_sources(original, resultfile)
    torch.set_num_threads(2)
    torch.manual_seed(t.SEED)
    tok = AutoTokenizer.from_pretrained(c.MODEL, revision=c.REV, trust_remote_code=False)
    train, enc, plans, budgets = p.plan_audit(tok, budgetfile)
    old, new, og, ng, selected, anchors = plan()
    need(old == train, "OLD_TRAIN")
    newenc = b.encode(tok, ng)
    model = AutoModelForCausalLM.from_pretrained(c.MODEL, revision=c.REV, trust_remote_code=False, torch_dtype=torch.float32)
    need(model.config._commit_hash == c.REV, "REVISION")
    model.config.use_cache = False
    model = get_peft_model(model, t.lora_config())
    named = [(name, w) for name, w in model.named_parameters() if w.requires_grad]
    params = [w for _, w in named]
    frozen = [(name, w) for name, w in model.named_parameters() if not w.requires_grad]
    need(named and all("lora_" in name for name, _ in named), "TRAINABLE_SCOPE")
    need(r.tensor_hash(named) == manifest["initial_adapter_sha"] and r.tensor_hash(frozen) == manifest["frozen_base_sha"], "INITIAL_STATE")
    opt = torch.optim.AdamW(params, lr=.0002, weight_decay=0.)
    dev = c.build("dev", t.SEED + 1)
    for j in (0, 1):
        if j:
            model.train()
            for i, ids in enumerate(plans["adaptive"]["batches"]):
                t.optimizer_step(model, opt, params, t.collate(tok, enc, ids), "adaptive")
                if (i + 1) % 16 == 0:
                    print("PROTECT24 reproduction", i + 1, "/128", flush=True)
        _, trace = r.evaluate_dev(model, tok, dev)
        need(a.rawmap(trace) == a.rawmap(a.load(original / ("dev-%d.json" % j))), "DEV_REPRODUCTION")
    need(r.tensor_hash(named) == manifest["final_transaction_adapter_sha"], "TENSOR_REPRODUCTION")
    with tempfile.TemporaryDirectory() as tmp:
        files = r.save_adapter(model, Path(tmp) / "adapter")
        need(files["adapter_model.safetensors"] == a.EXPECTED, "FILE_REPRODUCTION")
    checkpoint = r.tensor_hash(named)
    snapshot = [w.detach().clone() for w in params]
    optstate = copy.deepcopy(opt.state_dict())
    rngstate = torch.random.get_rng_state()

    def restore():
        with torch.no_grad():
            for w, saved in zip(params, snapshot):
                w.copy_(saved)
        opt.load_state_dict(copy.deepcopy(optstate))
        opt.zero_grad(set_to_none=True)
        torch.random.set_rng_state(rngstate)
        need(r.tensor_hash(named) == checkpoint, "ROLLBACK")

    oldrows = x.make(SEED, "protect24-old")
    newrows = n.build("fixture", SEED + 1)
    # Public same-author DEVELOPMENT cohorts; never an independent exam.
    r.json_write(out / "labels-old.json", oldrows)
    r.json_write(out / "labels-new.json", newrows)
    r.json_write(out / "questions.json", [{key: z[key] for key in ("id", "prompt")} for z in oldrows + newrows])
    r.json_write(out / "plan.json", dict(new_pairs=selected, anchors=anchors, steps_per_arm=STEPS,
                                        same_training_data_and_auxiliary_work=True))
    scores = {"control": a.eval_fresh(model, tok, oldrows, newrows, out, "control")}
    all_steps = {}
    try:
        for arm in ("ordinary", "protected"):
            restore()
            all_steps[arm] = []
            for i, pair in enumerate(selected):
                nb = t.collate(tok, newenc, [z["id"] for z in ng[pair]])
                ab = [t.collate(tok, enc, [z["id"] for z in og[anchors[i][s]]]) for s in c.KINDS]
                step = projected_step(model, opt, params, nb, ab, arm == "protected")
                all_steps[arm].append(step)
                r.json_write(out / (arm + "-steps.json"), all_steps[arm])
                if (i + 1) % 8 == 0:
                    print("PROTECT24", arm, i + 1, "/32", flush=True)
            need(r.tensor_hash(frozen) == manifest["frozen_base_sha"], "FROZEN_BASE_CHANGED")
            scores[arm] = a.eval_fresh(model, tok, oldrows, newrows, out, arm)
    finally:
        restore()
    need(r.tensor_hash(frozen) == manifest["frozen_base_sha"], "FINAL_BASE")
    gates = {arm: n.retention(scores["control"]["old"], scores[arm]["old"], scores[arm]["new"]) for arm in ("ordinary", "protected")}
    report = dict(status="PROTECT24_EXPLORATORY_TRAINING_COMPLETE", model=c.MODEL, revision=c.REV,
                  reproduced_first_block_updates=128, first_block_adapter_sha=a.EXPECTED,
                  new_optimizer_updates=2 * STEPS, candidate_steps_per_arm=STEPS,
                  scores=scores, retention=gates, prospective_route=decision,
                  auxiliary_anchor_gradients_per_arm=4 * STEPS,
                  equal_training_batches=True, equal_auxiliary_work=True,
                  optimizer_moments="proposed ordinary AdamW moments retained in both arms",
                  seconds=time.monotonic() - started, rollback_exact=True,
                  independent_curator=False, final_exam_consumed=False,
                  scope="single-seed small development pilot; not independent retention qualification",
                  retained_second_block_updates=0, weights_published=False, promotion_authorized=False)
    r.json_write(out / "result.json", report)
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", choices=("selftest", "toytest", "run"))
    for name in ("budget", "original", "result", "probes", "out"):
        parser.add_argument("--" + name)
    args = parser.parse_args()
    if args.cmd == "selftest":
        selftest()
    elif args.cmd == "toytest":
        toytest()
    else:
        need(all(getattr(args, name) for name in ("budget", "original", "result", "probes", "out")), "ARGUMENTS")
        run(args.budget, args.original, args.result, args.probes, args.out)
