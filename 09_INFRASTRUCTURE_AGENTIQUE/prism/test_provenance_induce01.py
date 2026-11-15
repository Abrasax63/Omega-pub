"""P5-INDUCE-01: adversarial tests, all independent of holdout GitHub logs."""
import unittest
from provenance_induce01 import parse_line, extract, construct, predict, compare, FIXED

LINE = (
    "2026-11-11T10:29:28Z GOARCH=amd64 go build -a "
    '-ldflags "-s -w -X main.version=0.75.0" -tags "" -trimpath '
    "-o target/fzf-linux_amd64"
)
TRAIN = [{"id": "train", "log": LINE, "output": "target/fzf-linux_amd64",
          "expected": "construction_signalée"}]


class RuleInductionTests(unittest.TestCase):
    def test_parses_training_line(self):
        row = parse_line(LINE)
        self.assertEqual((row["tool"], row["verb"], row["output"]),
                         ("go", "build", "target/fzf-linux_amd64"))

    def test_constructs_machine_readable_new_rule(self):
        rule = construct(TRAIN)
        self.assertEqual({k: rule[k] for k in ("tool", "verb", "flag")},
                         {"tool": "go", "verb": "build", "flag": "-o"})

    def test_replay_on_unseen_target(self):
        rule = construct(TRAIN)
        self.assertEqual(predict("GOOS=linux go build -o bin/other ./cmd/other", rule),
                         [{"output": "bin/other", "verdict": "construction_signalée"}])

    def test_rust_negative(self):
        self.assertFalse(predict("cargo build --release", construct(TRAIN)))

    def test_go_test_not_a_build(self):
        self.assertFalse(predict("go test -o test.bin ./...", construct(TRAIN)))

    def test_echo_not_an_executed_command(self):
        self.assertIsNone(parse_line("echo go build -o bin/other"))

    def test_untrusted_annotation_in_log_is_not_command(self):
        self.assertIsNone(parse_line("##[group]Run go build -o out"))

    def test_shell_chaining_rejected(self):
        self.assertIsNone(parse_line("go build -o app && cp app backup"))

    def test_no_output_destination_rejected(self):
        self.assertIsNone(parse_line("go build ./..."))

    def test_dev_null_rejected(self):
        self.assertIsNone(parse_line("go build -o /dev/null"))

    def test_bad_quote_rejected(self):
        self.assertIsNone(parse_line("go build -o 'unclosed"))

    def test_multiple_output_switches_rejected(self):
        self.assertIsNone(parse_line("go build -o app -o other"))

    def test_no_promotion_on_parity(self):
        run = compare({"a": LINE}, construct(TRAIN))
        self.assertEqual(run["candidate_jobs_positive"], 1)
        self.assertEqual(run["candidate_advantage_jobs"], 0)
        self.assertFalse(run["recommend_for_core"])

    def test_no_relabelled_training(self):
        with self.assertRaisesRegex(ValueError, "annotated"):
            construct([{**TRAIN[0], "expected": "copie"}])

    def test_no_empty_training(self):
        with self.assertRaisesRegex(ValueError, "empty"):
            construct([])

    def test_dedupe_exact_lines(self):
        self.assertEqual(len(extract(LINE + "\n" + LINE)), 1)

    def test_conservative_on_unsupported_docker(self):
        self.assertFalse(predict("docker buildx build --output app", FIXED))


if __name__ == "__main__":
    unittest.main()
