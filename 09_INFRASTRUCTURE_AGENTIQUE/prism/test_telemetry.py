import unittest

from telemetry import (
    SCHEMA_VERSION, TelemetryRecordError, summarize_calls, validate_call_record,
)


def valid_call(**overrides):
    record = {
        "schema_version": SCHEMA_VERSION, "experiment_id": "pilot-01",
        "case_id": "case-01", "arm": "A", "call_id": "call-01",
        "provider": "provider-x", "model": "model-y", "model_version": "snapshot-1",
        "provider_request_id": "req-123", "started_at": "2026-11-10T13:00:00+01:00",
        "elapsed_seconds": 1.25, "status": "completed",
        "input_tokens": 100, "output_tokens": 20, "cached_input_tokens": 30,
        "token_usage_source": "provider_response", "cost_usd": 0.001,
        "cost_source": "provider_reported", "tool_calls": 2, "cpu_seconds": 0.4,
        "peak_memory_bytes": 1024, "io_read_bytes": 2048, "io_write_bytes": 512,
        "result_validation_status": "not_assessed", "validation_ref": None,
    }
    record.update(overrides)
    return record


class TelemetryValidationTests(unittest.TestCase):
    def test_accepts_complete_provider_reported_record(self):
        validate_call_record(valid_call())

    def test_rejects_missing_required_field(self):
        record = valid_call()
        del record["provider"]
        with self.assertRaises(TelemetryRecordError):
            validate_call_record(record)

    def test_rejects_naive_timestamp(self):
        with self.assertRaises(TelemetryRecordError):
            validate_call_record(valid_call(started_at="2026-11-10T13:00:00"))

    def test_rejects_boolean_and_negative_counts(self):
        for value in (True, -1, 1.5):
            with self.subTest(value=value):
                with self.assertRaises(TelemetryRecordError):
                    validate_call_record(valid_call(input_tokens=value))

    def test_unavailable_usage_requires_null_token_counts(self):
        validate_call_record(valid_call(
            input_tokens=None, output_tokens=None, cached_input_tokens=None,
            token_usage_source="unavailable",
        ))
        with self.assertRaises(TelemetryRecordError):
            validate_call_record(valid_call(token_usage_source="unavailable"))

    def test_cached_tokens_cannot_exceed_input(self):
        with self.assertRaises(TelemetryRecordError):
            validate_call_record(valid_call(cached_input_tokens=101))

    def test_cost_source_and_value_must_agree(self):
        with self.assertRaises(TelemetryRecordError):
            validate_call_record(valid_call(cost_usd=None, cost_source="provider_reported"))
        validate_call_record(valid_call(cost_usd=None, cost_source="unavailable"))

    def test_rejects_non_finite_cost_and_negative_resource(self):
        for record in (valid_call(cost_usd=float("nan")), valid_call(cpu_seconds=-0.1),
                       valid_call(io_read_bytes=1.5)):
            with self.subTest(record=record):
                with self.assertRaises(TelemetryRecordError):
                    validate_call_record(record)

    def test_rejects_unknown_arm_and_validation_status(self):
        for record in (valid_call(arm="D"), valid_call(result_validation_status="scientifically_true")):
            with self.subTest(record=record):
                with self.assertRaises(TelemetryRecordError):
                    validate_call_record(record)

    def test_summary_does_not_turn_missing_metrics_into_zero(self):
        first = valid_call()
        second = valid_call(
            call_id="call-02", input_tokens=None, output_tokens=None,
            cached_input_tokens=None, token_usage_source="unavailable",
            cost_usd=None, cost_source="unavailable", cpu_seconds=None,
            peak_memory_bytes=None, io_read_bytes=None, io_write_bytes=None,
            result_validation_status="indeterminate",
        )
        summary = summarize_calls([first, second])["arm_summaries"][0]
        self.assertIsNone(summary["input_tokens_total"])
        self.assertEqual(summary["input_tokens_missing_calls"], 1)
        self.assertIsNone(summary["cost_usd_total"])
        self.assertEqual(summary["cost_missing_calls"], 1)
        self.assertIsNone(summary["peak_memory_bytes_max"])
        self.assertEqual(summary["peak_memory_missing_calls"], 1)
        self.assertEqual(summary["call_count"], 2)

    def test_summary_keeps_arms_separate(self):
        summaries = summarize_calls([
            valid_call(), valid_call(arm="B", call_id="call-B")
        ])["arm_summaries"]
        self.assertEqual([row["arm"] for row in summaries], ["A", "B"])

    def test_rejects_duplicate_call_identity(self):
        with self.assertRaises(TelemetryRecordError):
            summarize_calls([valid_call(), valid_call()])


if __name__ == "__main__":
    unittest.main()
