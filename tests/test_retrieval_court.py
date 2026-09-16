import unittest
from pathlib import Path

from tristan.registry import Registry
from tristan.retrieval_court import (
    normalized_terms,
    rank_current,
    rank_tfidf_full,
    run_court,
)

ROOT = Path(__file__).resolve().parents[1]


class RetrievalCourtTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = Registry.load(ROOT / "registry" / "objects.jsonl")

    def test_structured_token_normalization(self) -> None:
        self.assertEqual(
            normalized_terms("right_to_lose RepositoryEngineeringPASS"),
            ("right", "to", "lose", "repository", "engineering", "pass"),
        )

    def test_full_text_finds_negative_memory(self) -> None:
        ranking = rank_tfidf_full(
            "setuptools build meta failure negative memory qualification court",
            self.registry,
        )
        self.assertEqual(ranking[0], "public-kstar-kernel-r0-1")

    def test_current_baseline_is_preserved(self) -> None:
        ranking = rank_current(
            "minimum sufficient memory context routing index", self.registry
        )
        self.assertEqual(ranking[0], "context-registry-v0-4")

    def test_court_is_shadow_only(self) -> None:
        result = run_court(
            ROOT / "registry" / "objects.jsonl",
            ROOT / "benchmarks" / "context_retrieval_r0_2.json",
        )
        self.assertEqual(result["counts"]["queries"], 16)
        self.assertFalse(result["runtime_mutation_authorized"])
        self.assertIn(
            result["decision"],
            {
                "NO_ACTION",
                "TIE_KEEP_RUNTIME_UNCHANGED_SHADOW_CHALLENGERS",
                "SHADOW_CANDIDATE_ONLY_NEEDS_LARGER_INDEPENDENT_COURT",
            },
        )
        self.assertGreaterEqual(
            result["results"]["CURRENT_R0_1"]["holdout"]["mrr"], 0.0
        )
        self.assertIn("TFIDF_FULL_NORMALIZED", result["results"])


if __name__ == "__main__":
    unittest.main()
