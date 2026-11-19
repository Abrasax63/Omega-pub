# PROOFNET26 — genuine external math statements with an audited Lean reference

**Preregistered 2026-11-19, BEFORE downloading selected examples into the evaluation and BEFORE writing evaluation code.**

## Scientific question
Can Omega's **unchanged** two formalizers A (TYPED24) and B (DUAL25) recognize complete natural-language theorem statements drawn from a pre-existing, externally audited human-written mathematics corpus, without introducing invented hypotheses, fake finite domains or false claims of Lean certification?

## Authoritative external corpus
- `marcusm117/ProofNet-Verified`, pinned upstream Git commit **`b7ca411a2abaa6caf3580192b30d865e5bd10bc4`** dated 2026-11-07 (pre-dating this experiment), Apache-2.0 licensed project.
- Original audited project has 367 paired informal statements and Lean formal theorem statements. The project describes human reviewers **and an AI agent**, NOT two independent human annotators hired for this Omega experiment. Reference is independently **created and externally audited**, but actual two-new-human blind annotation **does not exist here**.
- Preselected **16 deterministic indices**: 1, 2, 3, 6, 10, 22, 40, 80, 120, 160, 200, 240, 280, 320, 350, 367. No hand-picking cases after observing Omega results. If a selected file is missing or lacks both full informal statement and Lean formal statement, the whole experiment fails as `INCOMPLETE_EXTERNAL_COHORT` instead of picking replacements.
- Freeze each remote .lean file path and Git blob SHA in a manifest **before evaluation**. Workflow fetches only **pinned raw GitHub URLs** and validates byte-exact Git hashes. No paid API, no private resources, no edits to the outside dataset.
- The full **informal statement** and corresponding Lean theorem are read from the identical original file; no paraphrasing, rewriting of hypotheses, synthetic constraints, or treating an isolated fragment as a complete theorem. The informal statement is complete as represented in this curated dataset; textbook references may have extra implicit context, which Omega must not invent.

## Comparison and scoring
1. Source/provenance stage: exact original-file hash, real informal-statement span, Lean reference region. Evidence is a literal reference, NOT proof.
2. **A** and **B** (code frozen at DUAL25 #210) run on the same raw informal source **without formatting modifications**. Optional second stage wraps the original informal statement in a neutral Markdown document with **NO invented function or domain** to separate layout coverage from semantic coverage. Text itself must remain byte-for-byte identical.
3. Structural `agreement` means both emit the same completely typed claim with matched source citations and exact checks; a shared abstention is **not** a semantic agreement.
4. Refusals are classified as `SOURCE_FORMAT_UNSUPPORTED`, `MATHEMATICAL_DOMAIN_UNSUPPORTED`, `AMBIGUOUS`, or `OTHER`; never turn a missing inference into a FALSE assertion.
5. The existing Lean reference is a **curated independent target**, and may guide a *future* Lean translation evaluation. Our A/B currently produce a finite modular-function IR, **not Lean 4**. **Do not report an exact-match / semantic-fidelity accuracy against Lean at all** unless both sides share a valid comparison representation and the produced results can actually be checked for equivalence. Record `NOT_COMPARABLE_TYPE_SYSTEMS` instead.
6. Report (a) 16/16 provenance + full statement and formal reference pairs; (b) literal capture success; (c) actual A/B coverage + abstentions; (d) unsupported-domain categories; (e) number of human reviews commissioned or obtained = 0; (f) unchanged SEM22 168 previous exact cases.
7. If A/B cover 0/16, report **FAILED_GENERALIZATION_ON_PAIRED_EXTERNAL_SET**, even if refusal safety and exact input recovery are perfect. This is important negative evidence. Do not tune the frozen parsers on these 16 then rescore the same samples as holdout.
8. Test adversarial incomplete Lean delimiters, shifted reference spans, missing informal statements, altered raw bytes, duplicate/missing cases, and impossible formalization claims. Any ambiguity => quarantine, not promotion.

## Governance
DRAFT PR stacked on #210; main unchanged; no merge, no auto-generated rules, no assertion of AGI or general mathematical intelligence. Results archived with source citations, commit, exact hashes, and honest uncertainty.

## Sources
- ProofNet-Verified repository (Apache-2.0): https://github.com/marcusm117/ProofNet-Verified
- Paper: Ground False: Dissecting and Repairing Errors in Formal Mathematics Benchmarks (NeurIPS 2026), linked in upstream README.
- Poiroux et al., Reliable Evaluation and Benchmarks for Statement Autoformalization (EMNLP 2025), https://aclanthology.org/2025.emnlp-main.907/
