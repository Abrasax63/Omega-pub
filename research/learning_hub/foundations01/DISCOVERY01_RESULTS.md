# DISCOVERY01 — local result, 2026-11-24

Prospective protocol: 0c865361f762d931a324ee208da7ed157f4d7555.
Original COMPOSITION01 artifact 14924271795, ZIP SHA256
866102f8fefaa169fc2a099ea01cfbe64b96eb39ab8f8f82cb69dc66d30d2671.
All three frozen checkpoint hashes verified against original results.
Actual local execution, Python / torch 2.10.0+cpu, 2 threads, no gradients.
Source SHA256 5dd4b61103d36f13d99cc3d0c92cf79f421a8e29fee67a30d1da547513f19fc7.
Result JSON SHA256 10339d580d1ee25c7362acc49ffb82ac9d9d325925d05b92b66e6bb3a7a2f810.
Source and JSON retained as local downloadable artifacts; not uploaded
to this GitHub commit. Do not claim a new CI replication.

584 distinct truth functions of six Boolean variables in grammar
cost <=5, of which 420 have minimal cost 5 and support >=3.
24 sampled target functions; search has no target formula, only label
callback. Each task has new size6 pool, and 256 new size8/12 test graphs.
For each of seeds 11,22,33, identical results:
| arm | exact rules | unique rules | graph correct | labels requested |
|---|---:|---:|---:|---:|
| active neural |24/24|24/24|6144/6144|227|
| passive neural |11/24|10/24|5488/6144|268|
| active exact |24/24|24/24|6144/6144|227|
Active requested 9 or 10 labels per rule (max permitted 12).
Zero neural signature errors on all pool/test graphs across seeds.
18432/18432 aggregate active neural graph predictions, but same
24 tasks and evaluation graphs for each seed; correlated repetitions.
Primary pass true on all seeds. Independent enumeration without
minimal-cost pruning confirmed all 584 functions; all 216 search
transcripts checked for label consistency, remaining version-space size,
chosen membership and exact rule recovery. No weight changes.
This is bounded symbolic induction over a predefined Boolean language
using learned membership, with oracle feedback. Active exact lookup
matches active neural exactly; no evidence of a neural advantage over
symbolic lookup. No autonomous choice of task, invention of operators,
unbounded generalization, language understanding, or AGI. Target is
guaranteed in grammar by construction. Query scope (three vertices)
and all six inputs provided. Learner and teacher share process, isolated
only by interface, not security boundary.
Next prospective discriminant: hide out-of-grammar rules, require
abstention on inconsistent evidence, then permit controlled language
extension with a held-out evaluation and compare fixed grammar versus
extension under matched feedback budgets. No main change or promotion.
