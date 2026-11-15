import unittest
from unittest.mock import patch

from model_proposal import extract_candidate, generate_with_llama, validate_source


GOOD = """def q_power(rows, steps):
    n = len(rows)
    result = [1 << i for i in range(n)]
    for _ in range(steps):
        next_result = []
        for mask in result:
            total = 0
            for j in range(n):
                if mask & (1 << j):
                    total |= rows[j]
            next_result.append(total)
        result = next_result
    return result
"""


class ModelProposalTests(unittest.TestCase):
    def test_accepts_real_untemplated_python(self):
        self.assertIn("def q_power", validate_source(GOOD))

    def test_extracts_fenced_python(self):
        raw = "Example text\n" + chr(96) * 3 + "python\n" + GOOD + chr(96) * 3
        self.assertEqual(extract_candidate(raw), GOOD)

    def test_rejects_import(self):
        with self.assertRaisesRegex(ValueError, "exactly one function"):
            validate_source("import os\n" + GOOD)

    def test_rejects_unsafe_open(self):
        with self.assertRaisesRegex(ValueError, "call forbidden"):
            validate_source(GOOD.replace("    n = len(rows)", "    open('/tmp/bad', 'w')\n    n = len(rows)"))

    def test_rejects_attribute(self):
        with self.assertRaisesRegex(ValueError, "attribute access"):
            validate_source(GOOD.replace("    n = len(rows)", "    n = rows.__class__\n    n = len(rows)"))

    def test_rejects_nested_function(self):
        with self.assertRaisesRegex(ValueError, "nested functions"):
            validate_source("def q_power(rows, steps):\n    def helper():\n        pass\n    return []\n")

    def test_rejects_global(self):
        with self.assertRaisesRegex(ValueError, "forbidden"):
            validate_source("def q_power(rows, steps):\n    global other\n    return []\n")

    def test_rejects_wrong_signature(self):
        with self.assertRaisesRegex(ValueError, "signature"):
            validate_source("def q_power(a, b):\n    return []\n")

    @patch("model_proposal.subprocess.run")
    def test_real_cli_adapter_accepts_generated_source(self, proc):
        proc.return_value.returncode = 0
        proc.return_value.stdout = GOOD
        proc.return_value.stderr = ""
        candidate, meta = generate_with_llama("/models/llama-cli", "/models/checkpoint.gguf", 0)
        self.assertEqual(candidate, GOOD)
        self.assertEqual(meta["model_call_returncode"], 0)
        self.assertEqual(meta["source"], GOOD)
        self.assertEqual(proc.call_args.args[0][0], "/models/llama-cli")

    @patch("model_proposal.subprocess.run")
    def test_no_fake_model_success_on_cli_error(self, proc):
        proc.return_value.returncode = 1
        proc.return_value.stdout = ""
        proc.return_value.stderr = "load failed"
        candidate, meta = generate_with_llama("/x", "/m", 0)
        self.assertIsNone(candidate)
        self.assertEqual(meta["failure"], "llama-cli returned error")


if __name__ == "__main__":
    unittest.main()
