"""Pure-Python verification of the R150 result-access cryptographic boundary."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "jarvis_paid_fulfillment"))
from result_access import issue_result_access_token, verify_result_access


def test_valid_signature_is_session_bound_and_short_lived():
    secret = "independent_test_secret_only_minimum_32_bytes"
    first = "cs_test_r150_kernel_A"
    second = "cs_test_r150_kernel_B"
    signed = issue_result_access_token(first, secret, ttl_seconds=10, now=100)
    assert verify_result_access(first, "Bearer " + signed, secret, now=100)
    assert not verify_result_access(second, "Bearer " + signed, secret, now=100)
    assert not verify_result_access(first, "Bearer " + signed, secret, now=110)


def test_webhook_identity_is_not_a_report_read_capability():
    secret = "independent_test_secret_only_minimum_32_bytes"
    checkout_id = "cs_test_r150_kernel_C"
    forged = "Bearer " + issue_result_access_token(
        checkout_id, "another_distinct_secret_at_least_32_bytes", now=100
    )
    assert not verify_result_access(checkout_id, forged, secret, now=100)
    assert not verify_result_access(checkout_id, "", secret, now=100)


def test_malformed_or_weak_key_rejected():
    secret = "independent_test_secret_only_minimum_32_bytes"
    checkout_id = "cs_test_r150_kernel_D"
    signed = issue_result_access_token(checkout_id, secret, ttl_seconds=1, now=100)
    assert not verify_result_access(checkout_id, signed, secret, now=100)
    assert not verify_result_access(checkout_id, "Bearer " + signed, "weak", now=100)
