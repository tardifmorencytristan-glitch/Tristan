import unittest

from tristan.domain_cases_r4 import default_r4_cases
from tristan.r4 import compile_r4_status


class JarvisR4DomainCaseTests(unittest.TestCase):
    def test_all_four_public_domain_cases_compile_without_promotion(self):
        status = compile_r4_status()
        self.assertEqual(status.status, "PROVISIONAL_ENGINEERING_R4")
        self.assertFalse(status.scientific_pass)
        self.assertEqual(set(status.cases), {"tfuga", "prime", "lc_fractal", "gaia"})
        for case in status.cases.values():
            self.assertEqual(case["status"], "PROVISIONAL_DOMAIN_CASE")
            self.assertFalse(case["scientific_pass"])
            self.assertFalse(case["errors"])

    def test_claim_templates_never_start_above_testable(self):
        allowed = {"UNKNOWN", "ACTIVE", "FORMALIZED", "TESTABLE"}
        for case in default_r4_cases().values():
            for claim in case.claims:
                self.assertIn(claim.status, allowed)

    def test_tfuga_case_requires_formalization_and_validity_domain(self):
        case = default_r4_cases()["tfuga"]
        claim = case.claims[0]
        self.assertIn("typed", claim.statement.lower())
        self.assertTrue(claim.validity_domain)
        self.assertIn("formal operator", claim.witness.lower())
        self.assertIn("DomainCase != TheoryValidation", case.boundaries)

    def test_prime_case_blocks_speed_before_correctness(self):
        case = default_r4_cases()["prime"]
        self.assertIn("exact correctness", case.claims[0].statement.lower())
        self.assertEqual(case.missions[1].dependencies, ("PRIME-M1",))
        self.assertIn("NO_ACTION is admissible", case.boundaries)

    def test_lc_case_is_simulation_only_and_control_bounded(self):
        case = default_r4_cases()["lc_fractal"]
        claim = case.claims[0]
        self.assertIn("control", claim.statement.lower())
        self.assertIn("simulation-only", claim.assumptions[0])
        self.assertIn("Simulation != Measurement", case.boundaries)
        self.assertEqual(case.missions[1].dependencies, ("LCF-M1",))

    def test_gaia_case_keeps_scenario_separate_from_measurement(self):
        case = default_r4_cases()["gaia"]
        self.assertIn("scenario", case.claims[0].statement.lower())
        self.assertIn("SimulatedImpact != MeasuredImpact", case.boundaries)
        self.assertEqual(case.missions[1].dependencies, ("GAIA-M1",))

    def test_r4_explicitly_refuses_private_corpus_import(self):
        status = compile_r4_status()
        self.assertIn("PublicDomainCase != PrivateCorpusImport", status.boundaries)


if __name__ == "__main__":
    unittest.main()
