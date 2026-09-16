import importlib.util
from hashlib import sha256
from pathlib import Path
import shutil
import unittest

from omega_omni_compiler.src.parser_adapters import (
    PopplerBBoxAdapter,
    PyPDFAdapter,
    compare_texts,
    comparison_to_loss_tensor,
    invariant_presence,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "r4d_parser_fixture.pdf"
FIXTURE_SHA256 = "cc45d6d9511f68640442c736d05ccd625f34b634cd64115d34c3cf514d4890a4"
EXPECTED = ("Omni R4D Parser Court", "Generated != Verified", "Vmax = 4.20 V", "E = mc^2")
DEPS = importlib.util.find_spec("pypdf") is not None and shutil.which("pdftotext") is not None and shutil.which("pdfinfo") is not None


@unittest.skipUnless(DEPS, "R4D optional parser dependencies unavailable")
class ParserAdaptersR4DTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf_bytes = FIXTURE.read_bytes()
        cls.pypdf = PyPDFAdapter().parse_bytes(cls.pdf_bytes, "r4d-fixture.pdf", pages=(1,))
        cls.poppler = PopplerBBoxAdapter().parse_bytes(cls.pdf_bytes, "r4d-fixture.pdf", pages=(1,))

    def test_fixture_bytes_are_exact(self):
        self.assertEqual(sha256(self.pdf_bytes).hexdigest(), FIXTURE_SHA256)

    def test_two_real_parsers_execute_on_same_pdf_bytes(self):
        self.assertEqual(len(self.pypdf.observation.pages), 1)
        self.assertEqual(len(self.poppler.observation.pages), 1)
        self.assertEqual(self.pypdf.observation.source_sha256, FIXTURE_SHA256)
        self.assertEqual(self.poppler.observation.source_sha256, FIXTURE_SHA256)
        self.assertTrue(self.pypdf.parser_version)
        self.assertTrue(self.poppler.parser_version)

    def test_expected_invariants_are_present_in_both_outputs(self):
        self.assertTrue(all(invariant_presence(self.pypdf, EXPECTED).values()))
        self.assertTrue(all(invariant_presence(self.poppler, EXPECTED).values()))

    def test_fixture_parser_outputs_agree_after_normalization(self):
        comparison = compare_texts(self.pypdf.parser, self.pypdf.text, self.poppler.parser, self.poppler.text)
        self.assertTrue(comparison.exact_normalized_text_equal)
        self.assertEqual(comparison.sequence_similarity, 1.0)
        self.assertEqual(comparison.token_set_jaccard, 1.0)
        tensor = comparison_to_loss_tensor(comparison)
        self.assertEqual(tensor.entries[0].state, "PRESERVED")
        self.assertEqual(tensor.entries[0].severity, 0.0)

    def test_poppler_reports_real_block_geometry_while_pypdf_marks_page_envelope(self):
        poppler_blocks = self.poppler.observation.pages[0].blocks
        self.assertGreater(len(poppler_blocks), 1)
        self.assertTrue(all(dict(b.metadata)["geometry_semantics"] == "POPPLER_REPORTED_BBOX" for b in poppler_blocks))
        pypdf_block = self.pypdf.observation.pages[0].blocks[0]
        self.assertEqual(dict(pypdf_block.metadata)["geometry_semantics"], "PAGE_ENVELOPE_NOT_TEXT_BBOX")

    def test_disagreement_is_unknown_not_silently_declared_loss_or_truth(self):
        comparison = compare_texts("a", "Vmax = 4.20 V", "b", "Vmax = 420 V")
        self.assertFalse(comparison.exact_normalized_text_equal)
        self.assertLess(comparison.sequence_similarity, 1.0)
        tensor = comparison_to_loss_tensor(comparison)
        self.assertEqual(tensor.entries[0].state, "UNKNOWN")
        self.assertGreater(tensor.entries[0].severity, 0.0)
        self.assertIn("no independent adjudicator", tensor.entries[0].cause)


if __name__ == "__main__":
    unittest.main()
