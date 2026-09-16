from __future__ import annotations

from omega_omni_compiler.src.domain_ir import CodeIR, GitIR, DocumentIR, SpecIR


def spec_to_code(spec: SpecIR, language: str = "python") -> CodeIR:
    tests = []
    invariants = []
    for c in spec.constraints:
        name = c.get("name", "constraint")
        invariants.append(name)
        tests.append(f"test_{name}")
    return CodeIR(
        id=f"CODE-{spec.id}",
        language=language,
        modules=["generated_constraints"],
        invariants=invariants,
        tests=tests,
        provenance=f"derived:{spec.id}",
    )


def code_to_git(code: CodeIR, repository: str, branch: str, head_sha: str) -> GitIR:
    return GitIR(
        id=f"GIT-{code.id}",
        repository=repository,
        branch=branch,
        head_sha=head_sha,
        commits=[],
        checks=[{"name": t, "status": "DECLARED_NOT_RUN"} for t in code.tests],
        provenance=f"derived:{code.id}",
    )


def git_to_document(git: GitIR, code: CodeIR) -> DocumentIR:
    return DocumentIR(
        id=f"DOC-{git.id}",
        title=f"Technical report for {git.repository}",
        document_type="technical_report",
        claim_ids=[],
        sections=[
            {"id": "software", "title": "Software state", "head_sha": git.head_sha},
            {"id": "invariants", "title": "Declared invariants", "items": list(code.invariants)},
            {"id": "tests", "title": "Declared tests", "items": list(code.tests)},
        ],
        provenance=f"derived:{git.id}",
    )


def document_to_artifact(document: DocumentIR) -> dict:
    return {
        "id": f"ART-{document.id}",
        "type": "ARTIFACT",
        "media_type": "application/pdf-candidate",
        "title": document.title,
        "source_document_id": document.id,
        "provenance": f"derived:{document.id}",
        "status": "CANDIDATE_NOT_RENDERED",
    }


def artifact_to_document(artifact: dict, original: DocumentIR) -> DocumentIR:
    # R1 uses a provenance-preserving reversible fixture, not PDF parsing.
    return DocumentIR(
        id=original.id,
        title=artifact.get("title", original.title),
        document_type=original.document_type,
        claim_ids=list(original.claim_ids),
        sections=list(original.sections),
        provenance=f"reverse:{artifact['id']}",
    )
