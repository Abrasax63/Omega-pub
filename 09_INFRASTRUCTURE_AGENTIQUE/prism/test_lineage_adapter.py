"""Synthetic unit tests: no independent real-log performance inference."""
import unittest
from lineage_adapter import compare_pair, digest_from_log, source_of_copy
from lineage_pilot import UNKNOWN, SAME, DISTINCT

HASH = "b390d063dd02f23ec6bfa1ccb02f64cdae46f1af2b2c33596b9929a91b8e1747"
OTHER = "a" * 64

def recompute(path, digest=HASH):
    return (f"+ python3 -c 'from pathlib import Path; Path(\"{path}\").write_text(str(sum(i*i for i in range(1,12)))+chr(10))'\n"
            f"{digest}  {path}\n")

def snapshot(jobs):
    return {"repository":"Abrasax63/Omega-pub", "run": 123,
            "jobs":[{"id":i,"run_id":123,"name":f"job-{i}","conclusion":"success"} for i in jobs],
            "logs":{str(i):log for i,log in jobs.items()}}

def pair(*entries):
    return [{"job_id":j,"path":p} for j,p in entries]

class AdapterTests(unittest.TestCase):
    def test_distinct_direct_recomputation_equal_digest(self):
        p=pair((1,"evidence/a.json"),(2,"evidence/b.json"))
        s=snapshot({1:recompute(p[0]["path"]),2:recompute(p[1]["path"])})
        result=compare_pair(s,p)
        self.assertEqual((result['lineage'],result['selector_translation']), (DISTINCT,DISTINCT))
        self.assertEqual(result['reads_charged_each'],2)

    def test_copy_of_local_recompute_same_origin(self):
        log=recompute("evidence/a.json") + "+ cp evidence/a.json evidence/b.json\n" + f"{HASH}  evidence/b.json\n"
        p=pair((1,"evidence/a.json"),(1,"evidence/b.json"))
        result=compare_pair(snapshot({1:log}),p,budget=1)
        self.assertEqual((result['lineage'],result['selector_translation']), (SAME,UNKNOWN))
        self.assertEqual(result['reads_charged_each'],1)

    def test_copy_of_unknown_source_abstains(self):
        s=snapshot({1:"+ cp original.json evidence/a.json\n"+f"{HASH}  evidence/a.json\n"})
        result=compare_pair(s,pair((1,"evidence/a.json"),(1,"original.json")),budget=1)
        self.assertEqual(result['lineage'],UNKNOWN)

    def test_mismatching_copy_digest_abstains(self):
        log=recompute("evidence/a.json")+"+ cp evidence/a.json evidence/b.json\n"+f"{OTHER}  evidence/b.json\n"
        result=compare_pair(snapshot({1:log}),pair((1,"evidence/a.json"),(1,"evidence/b.json")),budget=1)
        self.assertEqual(result['lineage'],UNKNOWN)

    def test_ambiguous_multiple_writers_abstains(self):
        log=recompute("evidence/a.json") + "+ cp other evidence/a.json\n" + recompute("evidence/b.json")
        result=compare_pair(snapshot({1:log}),pair((1,"evidence/a.json"),(1,"evidence/b.json")),budget=1)
        self.assertEqual(result['lineage'],UNKNOWN)

    def test_no_hash_abstains(self):
        raw=recompute("a.json").splitlines()[0]+'\n'
        result=compare_pair(snapshot({1:raw}),pair((1,"a.json"),(1,"b.json")),budget=1)
        self.assertEqual(result['lineage'],UNKNOWN)

    def test_budget_rejects_without_reads(self):
        s=snapshot({1:recompute('a.json'),2:recompute('b.json')})
        result=compare_pair(s,pair((1,'a.json'),(2,'b.json')),budget=1)
        self.assertEqual(result['lineage'],UNKNOWN)
        self.assertEqual(result['reads_charged_each'],0)
        self.assertEqual(result['reason'],'budget_exceeded')

    def test_failed_job_abstains(self):
        s=snapshot({1:recompute('a.json'),2:recompute('b.json')})
        s['jobs'][0]['conclusion']='failure'
        result=compare_pair(s,pair((1,'a.json'),(2,'b.json')))
        self.assertEqual(result['lineage'],UNKNOWN)

    def test_missing_job_log_abstains(self):
        s=snapshot({1:recompute('a.json'),2:recompute('b.json')})
        del s['logs']['2']
        result=compare_pair(s,pair((1,'a.json'),(2,'b.json')))
        self.assertEqual(result['lineage'],UNKNOWN)

    def test_tampered_duplicate_checksum_abstains(self):
        log=recompute('a.json')+f'{OTHER}  a.json\n'
        self.assertIsNone(digest_from_log(log,'a.json'))
        result=compare_pair(snapshot({1:log}),pair((1,'a.json'),(1,'b.json')),budget=1)
        self.assertEqual(result['lineage'],UNKNOWN)

    def test_unsupported_writer_does_not_gain(self):
        log="+ python -c 'print(1)'\n"+f'{HASH}  a.json\n'
        result=compare_pair(snapshot({1:log}),pair((1,'a.json'),(1,'b.json')),budget=1)
        self.assertEqual(result['lineage'],UNKNOWN)

    def test_path_restriction_and_source_parsing(self):
        self.assertIsNone(source_of_copy('cp --version a.json','a.json'))
        log=recompute('b.json')+f'{HASH}  ../a.json\n'+"+ cp b.json ../a.json\n"
        result=compare_pair(snapshot({1:log}),pair((1,'../a.json'),(1,'b.json')),budget=1)
        self.assertEqual(result['lineage'],UNKNOWN)

    def test_timestamped_github_format(self):
        log=recompute('a.json').replace('+ python3','2026-11-13T19:09:30.6093346Z + python3').replace(f'{HASH}  a.json',f'2026-11-13T19:09:30.6313589Z {HASH}  a.json')
        self.assertEqual(digest_from_log(log,'a.json'),HASH)
        result=compare_pair(snapshot({1:log,2:recompute('b.json')}),pair((1,'a.json'),(2,'b.json')))
        self.assertEqual(result['lineage'],DISTINCT)

    def test_job_ids_are_not_external_attestations(self):
        s=snapshot({1:recompute('a.json'),2:recompute('b.json')})
        result=compare_pair(s,pair((1,'a.json'),(2,'b.json')))
        self.assertEqual(result['provenance_status'],'DECLARED_SNAPSHOT_NOT_AUTHENTICATED')

if __name__=='__main__':unittest.main()
