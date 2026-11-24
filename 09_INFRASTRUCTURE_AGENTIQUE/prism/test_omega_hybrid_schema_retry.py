"""One retry only, no silent mutation or true answer injection."""
import json
import unittest

from omega_hybrid_schema_retry import schema_retry


def raw_card():
    return {"concept":"Equivalence Relations",
            "definition":"A relation satisfying three axioms",
            "formal_axioms":["reflexive","symmetric","transitive"]}


def payload(positive=None, negative=None):
    pos = positive if positive is not None else [["a","a"],["b","b"],["c","c"]]
    neg = negative if negative is not None else [["a","b"]]
    return json.dumps({"positive_edges":pos,"negative_edges":neg})


class RetryTests(unittest.TestCase):
    def test_missing_graphs_request_once_and_check(self):
        card = raw_card()
        calls=[]
        def fake(messages, limit):
            calls.append((messages,limit))
            return {"text":payload()}
        result=schema_retry(card,fake)
        self.assertEqual(result["calls"],1)
        self.assertEqual(len(calls),1)
        self.assertEqual(calls[0][1],320)
        self.assertEqual(result["status"],"BOUNDED_GRAPH_PASS_QUARANTINE_ONLY")
        self.assertNotIn("positive_edges",card)
        self.assertFalse(result["source_semantics_verified"])
        self.assertEqual(result["scientific_claims_certified"],0)
        self.assertNotIn("candidate_addition",str(calls))

    def test_wrong_graph_is_not_fixed_by_changing_truth_afterwards(self):
        result=schema_retry(raw_card(),lambda *_:{"text":payload([["a","b"]])})
        self.assertEqual(result["status"],"QUARANTINE")
        self.assertEqual(result["reason"],"MATHEMATICAL_COUNTEREXAMPLE")
        self.assertIsNone(result["candidate_addition"])

    def test_already_supplied_wrong_example_does_not_retry(self):
        card=raw_card()
        card.update(json.loads(payload([["a","b"]])))
        def forbidden(*_):
            raise AssertionError("model must not be called")
        result=schema_retry(card,forbidden)
        self.assertEqual(result["calls"],0)
        self.assertEqual(result["reason"],"MATHEMATICAL_COUNTEREXAMPLE")

    def test_json_invalid_never_repaired(self):
        result=schema_retry(raw_card(),lambda *_:{"text":"not json"})
        self.assertEqual(result["reason"],"RETRY_JSON_INVALID")
        self.assertEqual(result["status"],"QUARANTINE")

    def test_no_silent_extra_model_fields(self):
        x=json.loads(payload());x["theorem_proved"]=True
        result=schema_retry(raw_card(),lambda *_:{"text":json.dumps(x)})
        self.assertEqual(result["reason"],"RETRY_SCHEMA_INVALID")

    def test_abstention_does_not_count_as_success(self):
        result=schema_retry(raw_card(),lambda *_:{"text":'{"abstain":true}'})
        self.assertEqual(result["reason"],"MODEL_ABSTAINED")
        self.assertEqual(result["calls"],1)

    def test_model_exception_is_protected_and_labeled(self):
        def fail(*_):raise ConnectionError("private-access-token")
        result=schema_retry(raw_card(),fail)
        self.assertEqual(result["reason"],"MODEL_CALL_FAILED")
        self.assertNotIn("private-access-token",str(result))
        self.assertEqual(result["error_type"],"ConnectionError")

    def test_invalid_formal_signature_stops_before_model(self):
        card=raw_card();card["formal_axioms"]=["reflexive"]
        result=schema_retry(card,lambda *_:{"text":payload()})
        self.assertEqual(result["calls"],0)
        self.assertEqual(result["reason"],"FORMAL_SIGNATURE_MISMATCH")


if __name__=="__main__": unittest.main()
