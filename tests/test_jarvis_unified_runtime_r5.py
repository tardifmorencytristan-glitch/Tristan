import unittest
from pathlib import Path

from tristan.jarvis_runtime import compile_jarvis_runtime, select_domains
from tristan.registry import Registry


ROOT = Path(__file__).resolve().parents[1]


class JarvisUnifiedRuntimeR5Tests(unittest.TestCase):
    def test_domain_router_selects_relevant_domains(self):
        self.assertEqual(select_domains("formalize TFUGA"), ("tfuga",))
        self.assertEqual(select_domains("benchmark prime factorization"), ("prime",))
        self.assertEqual(select_domains("simulate LC fractal circuit"), ("lc_fractal",))
        self.assertEqual(select_domains("Gaia water and climate"), ("gaia",))

    def test_domain_router_can_select_multiple_domains(self):
        selected = select_domains("TFUGA for prime factorization and Gaia energy")
        self.assertEqual(set(selected), {"tfuga", "prime", "gaia"})

    def test_generic_intent_does_not_invent_domain_claims(self):
        self.assertEqual(select_domains("improve repository context routing"), ())

    def test_unified_runtime_fuses_r1_to_r6_without_promotion(self):
        reg = Registry.load(ROOT / "registry/objects.jsonl")
        receipt = compile_jarvis_runtime("simulate LC fractal circuit with CERN and JWST evidence", reg)
        self.assertEqual(receipt.schema_version, "jarvis-tristan-unified-runtime-r6")
        self.assertEqual(receipt.selected_domains, ("lc_fractal",))
        self.assertIn("lc_fractal", receipt.domain_cases)
        self.assertTrue(receipt.core_plan)
        self.assertTrue(receipt.closure_plan)
        self.assertTrue(receipt.r3_capabilities)
        self.assertIn("hepdata", receipt.scientific_source_plan["selected_sources"])
        self.assertIn("jwst_mast", receipt.scientific_source_plan["selected_sources"])
        self.assertIsNotNone(receipt.evidence_contract)
        self.assertEqual(receipt.domino_engine["status"], "AVAILABLE_NOT_EXECUTED")
        self.assertFalse(receipt.scientific_pass)
        self.assertFalse(receipt.authority_granted)
        self.assertIn("UnifiedRuntime != ScientificPASS", receipt.boundaries)

    def test_unified_runtime_uses_closure_next_mission(self):
        reg = Registry.load(ROOT / "registry/objects.jsonl")
        receipt = compile_jarvis_runtime("context regeneration evidence", reg)
        self.assertEqual(receipt.next_mission_id, receipt.closure_plan["next_mission_id"])


if __name__ == "__main__":
    unittest.main()
