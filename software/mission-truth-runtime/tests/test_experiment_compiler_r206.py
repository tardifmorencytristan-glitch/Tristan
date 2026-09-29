import unittest

from experiment_compiler_r206 import (
    ExperimentNeed,
    analyze_matched_experiment,
    compile_matched_experiment,
)


class ExperimentCompilerR206Tests(unittest.TestCase):
    def need(self):
        return ExperimentNeed(
            residual_id="latency-residual",
            metric="latency_ms",
            direction="decrease",
            minimum_effect=2.0,
            intervention="resource-aware-routing",
            baseline="current-routing",
        )

    def test_insufficient_budget_holds(self):
        out = compile_matched_experiment(
            self.need(),
            available_controls=[{"control_id":"c","independent":True,"comparable":True,"distance":0}],
            candidate_confounds=[],
            budget={"max_runs":1,"max_seconds":10},
        )
        self.assertEqual(out["status"], "HOLD_INSUFFICIENT_BUDGET")

    def test_missing_control_holds(self):
        out = compile_matched_experiment(
            self.need(),
            available_controls=[],
            candidate_confounds=[],
            budget={"max_runs":4,"max_seconds":10},
        )
        self.assertEqual(out["status"], "HOLD_NO_MATCHED_CONTROL")

    def test_nearest_independent_control_is_selected(self):
        out = compile_matched_experiment(
            self.need(),
            available_controls=[
                {"control_id":"far","independent":True,"comparable":True,"distance":2},
                {"control_id":"near","independent":True,"comparable":True,"distance":0.2},
            ],
            candidate_confounds=["background-load"],
            budget={"max_runs":6,"max_seconds":60},
        )
        self.assertEqual(out["status"], "EXPERIMENT_COMPILED")
        self.assertEqual(out["control_id"], "near")
        self.assertFalse(out["authority_granted"])
        self.assertFalse(out["external_side_effects"])

    def test_clean_matched_effect_can_support_intervention(self):
        plan = compile_matched_experiment(
            self.need(),
            available_controls=[{"control_id":"c","independent":True,"comparable":True,"distance":0}],
            candidate_confounds=[],
            budget={"max_runs":4,"max_seconds":30},
        )
        measurements=[
            {"arm":"control","value":10.0,"valid":True},
            {"arm":"intervention","value":7.5,"valid":True},
            {"arm":"control","value":10.5,"valid":True},
            {"arm":"intervention","value":7.0,"valid":True},
        ]
        out = analyze_matched_experiment(plan, measurements)
        self.assertEqual(out["status"], "MATCHED_EFFECT_SUPPORTED")
        self.assertTrue(out["supports_intervention"])

    def test_confound_blocks_effect_promotion(self):
        plan = compile_matched_experiment(
            self.need(),
            available_controls=[{"control_id":"c","independent":True,"comparable":True,"distance":0}],
            candidate_confounds=[],
            budget={"max_runs":4,"max_seconds":30},
        )
        measurements=[
            {"arm":"control","value":10.0,"valid":True},
            {"arm":"intervention","value":6.0,"valid":True,"confound":"thermal-throttle"},
        ]
        out = analyze_matched_experiment(plan, measurements)
        self.assertEqual(out["status"], "HOLD_MATCHED_EFFECT")
        self.assertFalse(out["supports_intervention"])


if __name__ == "__main__":
    unittest.main()
