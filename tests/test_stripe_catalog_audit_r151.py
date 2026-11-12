"""Offline OAK tests for R151 catalog reconciliation, with synthetic products."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "jarvis_paid_fulfillment"))
from catalog_audit import CatalogEvidenceError, assess_catalog, main


def sample():
    prod = {"id": "prod_toy_1", "name": "PRIVATE_NAME_SSH", "active": True,
            "default_price": "price_toy_1", "metadata": {}}
    price = {"id": "price_toy_1", "product_id": "prod_toy_1", "active": True,
             "unit_amount": 100, "currency": "cad", "recurring_interval": None}
    link = {"id": "plink_toy_1", "active": True, "automatic_tax_enabled": True,
            "line_item_status": "VERIFIED_COMPLETE", "metadata": {},
            "line_items": [{"product_id": "prod_toy_1", "price_id": "price_toy_1",
                            "quantity": 1}]}
    return {"schema": "tristan-stripe-catalog-priv-r151-v1",
            "captured_date": "2026-11-12", "livemode": True,
            "products": [prod], "prices": [price], "links": [link],
            "supplemental_products": [], "supplemental_prices": [],
            "account_gates": {"live_webhook_endpoints": 1,
                              "tax_settings_status": "active", "stripe_tax_registrations": 1},
            "discovery": {"list_products_count": 1, "list_prices_count": 1,
                          "supplemental_direct_confirmed_products": 0,
                          "supplemental_direct_confirmed_prices": 0,
                          "all_payment_link_lines_complete": True}}


def test_clean_baseline_still_limits_exhaustiveness():
    report = assess_catalog(sample())
    assert report["coverage"]["identified_products_at_least"] == 1
    assert report["coverage"]["completeness"] == "NOT_PROVEN"
    assert report["findings"] == []
    assert report["promotion_status"] == "BLOCKED"


def test_realistic_discovery_gaps_and_hold_generate_blockers_without_ids():
    data = sample()
    data["supplemental_products"] = [{"id": "prod_hidden_2", "active": True,
                                     "default_price": None, "name": "PRIVATE_HIDDEN_NAME",
                                     "metadata": {"readiness": "HOLD_UNVERIFIED_FULFILLMENT"}}]
    data["supplemental_prices"] = [{"id": "price_hidden_2", "product_id": "prod_hidden_2",
                                  "active": True, "unit_amount": 900, "currency": "cad"}]
    data["links"].append({"id": "plink_toy_2", "active": True,
                          "line_item_status": "VERIFIED_COMPLETE", "automatic_tax_enabled": False,
                          "line_items": [{"product_id": "prod_hidden_2",
                                          "price_id": "price_hidden_2", "quantity": 1}]})
    data["discovery"]["supplemental_direct_confirmed_products"] = 1
    data["discovery"]["supplemental_direct_confirmed_prices"] = 1
    data["account_gates"] = {"live_webhook_endpoints": 0,
                            "tax_settings_status": "pending",
                            "stripe_tax_registrations": 0}
    report = assess_catalog(data)
    codes = {x["code"] for x in report["findings"]}
    assert {"LIST_DISCOVERY_INCOMPLETE", "LIVE_LINK_PRODUCT_HAS_HOLD_METADATA",
            "LIVE_WEBHOOK_DESTINATION_MISSING", "TAX_SETTINGS_NOT_ACTIVE",
            "TAX_AUTOMATION_DISABLED"} <= codes
    assert report["coverage"]["identified_products_at_least"] == 2
    assert report["observations"]["active_links_to_products_with_hold_metadata"] == 1
    dumped = json.dumps(report)
    assert "PRIVATE_NAME_SSH" not in dumped
    assert "PRIVATE_HIDDEN_NAME" not in dumped
    assert "prod_toy_1" not in dumped
    assert "plink_toy_2" not in dumped


def test_price_to_product_mismatch_is_blocker():
    d = sample()
    d["prices"][0]["product_id"] = "prod_conflicting"
    r = assess_catalog(d)
    assert "LINK_PRICE_PRODUCT_MISMATCH" in {x["code"] for x in r["findings"]}


def test_absent_direct_price_is_blocker():
    d = sample()
    d["links"][0]["line_items"][0]["price_id"] = "price_UNKNOWN_PRIVATE"
    r = assess_catalog(d)
    assert "UNRESOLVED_LINK_PRICE_REFERENCE" in {v["code"] for v in r["findings"]}


@pytest.mark.parametrize("mutation", [
    lambda d: d.update(schema="bad"),
    lambda d: d.update(livemode=False),
    lambda d: d["discovery"].update(all_payment_link_lines_complete=False),
    lambda d: d["products"].append(copy.deepcopy(d["products"][0])),
    lambda d: d["discovery"].update(list_products_count=77),
    lambda d: d["links"][0].update(line_item_status="UNREAD"),
    lambda d: d["links"][0].update(line_items=[]),
])
def test_incomplete_or_duplicate_inputs_fail_closed(mutation):
    d = sample()
    mutation(d)
    with pytest.raises(CatalogEvidenceError):
        assess_catalog(d)


def test_public_report_is_redacted_and_never_overwritten(tmp_path):
    source = tmp_path / "private.json"
    out = tmp_path / "public.json"
    source.write_text(json.dumps(sample()), encoding="utf-8")
    assert main(["--snapshot", str(source), "--report", str(out)]) == 0
    report = out.read_text(encoding="utf-8")
    assert "PRIVATE_NAME_SSH" not in report
    with pytest.raises(SystemExit):
        main(["--snapshot", str(source), "--report", str(out)])
    blocked = tmp_path / "strict.json"
    assert main(["--snapshot", str(source), "--report", str(blocked), "--gate"]) == 2
