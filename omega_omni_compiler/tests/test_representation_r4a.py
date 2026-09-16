import unittest

from omega_omni_compiler.src.provenance import BoundingBox, ProvenanceAnchor
from omega_omni_compiler.src.representation_ir import (
    ConfidenceVector,
    RepresentationGraph,
    RepresentationNode,
    RepresentationRelation,
)


HASH = "a" * 64


def anchor(page: int = 1) -> ProvenanceAnchor:
    return ProvenanceAnchor(
        source_artifact_id="source-pdf",
        source_content_hash=HASH,
        extractor="native-test",
        extractor_version="1.0",
        page=page,
        bbox=BoundingBox(0, 0, 10, 10),
        confidence=0.9,
    )


class RepresentationKernelR4ATests(unittest.TestCase):
    def test_atomic_provenance_is_hash_bound_and_geometric(self):
        p = anchor()
        self.assertEqual(p.validate(), [])
        self.assertEqual(p.bbox.width, 10)
        self.assertEqual(p.bbox.height, 10)

    def test_provenance_rejects_non_hex_hash_and_bad_page(self):
        p = ProvenanceAnchor("x", "z" * 64, "e", "1", page=0)
        errors = p.validate()
        self.assertTrue(any("64 hex" in e for e in errors))
        self.assertTrue(any("page" in e for e in errors))

    def test_confidence_is_vector_not_single_score(self):
        c = ConfidenceVector(text=0.99, math=0.61, provenance=1.0)
        self.assertEqual(c.validate(), [])
        self.assertEqual(c.observed_axes(), {"text": 0.99, "math": 0.61, "provenance": 1.0})

    def test_node_fails_closed_without_provenance(self):
        node = RepresentationNode("n", "TEXT", content="hello")
        self.assertIn("RepresentationNode.provenance required", node.validate())

    def test_nary_relation_and_graph_closure(self):
        g = RepresentationGraph()
        for node in [
            RepresentationNode("page", "PAGE", provenance=[anchor()]),
            RepresentationNode("eq", "EQUATION", content="E=mc^2", provenance=[anchor()]),
            RepresentationNode("s1", "SYMBOL", content="E", provenance=[anchor()]),
            RepresentationNode("s2", "SYMBOL", content="m", provenance=[anchor()]),
        ]:
            g.add_node(node)
        g.add_relation(RepresentationRelation("r1", "CONTAINS", ("page",), ("eq",)))
        g.add_relation(RepresentationRelation("r2", "DEFINES", ("eq",), ("s1", "s2")))
        self.assertEqual(g.descendants("page"), ["eq", "s1", "s2"])
        self.assertEqual(g.ancestors("s1"), ["eq", "page"])
        self.assertEqual(g.relations["r2"].target_ids, ("s1", "s2"))

    def test_relation_rejects_missing_nodes(self):
        g = RepresentationGraph()
        g.add_node(RepresentationNode("a", "TEXT", provenance=[anchor()]))
        with self.assertRaises(ValueError):
            g.add_relation(RepresentationRelation("r", "REFERENCES", ("a",), ("missing",)))


if __name__ == "__main__":
    unittest.main()
