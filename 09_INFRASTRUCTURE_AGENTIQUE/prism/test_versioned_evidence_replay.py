"""Adversarial non-regressions for real-source version-bound certificates.

Synthetic fixtures test edge cases. The separate GitHub Actions job then
checks actual upstream revisions and SHA-256 blobs, not these fixtures.
"""
from hashlib import sha256
import unittest

from versioned_evidence_replay import (
    EvidenceLedger,claims_for,selected_paths,sha256_git_blob,METHODS,
    FROZEN_HEAD,FIRST_PARENT_COMMITS,RECHECK_BUDGET,
)


class VersionedEvidenceTests(unittest.TestCase):
    def setup_four(self):
        paths=tuple(f"src/flask/p{i}.py" for i in range(4))
        deps=claims_for(paths)
        values={f"oid-{i}":f"baseline-{i}".encode() for i in range(4)}
        tree={path:{"oid":f"oid-{i}","mode":"100644"}
              for i,path in enumerate(paths)}
        reader=lambda oid:sha256(values[oid]).hexdigest()
        strategies={m:EvidenceLedger(m,paths,deps) for m in METHODS}
        for l in strategies.values():l.initialize("commit0",tree,reader)
        return paths,deps,values,tree,reader,strategies

    def test_same_initial_certificates_no_hidden_merge(self):
        paths,deps,values,old,reader,p=self.setup_four()
        self.assertEqual(len(deps),12)
        initial={path:reader(old[path]["oid"]) for path in paths}
        for obj in p.values():
            self.assertEqual(obj.assess("commit0",initial)["correct_current"],12)
            self.assertEqual(obj.assess("commit0",initial)["false_current"],0)
            self.assertEqual(sum(map(len,obj.historical.values())),12)
            self.assertTrue(all(len(x)==1 for x in obj.historical.values()))

    def test_actual_change_revokes_only_affected_evidence_and_keeps_history(self):
        paths,deps,values,old,reader,p=self.setup_four()
        new=dict(old)
        new[paths[1]]={"oid":"new-1","mode":"100644"}
        values["new-1"]=b"changed-source"
        changed={paths[1]}
        truth={path:reader(new[path]["oid"]) for path in paths}
        for name,obj in p.items():
            obj.transition(old,new,changed,"commit1",reader)
            scored=obj.assess("commit1",truth)
            if name=="no_refresh":
                self.assertGreater(scored["false_current"],0)
                self.assertEqual(obj.calls,0)
            elif name=="full_reverify":
                self.assertEqual(obj.calls,4)
                self.assertEqual(scored["correct_current"],12)
            elif name in ("dependency_index_8","omega_ledger_8"):
                self.assertEqual(obj.calls,1)
                self.assertEqual(scored["correct_current"],12)
                self.assertEqual(scored["false_current"],0)
                # Historical record remains verifiable at original commit,
                # and the updated current record has changed content.
                old_record=obj.historical["single:001"][0]
                new_record=obj.historical["single:001"][-1]
                self.assertEqual(old_record["certified_at_commit"],"commit0")
                self.assertEqual(new_record["certified_at_commit"],"commit1")
                self.assertEqual(old_record["digests"][0][1],reader(old[paths[1]]["oid"]))
                self.assertEqual(new_record["digests"][0][1],truth[paths[1]])
                self.assertEqual(len(obj.historical["single:000"]),1)

    def test_budget_eight_never_claims_unverified_changed_contents_current(self):
        paths=tuple(f"tests/test_p{i:02d}.py" for i in range(12))
        deps=claims_for(paths)
        old={p:{"oid":f"old-{i}","mode":"100644"}
             for i,p in enumerate(paths)}
        new={p:{"oid":f"new-{i}","mode":"100644"}
             for i,p in enumerate(paths)}
        values={**{f"old-{i}":f"old bytes {i}".encode() for i in range(12)},
                **{f"new-{i}":f"new bytes {i}".encode() for i in range(12)}}
        reader=lambda oid:sha256(values[oid]).hexdigest()
        truth={p:reader(new[p]["oid"]) for p in paths}
        index=EvidenceLedger("dependency_index_8",paths,deps)
        omega=EvidenceLedger("omega_ledger_8",paths,deps)
        for obj in (index,omega):
            obj.initialize("start",old,reader)
            obj.transition(old,new,set(paths),"changed",reader)
            s=obj.assess("changed",truth)
            self.assertEqual(obj.calls,RECHECK_BUDGET)
            self.assertEqual(s["false_current"],0)
            self.assertGreater(s["pending"],0)
            # Budget can catch up on subsequent no-change events.
            obj.transition(new,new,set(),"stable",reader)
            self.assertEqual(obj.calls,12)
            end=obj.assess("stable",truth)
            self.assertEqual(end["correct_current"],len(deps))
            self.assertEqual(end["false_current"],0)
        self.assertEqual(index.assess("stable",truth),
                         omega.assess("stable",truth))

    def test_deletion_is_unavailable_not_fictional_new_digest(self):
        paths,deps,values,old,reader,p=self.setup_four()
        new={k:v for k,v in old.items() if k!=paths[2]}
        truth={x:reader(v["oid"]) for x,v in new.items()}
        for name in ("dependency_index_8","omega_ledger_8","full_reverify"):
            obj=p[name]
            obj.transition(old,new,{paths[2]},"removed",reader)
            status=obj.assess("removed",truth)
            self.assertEqual(status["false_current"],0)
            self.assertGreater(status["unavailable"],0)
            self.assertEqual(obj.current[paths[2]],"missing")

    def test_mode_only_change_rechecked_without_new_content_version(self):
        paths,deps,values,old,reader,p=self.setup_four()
        new={**old,paths[0]:{**old[paths[0]],"mode":"100755"}}
        truth={k:reader(v["oid"]) for k,v in new.items()}
        for name in ("dependency_index_8","omega_ledger_8"):
            obj=p[name]
            obj.transition(old,new,{paths[0]},"chmod",reader)
            self.assertEqual(obj.calls,1)
            self.assertEqual(obj.assess("chmod",truth)["correct_current"],12)
            self.assertEqual(sum(map(len,obj.historical.values())),12)

    def test_tampered_diff_is_fail_closed_even_if_no_stale_certificate_yet(self):
        paths,deps,values,old,reader,p=self.setup_four()
        new={**old,paths[0]:{"oid":"modified","mode":"100644"}}
        values["modified"]=b"changed"
        for name,obj in p.items():
            with self.subTest(name=name),self.assertRaisesRegex(
                    ValueError,"manifest disagrees"):
                obj.transition(old,new,set(),"bad-diff",reader)
        # A false positive diff is also rejected; not simply trusted as an
        # authoritative statement.
        for name,obj in p.items():
            with self.subTest(name=name),self.assertRaisesRegex(
                    ValueError,"manifest disagrees"):
                obj.transition(old,old,{paths[1]},"fake-diff",reader)

    def test_stable_path_selection_fixed_from_start_tree(self):
        old={
            f"src/flask/a{i:03d}.py":{"oid":"a"*40,"mode":"100644"}
            for i in range(140)}
        selected=selected_paths(old)
        self.assertEqual(len(selected),128)
        self.assertEqual(selected,selected_paths(dict(reversed(list(old.items())))))
        self.assertEqual(len(set(selected)),128)
        self.assertEqual(len(claims_for(selected)),384)

    def test_source_scope_not_semantic_truth(self):
        self.assertEqual(len(FROZEN_HEAD),40)
        self.assertEqual(FIRST_PARENT_COMMITS,41)
        self.assertEqual(RECHECK_BUDGET,8)
        self.assertEqual(sha256(b"example").hexdigest(),
                         "50d858e0985ecc7f60418aaf0cc5ab587f42c2570a884095a9e8ccacd0f6545c")


if __name__=="__main__":
    unittest.main()
