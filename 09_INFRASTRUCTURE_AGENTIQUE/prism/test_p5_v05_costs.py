"""Off-network tests for P5 v0.5 USD quote gate. No billable API calls."""
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import unittest

from p5_v05_costs import (
    CostConfigurationError, validate_pricing, price_estimate,
    calculate_budget, per_arm_costs
)

MODEL = "provider/explicit-test-model"

def mock_rate_card(model=MODEL):
    return {
        "model": model, "currency": "USD", "processing_mode": "standard",
        "input_usd_per_million": "1.00",
        "output_usd_per_million": "5.00",
        "source_url": "https://platform.openai.com/pricing",
        "checked_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

class CostTests(unittest.TestCase):
    def test_official_rate_card_model_and_date(self):
        card = mock_rate_card()
        self.assertEqual(validate_pricing(card, MODEL), card)
        with self.assertRaises(CostConfigurationError):
            validate_pricing(card, "wrong-model")
        stale = dict(card)
        stale["checked_at_utc"] = (
            datetime.now(timezone.utc) - timedelta(days=8)
        ).isoformat().replace("+00:00", "Z")
        with self.assertRaises(CostConfigurationError):
            validate_pricing(stale, MODEL)
        unsupported = dict(card, processing_mode="priority")
        with self.assertRaises(CostConfigurationError):
            validate_pricing(unsupported, MODEL)

    def test_estimate_and_quote_96_full_output_tokens(self):
        card = mock_rate_card()
        self.assertEqual(price_estimate(350,40,card), Decimal("0.00055"))
        quote = calculate_budget([350]*96,400,card,"0.23")
        self.assertEqual(Decimal(quote["estimated_upper_usd"]), Decimal("0.2256"))
        self.assertEqual(quote["billed_usd"], None)
        with self.assertRaises(CostConfigurationError):
            calculate_budget([350]*96,400,card,"0.22")
        with self.assertRaises(CostConfigurationError):
            calculate_budget([350]*96,400,card,None)

    def test_per_arm_attribution_and_no_invoice_claim(self):
        card = mock_rate_card()
        rows = [
            {"arm":arm,"actual_input_tokens":350,"actual_output_tokens":40}
            for arm in ("A","B","C") for _ in range(32)
        ]
        groups=per_arm_costs(rows,card)
        self.assertEqual(set(groups),{"A","B","C"})
        self.assertEqual(sum(g["generations"] for g in groups.values()),96)
        self.assertEqual(Decimal(groups["C"]["estimated_model_usd"]),Decimal("0.01760"))

    def test_reject_invalid_rates_and_tokens(self):
        card=mock_rate_card()
        for invalid in ("NaN","Infinity","-1","0",None):
            with self.subTest(invalid=invalid),self.assertRaises(CostConfigurationError):
                validate_pricing(dict(card,input_usd_per_million=invalid),MODEL)
        with self.assertRaises(CostConfigurationError):
            price_estimate(True,40,card)
        with self.assertRaises(CostConfigurationError):
            calculate_budget([350],400,card,"NaN")

if __name__ == "__main__":
    unittest.main()
