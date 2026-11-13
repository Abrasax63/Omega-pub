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

    def test_unparseable_record_prevents_confirmation(self):
        trace = extract("+ cp input target\n+ python3 -c 'unterminated", "target")
        self.assertEqual(len(trace["writers"]), 1)
        self.assertEqual(fixed_verdict(trace), "indéterminé")

    def test_diff_comment_with_apostrophe_does_not_hide_copy(self):
        trace = extract("+    # Homebrew's binding\n+ cp input target", "target")
        self.assertEqual(fixed_verdict(trace), "copie")

    def test_buildkit_requires_same_step_verbose_output_and_completion(self):
        from provenance_xtrace import extract_buildkit_copy

        command = "#22 0.2 + cp -av source/file target/\n"
        verbose = "#22 0.3 'source/file' -> 'target/file'\n"
        done = "#22 DONE 1s\n"
        for log in [command + done, command + verbose, command + verbose.replace("#22", "#23") + done,
                    command + verbose + command + done, verbose + done]:
            with self.subTest(log=log):
                self.assertEqual(fixed_verdict(extract_buildkit_copy(log, "target/file")), "indéterminé")
        self.assertEqual(fixed_verdict(extract_buildkit_copy(command + verbose + done, "target/file")), "copie")
