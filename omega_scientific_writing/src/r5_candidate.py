from __future__ import annotations


def build_r5_candidate(thesis_state: dict) -> dict:
    claims = thesis_state.get("claims", [])
    residuals = thesis_state.get("residuals", [])
    return {
        "schema_version": "r5-candidate-r2",
        "source_project": thesis_state.get("project", {}).get("id"),
        "parent_anchor": thesis_state.get("frozen_head"),
        "epistemic_policy": {
            "no_status_upgrade": True,
            "generated_not_verified": True,
            "repository_pass_not_scientific_pass": True,
        },
        "sections": [
            {
                "id": "state",
                "title": "État vérifiable hérité de R4",
                "claim_ids": [c["id"] for c in claims],
            },
            {
                "id": "residuals",
                "title": "Frontières ouvertes et dette de preuve",
                "residual_ids": [r["id"] for r in residuals],
            },
            {
                "id": "next_evidence",
                "title": "Preuves à recharger avant promotion",
                "requirements": [
                    "read exact cited commits and receipts",
                    "re-run or inspect exact-head tests where applicable",
                    "separate software evidence from scientific evidence",
                    "attach primary literature or experimental evidence for scientific claims",
                ],
            },
        ],
    }


def validate_no_epistemic_upgrade(thesis_state: dict, candidate: dict) -> list[str]:
    errors: list[str] = []
    policy = candidate.get("epistemic_policy", {})
    if not policy.get("no_status_upgrade"):
        errors.append("R5 candidate must forbid automatic epistemic status upgrades")
    source_ids = {c.get("id") for c in thesis_state.get("claims", [])}
    projected = set(candidate.get("sections", [{}])[0].get("claim_ids", []))
    if projected != source_ids:
        errors.append("R5 candidate claim projection must preserve the R4 ThesisState claim set")
    return errors
