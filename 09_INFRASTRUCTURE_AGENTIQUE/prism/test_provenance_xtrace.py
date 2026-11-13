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

    def test_echoed_step_script_is_not_execution_trace(self):
        log = (
            "2026-10-15T09:38:37.4807663Z "
            "\x1b[36;1msudo install -m 0755 actionlint /usr/local/bin/actionlint\x1b[0m"
        )
        trace = extract(log, "/usr/local/bin/actionlint")
        self.assertEqual(trace["writers"], [])
        self.assertEqual(fixed_verdict(trace), "indéterminé")
