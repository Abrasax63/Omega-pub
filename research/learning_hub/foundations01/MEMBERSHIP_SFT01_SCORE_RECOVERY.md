# MEMBERSHIP-SFT01 — scoring-stage defect noticed before evaluation
Workflow source fc46910c1c84c4c8c556373c970932a1b01e5750, run
https://github.com/Abrasax63/Omega-pub/actions/runs/45387623052.
Static inspection finds two stale references in score job: downloaded
prediction basename should be membership-predictions.jsonl, not
atomic-predictions.jsonl; summary logging should read membership score
fields, not s['groups']['all']. Original one-shot workflow is immutable;
do not retrain or regenerate merely to fix reporting. If predictions
artifact is complete, verify its archive hash against GitHub metadata,
derive its file SHA256, verify frozen label SHA256 from freeze job,
then run membership_sft_score_archive.py on the original files.
Record any CI failure as technical; offline score recovery separately.
No threshold change, no evaluation labels opened, no model rerun.
