import unittest

from tristan.problem_foundry import (
    INGEST_MANUAL_ONLY,
    ProblemGenome,
    SOURCE_POLICIES,
    compile_problem_plan,
    problem_family_signature,
    rank_diverse_problems,
)


class ProblemFoundryTests(unittest.TestCase):
    def test_stackexchange_is_fail_closed_for_ai_publication(self):
        for source in ("stackoverflow", "mathoverflow", "physics-stackexchange"):
            policy = SOURCE_POLICIES[source]
            self.assertEqual(policy.ingestion_mode, INGEST_MANUAL_ONLY)
            problem = ProblemGenome(
                problem_id=f"{source}-1",
                source=source,
                title="bounded example",
                domain="code" if source == "stackoverflow" else "math",
            )
            plan = compile_problem_plan(problem)
            self.assertFalse(plan.publication_allowed)
            self.assertIn("AI_GENERATED_PUBLICATION_PROHIBITED", plan.publication_blockers)

    def test_domain_contracts_are_distinct(self):
        code = compile_problem_plan(ProblemGenome("c", "github", "bug", "code"))
        math = compile_problem_plan(ProblemGenome("m", "mathoverflow", "identity", "math"))
        physics = compile_problem_plan(ProblemGenome("p", "physics-stackexchange", "field", "physics"))
        self.assertIn("unit_tests", code.verification_contract)
        self.assertIn("counterexample_search", math.verification_contract)
        self.assertIn("dimensional_analysis", physics.verification_contract)

    def test_diversity_ranking_can_promote_a_different_domain(self):
        problems = [
            ProblemGenome("code-a", "github", "A", "code", utility=5, generalization=5, verifiability=5),
            ProblemGenome("code-b", "github", "B", "code", utility=4.9, generalization=5, verifiability=5),
            ProblemGenome("math-a", "mathoverflow", "M", "math", utility=4.8, generalization=5, verifiability=5),
        ]
        ranked = rank_diverse_problems(problems)
        self.assertEqual(ranked[0].problem_id, "code-a")
        self.assertEqual(ranked[1].problem_id, "math-a")

    def test_signature_is_order_independent(self):
        a = ProblemGenome("a", "github", "A", "code", tags=("numpy", "python"), languages=("python",))
        b = ProblemGenome("b", "github", "B", "code", tags=("python", "numpy"), languages=("python",))
        self.assertEqual(problem_family_signature(a), problem_family_signature(b))

    def test_invalid_problem_fails_closed(self):
        with self.assertRaises(ValueError):
            compile_problem_plan(ProblemGenome("", "unknown", "", "alien"))


if __name__ == "__main__":
    unittest.main()
