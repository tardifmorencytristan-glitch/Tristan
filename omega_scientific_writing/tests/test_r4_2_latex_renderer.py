import json
import unittest
from pathlib import Path

from omega_scientific_writing.src.latex_renderer import render_battery_manuscript, extract_required_tokens

ROOT = Path(__file__).resolve().parents[1]


class R42LatexRendererTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = json.loads((ROOT / "fixtures" / "battery_r4_2_packet.json").read_text(encoding="utf-8"))

    def test_render_preserves_exact_numeric_results(self):
        tex = render_battery_manuscript(self.packet)
        self.assertIn("0.07225", tex)
        self.assertIn("0.17085", tex)
        self.assertIn("0.25499", tex)
        self.assertIn("38--45\\%", tex)

    def test_render_preserves_scope_and_limits(self):
        tex = render_battery_manuscript(self.packet)
        self.assertIn("frozen three-cell first-cycle CALCE comparison", tex)
        self.assertIn("not evidence of universal model superiority", tex)
        self.assertIn("not an independent replication or ScientificPASS", tex)

    def test_exact_source_anchor_is_embedded(self):
        tex = render_battery_manuscript(self.packet)
        self.assertIn("d759105682704f037f21fef8f6d396b4d0408f3a", tex)
        self.assertIn("CALCE\\_ZERO\\_FIT\\_TRANSFER\\_R0\\_4.json", tex)

    def test_readback_contract_tokens_present(self):
        tex = render_battery_manuscript(self.packet)
        tokens = extract_required_tokens(tex)
        self.assertEqual({"CALCE", "DFN", "SPM", "SPMe", "ScientificPASS", "universal superiority", "capacity mismatch"}, tokens)

    def test_fails_if_ordering_is_mutated(self):
        bad = json.loads(json.dumps(self.packet))
        bad["results"]["DFN_mean_shape_rmse_v"] = 0.5
        with self.assertRaises(ValueError):
            render_battery_manuscript(bad)

    def test_fails_if_limitations_are_removed(self):
        bad = json.loads(json.dumps(self.packet))
        bad["limitations"] = []
        with self.assertRaises(ValueError):
            render_battery_manuscript(bad)


if __name__ == "__main__":
    unittest.main()
