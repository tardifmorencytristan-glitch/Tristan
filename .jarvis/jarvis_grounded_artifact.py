from __future__ import annotations

from hashlib import sha256
import argparse
import json
from pathlib import Path
import sys


PROTOCOL = "ULTIMATE-JARVIS-TRISTAN-LOCAL-PROOF-CARRYING-ARTIFACT-R1"
VISIBILITY_RANK = {"PUBLIC_SAFE": 0, "PRIVATE": 1, "SECRET": 2}


def _digest(value: object) -> str:
    body = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return "sha256:" + sha256(body.encode("utf-8")).hexdigest()


def _sha40(value: str, field: str) -> str:
    value = str(value).strip().lower()
    if len(value) != 40 or any(ch not in "0123456789abcdef" for ch in value):
        raise ValueError(f"{field} must be sha40")
    return value


def compile_artifact(profile: dict, mission: dict, local_commit: str, claims: list[dict]) -> dict:
    local_commit = _sha40(local_commit, "local_commit")
    root_commit = _sha40(profile["root_commit"], "root_commit")
    target_visibility = profile["target_visibility"]
    target_rank = VISIBILITY_RANK[target_visibility]
    allowed_repositories = set(profile["allowed_source_repositories"])
    local_repo = profile["local_repository"]
    root_repo = profile["root_repository"]
    local_paths = set(mission.get("local_sources", []))
    root_paths = set(mission.get("root_anchors", []))
    selected_roles = set(mission.get("selected_roles", []))

    unsupported = []
    bad_scope = []
    bad_path = []
    bad_commit = []
    bad_visibility = []
    bad_role = []
    grounded = []
    rendered = []

    substantive = [claim for claim in claims if claim.get("substantive", True)]

    for claim in claims:
        claim_id = str(claim.get("claim_id", "")).strip()
        text = str(claim.get("text", "")).strip()
        role = str(claim.get("role", "")).strip()
        sources = claim.get("sources", []) or []
        if not claim_id or not text or not role:
            raise ValueError("claim_id/text/role required")

        failed = False
        if claim.get("substantive", True):
            if role not in selected_roles:
                bad_role.append(claim_id)
                failed = True
            if not sources:
                unsupported.append(claim_id)
                rendered.append(text + " [HOLD_UNSOURCED]")
                continue

            refs = []
            for source in sources:
                repository = str(source.get("repository", ""))
                path = str(source.get("path", ""))
                commit = _sha40(source.get("commit", ""), "source.commit")
                locator = str(source.get("locator", "")).strip()
                visibility = str(source.get("visibility", "")).upper()
                if repository not in allowed_repositories:
                    bad_scope.append(claim_id)
                    failed = True
                    continue
                if repository == local_repo:
                    expected_commit = local_commit
                    allowed_paths = local_paths
                elif repository == root_repo:
                    expected_commit = root_commit
                    allowed_paths = root_paths
                else:
                    bad_scope.append(claim_id)
                    failed = True
                    continue
                if path not in allowed_paths:
                    bad_path.append(claim_id)
                    failed = True
                if commit != expected_commit:
                    bad_commit.append(claim_id)
                    failed = True
                if visibility not in VISIBILITY_RANK or VISIBILITY_RANK[visibility] > target_rank:
                    bad_visibility.append(claim_id)
                    failed = True
                if not locator:
                    unsupported.append(claim_id)
                    failed = True
                refs.append(f"{repository}@{commit}:{path}#{locator}")

            rendered.append(text + " [sources: " + "; ".join(refs) + "]")
            if not failed:
                grounded.append(claim)
        else:
            rendered.append(text)

    total_weight = sum(float(x.get("weight", 1.0)) for x in substantive)
    grounded_ids = {x["claim_id"] for x in grounded}
    grounded_weight = sum(
        float(x.get("weight", 1.0))
        for x in substantive
        if x["claim_id"] in grounded_ids
    )
    coverage = grounded_weight / total_weight if total_weight else 0.0

    def uniq(values):
        return sorted(set(values))

    if not substantive:
        status = "HOLD_EMPTY_ARTIFACT"
    elif unsupported:
        status = "HOLD_UNSOURCED"
    elif bad_scope:
        status = "HOLD_SOURCE_SCOPE"
    elif bad_path:
        status = "HOLD_SOURCE_PATH"
    elif bad_commit:
        status = "HOLD_COMMIT_MISMATCH"
    elif bad_visibility:
        status = "HOLD_VISIBILITY"
    elif bad_role:
        status = "HOLD_ROLE_SCOPE"
    elif coverage != 1.0:
        status = "HOLD_GROUNDING_GAP"
    else:
        status = "PASS_PROOF_CARRYING"

    artifact = {
        "protocol": PROTOCOL,
        "status": status,
        "target_visibility": target_visibility,
        "local_commit": local_commit,
        "root_commit": root_commit,
        "substantive_claim_count": len(substantive),
        "grounded_claim_count": len(grounded),
        "weighted_grounding_coverage": coverage,
        "unsupported_claim_ids": uniq(unsupported),
        "source_scope_violation_claim_ids": uniq(bad_scope),
        "source_path_violation_claim_ids": uniq(bad_path),
        "commit_mismatch_claim_ids": uniq(bad_commit),
        "visibility_violation_claim_ids": uniq(bad_visibility),
        "role_scope_violation_claim_ids": uniq(bad_role),
        "claims": claims,
        "rendered_markdown": "\\n\\n".join(rendered),
        "scientific_truth_claimed": False,
        "publication_authority_granted": False,
        "promotion_authority_granted": False,
        "boundaries": [
            "Generated != Verified",
            "CorrectPath != CorrectCommit",
            "RepositorySource != ScientificTruth",
            "PrivateSource -> PublicOutput = FORBIDDEN",
            "NoSource -> NoSubstantiveClaim",
        ],
    }
    artifact["digest"] = _digest(artifact)
    return artifact


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default=".jarvis/JARVIS_REPO_PROFILE.json")
    parser.add_argument("--mission", default=".jarvis/JARVIS_MISSION_PACKET.json")
    parser.add_argument("--claims", required=True)
    parser.add_argument("--local-commit", required=True)
    parser.add_argument("--output", default=".jarvis/JARVIS_PROOF_CARRYING_ARTIFACT.json")
    args = parser.parse_args()

    profile = json.loads(Path(args.profile).read_text(encoding="utf-8"))
    mission = json.loads(Path(args.mission).read_text(encoding="utf-8"))
    claims = json.loads(Path(args.claims).read_text(encoding="utf-8"))
    if not isinstance(claims, list):
        raise ValueError("claims payload must be a JSON list")

    artifact = compile_artifact(profile, mission, args.local_commit, claims)
    Path(args.output).write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\\n",
        encoding="utf-8",
    )
    print(json.dumps(artifact, indent=2, sort_keys=True))
    return 0 if artifact["status"] == "PASS_PROOF_CARRYING" else 2


if __name__ == "__main__":
    sys.exit(main())
