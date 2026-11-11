"""OMEGA-AST-001: exact syntax-fact certificates across real Flask Git revisions.

Scope: Python AST declaration syntax, *not* behavior, proof that code runs,
scientific propositions, package API contracts, or author authentication.
Frozen at Flask 49943b5a..., first-parent 41 commits, initial Python files.
Based on versioned_evidence_replay.py's Git provenance functions; this is a
read-only experimental adapter, not a new orchestrator / durable memory.
"""
from __future__ import annotations

import argparse
import ast
from collections import defaultdict
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

from versioned_evidence_replay import (
    FROZEN_HEAD, history, _tree, _changed, git,
)

POLICIES=(
    "stale_no_refresh",
    "file_path_invalidate",
    "full_ast_reverify",
    "ast_dependency_index_8",
    "omega_ast_ledger_8",
    "invalidate_all_8",
)
MAX_CHECKS=8
MAX_PATHS=65


def _fingerprint(obj):
    text=json.dumps(obj,sort_keys=True,ensure_ascii=False,
                    separators=(",",":"))
    return sha256(text.encode("utf-8")).hexdigest()


def declaration_facts(source: bytes):
    """Return fixed-schema syntax facts. Ignore comments and source locations.

    Module statement fingerprint includes bodies. Declaration signatures
    exclude their bodies and decorators. No runtime behavior is proved.
    """
    root=ast.parse(source)
    facts={"module_ast":_fingerprint(
        {"module":ast.dump(root,include_attributes=False)})}
    occurrences=defaultdict(int)

    def add(node,name):
        if isinstance(node,ast.ClassDef):
            kind="class"
            sig={
                "kind":kind,
                "bases":[ast.dump(x,include_attributes=False)
                         for x in node.bases],
                "keywords":[ast.dump(x,include_attributes=False)
                            for x in node.keywords],
                "type_params":[ast.dump(x,include_attributes=False)
                               for x in getattr(node,"type_params",[])],
            }
        elif isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
            kind=("async_def" if isinstance(node,ast.AsyncFunctionDef)
                  else "def")
            sig={
                "kind":kind,
                "args":ast.dump(node.args,include_attributes=False),
                "returns":(ast.dump(node.returns,include_attributes=False)
                           if node.returns is not None else None),
                "type_params":[ast.dump(x,include_attributes=False)
                               for x in getattr(node,"type_params",[])],
            }
        else:
            raise TypeError("unsupported syntax declaration")
        stem=kind+":"+name
        index=occurrences[stem]
        occurrences[stem]+=1
        facts[f"{stem}#{index}"]=_fingerprint(sig)

    for node in root.body:
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
            add(node,node.name)
        elif isinstance(node,ast.ClassDef):
            add(node,node.name)
            for item in node.body:
                if isinstance(item,(ast.FunctionDef,ast.AsyncFunctionDef)):
                    add(item,node.name+"."+item.name)
    return facts


@lru_cache(maxsize=8192)
def source_facts(repo_directory: str, oid: str):
    raw=git(Path(repo_directory),"cat-file","blob",oid,binary=True)
    try:
        return declaration_facts(raw)
    except (SyntaxError,UnicodeError,ValueError) as exc:
        # A syntax failure cannot become a certificate; report abstention.
        return {"_parse_error":type(exc).__name__}


def candidate_paths(initial_tree):
    paths=sorted(p for p in initial_tree
                 if (p.startswith("src/flask/") or p.startswith("tests/"))
                 and p.endswith(".py"))
    if len(paths)!=MAX_PATHS:
        raise ValueError("Frozen initial source must have exactly 65 Python files")
    return tuple(paths)


