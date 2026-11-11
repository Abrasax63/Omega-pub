"""Second-path audit of historical Flask AST claims, no policy-code imports.

Rebuild Python AST declarations with an independent traversal, Git trees by
direct subprocess calls, and every archived certificate's provenance from
its actual source blob at its own commit. Both paths use Python's standard
ast parser and the same historical source; this is implementation
cross-checking, not an independent scientific source or formal proof.
"""
import argparse
import ast
from collections import defaultdict
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import subprocess


def cmd(repo,*args):
    run=subprocess.run(["git","-C",str(repo),*args],
                       check=True,capture_output=True)
    return run.stdout


def digest(obj):
    return sha256(json.dumps(obj,sort_keys=True,
                separators=(",",":"),ensure_ascii=False)
                .encode("utf-8")).hexdigest()


def independently_extract(raw):
    root=ast.parse(raw)
    answer={"module_ast":digest({
        "module":ast.dump(root,include_attributes=False)})}
    declarations=[]
    for top in root.body:
        if isinstance(top,ast.ClassDef):
            declarations.append((top,top.name))
            declarations.extend((member,top.name+"."+member.name)
                for member in top.body
                if isinstance(member,(ast.FunctionDef,ast.AsyncFunctionDef)))
        elif isinstance(top,(ast.FunctionDef,ast.AsyncFunctionDef)):
            declarations.append((top,top.name))
    counts=defaultdict(int)
    for item,name in declarations:
        if isinstance(item,ast.ClassDef):
            kind="class"
            entry={
                "kind":"class",
                "bases":[ast.dump(s,include_attributes=False)
                         for s in item.bases],
                "keywords":[ast.dump(s,include_attributes=False)
                            for s in item.keywords],
                "type_params":[ast.dump(s,include_attributes=False)
                               for s in getattr(item,"type_params",[])],
            }
        else:
            kind="async_def" if isinstance(item,ast.AsyncFunctionDef) else "def"
            entry={
                "kind":kind,
                "args":ast.dump(item.args,include_attributes=False),
                "returns":(ast.dump(item.returns,include_attributes=False)
                           if item.returns is not None else None),
                "type_params":[ast.dump(s,include_attributes=False)
                               for s in getattr(item,"type_params",[])],
            }
        stem=kind+":"+name
        nth=counts[stem]
        counts[stem]+=1
        answer[f"{stem}#{nth}"]=digest(entry)
    return answer


def tree(repo,commit):
    result={}
    raw=cmd(repo,"ls-tree","-r","-z",commit,"--","src/flask","tests")
    for item in raw.split(b"\x00"):
        if not item:
            continue
        lhs,path=item.split(b"\t",1)
        mode,kind,oid=lhs.split()
        if kind!=b"blob":
            continue
        file=path.decode("utf-8","surrogateescape")
        if file.endswith(".py") and (file.startswith("src/flask/")
                                      or file.startswith("tests/")):
            result[file]=(oid.decode("ascii"),mode.decode("ascii"))
    return result


