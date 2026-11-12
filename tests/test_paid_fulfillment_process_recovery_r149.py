"""Subprocess-boundary recovery court: independent processes, one persistent local DB.

This is not proof of host-restart durability or Render filesystem persistence.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

MODULES = Path(__file__).resolve().parents[1] / "apps" / "jarvis_paid_fulfillment"


def run_python(source: str, database: Path) -> str:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(MODULES)
    result = subprocess.run(
        [sys.executable, "-c", source, str(database)],
        capture_output=True, text=True, check=True, timeout=20, env=env,
    )
    return result.stdout.strip()


def test_paid_queue_survives_worker_process_exit_and_releases_lease(tmp_path):
    database = tmp_path / "independent-processes.sqlite3"
    first = """
from core import PaidAuditIntake
from fulfillment_queue import enqueue_paid_checkout
import sys
intake = PaidAuditIntake(
    session_id='cs_test_restart_r149', project='https://github.com/example/repo',
    problem='bounded check', scope='public read only', customer_email='',
    payment_link='plink_test', offer='repo_quickcheck_first_5',
).with_digest()
print(enqueue_paid_checkout(sys.argv[1], intake, now=100))
"""
    assert run_python(first, database) == "QUEUED"

    crash_after_claim = """
import sys
from fulfillment_queue import claim_next_job
claim = claim_next_job(sys.argv[1], now=101, lease_seconds=10)
assert claim and claim.attempt == 1
print('PROCESS_1_CLAIMED')
"""
    assert run_python(crash_after_claim, database) == "PROCESS_1_CLAIMED"

    before_lease = """
import sys
from fulfillment_queue import claim_next_job
assert claim_next_job(sys.argv[1], now=105, lease_seconds=10) is None
print('SAFE_NOT_RECLAIMED')
"""
    assert run_python(before_lease, database) == "SAFE_NOT_RECLAIMED"

    recover = """
import sys
from fulfillment_queue import claim_next_job,finish_claim
claim = claim_next_job(sys.argv[1], now=112, lease_seconds=10)
assert claim and claim.attempt == 2
assert finish_claim(sys.argv[1], claim, result={'digest':'recovered-synthetic'},
                    now=113)
print('RECLAIMED_AND_READY')
"""
    assert run_python(recover, database) == "RECLAIMED_AND_READY"

    read_only = """
import sys
from core import load_result
from fulfillment_queue import claim_next_job
record = load_result(sys.argv[1], 'cs_test_restart_r149')
assert record['status']=='READY'
assert record['report']['digest']=='recovered-synthetic'
assert record['delivery_verified'] is False
assert claim_next_job(sys.argv[1], now=1000) is None
print('PERSISTED_NO_DUPLICATE')
"""
    assert run_python(read_only, database) == "PERSISTED_NO_DUPLICATE"
