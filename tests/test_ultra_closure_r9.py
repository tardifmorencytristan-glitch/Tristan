import unittest
from pathlib import Path

from tristan.ultra_closure import (
    CapabilityCrystal,
    DebtVector,
    ProofCarryingResearchObject,
    compile_mission_genome,
    compile_ultra_closure,
    generation_throttle,
    select_regime,
)


class UltraClosureR9Tests(unittest.TestCase):
    def test_mission_genome_has_five_origin_court(self):
        genome = compile_mission_genome(
            mission_id="M-R9-1",
            goal="close evidence debt",
            residuals=("EVIDENCE_GAP", "CANONICALIZE_DUPLICATE_FAMILY"),
            context_ids=("atlas-r8",),
            debt=DebtVector(evidence=2.0, merge=1.0),
        )
        self.assertEqual(
            set(genome.candidate_origins),
            {"TRISTAN", "SIMPLE", "EXTERNAL", "HYBRID", "NO_ACTION"},
        )
        self.assertIn("evidence", genome.required_capabilities)
        self.assertIn("identity", genome.required_capabilities)

    def test_generation_throttle_activates_on_overload(self):
        receipt = generation_throttle(
            generation_rate=10.0,
            verification_rate=1.0,
            closure_rate=1.0,
            debt_absorption_rate=1.0,
        )
        self.assertEqual(receipt.status, "THROTTLE_GENERATION")
        self.assertLess(receipt.generation_budget_multiplier, 1.0)
        self.assertGreater(receipt.closure_budget_multiplier, 1.0)

    def test_regime_prefers_close_when_backlog_dominates(self):
        decision = select_regime(
            backlog=5.0,
            evidence_debt=4.0,
            reality_debt=1.0,
            verified_demand=0.0,
            risk=0.0,
        )
        self.assertEqual(decision.mode, "CLOSE")

    def test_capability_crystal_requires_evidence_and_regeneration(self):
        crystal = CapabilityCrystal(
            capability_id="cap-x",
            interface="run(x)->y",
            domain=("software",),
            evidence_ids=("receipt:1",),
            dependencies=("python",),
            limits=("bounded fixture",),
            falsifiers=("regression",),
            regeneration_recipe=("install", "run tests"),
            right_to_lose=True,
            provenance=("commit:abc",),
            version="1",
        )
        self.assertTrue(crystal.crystal_ready)
        self.assertFalse(crystal.to_dict()["scientific_pass"])

    def test_pcro_is_not_scientific_pass_by_construction(self):
        pcro = ProofCarryingResearchObject(
            object_id="pcro-1",
            claims=("claim-1",),
            data_refs=("data-1",),
            code_refs=("code-1",),
            environment_refs=("env-1",),
            evidence_refs=("ev-1",),
            negative_results=("neg-1",),
            falsifiers=("falsifier-1",),
            provenance=("commit:abc",),
            limitations=("not independently replicated",),
            replication_state="AUTHOR_REPRODUCED",
        )
        self.assertEqual(pcro.validate(), [])
        self.assertFalse(pcro.to_dict()["scientific_pass"])

    def test_ultra_closure_reuses_minimal_coalition_owner(self):
        receipt = compile_ultra_closure(
            intent="close atlas evidence and identity debt",
            mission_id="M-R9-2",
            residuals=("EVIDENCE_GAP", "CANONICAL_IDENTITY_GAP"),
            context_ids=("jarvis-r8",),
            debt=DebtVector(evidence=2.0, complexity=1.0),
        )
        self.assertEqual(receipt.schema_version, "tristan-ultra-closure-r9")
        self.assertIn(receipt.regime["mode"], {"CLOSE", "REALITY", "VERIFY", "EXPLORE"})
        self.assertFalse(receipt.scientific_pass)
        self.assertFalse(receipt.authority_granted)


if __name__ == "__main__":
    unittest.main()
