import unittest

from causal_effect_r205 import (
    OutcomeContract,
    causal_attribution,
    feedback_decision,
    verify_outcome_contract,
)


class CausalEffectR205Tests(unittest.TestCase):
    def contract(self):
        return OutcomeContract(
            outcome_id="latency-improvement",
            metric="latency_ms",
            direction="decrease",
            minimum_delta=2.0,
            baseline_ref="baseline.json",
            observation_ref="observation.json",
        )

    def test_outcome_contract_passes_only_with_fresh_independent_observation(self):
        out = verify_outcome_contract(
            self.contract(),
            {
                "baseline": 10.0,
                "observed": 7.5,
                "fresh": True,
                "independent": True,
                "outcome_observed": True,
            },
        )
        self.assertEqual(out["status"], "OUTCOME_CONTRACT_PASS")

    def test_stale_or_nonindependent_outcome_holds(self):
        stale = verify_outcome_contract(
            self.contract(),
            {
                "baseline": 10.0,
                "observed": 7.0,
                "fresh": False,
                "independent": True,
                "outcome_observed": True,
            },
        )
        nonind = verify_outcome_contract(
            self.contract(),
            {
                "baseline": 10.0,
                "observed": 7.0,
                "fresh": True,
                "independent": False,
                "outcome_observed": True,
            },
        )
        self.assertEqual(stale["status"], "HOLD_OUTCOME_CONTRACT")
        self.assertEqual(nonind["status"], "HOLD_OUTCOME_CONTRACT")

    def test_causality_requires_control_and_no_confounds(self):
        outcome = verify_outcome_contract(
            self.contract(),
            {
                "baseline": 10.0,
                "observed": 7.0,
                "fresh": True,
                "independent": True,
                "outcome_observed": True,
            },
        )
        without_control = causal_attribution(
            execution_verified=True,
            local_effect_verified=True,
            outcome_contract=outcome,
            controls=[],
            confounds=[],
        )
        with_confound = causal_attribution(
            execution_verified=True,
            local_effect_verified=True,
            outcome_contract=outcome,
            controls=[{"independent": True, "supports_intervention": True}],
            confounds=["concurrent_workload_change"],
        )
        supported = causal_attribution(
            execution_verified=True,
            local_effect_verified=True,
            outcome_contract=outcome,
            controls=[{"independent": True, "supports_intervention": True}],
            confounds=[],
        )
        self.assertEqual(without_control["status"], "HOLD_CAUSAL_ATTRIBUTION")
        self.assertEqual(with_confound["status"], "HOLD_CAUSAL_ATTRIBUTION")
        self.assertEqual(supported["status"], "CAUSAL_EFFECT_SUPPORTED")

    def test_unverified_causal_gain_never_triggers_reauction(self):
        out = feedback_decision(
            causal_receipt={"causal_effect_supported": False},
            current_node="A",
            candidate_nodes=[{"node":"B","capabilities":["x"],"verified_gain_per_cost":99}],
            required_capabilities=["x"],
        )
        self.assertEqual(out["status"], "NO_ACTION_UNVERIFIED_CAUSAL_GAIN")
        self.assertEqual(out["next_node"], "A")

    def test_verified_causal_gain_can_reauction(self):
        out = feedback_decision(
            causal_receipt={"causal_effect_supported": True},
            current_node="A",
            candidate_nodes=[
                {"node":"A","capabilities":["x"],"verified_gain_per_cost":1.0},
                {"node":"B","capabilities":["x"],"verified_gain_per_cost":2.0},
            ],
            required_capabilities=["x"],
        )
        self.assertEqual(out["status"], "REAUCTION")
        self.assertEqual(out["next_node"], "B")


if __name__ == "__main__":
    unittest.main()
