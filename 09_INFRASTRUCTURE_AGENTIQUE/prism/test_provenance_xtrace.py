import unittest

from provenance_xtrace import extract, fixed_verdict


class InstallTraceTests(unittest.TestCase):
    def test_copy_and_wrong_output(self):
        log = "+ install -m 0600 input 'target file.json'"
        self.assertEqual(fixed_verdict(extract(log, "target file.json")), "copie")
        self.assertEqual(fixed_verdict(extract(log, "other.json")), "indéterminé")

    def test_multiple_writers(self):
        log = "+ cp input target\n+ install -m 0644 input target"
        self.assertEqual(fixed_verdict(extract(log, "target")), "indéterminé")
        self.assertEqual(fixed_verdict(extract(log, "target", recognize_install=False)), "copie")

    def test_unsupported_mode(self):
        self.assertEqual(
            fixed_verdict(extract("+ install -m invalid input target", "target")),
            "indéterminé",
        )
