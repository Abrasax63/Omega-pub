# Omega AutoResearch — transverse promotion gate (pilot)

Purpose: compare the output of an incumbent and a proposed improvement on a **pre-registered, separate holdout**, across provenance and math tasks. This is an offline audit component, not a model, an agent, a proof assistant, or a code-execution sandbox.

The core design follows the small-edit / fixed-evaluation / retain-or-reject principle in [Karpathy's autoresearch](https://github.com/karpathy/autoresearch) and the [OpenAI NanoGPT evaluation](https://deploymentsafety.openai.com/gpt-6-astra). Here the focus is **not** maximizing training throughput but checking whether a scientific change transfers beyond its development cases.

## Use

Prepare a private manifest with the intended holdout case IDs, their independent reference answers, and the permitted cost unit. Keep this manifest OUTSIDE the candidate's context. **Before seeing predictions**, independently record the canonical SHA-256 emitted by:

```sh
python gate.py freeze manifest.json
```

Once the baseline and candidate have been run separately on the reserved cases, record their predictions and measured costs in `observations.json`, then:

```sh
python gate.py evaluate manifest.json observations.json --manifest-sha256 YOUR_PRE_REGISTERED_SHA256
python -m unittest -v test_gate.py
```

The two arms must have the same case set and bounded per-case cost. The gate rejects missing or duplicated cases, case ID/group overlap with training, a changed manifest, false candidate confirmations, loss of known-correct cases, aggregate cost violations, and candidates that have neither improved correct responses nor reduced work at equal accuracy. Every required domain must be represented. A pass is only `REVIEW_REQUIRED`: it never upgrades a scientific status, merges a PR, or changes a canonical reference.

## Cost fairness and grouped holdout (v0.2)

The manifest now requires `training_group_ids` (possibly `[]`) and a
nonempty `group_id` on **each** holdout case. Choose the group before
evaluation, using a physical source, mathematical problem family, original
benchmark item, database, or other lineage that would make near-duplicates
dependent. The evaluator rejects overlap in groups between training and
holdout, in addition to overlap in case IDs. Optionally set
`previous_holdout_group_ids` to previously consumed families; this only
checks the declared list and **does not** constitute a trusted ledger.

Pre-register `cost_policy` as `"no_increase"` (default; total candidate cost
must be at most total baseline cost) or `"exact_parity"` (total costs must be
equal). Both arms must still respect the `max_cost_per_case` limit.
An optional `max_total_cost` limits each arm's aggregate consumption.
Costs must be genuinely measured in the **same frozen unit**. Under
`no_increase`, greater correctness at greater total cost is **not**
accepted. `exact_parity` intentionally rejects cost-only improvements,
so select it only when strict equality is the scientific objective.

Example additional manifest fields:

```json
{
  "training_group_ids": ["training-source-a"],
  "previous_holdout_group_ids": [],
  "cost_policy": "no_increase",
  "max_total_cost": 100,
  "holdout": [
    {"case_id": "reserved-001", "group_id": "reserved-source-b",
     "domain": "provenance", "expected": "copie"}
  ]
}
```

The rest of the required manifest schema (experiment ID, cost unit, per-case
budget, training IDs and domains) still applies. A candidate can only be
recommended for *independent review*, never accepted as proven.

The gate neither authenticates run IDs nor proves independence between
different group IDs. It also cannot prevent repeated adaptive evaluations
on the same holdout if the evaluator omits prior groups or leaks feedback.
A separate trusted experiment register, fresh reserved groups, immutable
source commits, and independently checked runtime/quality metrics remain
necessary before any claim of autonomous improvement.

## Trust boundary / limits

- **No arbitrary code is executed.** This is deliberate: model-generated source requires a separate resource-limited sandbox with no tokens/secrets/write permissions. GitHub Actions is not itself a scientific proof of behavior.
- Prediction and run metadata are input **claims**, not independently verified evidence. The gate does NOT authenticate `source_commit` or `run_url` against GitHub; an independent auditor must follow the links and rerun results.
- The pre-registration SHA-256 does not prove it was created before the predictions; publish or timestamp it independently before evaluation.
- Case-ID separation does not prevent leakage via mirrors, paraphrases, correlated cases, or gold labels exposed to the candidate.
- Costs are whatever **unit was frozen** (e.g. verifier calls), not currency/tokens/wall time unless actually measured and made comparable.
- Synthetic test fixtures demonstrate correctness of the *gate only*. No Omega generalization or algorithmic improvement is claimed.

Integration contract for the parallel PRs: PR #81 may provide `provenance` predictions, and PR #82 may provide `math` predictions; neither PR is touched here. An external evaluator owns the holdout. Record all rejected attempts, not just winners, with traceable versions of candidates.
