import unittest

from tristan.jarvis_runtime import select_domains
from tristan.tesla_omega.extract import PATENT_SEEDS, compile_extraction_queue
from tristan.tesla_omega.runner import compile_tesla_omega_r02
from tristan.tesla_omega.search import (
    search_tree_topologies,
    tree_from_prufer,
    unique_labeled_trees,
    unique_unlabeled_trees,
)
from tristan.tesla_omega.spectral import (
    adjacency_eigenvalues,
    coupled_mode_frequencies_hz,
    modal_metrics,
)
from tristan.tesla_omega.topology import chain, star


class TeslaOmegaR02Tests(unittest.TestCase):
    def test_chain_adjacency_spectrum_is_symmetric(self):
        eig = adjacency_eigenvalues(chain(4))
        self.assertAlmostEqual(eig[0], -eig[-1], places=10)
        self.assertAlmostEqual(eig[1], -eig[-2], places=10)

    def test_zero_coupling_collapses_modes(self):
        modes = coupled_mode_frequencies_hz(chain(4), 10e-6, 100e-9, 0.0)
        self.assertAlmostEqual(min(modes), max(modes), places=9)

    def test_star_and_chain_differ_at_equal_budget(self):
        a = modal_metrics(coupled_mode_frequencies_hz(
            chain(5), 10e-6, 100e-9, 0.08
        ))
        b = modal_metrics(coupled_mode_frequencies_hz(
            star(5), 10e-6, 100e-9, 0.08
        ))
        self.assertNotAlmostEqual(
            a["modal_span_hz"], b["modal_span_hz"], places=6
        )

    def test_prufer_tree_has_n_minus_one_edges(self):
        tree = tree_from_prufer((0, 1, 2))
        self.assertEqual(len(tree.nodes), 5)
        self.assertEqual(len(tree.edges), 4)

    def test_tree_search_is_bounded_deduplicated_and_deterministic(self):
        result = search_tree_topologies(
            6, 10e-6, 100e-9, 0.08, limit=6
        )
        self.assertEqual(len(result), 6)
        self.assertGreaterEqual(
            result[0]["screening_score"], result[-1]["screening_score"]
        )
        self.assertEqual(
            len({r["unlabeled_signature"] for r in result}), 6
        )

    def test_cayley_count_for_five_labeled_trees(self):
        self.assertEqual(len(unique_labeled_trees(5)), 5 ** 3)

    def test_unlabeled_tree_counts(self):
        self.assertEqual(len(unique_unlabeled_trees(5)), 3)
        self.assertEqual(len(unique_unlabeled_trees(6)), 6)

    def test_extraction_queue_blocks_promotion(self):
        queue = compile_extraction_queue()
        self.assertEqual(len(PATENT_SEEDS), 3)
        self.assertTrue(queue)
        self.assertTrue(all(item["promotion_blocked"] for item in queue))

    def test_runner_is_bounded_and_non_authoritative(self):
        receipt = compile_tesla_omega_r02()
        self.assertEqual(receipt["status"], "COMPUTATIONAL_SCREENING_ONLY")
        self.assertFalse(receipt["authority_granted"])
        self.assertFalse(receipt["novelty_claimed"])
        self.assertEqual(
            receipt["model"]["edges"], receipt["model"]["nodes"] - 1
        )
        self.assertIn(
            "BestInBoundedSearch != Novelty", receipt["boundaries"]
        )

    def test_tesla_routes_to_existing_lc_domain(self):
        self.assertEqual(select_domains("reconstruct Tesla resonator"), ("lc_fractal",))


if __name__ == "__main__":
    unittest.main()
