from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REQUIRED = (
    "schema",
    "local_repository",
    "root_repository",
    "root_commit",
    "target_visibility",
    "root_access_mode",
    "allowed_source_repositories",
    "grounding_policy",
    "authority_granted",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default=".jarvis/JARVIS_REPO_PROFILE.json")
    parser.add_argument("--repo-private", required=True)
    args = parser.parse_args()

    profile = json.loads(Path(args.profile).read_text(encoding="utf-8"))
    missing = [key for key in REQUIRED if key not in profile]
    errors = []
    if missing:
        errors.append("missing:" + ",".join(missing))

    is_private = str(args.repo_private).strip().lower() in {"1", "true", "yes"}
    expected_visibility = "PRIVATE" if is_private else "PUBLIC_SAFE"
    expected_access = "FULL_PRIVATE_AUTHORIZED" if is_private else "PUBLIC_SAFE_PROJECTION_ONLY"

    if profile.get("target_visibility") != expected_visibility:
        errors.append("target_visibility_mismatch")
    if profile.get("root_access_mode") != expected_access:
        errors.append("root_access_mode_mismatch")
    if profile.get("authority_granted") is not False:
        errors.append("authority_must_remain_false")
    if profile.get("grounding_policy", {}).get("required_weighted_coverage") != 1.0:
        errors.append("grounding_coverage_must_equal_1")
    if profile.get("grounding_policy", {}).get("unsourced_substantive_claim") != "HOLD":
        errors.append("unsourced_claim_policy_must_hold")

    allowed = profile.get("allowed_source_repositories", [])
    expected_sources = {
        profile.get("root_repository"),
        profile.get("local_repository"),
    }
    if set(allowed) != expected_sources:
        errors.append("source_scope_must_equal_root_plus_local")

    root_commit = str(profile.get("root_commit", ""))
    if len(root_commit) != 40 or any(ch not in "0123456789abcdef" for ch in root_commit.lower()):
        errors.append("root_commit_must_be_exact_sha40")

    receipt = {
        "protocol": "ULTIMATE-JARVIS-TRISTAN-LOCAL-GUARD-R1",
        "status": "PASS" if not errors else "HOLD",
        "errors": errors,
        "authority_granted": False,
        "scientific_pass": False,
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
