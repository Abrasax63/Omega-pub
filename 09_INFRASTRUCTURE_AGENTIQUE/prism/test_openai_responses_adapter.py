import unittest

from telemetry import TelemetryRecordError, summarize_calls
from openai_responses_adapter import build_openai_responses_record, measure_call


class OpenAIResponsesAdapterTests(unittest.TestCase):
    def test_extracts_provider_reported_usage(self):
        record = build_openai_responses_record(
            {
                "id": "resp_test_123",
                "model": "gpt-test",
                "usage": {
                    "input_tokens": 120,
                    "output_tokens": 35,
                    "input_tokens_details": {"cached_tokens": 40},
                },
            },
            experiment_id="synthetic-01", case_id="case-01", arm="A",
            call_id="call-01", started_at="2026-11-10T14:00:00+00:00",
            elapsed_seconds=1.2,
        )
        self.assertEqual(record["provider"], "openai")
        self.assertEqual(record["provider_response_id"], "resp_test_123")
        self.assertEqual(record["input_tokens"], 120)
        self.assertEqual(record["output_tokens"], 35)
        self.assertEqual(record["cached_input_tokens"], 40)
        self.assertEqual(record["token_usage_source"], "provider_response")
        self.assertIsNone(record["cost_usd"])

    def test_missing_usage_stays_unknown(self):
        record = build_openai_responses_record(
            {"id": "resp_no_usage", "model": "gpt-test"},
            experiment_id="synthetic-01", case_id="case-02", arm="B",
            call_id="call-02", started_at="2026-11-10T14:00:00+00:00",
            elapsed_seconds=0.5,
        )
        self.assertIsNone(record["input_tokens"])
        self.assertIsNone(record["output_tokens"])
        self.assertEqual(record["token_usage_source"], "unavailable")

    def test_partial_usage_fails_and_interruption_is_preserved(self):
        args = dict(experiment_id="synthetic", case_id="case-01", arm="C",
                    call_id="call-01", started_at="2026-11-10T14:00:00+00:00",
                    elapsed_seconds=1, context={"repetition": 2, "operation_id": "op-1", "attempt": 1})
        with self.assertRaises(TelemetryRecordError):
            build_openai_responses_record({"usage": {"input_tokens": 10}}, **args)
        record = build_openai_responses_record({"status": "incomplete"}, **args)
        self.assertEqual(record["status"], "interrupted")
        self.assertIsNone(record["model"])
        self.assertIsNone(record["tool_calls"])
        totals = summarize_calls([record], by_execution=True)["execution_summaries"][0]
        self.assertEqual((totals["case_id"], totals["repetition"]), ("case-01", 2))
        self.assertEqual(totals["status_counts"], {"interrupted": 1})
        self.assertIsNone(totals["tool_calls_total"])
        with self.assertRaisesRegex(TelemetryRecordError, "duplicate operation attempt"):
            summarize_calls([record, {**record, "call_id": "call-02"}])

    def test_measures_callable_wall_time_and_returns_response(self):
        marker = {"ok": True}
        response, started_at, elapsed = measure_call(lambda: marker)
        self.assertIs(response, marker)
        self.assertIn("+00:00", started_at)
        self.assertGreaterEqual(elapsed, 0)


if __name__ == "__main__":
    unittest.main()
