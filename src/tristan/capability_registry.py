from __future__ import annotations

from dataclasses import dataclass

from .demand_ir import CapabilityIR


@dataclass(frozen=True)
class CapabilityRecord:
    capability: CapabilityIR
    status: str
    evidence_receipts: tuple[str, ...]
    limitations: tuple[str, ...] = ()


def default_capability_registry() -> tuple[CapabilityRecord, ...]:
    """Only capabilities with repository-persisted evidence receipts are listed."""
    return (
        CapabilityRecord(
            CapabilityIR("ScientificConsistency", ("model_validation", "technical_consistency"), ("receipts/SCIENTIFIC_CONSISTENCY_REALWORLD_R0_5_ADJUDICATION.json",), "PARTIAL_AUTOMATION"),
            "PARTIAL_REALWORLD_EVIDENCE",
            ("receipts/SCIENTIFIC_CONSISTENCY_REALWORLD_R0_5_ADJUDICATION.json",),
            ("R0.5 binary recall 0.35", "real-world precision/FPR unknown"),
        ),
        CapabilityRecord(
            CapabilityIR("SemanticIR", ("code_semantics", "dataflow", "architecture", "protocol"), ("receipts/SEMANTIC_IR_R0_2.json",), "AUTOMATED"),
            "LOCAL_CI_VERIFIED",
            ("receipts/SEMANTIC_IR_R0_2.json",),
            ("not real-world promoted",),
        ),
        CapabilityRecord(
            CapabilityIR("ScientificWritingCompiler", ("evidence_bounded_writing", "traceability"), ("docs",), "AUTOMATED"),
            "REPOSITORY_IMPLEMENTED",
            ("docs",),
            ("document generation does not certify claim truth",),
        ),
        CapabilityRecord(
            CapabilityIR(
                "CommunicationProjection",
                ("timed_projection", "claim_evidence_binding", "webvtt_export"),
                ("omega_omni_compiler/evidence/R4H_COMMUNICATION_PROJECTION_R01.json",),
                "AUTOMATED",
            ),
            "LOCAL_BOUNDED_ENGINEERING_PASS",
            ("omega_omni_compiler/evidence/R4H_COMMUNICATION_PROJECTION_R01.json",),
            (
                "structural projection pass is not semantic equivalence",
                "voice/video rendering and human comprehension remain separate gates",
            ),
        ),
        CapabilityRecord(
            CapabilityIR("DemandToCapability", ("opportunity_assessment", "capability_gap", "evidence_gap"), ("src/tristan/demand_ir.py",), "AUTOMATED"),
            "LOCAL_CI_VERIFIED",
            ("src/tristan/demand_ir.py",),
            ("open demand is not revenue",),
        ),
    )


def capabilities() -> tuple[CapabilityIR, ...]:
    return tuple(r.capability for r in default_capability_registry())