class SyntaxFactLedger:
    """Explicitly experimental fact ledger; no persistent writes or model calls."""
    def __init__(self,mode,claim_paths):
        if mode not in POLICIES:raise ValueError("unsupported policy")
        self.mode=mode
        self.claim_paths=dict(claim_paths)
        self.by_path=defaultdict(list)
        for key,path in claim_paths.items():self.by_path[path].append(key)
        self.current={}
        self.known_oid={}
        self.archived=defaultdict(list)
        self.calls=0

    def _archive(self,claim,commit,path,oid,digest):
        if digest in (None,"missing","parse_error"):
            return
        last=self.archived[claim][-1] if self.archived[claim] else None
        if last is None or last["source_blob_oid"]!=oid or last["signature_sha256"]!=digest:
            self.archived[claim].append({
                "certified_at_commit":commit,"source_blob_oid":oid,
                "signature_sha256":digest,"source_path":path})

    def initialize(self,commit,tree,initial_facts):
        for path in self.by_path:
            source=tree[path]
            values=initial_facts[path]
            if "_parse_error" in values:
                raise ValueError("initial syntax is not parseable: "+path)
            self.known_oid[path]=source["oid"]
            for claim in self.by_path[path]:
                fact_id=claim.rsplit("::",1)[-1]
                d=values[fact_id]
                self.current[claim]=d
                self._archive(claim,commit,path,source["oid"],d)

    def transition(self,old,new,changed,commit,repo_directory):
        # Fail closed when the declared path manifest omits a tree change,
        # or invents one. Metadata is assumed Git-trustworthy, not signed.
        tracked=set(self.by_path)
        observed=changed & tracked
        independent={p for p in tracked if old.get(p)!=new.get(p)}
        if observed!=independent:
            raise ValueError("declared Git manifest contradicts tree metadata")
        if self.mode=="stale_no_refresh":
            return []
        if self.mode=="full_ast_reverify":
            for path in tracked:
                self._mark_pending(path,new)
            queue=sorted(p for p in tracked if p in new)
        else:
            if self.mode=="invalidate_all_8":
                targets=tracked
            elif self.mode=="file_path_invalidate":
                targets=observed
            else:
                targets=observed
            for path in targets:
                self._mark_pending(path,new)
            if self.mode=="file_path_invalidate":
                return []
            pending=[p for p in tracked if p in new and
                     any(self.current[c] is None for c in self.by_path[p])]
            queue=sorted(pending,key=lambda p:(p not in observed,p))
            queue=queue[:MAX_CHECKS]

        for p in queue:
            values=source_facts(str(repo_directory),new[p]["oid"])
            for claim in self.by_path[p]:
                fact_id=claim.rsplit("::",1)[-1]
                status=("parse_error" if "_parse_error" in values
                        else values.get(fact_id,"missing"))
                self.current[claim]=status
                self._archive(claim,commit,p,new[p]["oid"],status)
            self.known_oid[p]=new[p]["oid"]
        self.calls+=len(queue)
        return queue

    def _mark_pending(self,path,tree):
        for claim in self.by_path[path]:
            self.current[claim]=None if path in tree else "missing"

    def assess(self,actual):
        counts={"verified_current":0,"false_current":0,"pending":0,
                "unavailable":0,"parse_error":0}
        for claim,value in self.current.items():
            if value is None:counts["pending"]+=1
            elif value=="missing":counts["unavailable"]+=1
            elif value=="parse_error":counts["parse_error"]+=1
            elif value==actual[claim]:counts["verified_current"]+=1
            else:counts["false_current"]+=1
        assert sum(counts.values())==len(self.claim_paths)
        return {**counts,
                "cumulative_parse_reads":self.calls,
                "historical_certificates":sum(map(len,self.archived.values()))}


