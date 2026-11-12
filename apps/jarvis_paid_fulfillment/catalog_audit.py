"""R151 Stripe catalog read-only reconciliation (owner: Jarvis paid fulfillment).

Pure standard library; consumes a pre-sanitized Stripe snapshot. It never uses
Stripe API credentials, changes live prices, processes personal data, or deploys.
List API results are not presumed exhaustive if direct linked reads disagree.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping


class CatalogEvidenceError(ValueError):
    """Incomplete or inconsistent source evidence; do not issue a PASS."""


def _unique_dict(rows: list[dict], kind: str) -> dict[str, dict]:
    seen: dict[str, dict] = {}
    for row in rows:
        ident = row.get("id")
        if not isinstance(ident, str) or not ident or ident in seen:
            raise CatalogEvidenceError(f"invalid_or_duplicate_{kind}_id")
        seen[ident] = row
    return seen


def assess_catalog(data: Mapping[str, Any]) -> dict[str, Any]:
    """Deterministic redacted summary; no URLs, emails, names, or Stripe IDs."""
    if data.get("schema") != "tristan-stripe-catalog-priv-r151-v1":
        raise CatalogEvidenceError("unknown_snapshot_schema")
    if data.get("livemode") is not True:
        raise CatalogEvidenceError("live_catalog_snapshot_expected")
    if data.get("discovery", {}).get("all_payment_link_lines_complete") is not True:
        raise CatalogEvidenceError("link_line_coverage_unverified")
    raw_products = list(data.get("products", []))
    raw_prices = list(data.get("prices", []))
    direct_products = list(data.get("supplemental_products", []))
    direct_prices = list(data.get("supplemental_prices", []))
    raw_links = list(data.get("links", []))
    _unique_dict(raw_products, "listed_product")
    _unique_dict(raw_prices, "listed_price")
    _unique_dict(direct_products, "direct_product")
    _unique_dict(direct_prices, "direct_price")
    original_product_ids = {p["id"] for p in raw_products}
    original_price_ids = {p["id"] for p in raw_prices}
    if original_product_ids & {p["id"] for p in direct_products}:
        raise CatalogEvidenceError("direct_product_duplicate_of_list")
    if original_price_ids & {p["id"] for p in direct_prices}:
        raise CatalogEvidenceError("direct_price_duplicate_of_list")
    products = _unique_dict(raw_products + direct_products, "all_product")
    prices = _unique_dict(raw_prices + direct_prices, "all_price")
    links = _unique_dict(raw_links, "link")

    discovery = data.get("discovery", {})
    if discovery.get("list_products_count") != len(raw_products):
        raise CatalogEvidenceError("list_product_count_mismatch")
    if discovery.get("list_prices_count") != len(raw_prices):
        raise CatalogEvidenceError("list_price_count_mismatch")
    if discovery.get("supplemental_direct_confirmed_products") != len(direct_products):
        raise CatalogEvidenceError("direct_product_count_mismatch")
    if discovery.get("supplemental_direct_confirmed_prices") != len(direct_prices):
        raise CatalogEvidenceError("direct_price_count_mismatch")

    referenced_products: set[str] = set()
    linked_prices: set[str] = set()
    active_products_linked: set[str] = set()
    unresolved_price_references = 0
    price_product_mismatches = 0
    unresolved_product_references = 0
    inactive_product_live_links = 0
    inactive_price_live_links = 0
    held_product_live_links = 0
    active_link_without_tax = 0
    count_items = 0
    for link in links.values():
        if link.get("line_item_status") != "VERIFIED_COMPLETE":
            raise CatalogEvidenceError("some_payment_link_lines_not_verified")
        lines = link.get("line_items")
        if not isinstance(lines, list) or not lines:
            raise CatalogEvidenceError("payment_link_without_line_items")
        count_items += len(lines)
        if not link.get("active"):
            continue
        if link.get("automatic_tax_enabled") is not True:
            active_link_without_tax += 1
        for row in lines:
            price_id = row.get("price_id")
            product_id = row.get("product_id")
            linked_prices.add(price_id)
            referenced_products.add(product_id)
            price = prices.get(price_id)
            product = products.get(product_id)
            if not price:
                unresolved_price_references += 1
            if not product:
                unresolved_product_references += 1
            if price and not price.get("active"):
                inactive_price_live_links += 1
            if price and product_id and price.get("product_id") != product_id:
                price_product_mismatches += 1
            if product:
                if not product.get("active"):
                    inactive_product_live_links += 1
                else:
                    active_products_linked.add(product_id)
                meta = product.get("metadata") or {}
                if any("HOLD" in str(meta.get(k, "")).upper() for k in ("readiness", "stage")):
                    held_product_live_links += 1

    active_products = [p for p in products.values() if p.get("active")]
    active_links = [x for x in links.values() if x.get("active")]
    active_prices = [x for x in prices.values() if x.get("active")]
    missing_default_active = sum(not p.get("default_price") for p in active_products)
    missing_link_active = sum(p["id"] not in active_products_linked for p in active_products)
    linked_discovered_extras = sum(x in referenced_products for x in (set(products) - original_product_ids))
    gates = data.get("account_gates", {})
    problems = []
    def flag(code: str, severity: str, count: int, reason: str) -> None:
        if count:
            problems.append({"code": code, "severity": severity, "affected_count": count, "scope": reason})
    flag("LIST_DISCOVERY_INCOMPLETE", "BLOCKER", len(direct_products) + len(direct_prices),
         "Confirmed direct objects absent from list result; completeness cannot be claimed")
    flag("UNRESOLVED_LINK_PRICE_REFERENCE", "BLOCKER", unresolved_price_references,
         "Live link item references price not verified in list or direct reads")
    flag("UNRESOLVED_LINK_PRODUCT_REFERENCE", "BLOCKER", unresolved_product_references,
         "Live link item references product not verified in list or direct reads")
    flag("LINK_PRICE_PRODUCT_MISMATCH", "BLOCKER", price_product_mismatches,
         "Live payment link price belongs to a different product; resolve by direct Stripe read")
    flag("LIVE_LINK_TO_INACTIVE_PRODUCT", "BLOCKER", inactive_product_live_links, "Active sale link points to inactive product")
    flag("LIVE_LINK_TO_INACTIVE_PRICE", "BLOCKER", inactive_price_live_links, "Active sale link points to inactive price")
    flag("LIVE_LINK_PRODUCT_HAS_HOLD_METADATA", "BLOCKER", held_product_live_links,
         "Live payment link advertises a product marked HOLD or unverified in catalog metadata")
    flag("LIVE_WEBHOOK_DESTINATION_MISSING", "BLOCKER", int(gates.get("live_webhook_endpoints") == 0),
         "Account list shows no webhook endpoint for automatic fulfillment")
    flag("TAX_SETTINGS_NOT_ACTIVE", "REVIEW", int(gates.get("tax_settings_status") != "active"),
         "Tax configuration needs competent review; no legal obligation inferred")
    flag("TAX_AUTOMATION_DISABLED", "REVIEW", active_link_without_tax,
         "Automatic tax off on active link; collection obligation not determined")
    flag("ACTIVE_PRODUCTS_WITHOUT_DEFAULT_PRICE", "REVIEW", missing_default_active,
         "Product has no default price; may be intentional for link-only offers")
    flag("ACTIVE_PRODUCTS_WITHOUT_ACTIVE_PAYMENT_LINK", "INFO", missing_link_active,
         "Might be intentionally sold via invoice or custom Checkout; not proof of breakage")
    severity_counts = dict(sorted(Counter(p["severity"] for p in problems).items()))
    return {
        "schema": "tristan-stripe-catalog-audit-r151-v1",
        "captured_date": str(data.get("captured_date", "UNKNOWN")),
        "mode": "READ_ONLY_RECONCILIATION",
        "coverage": {
            "listed_products": len(raw_products),
            "direct_confirmed_additional_products": len(direct_products),
            "identified_products_at_least": len(products),
            "listed_prices": len(raw_prices),
            "direct_confirmed_additional_prices": len(direct_prices),
            "identified_prices_at_least": len(prices),
            "payment_links_checked": len(links),
            "link_line_items_checked": count_items,
            "linked_extra_products": linked_discovered_extras,
            "completeness": "NOT_PROVEN",
        },
        "observations": {
            "active_products_identified": len(active_products),
            "active_prices_identified": len(active_prices),
            "active_payment_links": len(active_links),
            "active_products_linked": len(active_products_linked),
            "active_links_with_automatic_tax_disabled": active_link_without_tax,
            "active_links_to_products_with_hold_metadata": held_product_live_links,
            "active_products_without_default_price": missing_default_active,
            "active_products_without_active_link": missing_link_active,
            "webhook_endpoints": gates.get("live_webhook_endpoints", None),
            "stripe_tax_registrations": gates.get("stripe_tax_registrations", None),
            "tax_settings_status": gates.get("tax_settings_status", None),
        },
        "findings": problems,
        "severity_counts": severity_counts,
        "promotion_status": "BLOCKED",
        "actions": [
            "Do not delete/archive/change live products, tax settings, links, or subscriptions from incomplete list reads",
            "Confirm every direct-linked item, fulfillment owner, refunds/support policy, and existing customer obligations",
            "Compare list/search/direct results; reconcile pagination inconsistencies before any catalog migration",
            "Establish verified sandbox paid-order fulfillment and customer delivery before promoting automation",
            "Require Stripe fiscal/tax authority and independent Jarvis/OAK reviews before financial configuration changes",
        ],
        "invariants": [
            "Listed != Exhaustive", "Checkout != Paid", "Paid != Delivered",
            "ConfigurationReady != DeliveryVerified", "Generated != Verified",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path, required=True, help="private read-only snapshot JSON")
    parser.add_argument("--report", type=Path, required=True, help="redacted report output")
    parser.add_argument("--gate", action="store_true", help="exit 2 if promotion remains blocked")
    args = parser.parse_args(argv)
    source = json.loads(args.snapshot.read_text(encoding="utf-8"))
    report = assess_catalog(source)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    if args.report.exists():
        parser.error("report already exists; refusing overwrite")
    args.report.write_text(json.dumps(report,sort_keys=True,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("CATALOG_AUDIT_R151: redacted, read-only, completeness NOT_PROVEN")
    print("IDENTIFIED_AT_LEAST", report["coverage"]["identified_products_at_least"], report["coverage"]["identified_prices_at_least"])
    print("ISSUES", json.dumps(report["severity_counts"], sort_keys=True))
    if args.gate and report["promotion_status"] == "BLOCKED":
        print("PROMOTION_GATE_BLOCKED")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
