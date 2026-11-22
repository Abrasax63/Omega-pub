"""Queue contracts: two process invocations, fail-closed state, immutable questions."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fast_cycle_queue import check_state, read_catalog, run_queue, unverified_research_inbox
from fast_cycle import digest


def fixture(root):
    root = Path(root)
    omega, math, prov = (root / p for p in ("omega", "math", "provenance"))
    (omega / "research/omega-100").mkdir(parents=True)
    (math / "research/code").mkdir(parents=True)
    (prov / "09_INFRASTRUCTURE_AGENTIQUE/prism").mkdir(parents=True)
    (omega / "research/omega-100/PROGRAMME.md").write_text("program")
    (omega / "research/omega-100/001.md").write_text("Prochain essai : nouveaux cas")
    (math / "research/code/audit_v19_shadow_guard.py").write_text(
        'def compare(cases):\n'
        '    return {"projections":2*len(cases),"old_errors":0,'
        '"new_errors":0,"locality_errors":0}\n')
    (math / "research/code/test_v19_locality_l_plus_1.py").write_text(
        'def forced_edges(t): return ()\n'
        'def coherent(n,edges): return True\n')
    (prov / "09_INFRASTRUCTURE_AGENTIQUE/prism/provenance_cycle.py").write_text(
        'def propose(training,baseline): return {"proposal":1}\n'
        'def evaluate_proposal(p,b,r):\n'
        '    return {"baseline":{"correct_confirmations":0,"false_confirmations":0,"abstentions":4},'
        '"candidate":{"correct_confirmations":2,"false_confirmations":0,"abstentions":2},'
        '"recommend_for_review":True}\n')
    (prov / "09_INFRASTRUCTURE_AGENTIQUE/prism/provenance_lab.py").write_text(
        'def score(cases,program):\n'
        '    return {"correct_confirmations":2,"false_confirmations":0,"abstentions":2}\n')
    return omega, math, prov


def task(id, kind="math_family", **kw):
    t = {"id": id, "kind": kind, "question": "Q", "hypothesis": "H",
         "reference": "R", "scope": "Finite replay"}
    if kind == "math_family":
        t.update({"q": 4, "n": 6, "horizon": 2, "max_cases": 4})
    t.update(kw)
    return t


class QueueTests(unittest.TestCase):
    def create_catalog(self, root):
        path = Path(root) / "catalog.json"
        tasks = [task("PROV-1", kind="provenance_pilot"),
                 task("MATH-1", kind="math_smoke"),
                 task("MATH-2"), task("MATH-3", horizon=3)]
        path.write_text(json.dumps({"schema": 1, "tasks": tasks}), encoding="utf-8")
        return path, tasks

    def test_staged_theses_cannot_be_promoted_into_completed_work(self):
        with TemporaryDirectory() as td:
            path = Path(td) / "ideas.json"
            payload = {"scientific_claims_certified": 0,
                       "grounded_hypothesis_proposals": [
                           {"id": "HYP-1", "status": "PROPOSED_UNVERIFIED",
                            "can_enter_executed_ledger": False,
                            "anchor": {"git_blob": "a" * 40}}
                       ]}
            path.write_text(json.dumps(payload))
            self.assertEqual(unverified_research_inbox(path)[0]["status"],
                             "NOT_EXECUTED_NEEDS_INDEPENDENT_TEST")
            payload["grounded_hypothesis_proposals"][0]["can_enter_executed_ledger"] = True
            path.write_text(json.dumps(payload))
            with self.assertRaisesRegex(ValueError, "promotion"):
                unverified_research_inbox(path)
            payload["grounded_hypothesis_proposals"][0]["can_enter_executed_ledger"] = False
            payload["scientific_claims_certified"] = 1
            path.write_text(json.dumps(payload))
            with self.assertRaisesRegex(ValueError, "certified"):
                unverified_research_inbox(path)

    def test_separate_process_passes_do_not_replay(self):
        with TemporaryDirectory() as td:
            omega, math, prov = fixture(td)
            catalog, tasks = self.create_catalog(td)
            state, out = Path(td) / "state.json", Path(td) / "output"
            kwargs = dict(state_file=state, output_dir=out, catalog_file=catalog,
                          omega_dir=omega, math_dir=math, provenance_dir=prov)
            first = run_queue(**kwargs, bootstrap=True)
            self.assertEqual(first["finite_probes_completed"], 2)
            self.assertEqual(first["remaining_preregistered"], 2)
            self.assertEqual(first["inbox"]["from_experiment"], 1)
            second = run_queue(**kwargs)
            self.assertEqual(second["finite_probes_completed"], 2)
            self.assertFalse(set(first["executed_ids"]) & set(second["executed_ids"]))
            self.assertEqual(run_queue(**kwargs)["finite_probes_completed"], 0)
            journal = json.loads(state.read_text(encoding="utf-8"))
            self.assertEqual(len(journal["entries"]), 4)
            self.assertEqual([e["id"] for e in journal["entries"]],
                             [t["id"] for t in tasks])
            check_state(journal, tasks, out / "results")

    def test_missing_ledger_requires_explicit_bootstrap(self):
        with TemporaryDirectory() as td:
            omega, math, prov = fixture(td)
            catalog, _ = self.create_catalog(td)
            with self.assertRaises(FileNotFoundError):
                run_queue(Path(td) / "missing.json", Path(td) / "out",
                          catalog_file=catalog, omega_dir=omega, math_dir=math,
                          provenance_dir=prov)

    def test_tampered_results_or_changed_protocol_are_rejected(self):
        with TemporaryDirectory() as td:
            omega, math, prov = fixture(td)
            catalog, tasks = self.create_catalog(td)
            state, out = Path(td) / "state.json", Path(td) / "output"
            kwargs = dict(state_file=state, output_dir=out, catalog_file=catalog,
                          omega_dir=omega, math_dir=math, provenance_dir=prov)
            run_queue(**kwargs, bootstrap=True, max_cycles=1)
            event = json.loads(state.read_text())["entries"][0]
            report_path = out / "results" / (event["id"] + ".json")
            report = json.loads(report_path.read_text())
            report["result"]["passed"] = False
            report_path.write_text(json.dumps(report))
            with self.assertRaisesRegex(ValueError, "Result digest mismatch"):
                run_queue(**kwargs)
            report["result"]["passed"] = True
            report_path.write_text(json.dumps(report))
            tasks[0]["hypothesis"] = "CHANGED AFTER THE FACT"
            catalog.write_text(json.dumps({"schema": 1, "tasks": tasks}))
            with self.assertRaisesRegex(ValueError, "Changed/unknown"):
                run_queue(**kwargs)

    def test_invalid_and_unsafe_catalogs_fail(self):
        with TemporaryDirectory() as td:
            catalog = Path(td) / "catalog.json"
            catalog.write_text(json.dumps({"schema": 1, "tasks":
                                            [task("same"), task("same")]}))
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                read_catalog(catalog)
            catalog.write_text(json.dumps({"schema": 1, "tasks":
                                            [task("../unsafe")]}))
            with self.assertRaisesRegex(ValueError, "unsafe"):
                read_catalog(catalog)

    def test_no_coherent_family_is_not_marked_complete(self):
        with TemporaryDirectory() as td:
            omega, math, prov = fixture(td)
            (math / "research/code/test_v19_locality_l_plus_1.py").write_text(
                'def forced_edges(t): return ()\n'
                'def coherent(n, edges): return False\n')
            catalog = Path(td) / "catalog.json"
            catalog.write_text(json.dumps({"schema": 1, "tasks": [task("FAMILY")]}))
            state, out = Path(td) / "state.json", Path(td) / "output"
            result = run_queue(state, out, catalog_file=catalog, omega_dir=omega,
                               math_dir=math, provenance_dir=prov, bootstrap=True)
            self.assertEqual(result["blocked"], 1)
            self.assertEqual(result["finite_probes_completed"], 0)
            self.assertEqual(json.loads(state.read_text())["entries"], [])


if __name__ == "__main__":
    unittest.main()