def evaluate(repo_path: Path):
    commits=history(repo_path)
    trees=[_tree(repo_path,c) for c in commits]
    paths=candidate_paths(trees[0])
    initial={p:source_facts(str(repo_path),trees[0][p]["oid"])
             for p in paths}
    if any("_parse_error" in x for x in initial.values()):
        raise ValueError("initial source parse failure")
    claims={}
    for path,values in sorted(initial.items()):
        for fact_key in sorted(values):
            claim_id=path+"::"+fact_key
            if claim_id in claims:raise AssertionError("duplicate claim")
            claims[claim_id]=path

    policies={name:SyntaxFactLedger(name,claims) for name in POLICIES}
    for ledger in policies.values():
        ledger.initialize(commits[0],trees[0],initial)

    events=[]
    observed_syntax_changes=0
    source_revisions_with_unchanged_module_ast=0
    declaration_deltas=0
    prior_actual={
        c:initial[p][c.rsplit("::",1)[-1]] for c,p in claims.items()
    }

    for step in range(1,41):
        previous,target=commits[step-1:step+1]
        old,new=trees[step-1:step+1]
        changed=_changed(repo_path,previous,target)
        chosen={}
        for name,ledger in policies.items():
            chosen[name]=ledger.transition(old,new,changed,target,repo_path)
        # Oracle is explicitly computed *after* all policy choices.
        current_source={
            p:(source_facts(str(repo_path),new[p]["oid"])
               if p in new else None)
            for p in paths
        }
        actual={
            c:("missing" if current_source[p] is None
               else ("parse_error" if "_parse_error" in current_source[p]
                     else current_source[p].get(c.rsplit("::",1)[-1],"missing")))
            for c,p in claims.items()
        }
        scores={name:policy.assess(actual)
                for name,policy in policies.items()}
        for name in ("ast_dependency_index_8","omega_ast_ledger_8"):
            if scores[name]["false_current"]!=0:
                raise AssertionError("stale confident AST claim")
        if scores["omega_ast_ledger_8"]!=scores["ast_dependency_index_8"]:
            raise AssertionError("no unique Omega credit vs equal AST index")
        if chosen["omega_ast_ledger_8"]!=chosen["ast_dependency_index_8"]:
            raise AssertionError("Omega and index decisions diverged")
        for p in set(paths)&changed:
            if p in old and p in new:
                old_values=source_facts(str(repo_path),old[p]["oid"])
                new_values=current_source[p]
                if ("_parse_error" not in old_values
                        and "_parse_error" not in new_values
                        and old_values["module_ast"]==new_values["module_ast"]):
                    source_revisions_with_unchanged_module_ast+=1
        change_count=sum(
            prior_actual[c]!=actual[c] for c in claims
            if prior_actual[c]!="parse_error"
            and actual[c]!="parse_error")
        observed_syntax_changes+=change_count
        declaration_change_count=sum(
            prior_actual[c]!=actual[c] for c in claims
            if not c.endswith("::module_ast")
            and prior_actual[c]!="parse_error"
            and actual[c]!="parse_error")
        declaration_deltas+=declaration_change_count
        prior_actual=actual
        events.append({
            "step":step,"split":"calibration" if step<=20 else "test",
            "commit":target,
            "source_changed_paths":len(changed&set(paths)),
            "exact_fact_deltas":change_count,
            "declaration_fact_deltas":declaration_change_count,
            "rechecks":{k:list(v) for k,v in chosen.items()},
            "scores":scores,
        })

    def summary(group):
        out={}
        for name in POLICIES:
            ss=[x["scores"][name] for x in group]
            previous=(events[group[0]["step"]-2]["scores"][name]
                      ["cumulative_parse_reads"]
                      if group[0]["step"]>1 else 0)
            out[name]={
                "steps":len(group),
                "verified_current_claim_steps":sum(x["verified_current"] for x in ss),
                "false_current_claim_steps":sum(x["false_current"] for x in ss),
                "pending_claim_steps":sum(x["pending"] for x in ss),
                "unavailable_claim_steps":sum(x["unavailable"] for x in ss),
                "parse_error_claim_steps":sum(x["parse_error"] for x in ss),
                "logical_ast_file_parses":
                    ss[-1]["cumulative_parse_reads"]-previous,
                "final_archived_certificates":ss[-1]["historical_certificates"],
            }
        return out

    return {
        "status":"EXTERNAL_HISTORICAL_PYTHON_AST_DECLARATION_CLAIMS",
        "source_commit":FROZEN_HEAD,
        "start_commit":commits[0],
        "n_source_revisions":41,
        "n_transitions":40,
        "n_original_python_files":len(paths),
        "n_fixed_syntax_claims":len(claims),
        "n_initial_declaration_claims":
            len(claims)-len(paths),
        "n_syntax_fact_deltas_in_all_history":observed_syntax_changes,
        "n_declaration_fact_deltas_in_all_history":declaration_deltas,
        "n_changed_python_file_events_with_same_module_ast":
            source_revisions_with_unchanged_module_ast,
        "n_test_declaration_fact_deltas":sum(
            x["declaration_fact_deltas"] for x in events[20:]),
        "n_source_file_changes_in_test":sum(
            x["source_changed_paths"] for x in events[20:]),
        "summaries":{"calibration":summary(events[:20]),
                     "test":summary(events[20:])},
        "equal_budget_omega_and_ast_index_identical":True,
        "semantic_meaning":"only Python AST syntax (not runtime behavior)",
        "external_solver_or_llm_calls":0,
        "selected_paths":paths,
        "fixed_claims":claims,
        "archived_omega_claims":{
            k:list(v) for k,v in policies["omega_ast_ledger_8"].archived.items()},
        "events":events,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-repo",required=True)
    parser.add_argument("--json-output")
    args=parser.parse_args()
    result=evaluate(Path(args.source_repo))
    if args.json_output:
        Path(args.json_output).write_text(
            json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2),
            encoding="utf-8")
    keep=("status","source_commit","n_source_revisions",
          "n_original_python_files","n_fixed_syntax_claims",
          "n_initial_declaration_claims","n_syntax_fact_deltas_in_all_history",
          "n_declaration_fact_deltas_in_all_history",
          "n_changed_python_file_events_with_same_module_ast",
          "n_test_declaration_fact_deltas","n_source_file_changes_in_test",
          "summaries","equal_budget_omega_and_ast_index_identical")
    print("OMEGA_AST_FACT_REPLAY "+json.dumps(
        {k:result[k] for k in keep},sort_keys=True,ensure_ascii=False))


if __name__=="__main__":
    main()
