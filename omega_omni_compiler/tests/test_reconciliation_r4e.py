import json
import unittest
from pathlib import Path

from omega_omni_compiler.src.parser_adapters import ParserRun
from omega_omni_compiler.src.pdf_ir import PDFDocumentObservation, PDFPageObservation
from omega_omni_compiler.src.reconciliation import (
    IndependentAdjudication,
    reconcile_recorded_evidence,
    reconcile_runs,
)


ROOT = Path(__file__).resolve().parents[1]
R4D_RECEIPT = ROOT / "evidence" / "R4D_REAL_PARSER_COURT.json"
HASH_A = "a" * 64
HASH_B = "b" * 64


def run(parser: str, text: str, source_hash: str = HASH_A) -> ParserRun:
    observation = PDFDocumentObservation(
        source_artifact_id="fixture.pdf",
        source_sha256=source_hash,
        parser=parser,
        parser_version="1",
        pages=(PDFPageObservation(1, 100, 100),),
    )
    return ParserRun(parser, "1", observation, text)


class ReconciliationCourtR4ETests(unittest.TestCase):
    def test_exact_consensus_is_consensus_not_truth_claim(self):
        decision = reconcile_runs(
            [run("a", "Generated != Verified"), run("b", "Generated != Verified")],
            required_invariants=("Generated != Verified",),
        )
        self.assertEqual(decision.status, "CONSENSUS_TEXT")
        self.assertEqual(decision.accepted_parser_ids, ())
        self.assertEqual(decision.max_pairwise_disagreement, 0.0)
        self.assertEqual(decision.validate(), [])
        self.assertEqual(decision.to_loss_tensor().entries[0].state, "PRESERVED")

    def test_disagreement_holds_without_independent_adjudication(self):
        decision = reconcile_runs([run("a", "Vmax = 4.20 V"), run("b", "Vmax = 420 V")])
        self.assertEqual(decision.status, "HOLD_DISAGREEMENT")
        self.assertEqual(decision.accepted_parser_ids, ())
        self.assertGreater(decision.max_pairwise_disagreement, 0)
        loss = decision.to_loss_tensor().entries[0]
        self.assertEqual(loss.state, "UNKNOWN")
        self.assertEqual(loss.dimension, "SEMANTIC")

    def test_missing_required_invariant_has_priority_over_text_consensus(self):
        decision = reconcile_runs(
            [run("a", "same"), run("b", "same")],
            required_invariants=("Capability != Authority",),
        )
        self.assertEqual(decision.status, "HOLD_MISSING_INVARIANT")
        self.assertEqual(len(decision.missing_invariants), 2)

    def test_source_hash_mismatch_holds_before_semantic_adjudication(self):
        decision = reconcile_runs([run("a", "same", HASH_A), run("b", "same", HASH_B)])
        self.assertEqual(decision.status, "HOLD_SOURCE_MISMATCH")
        loss = decision.to_loss_tensor().entries[0]
        self.assertEqual(loss.dimension, "PROVENANCE")
        self.assertEqual(loss.state, "UNKNOWN")

    def test_external_adjudication_requires_explicit_authority_and_provenance(self):
        adjudication = IndependentAdjudication(
            id="court:human-reference:1",
            accepted_parser_ids=("a",),
            provenance=("gold://fixture/1",),
            authority="bounded-fixture-owner",
            scope="fixture page 1 only",
        )
        decision = reconcile_runs(
            [run("a", "Vmax = 4.20 V"), run("b", "Vmax = 420 V")],
            adjudication=adjudication,
        )
        self.assertEqual(decision.status, "ADJUDICATED_EXTERNAL")
        self.assertEqual(decision.accepted_parser_ids, ("a",))
        self.assertEqual(decision.authority, "bounded-fixture-owner")
        self.assertEqual(decision.validate(), [])
        self.assertEqual(decision.to_loss_tensor().entries[0].state, "RECONSTRUCTED")

    def test_adjudication_cannot_reference_parser_outside_court(self):
        adjudication = IndependentAdjudication(
            id="x",
            accepted_parser_ids=("missing",),
            provenance=("gold://x",),
            authority="owner",
            scope="fixture",
        )
        with self.assertRaises(ValueError):
            reconcile_runs([run("a", "x"), run("b", "y")], adjudication=adjudication)

    def test_persisted_r4d_real_court_remains_hold_disagreement(self):
        payload = json.loads(R4D_RECEIPT.read_text(encoding="utf-8"))
        decision = reconcile_recorded_evidence(payload)
        self.assertEqual(decision.status, "HOLD_DISAGREEMENT")
        self.assertEqual(decision.source_sha256, "ac4c774094bbecc7f52bf5fb9d1e035595e7a79e483685ed0bea29db7aaee68a")
        self.assertAlmostEqual(decision.max_pairwise_disagreement, 1.0 - 0.9737017310252996)
        self.assertEqual(decision.accepted_parser_ids, ())


if __name__ == "__main__":
    unittest.main()
