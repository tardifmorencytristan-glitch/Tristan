from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
from typing import Any

from omega_scientific_writing.src.latex_renderer import extract_required_tokens, render_battery_manuscript


REQUIRED_TOKENS = {
    "CALCE",
    "DFN",
    "SPM",
    "SPMe",
    "ScientificPASS",
    "universal superiority",
    "capacity mismatch",
}


@dataclass(frozen=True)
class ScientificRenderArtifact:
    renderer_id: str
    renderer_version: str
    tex_sha256: str
    source_anchor: str
    required_tokens: tuple[str, ...]
    status: str = "GENERATED_NOT_PDF_VERIFIED"

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.renderer_id or not self.renderer_version:
            errors.append("renderer id/version required")
        if len(self.tex_sha256) != 64:
            errors.append("tex_sha256 must be SHA-256 hex")
        if not self.source_anchor:
            errors.append("source_anchor required")
        if set(self.required_tokens) != REQUIRED_TOKENS:
            errors.append("required token contract incomplete")
        if self.status != "GENERATED_NOT_PDF_VERIFIED":
            errors.append("source renderer adapter may not self-promote PDF verification")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def render_battery_packet(packet: dict[str, Any]) -> tuple[str, ScientificRenderArtifact]:
    tex = render_battery_manuscript(packet)
    observed_tokens = extract_required_tokens(tex)
    missing = sorted(REQUIRED_TOKENS - observed_tokens)
    if missing:
        raise ValueError(f"renderer output missing required tokens: {missing}")
    source_anchor = str(packet.get("source_anchor", ""))
    if not source_anchor or source_anchor not in tex:
        raise ValueError("exact source anchor missing from rendered LaTeX")
    artifact = ScientificRenderArtifact(
        renderer_id="omega_scientific_writing.latex_renderer.render_battery_manuscript",
        renderer_version="r4.2-exact-blob-a525a318d01ceb81a140c0c0438afcfe7bcad22a",
        tex_sha256=sha256(tex.encode("utf-8")).hexdigest(),
        source_anchor=source_anchor,
        required_tokens=tuple(sorted(observed_tokens)),
    )
    errors = artifact.validate()
    if errors:
        raise ValueError(errors)
    return tex, artifact
