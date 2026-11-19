#!/usr/bin/env python3
"""Agent tool registry refuses unbounded requests; zero real network in tests."""
import sys
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from agent_tools import ALLOWED_TOOLS, dispatch
from web_access import NetworkPolicyError
from test_web_access import FakeTransport


class AgentToolRegistryTests(unittest.TestCase):
    def test_two_named_tools_retrieve_only_untrusted_data(self):
        for name,args in (
            ("search_bibliography",{"query":"finite dynamics observability"}),
            ("read_omega_public_math_source",{}),
        ):
            transport=FakeTransport()
            output=dispatch(name,args,transport=transport)
            self.assertEqual(output["tool"],name)
            self.assertTrue(output["read_only"])
            self.assertEqual(output["web_content_trust"],"UNTRUSTED")
            self.assertFalse(output["repo_write"])
            self.assertFalse(output["theorem_certificate"])
            self.assertEqual(output["max_network_calls"],1)
            self.assertEqual(len(transport.calls),1)
            self.assertEqual(output["result"]["real_fetch_success_count"],1)
            self.assertTrue(all(r["status"]=="WEB_FETCHED_UNTRUSTED" for r in
                                output["result"]["results"]))

    def test_unknown_tools_and_unbounded_arguments_refused_without_http(self):
        t=FakeTransport()
        for name,args in (
            ("execute_code",{"cmd":"ls"}),
            ("navigate_web",{"url":"https://localhost"}),
            ("search_bibliography",{"query":"bad&rows=100"}),
            ("search_bibliography",{"query":"valid query","host":"localhost"}),
            ("read_omega_public_math_source",{"path":"../.env"}),
            ("read_omega_public_math_source",{"url":"file:///etc/passwd"}),
            ("search_bibliography",{}),
            ("search_bibliography",None),
        ):
            with self.subTest(name=name,args=args):
                with self.assertRaises(NetworkPolicyError):
                    dispatch(name,args,transport=t)
        self.assertEqual(t.calls,[])


if __name__=="__main__":
    unittest.main(verbosity=2)
