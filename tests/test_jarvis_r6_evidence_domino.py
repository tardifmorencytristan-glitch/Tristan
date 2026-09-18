import unittest

from tristan.domino_engine import DominoEdge, DominoEvent, DominoNode, critical_test_priority, propagation_cone
from tristan.evidence_foundry import blank_evidence_receipt, compile_evidence_contract
from tristan.scientific_connectors import build_source_plan, select_scientific_sources


class JarvisR6EvidenceDominoTests(unittest.TestCase):
    def test_source_router_selects_multiple_scientific_archives(self):
        selected = select_scientific_sources("Use CERN, JWST, Gaia astrometry, Planck and Sentinel satellite data")
        self.assertIn("hepdata", selected)
        self.assertIn("cern_open_data", selected)
        self.assertIn("jwst_mast", selected)
        self.assertIn("gaia_archive", selected)
        self.assertIn("planck_legacy", selected)
        self.assertIn("copernicus", selected)

    def test_source_plan_is_planning_only(self):
        plan = build_source_plan("CERN JWST")
        self.assertFalse(plan["network_executed"])
        self.assertEqual(plan["status"], "READY_FOR_BOUNDED_RETRIEVAL")
        self.assertIn("SourceSelection != DataRetrieved", plan["boundaries"])

    def test_evidence_contract_fails_closed_to_inconclusive(self):
        contract = compile_evidence_contract(
            claim_id="C1",
            datasets=("hepdata", "jwst_mast"),
            observables=("observable-x",),
        )
        self.assertEqual(contract.validate(), [])
        receipt = blank_evidence_receipt(contract)
        self.assertEqual(receipt.status, "INCONCLUSIVE")
        self.assertFalse(receipt.data_retrieved)
        self.assertFalse(receipt.analysis_executed)
        self.assertEqual(receipt.validate(), [])

    def test_domino_firewall_blocks_weak_edge_and_propagates_strong_edge(self):
        nodes = (
            DominoNode("claim", "claim", "claim"),
            DominoNode("prediction", "prediction", "prediction"),
            DominoNode("weak", "claim", "weak dependent"),
        )
        edges = (
            DominoEdge("claim", "prediction", "depends", 0.9, 0.9, 0.9, 0.9),
            DominoEdge("claim", "weak", "depends", 0.9, 0.2, 0.2, 0.2),
        )
        event = DominoEvent("claim", "falsification", -1.0, "bounded counterevidence")
        impacts = propagation_cone(nodes, edges, event, threshold=0.15)
        ids = {impact.node_id for impact in impacts}
        self.assertIn("prediction", ids)
        self.assertNotIn("weak", ids)

    def test_domino_rejects_cycles_and_critical_test_metric_is_bounded(self):
        nodes = (
            DominoNode("a", "claim", "a"),
            DominoNode("b", "claim", "b"),
        )
        edges = (
            DominoEdge("a", "b", "depends", 1, 1, 1, 1),
            DominoEdge("b", "a", "depends", 1, 1, 1, 1),
        )
        impacts = propagation_cone(nodes, edges, DominoEvent("a", "prediction", 1, "test"), max_depth=8)
        self.assertEqual([impact.node_id for impact in impacts], ["b"])
        self.assertAlmostEqual(
            critical_test_priority(
                expected_information_gain=4,
                independence=0.5,
                reproducibility=0.5,
                cost=2,
            ),
            0.5,
        )


if __name__ == "__main__":
    unittest.main()
