import copy
import unittest
from tools.repro_fingerprint import fingerprint, reusable


def sample():
    return {
        "schema_version": 1, "result_id": "test-1",
        "code_sha256": "a" * 64, "data_sha256": "b" * 64,
        "parameters": {"seed": 7}, "dependencies": {"python": "3.12"},
        "execution": {"mode": "exact"},
    }


class FingerprintTests(unittest.TestCase):
    def test_same_content_different_order(self):
        m = sample()
        self.assertEqual(fingerprint(m), fingerprint(dict(reversed(list(m.items())))))

    def test_parameter_change_invalidates(self):
        m = sample()
        changed = copy.deepcopy(m)
        changed["parameters"]["seed"] = 8
        self.assertFalse(reusable(m, fingerprint(m), changed))

    def test_dependency_change_invalidates(self):
        m = sample()
        changed = copy.deepcopy(m)
        changed["dependencies"]["python"] = "3.13"
        self.assertFalse(reusable(m, fingerprint(m), changed))

    def test_execution_change_invalidates(self):
        m = sample()
        changed = copy.deepcopy(m)
        changed["execution"]["mode"] = "approximate"
        self.assertFalse(reusable(m, fingerprint(m), changed))

    def test_unchanged_reusable(self):
        m = sample()
        self.assertTrue(reusable(m, fingerprint(m), copy.deepcopy(m)))

    def test_corrupt_prior_fingerprint(self):
        m = sample()
        self.assertFalse(reusable(m, "0" * 64, m))

    def test_missing_dependency_field(self):
        m = sample()
        del m["dependencies"]
        with self.assertRaises(ValueError):
            fingerprint(m)

    def test_unknown_field(self):
        m = sample()
        m["secret_setting"] = "untracked"
        with self.assertRaises(ValueError):
            fingerprint(m)

    def test_float_rejected(self):
        m = sample()
        m["parameters"]["threshold"] = 0.1
        with self.assertRaises(ValueError):
            fingerprint(m)

    def test_code_change_invalidates(self):
        m = sample()
        changed = copy.deepcopy(m)
        changed["code_sha256"] = "c" * 64
        self.assertFalse(reusable(m, fingerprint(m), changed))

    def test_data_change_invalidates(self):
        m = sample()
        changed = copy.deepcopy(m)
        changed["data_sha256"] = "c" * 64
        self.assertFalse(reusable(m, fingerprint(m), changed))


if __name__ == "__main__":
    unittest.main()
