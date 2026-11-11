"""Safety and exact semantic-scope regressions for frozen AST claim replay."""
import ast
from hashlib import sha256
import subprocess
import tempfile
from pathlib import Path
import unittest

from ast_claim_versioning import (
    declaration_facts, candidate_paths, SyntaxFactLedger, source_facts,
    POLICIES, MAX_CHECKS,
)


class AstClaimVersioningTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo=Path(self.tmp.name)
        subprocess.run(["git","init","-q",str(self.repo)],check=True)
        self.path="src/flask/test.py"

    def oid(self,bytestring):
        r=subprocess.run(["git","-C",str(self.repo),"hash-object","-w","--stdin"],
                         input=bytestring,check=True,capture_output=True)
        return r.stdout.decode().strip()

    def versions(self,a,b):
        old_oid=self.oid(a)
        new_oid=self.oid(b)
        old={self.path:{"oid":old_oid,"mode":"100644"}}
        new={self.path:{"oid":new_oid,"mode":"100644"}}
        facts=source_facts(str(self.repo),old_oid)
        claims={self.path+"::"+key:self.path for key in facts}
        policies={m:SyntaxFactLedger(m,claims) for m in POLICIES}
        for obj in policies.values():
            obj.initialize("original",old,{self.path:facts})
        truth=source_facts(str(self.repo),new_oid)
        actual={key:truth.get(key.rsplit("::",1)[-1],"missing")
                for key in claims}
        return old,new,claims,policies,actual

    def test_comments_and_formatting_do_not_change_any_ast_facts(self):
        a=b"def f(x: int):\n    return x + 1\n"
        b=b"# added source note\n\ndef f( x:int ):\n    return x+1  # trailing\n"
        self.assertEqual(declaration_facts(a),declaration_facts(b))
        old,new,claims,policies,actual=self.versions(a,b)
        for name,obj in policies.items():
            obj.transition(old,new,{self.path},"new",str(self.repo))
            result=obj.assess(actual)
            if name in ("ast_dependency_index_8","omega_ast_ledger_8"):
                self.assertEqual(result["verified_current"],len(claims))
                self.assertEqual(result["false_current"],0)
            if name=="file_path_invalidate":
                self.assertEqual(result["pending"],len(claims))

    def test_function_body_changes_module_ast_not_signature(self):
        a=b"def f(x: int) -> int:\n    return x + 1\n"
        b=b"def f(x: int) -> int:\n    return x + 2\n"
        da,db=declaration_facts(a),declaration_facts(b)
        self.assertNotEqual(da["module_ast"],db["module_ast"])
        self.assertEqual(da["def:f#0"],db["def:f#0"])

    def test_real_signature_change_is_visible_and_archives_past_version(self):
        a=b"def f(x: int) -> int:\n    return x\n"
        b=b"def f(x: int, *, y=3) -> int:\n    return x+y\n"
        old,new,claims,policies,actual=self.versions(a,b)
        item=self.path+"::def:f#0"
        self.assertNotEqual(policies["omega_ast_ledger_8"].current[item],
                            actual[item])
        for name,obj in policies.items():
            obj.transition(old,new,{self.path},"revised",str(self.repo))
            x=obj.assess(actual)
            if name=="stale_no_refresh":
                self.assertGreater(x["false_current"],0)
            if name in ("ast_dependency_index_8","omega_ast_ledger_8"):
                self.assertEqual(x["verified_current"],len(claims))
                self.assertEqual(x["false_current"],0)
                self.assertEqual(len(obj.archived[item]),2)
                self.assertEqual(obj.archived[item][0]["certified_at_commit"],"original")
                self.assertEqual(obj.archived[item][-1]["certified_at_commit"],"revised")
                self.assertNotEqual(obj.archived[item][0]["signature_sha256"],
                                    obj.archived[item][-1]["signature_sha256"])

    def test_deletion_and_new_symbol_do_not_invent_old_claim(self):
        source=b"class C:\n    def method(self, x):\n        return x\n"
        newer=b"class C:\n    def newly_added(self):\n        return 5\n"
        a=declaration_facts(source)
        b=declaration_facts(newer)
        self.assertIn("def:C.method#0",a)
        self.assertNotIn("def:C.method#0",b)
        self.assertNotIn("def:C.newly_added#0",a)
        old,new,claims,policies,actual=self.versions(source,newer)
        for name in ("ast_dependency_index_8","omega_ast_ledger_8"):
            obj=policies[name]
            obj.transition(old,new,{self.path},"new",str(self.repo))
            self.assertEqual(obj.current[self.path+"::def:C.method#0"],"missing")
            self.assertNotIn(self.path+"::def:C.newly_added#0",obj.current)
            self.assertGreater(obj.assess(actual)["unavailable"],0)

    def test_deleted_file_is_unavailable_and_never_false_current(self):
        a=b"def f():\n    pass\n"
        old,_,claims,policies,actual=self.versions(a,a)
        for name in ("ast_dependency_index_8","omega_ast_ledger_8"):
            obj=policies[name]
            obj.transition(old,{},set([self.path]),"deleted",str(self.repo))
            expected={key:"missing" for key in claims}
            scores=obj.assess(expected)
            self.assertEqual(scores["unavailable"],len(claims))
            self.assertEqual(scores["false_current"],0)

    def test_missing_or_fabricated_git_manifest_is_rejected(self):
        a=b"def f():\n    return True\n"
        b=b"def f():\n    return False\n"
        old,new,claims,policies,actual=self.versions(a,b)
        for name,obj in policies.items():
            with self.subTest(name=name),self.assertRaises(ValueError):
                obj.transition(old,new,set(),"falsified",str(self.repo))
            with self.subTest(name=name),self.assertRaises(ValueError):
                obj.transition(old,old,{self.path},"imagined",str(self.repo))

    def test_budget_eight_suspends_unverified_signatures(self):
        files=[f"tests/fixture_{i:02d}.py" for i in range(10)]
        repo=self.repo
        blob_a=self.oid(b"def f(x):\n    return x\n")
        blob_b=self.oid(b"def f(x, y):\n    return x+y\n")
        initial=source_facts(str(repo),blob_a)
        claimpaths={p+"::"+k:p for p in files for k in initial}
        old={p:{"oid":blob_a,"mode":"100644"} for p in files}
        new={p:{"oid":blob_b,"mode":"100644"} for p in files}
        actual={p+"::"+k:source_facts(str(repo),blob_b)[k]
                for p in files for k in initial}
        strong=SyntaxFactLedger("ast_dependency_index_8",claimpaths)
        strong.initialize("old",old,{p:initial for p in files})
        checks=strong.transition(old,new,set(files),"new",str(repo))
        self.assertEqual(len(checks),MAX_CHECKS)
        x=strong.assess(actual)
        self.assertEqual(x["false_current"],0)
        self.assertGreater(x["pending"],0)
        strong.transition(new,new,set(),"unchanged",str(repo))
        y=strong.assess(actual)
        self.assertEqual(y["verified_current"],len(claimpaths))
        self.assertEqual(y["false_current"],0)

    def test_ast_failure_produces_abstention_not_certificate(self):
        original=b"def f():\n    return True\n"
        malformed=b"def f(:\n BAD\n"
        old,new,claims,policies,actual=self.versions(original,malformed)
        obj=policies["omega_ast_ledger_8"]
        obj.transition(old,new,{self.path},"broken",str(self.repo))
        status=obj.assess({key:"parse_error" for key in claims})
        self.assertEqual(status["parse_error"],len(claims))
        self.assertEqual(status["false_current"],0)

    def test_class_and_method_signatures_are_precisely_scoped(self):
        a=b"class C(Base):\n    @staticmethod\n    def method(self,x):\n        return x\n"
        b=b"class C(Base):\n    def method(self,x):\n        return x\n"
        c=b"class C(Other):\n    def method(self,x):\n        return x\n"
        x,y,z=map(declaration_facts,[a,b,c])
        self.assertEqual(x["def:C.method#0"],y["def:C.method#0"])
        self.assertEqual(x["class:C#0"],y["class:C#0"])
        self.assertNotEqual(y["class:C#0"],z["class:C#0"])
        self.assertNotEqual(x["module_ast"],y["module_ast"])
        # This explicitly does NOT certify decorated-method runtime semantics.

if __name__=="__main__":
    unittest.main()
