"""One-shot Jarvis fulfillment worker; invoke only from the existing authorized runtime.

No daemon or scheduler is created here. No payment or customer delivery is performed.
"""
from __future__ import annotations

import argparse
import json
import sys

from app import fulfillment_prerequisites, result_db_path
from fulfillment_queue import process_one


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Bounded Stripe→Jarvis work-queue drain")
    parser.add_argument("--max-jobs", type=int, default=1,
                        help="Maximum attempts this invocation may process (default: one)")
    parser.add_argument("--check", action="store_true",
                        help="Read configuration state without claiming work")
    args = parser.parse_args(argv)
    if not 1 <= args.max_jobs <= 100:
        parser.error("--max-jobs must be between 1 and 100")
    checks = fulfillment_prerequisites()
    if args.check:
        # Boolean configuration only; never disclose signing secret, DB path or PII.
        print(json.dumps({"configuration_ready": checks["configuration_ready"],
                          "delivery_verified": False}, sort_keys=True))
        return 0
    if not checks["configuration_ready"]:
        print(json.dumps({"status": "DISABLED_OR_UNCONFIGURED"}))
        return 2
    outcomes: dict[str, int] = {}
    try:
        for _ in range(args.max_jobs):
            status = process_one(result_db_path())
            outcomes[status] = outcomes.get(status, 0) + 1
            if status == "NO_ACTION":
                break
    except Exception:
        print(json.dumps({"status": "WORKER_FAILURE_REQUIRES_RETRY"}))
        return 1
    print(json.dumps({"outcomes": outcomes, "delivery_verified": False}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