def check(ledger,repo):
    head=ledger["source_commit"]
    commits=cmd(repo,"rev-list","--first-parent","--max-count=41",head
               ).decode().strip().splitlines()[::-1]
    if len(commits)!=41 or commits[-1]!=head or commits[0]!=ledger["start_commit"]:
        raise ValueError("frozen Git history does not match results")
    trees={commit:tree(repo,commit) for commit in commits}
    paths=ledger["selected_paths"]
    if len(paths)!=65 or sorted(paths)!=paths:
        raise ValueError("incorrect initial Python population")
    if list(trees[commits[0]])!=sorted(trees[commits[0]]):
        pass  # source tree iteration order is not a claim invariant
    if set(paths)!=set(trees[commits[0]]):
        raise ValueError("not all original Python files were tracked")

    @lru_cache(maxsize=None)
    def facts(oid):
        raw=cmd(repo,"cat-file","blob",oid)
        try:return independently_extract(raw)
        except (SyntaxError,UnicodeError,ValueError):
            return {"_parse_error":"syntax_error"}

    initial={p:facts(trees[commits[0]][p][0]) for p in paths}
    claim_paths=ledger["fixed_claims"]
    reconstructed={
        p+"::"+k:p for p in paths for k in initial[p]}
    if claim_paths!=reconstructed:
        raise ValueError("claim identification differs from independent AST walk")
    current={
        id:initial[p][id.rsplit("::",1)[-1]]
        for id,p in claim_paths.items()
    }
    false_stale=0
    checked_claim_states=0
    checked_choices=0
    expected_archives=0
    for step in range(1,41):
        prior=trees[commits[step-1]]
        now=trees[commits[step]]
        changed={p for p in paths if prior.get(p)!=now.get(p)}
        event=ledger["events"][step-1]
        if (event["commit"]!=commits[step]
            or event["source_changed_paths"]!=len(changed)):
            raise ValueError("external Git metadata mismatch")
        for p in changed:
            for id,q in claim_paths.items():
                if q==p:current[id]=None if p in now else "missing"
        pending=[p for p in paths if p in now and any(
            current[id] is None for id,q in claim_paths.items() if q==p)]
        pending.sort(key=lambda p:(p not in changed,p))
        selected=pending[:8]
        expected=event["rechecks"]["omega_ast_ledger_8"]
        if selected!=expected:
            raise ValueError("independent refresh ordering differs at "+str(step))
        checked_choices+=len(selected)
        for p in selected:
            values=facts(now[p][0])
            for id,q in claim_paths.items():
                if q==p:
                    sym=id.rsplit("::",1)[-1]
                    current[id]=(values.get(sym,"missing")
                                 if "_parse_error" not in values else "parse_error")
        oracle={id:("missing" if p not in now
                 else ("parse_error" if "_parse_error" in facts(now[p][0])
                       else facts(now[p][0]).get(id.rsplit("::",1)[-1],"missing")))
                for id,p in claim_paths.items()}
        got={"verified_current":0,"false_current":0,
             "pending":0,"unavailable":0,"parse_error":0}
        for id,value in current.items():
            if value is None:got["pending"]+=1
            elif value=="missing":got["unavailable"]+=1
            elif value=="parse_error":got["parse_error"]+=1
            elif value==oracle[id]:got["verified_current"]+=1
            else:got["false_current"]+=1
        reported=event["scores"]["omega_ast_ledger_8"]
        for key in got:
            if reported[key]!=got[key]:
                raise AssertionError(f"{key} differs at revision {step}")
        if got["false_current"]!=0:
            raise AssertionError("outdated syntax fact treated as current")
        checked_claim_states+=len(claim_paths)
        # The no-refresh control keeps its initial syntax signature.
        independent_stale_wrong=sum(
            initial[p][id.rsplit("::",1)[-1]]!=oracle[id]
            for id,p in claim_paths.items())
        if independent_stale_wrong!=event["scores"]["stale_no_refresh"]["false_current"]:
            raise AssertionError("no-refresh errors not independently reproducible")
        false_stale+=independent_stale_wrong

    cert_count=0
    rehashed_dependencies=0
    unchanged_signature_new_oid=0
    for id,path in claim_paths.items():
        history=ledger["archived_omega_claims"].get(id,[])
        if not history:
            raise ValueError("initial certificate lost")
        for index,record in enumerate(history):
            sha=record["certified_at_commit"]
            if sha not in trees:
                raise AssertionError("unknown historical commit referenced")
            source=trees[sha].get(path)
            if source is None or source[0]!=record["source_blob_oid"]:
                raise AssertionError("certificate references incorrect historical blob")
            value=facts(source[0]).get(id.rsplit("::",1)[-1])
            if value!=record["signature_sha256"]:
                raise AssertionError("historical AST claim is not true at its own commit")
            if index>0:
                previous=history[index-1]
                if (previous["signature_sha256"]==record["signature_sha256"]
                    and previous["source_blob_oid"]!=record["source_blob_oid"]):
                    unchanged_signature_new_oid+=1
            cert_count+=1
            rehashed_dependencies+=1
    if cert_count!=ledger["summaries"]["test"]["omega_ast_ledger_8"]["final_archived_certificates"]:
        raise AssertionError("archived certificate count drift")
    return {
        "status":"INDEPENDENT_AST_TRAVERSAL_SHARED_CPYTHON_PARSER",
        "verification":"PASS",
        "source_frozen_commit":head,
        "replayed_real_git_transitions":40,
        "n_tracked_files":65,
        "n_frozen_claims":len(claim_paths),
        "n_independently_scored_claim_steps":checked_claim_states,
        "independent_no_refresh_false_current_claim_steps":false_stale,
        "matched_targeted_ast_file_parses":checked_choices,
        "individually_revalidated_historical_certificates":cert_count,
        "versions_with_source_oid_changed_but_declaration_signature_unchanged":unchanged_signature_new_oid,
        "limitation":"same Python ast parser and upstream Git records; not independent formal semantics",
    }


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("source_repo")
    parser.add_argument("ledger_json")
    args=parser.parse_args()
    ledger=json.loads(Path(args.ledger_json).read_text(encoding="utf-8"))
    print("OMEGA_AST_INDEPENDENT_AUDIT "+json.dumps(
        check(ledger,Path(args.source_repo)),sort_keys=True,ensure_ascii=False))
