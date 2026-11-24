# SEMANTIC-IR01 — guarded intermediate representation
Prospective follow-up to failed TOOLROUTE01. Freeze deterministic parser
and typed plan guard before new holdout commit. Not an LLM, not learned
semantic knowledge. Text-only routing (same envelope as prior test),
French; compare frozen old NB and keyword baselines, oracle, new IR.
IR expresses domain evidence, positive goals, forbidden operations,
ordered dependencies and abstention reason. Parser may abstain; require
positive evidence of task scope, fail on unsupported domain, ambiguity,
missing information or conflicting instructions. Guard independently
validates operation scope/order and absence of forbidden operations;
it cannot certify correct interpretation of arbitrary language.
Fresh 60 short text templates, 12 per class (projection, closure, inverse,
compose, unsupported); 2 payloads each, 120 total; no exact text reuse.
Include negation, reversed/ambiguous ordering, continuous/discrete scope,
unsupported multiple goals, and missing observations. New templates
authored by same experimenter after parser freeze, not external/blind.
No tuning on holdout. Independent mathematical verifier from TOOLROUTE01,
rank-one payload limits unchanged. Record exact route+result, class
counts, unsafe dispatch, abstention on supported, and reasons. Primary:
>=108/120 exact, >=22/24 composition, zero unsupported dispatch, >=6
more correct than best baseline. Oracle 120/120 required. Independent
guard mutation tests for forged/invalid plans (unknown, forbidden,
reversed dependency, missing domain). No promotion if any primary
condition fails; even pass only scoped experimental evidence. No
automatic runtime activation, model training, paid API or main change.
