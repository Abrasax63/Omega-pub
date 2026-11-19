import tempfile
import unittest
from pathlib import Path
from tools.repro_adversarial_integrity import capture, check


class AdversarialIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.script = root / "script.py"
        self.input = root / "input.csv"
        self.dep = root / "indirect_dep.py"
        self.output = root / "cached_result.json"
        for path, content in ((self.script, "print('ok')"),
                              (self.input, "x,1\n"),
                              (self.dep, "FACTOR=2\n"),
                              (self.output, '{"answer":2}\n')):
            path.write_text(content)
        self.saved = capture(self.script, [self.input], [self.dep], self.output)

    def valid(self, inputs=None, deps=None):
        return check(self.saved, self.script,
                     [self.input] if inputs is None else inputs,
                     [self.dep] if deps is None else deps, self.output)

    def test_unchanged_is_eligible(self):
        self.assertTrue(self.valid())

    def test_changed_input_is_rejected(self):
        self.input.write_text("x,2\n")
        self.assertFalse(self.valid())

    def test_indirect_dependency_is_rejected(self):
        self.dep.write_text("FACTOR=3\n")
        self.assertFalse(self.valid())

    def test_tampered_cached_result_is_rejected(self):
        self.output.write_text('{"answer":999}\n')
        self.assertFalse(self.valid())

    def test_missing_input_is_rejected(self):
        self.input.unlink()
        self.assertFalse(self.valid())

    def test_added_input_is_rejected(self):
        new_input = Path(self.temp.name) / "extra.csv"
        new_input.write_text("extra")
        self.assertFalse(self.valid(inputs=[self.input, new_input]))

    def test_changed_script_is_rejected(self):
        self.script.write_text("print('changed')")
        self.assertFalse(self.valid())


if __name__ == "__main__":
    unittest.main()
