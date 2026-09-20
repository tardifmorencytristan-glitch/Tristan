import hashlib
import hmac
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
EXPORT = ROOT / "apps" / "jarvis_paid_fulfillment"
sys.path.insert(0, str(EXPORT))

from core import (
    AUDIT_PAYMENT_LINK_ID,
    QUICKCHECK_PAYMENT_LINK_ID,
    QUICKCHECK_MAX_FILES,
    QUICKCHECK_MAX_TOTAL_BYTES,
    audit_repo_snapshot,
    intake_from_checkout_session,
    parse_public_github_repo,
    render_report_html,
    verify_stripe_signature,
    claim_result_slot,
    load_result,
    store_result,
)

def test_stripe_signature_valid_invalid_and_stale():
    payload = b'{"id":"evt_1"}'
    secret = "whsec_test"
    ts = 1000
    sig = hmac.new(secret.encode(), str(ts).encode() + b"." + payload, hashlib.sha256).hexdigest()
    header = f"t={ts},v1={sig}"
    assert verify_stripe_signature(payload, header, secret, now=1000)
    assert not verify_stripe_signature(payload, header, secret + "x", now=1000)
    assert not verify_stripe_signature(payload, header, secret, now=1401)

def test_paid_audit_intake_is_bound_to_offer():
    session = {
        "id": "cs_test_123",
        "payment_status": "paid",
        "payment_link": AUDIT_PAYMENT_LINK_ID,
        "metadata": {"offer": "audit_express_99", "fulfillment": "auto_oak_audit_v1"},
        "custom_fields": [
            {"key": "project", "text": {"value": "https://github.com/acme/demo"}},
            {"key": "problem", "text": {"value": "Review CI and dependency risks"}},
            {"key": "scope", "text": {"value": "Public repository read-only review only"}},
        ],
        "customer_details": {"email": "buyer@example.com"},
    }
    intake = intake_from_checkout_session(session)
    assert intake.project == "https://github.com/acme/demo"
    assert intake.digest

def test_paid_quickcheck_intake_is_bound_to_offer_and_limits():
    session = {
        "id": "cs_test_quickcheck",
        "payment_status": "paid",
        "payment_link": QUICKCHECK_PAYMENT_LINK_ID,
        "metadata": {
            "offer": "repo_quickcheck_first_5",
            "fulfillment": "jarvis_quickcheck_v1",
        },
        "custom_fields": [
            {"key": "project", "text": {"value": "https://github.com/acme/demo"}},
        ],
        "customer_details": {"email": "buyer@example.com"},
    }
    intake = intake_from_checkout_session(session)
    assert intake.offer == "repo_quickcheck_first_5"
    assert intake.problem == "General bounded repository QuickCheck"
    report = audit_repo_snapshot(
        {"full_name": "acme/demo", "default_branch": "main", "archived": False, "fork": False},
        [{"path": f"src/f{i}.py", "type": "blob", "size": 10} for i in range(20)],
        {},
        problem=intake.problem,
        scope=intake.scope,
        max_files=QUICKCHECK_MAX_FILES,
        max_total_bytes=QUICKCHECK_MAX_TOTAL_BYTES,
    )
    assert report["coverage"]["bounded_max_files"] == 10
    assert report["coverage"]["bounded_max_total_bytes"] == 500_000
    assert report["coverage"]["files_selected"] == 10

def test_wrong_or_unpaid_offer_is_rejected():
    for session in (
        {"id": "cs_x", "payment_status": "unpaid", "payment_link": AUDIT_PAYMENT_LINK_ID},
        {"id": "cs_x", "payment_status": "paid", "payment_link": "plink_other", "metadata": {}},
    ):
        try:
            intake_from_checkout_session(session)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid checkout must fail closed")

def test_public_github_parser_is_narrow():
    assert parse_public_github_repo("https://github.com/acme/demo") == ("acme", "demo")
    assert parse_public_github_repo("acme/demo") == ("acme", "demo")
    try:
        parse_public_github_repo("https://example.com/acme/demo")
    except ValueError:
        pass
    else:
        raise AssertionError("non-GitHub host must fail closed")

def test_audit_redacts_secret_values_and_preserves_boundaries():
    tree = [
        {"path": "README.md", "type": "blob", "size": 20},
        {"path": "requirements.txt", "type": "blob", "size": 20},
        {"path": "src/app.py", "type": "blob", "size": 100},
    ]
    secret = "sk-proj-ABCDEFGHIJKLMNOPQRSTUVWXYZ012345"
    files = {
        "README.md": "demo",
        "requirements.txt": "requests>=2\n",
        "src/app.py": f'x="{secret}"\nrequests.get(url, verify=False)\n',
    }
    report = audit_repo_snapshot(
        {"full_name": "acme/demo", "default_branch": "main", "archived": False, "fork": False},
        tree,
        files,
        problem="security review",
        scope="public read-only",
    )
    codes = {row["code"] for row in report["findings"]}
    assert {"OPENAI_KEY_LIKE", "TLS_VERIFY_FALSE", "TESTS_MISSING", "CI_MISSING"} <= codes
    assert secret not in json.dumps(report)
    assert report["authority_granted"] is False
    assert "NoFlag != Safe" in report["boundaries"]

def test_report_html_escapes_untrusted_values():
    report = {
        "status": "REVIEW",
        "repository": {"full_name": "<script>x</script>"},
        "digest": "d",
        "findings": [],
        "boundaries": ["Audit != Certification"],
    }
    rendered = render_report_html(report)
    assert "<script>x</script>" not in rendered
    assert "&lt;script&gt;" in rendered

def test_sqlite_result_store_is_idempotent(tmp_path):
    path = str(tmp_path / "results.sqlite3")
    assert claim_result_slot(path, "cs_test", {"status": "PROCESSING"})
    assert not claim_result_slot(path, "cs_test", {"status": "PROCESSING"})
    store_result(path, "cs_test", {"status": "READY", "value": 7})
    assert load_result(path, "cs_test") == {"status": "READY", "value": 7}

def test_optional_problem_and_scope_use_safe_defaults():
    session = {
        "id": "cs_test_optional",
        "payment_status": "paid",
        "payment_link": AUDIT_PAYMENT_LINK_ID,
        "metadata": {
            "offer": "audit_express_99",
            "fulfillment": "auto_oak_audit_v1",
            "conversion_experiment": "friction_reduction_r1",
            "intake": "checkout_project_required_problem_scope_optional_v2",
        },
        "custom_fields": [
            {"key": "project", "text": {"value": "https://github.com/acme/demo"}},
            {"key": "problem", "text": {"value": ""}},
            {"key": "scope", "text": {"value": ""}},
        ],
        "customer_details": {"email": "buyer@example.com"},
    }
    intake = intake_from_checkout_session(session)
    assert intake.problem == "General bounded technical audit"
    assert "read-only" in intake.scope
    assert "no mutation" in intake.scope

def test_after_purchase_page_is_zero_touch_and_non_authoritative():
    html = (ROOT / "after-purchase.html").read_text(encoding="utf-8")
    assert "Aucune action supplémentaire requise." in html
    assert "Cette page ne prouve pas qu’un paiement a réussi." in html
    assert "Stripe reste la source de vérité" in html
    assert "Envoyer l’intake" not in html
    assert "Audit ≠ certification" in html
    assert "PublicRead ≠ autorité de mutation" in html
