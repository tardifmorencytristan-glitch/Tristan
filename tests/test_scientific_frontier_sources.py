import unittest

from tristan.scientific_connectors import build_source_plan, source_catalog


class ScientificFrontierSourceTests(unittest.TestCase):
    def test_desi_dark_energy_intent(self):
        plan = build_source_plan("DESI BAO dark energy large-scale structure")
        self.assertIn("desi_data", plan["selected_sources"])
        self.assertFalse(plan["network_executed"])

    def test_gwosc_gravitational_wave_intent(self):
        plan = build_source_plan("GWOSC LIGO gravitational-wave strain data")
        self.assertIn("gwosc", plan["selected_sources"])
        source = source_catalog()["gwosc"]
        self.assertEqual(source["base_url"], "https://gwosc.org/api/v2/")

    def test_multi_instrument_includes_new_frontier_sources(self):
        plan = build_source_plan("multi-instrument physics validation")
        self.assertIn("desi_data", plan["selected_sources"])
        self.assertIn("gwosc", plan["selected_sources"])
        self.assertIn("RetrievalMethodMustBeCurrent", plan["boundaries"])


if __name__ == "__main__":
    unittest.main()
