"""OMEGA-EVIDENCE-001: Git-backed, version-scoped evidence replay.

This is an experiment about the *applicability* of file-content certificates
to Git versions. It does not prove semantic claims about Flask, authenticate
repository authors, or make an LLM reason about source content.

The external Flask history is pinned to a specific commit and its previous
40 first-parent transitions. Logical verification cost = SHA-256 computation
from retrieved Git blob bytes; diff metadata retrieval is common and unpriced.
Strong indexed baseline and Omega-labeled experimental ledger share the same
information, budget, and refresh order. No unique Omega gain is assumed.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from hashlib import sha256
from itertools import chain
import json
from pathlib import Path
import subprocess


SOURCE_REPOSITORY = "https://github.com/pallets/flask"
FROZEN_HEAD = "49943b5a94413a530761350f04e896f76e8d620e"
FIRST_PARENT_COMMITS = 41
TRANSITIONS = FIRST_PARENT_COMMITS - 1
SELECTED_PATHS_LIMIT = 128
RECHECK_BUDGET = 8
PREFIXES = ("src/flask/", "tests/", "docs/")
EXTENSIONS = (".py", ".rst", ".md", ".toml")
METHODS = (
    "no_refresh", "full_reverify", "dependency_index_8",
    "omega_ledger_8", "invalidate_all_8",
)


def git(repo: Path, *args: str, binary=False):
    cmd = ["git", "-C", str(repo), *args]
    r = subprocess.run(cmd, check=True, capture_output=True)
    return r.stdout if binary else r.stdout.decode("utf-8", "surrogateescape").strip()


def history(repo: Path):
    # This also verifies that the pinned object exists in the source clone.
    actual = git(repo, "rev-parse", "--verify", FROZEN_HEAD + "^{commit}")
    if actual != FROZEN_HEAD:
        raise ValueError("wrong upstream head")
    backwards = git(
        repo, "rev-list", "--first-parent", f"--max-count={FIRST_PARENT_COMMITS}",
        FROZEN_HEAD,
    ).splitlines()
    if len(backwards) != FIRST_PARENT_COMMITS:
        raise ValueError("source checkout lacks the 41 pinned ancestor commits")
    return list(reversed(backwards))


def _tree(repo: Path, commit: str):
    # File modes are deliberately not treated as content digests; a chmod
    # can require a recheck but need not change the content hash.
    result = {}
    raw = git(repo, "ls-tree", "-r", "-z", commit, "--", "src/flask", "tests",
              "docs", binary=True)
    for entry in raw.split(b"\x00"):
        if not entry:
            continue
        lhs, path = entry.split(b"\t", 1)
        parts = lhs.split()
        if len(parts) != 3 or parts[1] != b"blob":
            continue
        name = path.decode("utf-8", "surrogateescape")
        if name.startswith(PREFIXES) and name.endswith(EXTENSIONS):
            result[name] = {"oid": parts[2].decode("ascii"),
                            "mode": parts[0].decode("ascii")}
    return result


def _changed(repo: Path, previous: str, target: str):
    # --no-renames exposes both old and new paths, rather than concealing
    # deletions behind rename detection.
    raw = git(repo, "diff", "--no-renames", "--name-only", "-z",
              previous, target, binary=True)
    return {s.decode("utf-8", "surrogateescape")
            for s in raw.split(b"\x00") if s}


def selected_paths(start_tree):
    eligible = list(start_tree)
    ordered = sorted(eligible, key=lambda p:(sha256(p.encode("utf-8",
                                              "surrogateescape")).digest(),p))
    if len(ordered) < 4:
        raise ValueError("not enough source paths to study dependency claims")
    return tuple(ordered[:SELECTED_PATHS_LIMIT])


def claims_for(paths):
    n = len(paths)
    claims = {}
    for i, p in enumerate(paths):
        claims[f"single:{i:03d}"] = (p,)
        claims[f"pair:{i:03d}"] = (p, paths[(i + 1) % n])
        claims[f"triple:{i:03d}"] = (
            p,paths[(i+1)%n],paths[(i+2)%n])
    return claims


def sha256_git_blob(repo: Path, oid: str):
    if len(oid) != 40 or any(x not in "0123456789abcdef" for x in oid):
        raise ValueError("unexpected Git object id")
    raw = git(repo, "cat-file", "blob", oid, binary=True)
    return sha256(raw).hexdigest()


class EvidenceLedger:
    def __init__(self, name, paths, claim_deps):
        if name not in METHODS:
            raise ValueError("unsupported policy")
        self.name = name
        self.paths = tuple(paths)
        self.deps = claim_deps
        self.current = {}  # path -> sha256, or None (pending) or marker (missing)
        self.historical = defaultdict(list)  # immutable assertion revisions
        self.history_validations = 0
        self.calls = 0
        self._start = None

    def initialize(self, commit, tree, blob_reader):
        if self._start is not None:
            raise ValueError("already initialized")
        self._start = commit
        for p in self.paths:
            entry = tree.get(p)
            if entry is None:
                raise AssertionError("all initial paths must be present")
            self.current[p] = blob_reader(entry["oid"])
        self._archive_current(commit)

    def _archive_current(self, commit):
        for key, dependent in self.deps.items():
            if any(self.current[p] is None or self.current[p] == "missing"
                   for p in dependent):
                continue
            digests = tuple((p,self.current[p]) for p in dependent)
            last = self.historical[key][-1] if self.historical[key] else None
            if last is None or last["digests"] != digests:
                self.historical[key].append({
                    "certified_at_commit":commit,
                    "digests":digests,
                })

    def transition(self, previous_tree, target_tree, changed_paths, commit,
                   blob_reader):
        """Decide from metadata; never inspect target answers/oracle for choices."""
        if self._start is None:
            raise ValueError("not initialized")
        scope = set(self.paths)
        relevant = changed_paths & scope

        if self.name == "no_refresh":
            chosen = []
        elif self.name == "full_reverify":
            chosen = sorted(p for p in self.paths if p in target_tree)
            for p in self.paths:
                self.current[p] = None if p in target_tree else "missing"
        else:
            if self.name == "invalidate_all_8":
                for p in self.paths:
                    self.current[p] = None if p in target_tree else "missing"
            else:
                for p in relevant:
                    self.current[p] = None if p in target_tree else "missing"
            pending = {
                p for p in self.paths if self.current[p] is None
                and p in target_tree
            }
            # Current changes first, then older pending certificates.
            priority = sorted(pending,key=lambda p:(p not in relevant,p))
            chosen = priority[:RECHECK_BUDGET]

        # Every read corresponds to a Git blob and SHA-256 computation; the
        # source tree is an immutable content-addressed repository snapshot.
        for p in chosen:
            entry = target_tree.get(p)
            if entry is None:
                raise AssertionError("cannot hash deleted source")
            self.current[p] = blob_reader(entry["oid"])
        self.calls += len(chosen)
        self._archive_current(commit)
        return {"changed_in_portfolio":len(relevant),
                "chosen_for_verification":list(chosen)}

    def assess(self, commit, truth):
        """Truth is passed ONLY after all policies have made the decisions."""
        safe = false_current = pending = unavailable = 0
        bad_examples = []
        for key, dependent in self.deps.items():
            vals = [self.current[p] for p in dependent]
            if any(v == "missing" for v in vals):
                unavailable += 1
            elif any(v is None for v in vals):
                pending += 1
            else:
                actual = all(
                    truth.get(p) is not None and self.current[p] == truth[p]
                    for p in dependent
                )
                if actual:
                    safe += 1
                else:
                    false_current += 1
                    if len(bad_examples) < 4:
                        bad_examples.append(key)
        total=len(self.deps)
        if sum((safe,false_current,pending,unavailable))!=total:
            raise AssertionError("claim partition mismatch")
        return {
            "commit":commit,
            "correct_current":safe,
            "false_current":false_current,
            "pending":pending,
            "unavailable":unavailable,
            "total_assertions":total,
            "cumulative_verified_blob_reads":self.calls,
            "preserved_certificate_versions":
                sum(len(v) for v in self.historical.values()),
            "false_current_examples":bad_examples,
        }


def evaluate_repo(repo: Path):
    commits=history(repo)
    trees=[_tree(repo,oid) for oid in commits]
    paths=selected_paths(trees[0])
    deps=claims_for(paths)
    policies={m:EvidenceLedger(m,paths,deps) for m in METHODS}

    for policy in policies.values():
        policy.initialize(
            commits[0],trees[0],lambda oid:sha256_git_blob(repo,oid))
    events=[]
    raw_stats=[]
    for index in range(1,len(commits)):
        parent,target=commits[index-1:index+1]
        old,new=trees[index-1:index+1]
        changed=_changed(repo,parent,target)
        changes={}
        for name,ledger in policies.items():
            changes[name]=ledger.transition(
                old,new,changed,target,
                lambda oid:sha256_git_blob(repo,oid))
        # The reference rehashes all paths separately after every decision,
        # not as a hidden input to the policy.
        actual={p:(sha256_git_blob(repo,new[p]["oid"]) if p in new else None)
                for p in paths}
        statuses={name:ledger.assess(target,actual)
                  for name,ledger in policies.items()}
        for name in ("dependency_index_8","omega_ledger_8"):
            if statuses[name]["false_current"]!=0:
                raise AssertionError("indexed policy asserted stale current evidence")
        events.append({
            "step":index,
            "split":"calibration" if index<=20 else "test",
            "previous_commit":parent,"commit":target,
            "n_all_changed_paths":len(changed),
            "n_portfolio_changed_paths":len(changed&set(paths)),
            "decisions":changes,
            "scores":statuses,
        })
        raw_stats.append(len(changed&set(paths)))

    def summarize(group):
        stats={}
        for name in METHODS:
            instances=[e["scores"][name] for e in group]
            stats[name]={
                "steps":len(instances),
                "correct_current_claim_steps":
                    sum(x["correct_current"] for x in instances),
                "false_current_claim_steps":
                    sum(x["false_current"] for x in instances),
                "pending_claim_steps":
                    sum(x["pending"] for x in instances),
                "unavailable_claim_steps":
                    sum(x["unavailable"] for x in instances),
                "blob_read_verifications":
                    (instances[-1]["cumulative_verified_blob_reads"]-
                     (events[group[0]["step"]-2]["scores"][name]
                       ["cumulative_verified_blob_reads"]
                      if group[0]["step"]>1 else 0)),
                "final_preserved_certificate_versions":
                    instances[-1]["preserved_certificate_versions"],
            }
        return stats

    calibration=events[:20]
    holdout=events[20:]
    assert len(calibration)==len(holdout)==20
    total=sum(len(deps) for _ in events)
    if any(s["total_assertions"]!=len(deps)
           for e in events for s in e["scores"].values()):
        raise AssertionError("claim count drift")
    for e in events:
        if e["scores"]["omega_ledger_8"]!=e["scores"]["dependency_index_8"]:
            raise AssertionError("Omega is not allowed to claim special gain")
        if e["decisions"]["omega_ledger_8"]!=e["decisions"]["dependency_index_8"]:
            raise AssertionError("policy mismatch")
    return {
        "status":"REAL_EXTERNAL_GIT_VERSION_EVIDENCE_NOT_SEMANTIC_PROOF",
        "source_repository":SOURCE_REPOSITORY,
        "frozen_source_commit":FROZEN_HEAD,
        "source_start_commit":commits[0],
        "n_source_commits":len(commits),
        "n_actual_changes":TRANSITIONS,
        "n_sampled_paths":len(paths),
        "n_compound_assertions":len(deps),
        "claim_steps_per_policy":total,
        "budget_sha256_reads_per_change":RECHECK_BUDGET,
        "n_events_with_relevant_changes":
            sum(bool(n) for n in raw_stats),
        "n_events_without_relevant_changes":
            sum(not bool(n) for n in raw_stats),
        "n_events_over_eight_changed_paths":
            sum(n>RECHECK_BUDGET for n in raw_stats),
        "summaries":{
            "calibration":summarize(calibration),
            "test":summarize(holdout),
        },
        "comparable_index_omega_identical_for_all_events":True,
        "source_content_certification_scope":
            "SHA-256 of Git blob bytes at a commit, not semantic truth",
        "source_author_authenticity_verified":False,
        "source_metadata_changes_priced":False,
        "llm_calls":0,
        "external_solver_executions":0,
        "selected_paths":paths,
        "events":events,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-repo",required=True)
    parser.add_argument("--json-output",default=None)
    args=parser.parse_args()
    result=evaluate_repo(Path(args.source_repo))
    if args.json_output:
        Path(args.json_output).write_text(
            json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False),
            encoding="utf-8")
    print("OMEGA_VERSIONED_EVIDENCE_RESULT "+json.dumps({
        key:result[key] for key in (
            "status","frozen_source_commit","source_start_commit",
            "n_source_commits","n_actual_changes","n_sampled_paths",
            "n_compound_assertions","n_events_with_relevant_changes",
            "n_events_without_relevant_changes",
            "n_events_over_eight_changed_paths","summaries",
            "comparable_index_omega_identical_for_all_events",
        )},sort_keys=True,ensure_ascii=False))


if __name__=="__main__":
    main()
