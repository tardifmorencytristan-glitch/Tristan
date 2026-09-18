import unittest

from tristan.architecture_mutation import MutationCandidate, select_mutation
from tristan.experiment_designer import ExperimentCandidate, rank_experiments
from tristan.jarvis_ir import TransformationIR
from tristan.meta_learning import StrategyOutcome, learn_strategy_preferences
from tristan.tool_discovery import ToolCandidate, select_tool
from tristan.world_model import (
    TransitionHypothesis,
    WorldState,
    compare_prediction_to_observation,
    predict_transition,
)


class IntelligenceR05Tests(unittest.TestCase):
    def test_meta_learning_requires_contextual_evidence(self):
        receipt = learn_strategy_preferences(
            (
                StrategyOutcome("A", ("physics",), 0.9, True, 0.1),
            ),
            target_context=("chemistry",),
            min_samples=1,
        )
        self.assertEqual(receipt.status, "HOLD_INSUFFICIENT_CONTEXTUAL_EVIDENCE")
        self.assertIsNone(receipt.recommended_strategy)

    def test_meta_learning_recommends_conservatively(self):
        receipt = learn_strategy_preferences(
            (
                StrategyOutcome("A", ("physics", "lc"), 0.9, True, 0.1),
                StrategyOutcome("A", ("physics", "lc"), 0.8, True, 0.1),
                StrategyOutcome("B", ("physics", "lc"), 0.95, True, 0.3),
                StrategyOutcome("B", ("physics", "lc"), 0.95, True, 0.3),
            ),
            target_context=("physics", "lc"),
        )
        self.assertEqual(receipt.status, "CONTEXTUAL_PREFERENCE_ONLY")
        self.assertEqual(receipt.recommended_strategy, "A")
        self.assertFalse(receipt.authority_granted)

    def test_world_model_prediction_and_residual(self):
        state = WorldState(
            "s0",
            (("x", 1.0), ("y", 2.0)),
            ("measurement:0",),
        )
        hypothesis = TransitionHypothesis(
            "h1",
            (("x", 1.0), ("y", -1.0)),
            ("linear-step",),
            0.1,
        )
        prediction = predict_transition(state, hypothesis)
        observed = WorldState(
            "s1",
            (("x", 2.2), ("y", 1.1)),
            ("measurement:1",),
        )
        residual = compare_prediction_to_observation(prediction, observed)
        self.assertEqual(prediction.status, "MODEL_PREDICTION_ONLY")
        self.assertEqual(residual.status, "RESIDUAL_MEASURED")
        self.assertGreater(residual.mean_absolute_residual, 0.0)
        self.assertFalse(residual.scientific_pass)

    def test_experiment_designer_can_choose_no_action(self):
        receipt = rank_experiments(
            (
                ExperimentCandidate("e1", 0.1, 10.0, 5.0, 5.0, 0.5, 0.5),
            ),
            minimum_utility=1.0,
        )
        self.assertEqual(receipt.status, "NO_ACTION")
        self.assertIsNone(receipt.selected_experiment)

    def test_experiment_designer_selects_high_information_gain(self):
        receipt = rank_experiments(
            (
                ExperimentCandidate("cheap", 0.5, 1.0, 0.1, 1.0, 0.9, 0.9),
                ExperimentCandidate("expensive", 0.8, 20.0, 5.0, 20.0, 0.9, 0.9),
            )
        )
        self.assertEqual(receipt.selected_experiment, "cheap")
        self.assertFalse(receipt.authority_granted)

    def test_tool_discovery_requires_capability_coverage(self):
        receipt = select_tool(
            ("search", "model"),
            (
                ToolCandidate("t1", ("search",), ("e1",), 0.9, 0.1, 0.0),
            ),
        )
        self.assertEqual(receipt.status, "NO_TOOL_FOUND")
        self.assertIsNone(receipt.selected_tool)

    def test_tool_discovery_selects_evidence_bound_candidate(self):
        receipt = select_tool(
            ("search",),
            (
                ToolCandidate("t1", ("search",), ("e1",), 0.7, 0.2, 0.0),
                ToolCandidate("t2", ("search",), ("e2",), 0.9, 0.1, 1.0),
            ),
        )
        self.assertEqual(receipt.selected_tool, "t2")
        self.assertFalse(receipt.authority_granted)

    def test_architecture_mutation_requires_positive_net_gain(self):
        transformation = TransformationIR(
            transformation_id="tr1",
            operator="replace-router",
            source_id="router-v1",
            target_kind="router-v2",
            expected_gain=0.0,
            cost=0.0,
            risk=0.1,
            evidence_debt=0.1,
            rollback="restore-router-v1",
        )
        receipt = select_mutation(
            (
                MutationCandidate(
                    "m1",
                    transformation,
                    ("test-router",),
                    baseline_score=0.8,
                    expected_score=0.81,
                    complexity_delta=0.1,
                    evidence_gain=0.0,
                ),
            )
        )
        self.assertEqual(receipt.status, "NO_ACTION")
        self.assertIsNone(receipt.mutation_id)

    def test_architecture_mutation_requires_retest_and_rollback(self):
        transformation = TransformationIR(
            transformation_id="tr2",
            operator="add-memory-gate",
            source_id="router-v1",
            target_kind="router-v2",
            expected_gain=0.0,
            cost=0.0,
            risk=0.05,
            evidence_debt=0.02,
            rollback="restore-router-v1",
        )
        receipt = select_mutation(
            (
                MutationCandidate(
                    "m2",
                    transformation,
                    ("test-router", "test-memory"),
                    baseline_score=0.6,
                    expected_score=0.9,
                    complexity_delta=0.05,
                    evidence_gain=0.1,
                ),
            )
        )
        self.assertEqual(receipt.status, "CANDIDATE_MUTATION_REQUIRES_RETEST")
        self.assertFalse(receipt.executable)
        self.assertFalse(receipt.promotion_authority)
        self.assertEqual(receipt.rollback, "restore-router-v1")


if __name__ == "__main__":
    unittest.main()
