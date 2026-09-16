import json
import unittest
from pathlib import Path

from omega_omni_compiler.src.scientific_renderer_adapter import REQUIRED_TOKENS, render_battery_packet


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT.parent / "omega_scientific_writing" / "fixtures" / "battery_r4_2_packet.json"
EXPECTED_TEX = ROOT.parent / "omega_scientific_writing" / "artifacts" / "r4_2" / "BATTERY_R4_2_EVIDENCE_BOUNDED.tex"
EXPECTED_TEX_SHA256 = "6f024984f9b1dac291f1c64243f2758783917712e2bbfd04abea76651d1a03f8"


class ScientificRendererAdapterR4GTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_exact_r4_2_renderer_is_reused_through_omni_adapter(self):
        tex, artifact = render_battery_packet(self.packet)
        expected = EXPECTED_TEX.read_text(encoding="utf-8")
        self.assertEqual(tex, expected)
        self.assertEqual(artifact.tex_sha256, EXPECTED_TEX_SHA256)
        self.assertEqual(set(artifact.required_tokens), REQUIRED_TOKENS)
        self.assertIn(self.packet["source_anchor"], tex)
        self.assertEqual(artifact.validate(), [])

    def test_renderer_adapter_does_not_self_promote_pdf_status(self):
        _, artifact = render_battery_packet(self.packet)
        self.assertEqual(artifact.status, "GENERATED_NOT_PDF_VERIFIED")

    def test_missing_source_anchor_fails_closed(self):
        packet = dict(self.packet)
        packet.pop("source_anchor")
        with self.assertRaises(ValueError):
            render_battery_packet(packet)

    def test_invalid_numeric_ordering_still_fails_in_reused_renderer(self):
        packet = json.loads(json.dumps(self.packet))
        packet["results"]["DFN_mean_shape_rmse_v"] = 1.0
        with self.assertRaises(ValueError):
            render_battery_packet(packet)


if __name__ == "__main__":
    unittest.main()
