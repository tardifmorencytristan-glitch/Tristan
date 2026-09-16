import unittest

from omega_omni_compiler.src.pdf_ir import (
    PDFBlockObservation,
    PDFDocumentObservation,
    PDFPageObservation,
    compile_pdf_observation,
)
from omega_omni_compiler.src.provenance import BoundingBox
from omega_omni_compiler.src.representation_ir import ConfidenceVector


SYNTH_HASH = "b" * 64
R3_SOURCE_HASH = "ac4c774094bbecc7f52bf5fb9d1e035595e7a79e483685ed0bea29db7aaee68a"


class PDFIRR4BTests(unittest.TestCase):
    def test_general_observation_compiles_to_document_page_block_graph(self):
        obs = PDFDocumentObservation(
            source_artifact_id="synthetic.pdf",
            source_sha256=SYNTH_HASH,
            parser="fixture-parser",
            parser_version="1.0",
            pages=(
                PDFPageObservation(
                    1,
                    100.0,
                    200.0,
                    blocks=(
                        PDFBlockObservation(
                            "h1", "HEADING", BoundingBox(10, 10, 90, 25), "Title", 0,
                            ConfidenceVector(text=1.0, structure=0.95, layout=1.0, provenance=1.0),
                        ),
                        PDFBlockObservation(
                            "p1", "PARAGRAPH", BoundingBox(10, 35, 90, 80), "Body", 1,
                            ConfidenceVector(text=0.99, structure=0.9, layout=1.0, provenance=1.0),
                        ),
                    ),
                ),
                PDFPageObservation(2, 100.0, 200.0),
            ),
        )
        pdfir = compile_pdf_observation(obs)
        self.assertEqual(pdfir.page_count, 2)
        self.assertIn("synthetic.pdf:page:1:block:h1", pdfir.graph.descendants("synthetic.pdf:document"))
        block = pdfir.graph.nodes["synthetic.pdf:page:1:block:p1"]
        self.assertEqual(block.metadata["reading_order"], 1)
        self.assertEqual(block.provenance[0].source_content_hash, SYNTH_HASH)

    def test_r3_real_source_hash_can_bind_readback_derived_observation(self):
        obs = PDFDocumentObservation(
            source_artifact_id="These_Tristan_R4_Living_Integrale_2026-09-15.pdf",
            source_sha256=R3_SOURCE_HASH,
            parser="r3-persisted-readback-adapter",
            parser_version="1",
            observation_status="PERSISTED_READBACK_DERIVED_NOT_AUTOMATIC_EXTRACTION",
            pages=(
                PDFPageObservation(
                    1,
                    1.0,
                    1.0,
                    blocks=(
                        PDFBlockObservation(
                            "inv-1",
                            "TEXT",
                            BoundingBox(0.0, 0.0, 1.0, 1.0),
                            "Generated != Verified",
                            0,
                            ConfidenceVector(text=1.0, provenance=1.0),
                        ),
                    ),
                ),
            ),
        )
        pdfir = compile_pdf_observation(obs)
        self.assertEqual(pdfir.source_sha256, R3_SOURCE_HASH)
        self.assertIn("NOT_AUTOMATIC_EXTRACTION", pdfir.observation_status)

    def test_out_of_bounds_block_fails_closed(self):
        obs = PDFDocumentObservation(
            "bad.pdf",
            SYNTH_HASH,
            "fixture",
            "1",
            pages=(
                PDFPageObservation(
                    1,
                    100,
                    100,
                    blocks=(PDFBlockObservation("x", "TEXT", BoundingBox(0, 0, 101, 10), "x", 0),),
                ),
            ),
        )
        with self.assertRaises(ValueError):
            compile_pdf_observation(obs)

    def test_duplicate_reading_order_fails_closed(self):
        page = PDFPageObservation(
            1,
            100,
            100,
            blocks=(
                PDFBlockObservation("a", "TEXT", BoundingBox(0, 0, 10, 10), "a", 0),
                PDFBlockObservation("b", "TEXT", BoundingBox(0, 20, 10, 30), "b", 0),
            ),
        )
        self.assertIn("PDFPageObservation reading_order must be unique within page", page.validate())

    def test_invalid_source_hash_fails_closed(self):
        obs = PDFDocumentObservation("bad.pdf", "not-a-hash", "fixture", "1", (PDFPageObservation(1, 1, 1),))
        self.assertTrue(any("64 hex" in e for e in obs.validate()))


if __name__ == "__main__":
    unittest.main()
