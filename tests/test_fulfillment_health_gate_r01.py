"""Fail-closed public /health contract, independent of FastAPI runtime imports.

This is a static/pure-function acceptance test. It does not authenticate
Stripe, establish a webhook endpoint, or authorize commercial fulfillment.
"""
from __future__ import annotations
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "jarvis_paid_fulfillment" / "app.py"


def health_response():
    original = ast.parse(APP.read_text(encoding="utf-8"))
    found = [n for n in original.body if isinstance(n, ast.FunctionDef) and n.name == "health"]
    if len(found) != 1:
        raise AssertionError("expected exactly one health function")
    fn = found[0]
    body = ast.Module(
        body=[ast.FunctionDef(
            name="health", args=fn.args, body=fn.body, decorator_list=[],
            returns=fn.returns, type_comment=fn.type_comment
        )],
        type_ignores=[]
    )
    scope = {}
    exec(compile(ast.fix_missing_locations(body), str(APP), "exec"), scope)
    return scope["health"]()


class FulfillmentHealthGateTests(unittest.TestCase):
    def test_service_is_live_without_claiming_fulfillment(self):
        result = health_response()
        self.assertEqual(result["status"], "ok")
        self.assertFalse(result["commercial_fulfillment_authority_granted"])

    def test_readiness_is_explicitly_unverified(self):
        self.assertEqual(
            health_response()["operational_readiness"],
            "HOLD_UNVERIFIED_FULFILLMENT",
        )

    def test_external_proof_requirements_are_not_silently_omitted(self):
        requirements = set(health_response()["readiness_requirements"])
        self.assertTrue({
            "live_webhook_delivery_verified",
            "durable_receipt_storage_verified",
            "paid_order_to_customer_delivery_verified",
        }.issubset(requirements))

    def test_scientific_authority_remains_false(self):
        self.assertFalse(health_response()["scientific_authority_granted"])

    def test_storage_debt_is_not_hidden(self):
        self.assertEqual(health_response()["storage"], "sqlite-ephemeral")


if __name__ == "__main__":
    unittest.main()
