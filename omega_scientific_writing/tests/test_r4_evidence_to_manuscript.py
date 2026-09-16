import unittest

from omega_scientific_writing.src.argument_graph import build_argument_graph
from omega_scientific_writing.src.claim_writer import bounded_claim
from omega_scientific_writing.src.citation_bindings import validate_bindings
from omega_scientific_writing.src.manuscript_compiler import compile_manuscript
from omega_scientific_writing.src.reviewer_council import review


class R4EvidenceToManuscriptTests(unittest.TestCase):
    def test_language_ceiling_preserves_scope(self):
        out = bounded_claim({"id":"C1","statement":"method A exceeds baseline B","status":"OBSERVED","scope":"the frozen internal benchmark"})
        self.assertIn("the frozen internal benchmark", out["text"])
        self.assertTrue(out["no_globalization"])
        self.assertNotIn("universally", out["text"].lower())

    def test_argument_graph_flags_unsupported_result(self):
        graph = build_argument_graph([{"id":"R","role":"RESULT"}], [])
        self.assertTrue(any(x["code"] == "ARGUMENT_UNSUPPORTED" for x in graph["findings"]))

    def test_non_entailing_citation_fails_closed(self):
        findings = validate_bindings(
            [{"id":"C1"}], [{"id":"S1"}],
            [{"id":"B1","claim_id":"C1","source_id":"S1","support_type":"NOT_ENTAILING"}],
        )
        self.assertTrue(any(x["code"] == "CITATION_DOES_NOT_ENTAIL" and x["severity"] == "ERROR" for x in findings))

    def test_reviewer_blocks_unclosed_novelty(self):
        result = review({"claims":[{"id":"C1","statement":"a novel universal method","status":"PROPOSED"}]})
        self.assertEqual("HOLD", result["verdict"])
        self.assertTrue(any(x["code"] == "STRONG_LANGUAGE_PRIOR_ART_OPEN" for x in result["findings"]))

    def test_battery_like_bounded_packet_can_compile(self):
        doc = {
            "claims":[{"id":"C1","statement":"DFN has lower voltage-shape RMSE than SPM in the stated comparison","status":"MEASURED","scope":"the frozen CALCE comparison","evidence_ids":["E1"],"prior_art_closed":False}],
            "sources":[{"id":"S1"}],
            "citation_bindings":[{"id":"B1","claim_id":"C1","source_id":"S1","support_type":"METHOD"}],
            "argument_nodes":[{"id":"E1","role":"EVIDENCE"},{"id":"R1","role":"RESULT"}],
            "argument_edges":[{"source":"E1","target":"R1","relation":"SUPPORTS"}],
        }
        out = compile_manuscript(doc)
        self.assertEqual("PASS", out["verdict"])
        self.assertIn("CALCE", out["paragraphs"][0]["text"])

    def test_causal_overclaim_is_held(self):
        out = compile_manuscript({
            "claims":[{"id":"C1","statement":"architecture A causes higher accuracy","status":"OBSERVED","scope":"one benchmark","evidence_ids":["E1"]}],
            "sources":[],"citation_bindings":[],"argument_nodes":[],"argument_edges":[]
        })
        self.assertEqual("HOLD", out["verdict"])
        self.assertTrue(any(x["code"] == "CAUSAL_LANGUAGE_UNSUPPORTED" for x in out["reviewer_council"]["findings"]))


if __name__ == "__main__":
    unittest.main()
