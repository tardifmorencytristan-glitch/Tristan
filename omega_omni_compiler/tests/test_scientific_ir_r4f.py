import unittest

from omega_omni_compiler.src.scientific_ir import (
    CitationIR,
    TableCellIR,
    TableIR,
    compare_quantities,
    equation_candidate,
    extract_explicit_quantities,
)


class ScientificIRR4FTests(unittest.TestCase):
    def test_explicit_quantity_preserves_decimal_lexeme_and_unit(self):
        quantities = extract_explicit_quantities("Vmax = 4.20 V", "page1:block3", ("prov:1",))
        self.assertEqual(len(quantities), 1)
        q = quantities[0]
        self.assertEqual(q.label, "Vmax")
        self.assertEqual(q.value_text, "4.20")
        self.assertEqual(str(q.decimal_value), "4.20")
        self.assertEqual(q.unit, "V")
        self.assertEqual(q.provenance_ids, ("prov:1",))

    def test_equation_candidate_is_typed_but_unverified(self):
        eq = equation_candidate("E = mc^2", "page1:eq1", ("prov:eq",))
        self.assertEqual(eq.lhs, "E")
        self.assertEqual(eq.rhs, "mc^2")
        self.assertEqual(eq.status, "CANDIDATE_UNVERIFIED")
        self.assertIn("E", eq.symbols)
        self.assertIn("mc", eq.symbols)
        self.assertEqual(eq.validate(), [])

    def test_equation_candidate_rejects_ambiguous_multiple_equals(self):
        with self.assertRaises(ValueError):
            equation_candidate("a=b=c", "node")

    def test_numeric_court_consensus_is_exact_decimal_and_unit(self):
        a = extract_explicit_quantities("Vmax = 4.20 V", "a")
        b = extract_explicit_quantities("Vmax = 4.200 V", "b")
        decision = compare_quantities({"parser-a": a, "parser-b": b}, "Vmax")
        self.assertEqual(decision.status, "CONSISTENT")
        self.assertEqual(decision.to_loss_tensor().entries[0].state, "PRESERVED")

    def test_numeric_value_disagreement_fails_closed(self):
        a = extract_explicit_quantities("Vmax = 4.20 V", "a")
        b = extract_explicit_quantities("Vmax = 420 V", "b")
        decision = compare_quantities({"parser-a": a, "parser-b": b}, "Vmax")
        self.assertEqual(decision.status, "HOLD_VALUE_DISAGREEMENT")
        loss = decision.to_loss_tensor().entries[0]
        self.assertEqual(loss.dimension, "NUMERIC")
        self.assertEqual(loss.state, "UNKNOWN")

    def test_unit_disagreement_fails_closed(self):
        a = extract_explicit_quantities("Vmax = 4.20 V", "a")
        b = extract_explicit_quantities("Vmax = 4.20 mV", "b")
        decision = compare_quantities({"parser-a": a, "parser-b": b}, "Vmax")
        self.assertEqual(decision.status, "HOLD_UNIT_DISAGREEMENT")
        self.assertEqual(decision.to_loss_tensor().entries[0].dimension, "UNITS")

    def test_missing_quantity_fails_closed(self):
        a = extract_explicit_quantities("Vmax = 4.20 V", "a")
        decision = compare_quantities({"parser-a": a, "parser-b": []}, "Vmax")
        self.assertEqual(decision.status, "HOLD_MISSING_QUANTITY")

    def test_table_ir_rejects_duplicate_coordinates(self):
        table = TableIR(
            id="t",
            source_node_id="table-node",
            cells=(
                TableCellIR(0, 0, "A", "cell-a"),
                TableCellIR(0, 0, "B", "cell-b"),
            ),
        )
        self.assertTrue(any("duplicate table coordinate" in error for error in table.validate()))

    def test_citation_resolution_does_not_imply_support(self):
        citation = CitationIR(
            id="c1",
            raw_marker="[12]",
            source_node_id="paragraph:1",
            resolved_source_id="doi:example",
            support_status="RESOLVED",
        )
        self.assertEqual(citation.validate(), [])
        self.assertNotEqual(citation.support_status, "SUPPORTS")

    def test_support_claim_requires_resolved_source(self):
        citation = CitationIR("c", "[1]", "p", support_status="SUPPORTS")
        self.assertTrue(any("resolved_source_id" in error for error in citation.validate()))


if __name__ == "__main__":
    unittest.main()
