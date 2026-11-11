"""Strict, read-only trust-boundary adapter for the existing Omega planner.

This is NOT an authenticator of raw content, nor a second orchestrator.
The *trusted caller* supplies the check catalog and, for normative questions,
an explicit map from task field to the exact normative publishing origin.
All consult callbacks still count toward the original policy budget.
"""
from provenance_policy import decide

# These fields are declared by the trusted acquisition catalog, not by
# text scraped from a retrieved page. Spoofed fields are not credentials.
IDENTITY_FIELDS = ("id", "origin", "url", "field", "version",
                   "published", "independence", "primary")


class TrustedReceiptAdapter:
    """Check that a receipt matches its expected catalog entry.

    Non-normative sources can be inspected but cannot settle a question
    explicitly scoped to another normative origin. Rejected consultations
    return None and remain charged through the existing planner's trace.
    """

    def __init__(self, task, consult, authority_by_field=None):
        self.checks = {c["id"]: c for c in task["checks"]}
        if len(self.checks) != len(task["checks"]):
            raise ValueError("duplicate check ids")
        self.consult = consult
        self.authority_by_field = dict(authority_by_field or {})
        if not set(self.authority_by_field).issubset(task["scopes"]):
            raise ValueError("authority field is outside task scopes")
        for field, origin in self.authority_by_field.items():
            if not isinstance(origin, str) or not origin:
                raise ValueError("authority origin must be nonempty")
            if not any(c["field"] == field and c["origin"] == origin
                       and c["primary"] is True for c in self.checks.values()):
                raise ValueError("normative origin requires a catalogued primary")
        self.rejections = []

    def __call__(self, check_id):
        check = self.checks[check_id]
        receipt = self.consult(check_id)
        if receipt is None:
            self.rejections.append({"check": check_id, "reason": "source_unavailable"})
            return None
        if not isinstance(receipt, dict):
            self.rejections.append({"check": check_id, "reason": "invalid_receipt_type"})
            return None
        for field in IDENTITY_FIELDS:
            if type(receipt.get(field)) != type(check[field]) or receipt.get(field) != check[field]:
                self.rejections.append({
                    "check": check_id, "reason": "catalog_mismatch",
                    "field": field,
                })
                return None
        expected = self.authority_by_field.get(check["field"])
        if expected is not None and check["origin"] != expected:
            self.rejections.append({
                "check": check_id, "reason": "not_normative_authority",
                "field": check["field"], "expected_origin": expected,
            })
            return None
        return receipt


def decide_guarded(task, consult, *, budget=2, fixed=False,
                   authority_by_field=None, horizon=4):
    """Reuse provenance_policy.decide and the installed Omega optimizer.

    The normative authority map must be provided by the trusted caller before
    source values are observed. No map is inferred from the source contents.
    """
    adapter = TrustedReceiptAdapter(task, consult, authority_by_field)
    result = decide(task, adapter, budget=budget, fixed=fixed,
                    horizon=horizon, verify=True)
    return {**result, "adapter_rejections": adapter.rejections,
            "adapter_version": "catalog_root_and_normative_v0_2"}
