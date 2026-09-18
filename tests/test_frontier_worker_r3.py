import tempfile
import unittest
from pathlib import Path

from tristan.autonomous_decision import ActionProposal
from tristan.frontier_worker import (
    AtomicJSONStateStore,
    PersistentFrontierWorker,
    WorkerOutcome,
    state_health,
)


class PersistentFrontierWorkerTests(unittest.TestCase):
    def test_state_survives_worker_recreation(self):
        with tempfile.TemporaryDirectory() as td:
            store = AtomicJSONStateStore(Path(td) / "state.json")

            def propose(state):
                if state.generation == 0:
                    return (
                        ActionProposal(
                            "A1", "internal_test", {"x": 1}, True, False, "discard",
                            ("seed",), 0.95, 2.0, 0.1, 0.0,
                        ),
                    )
                return ()

            def handler(proposal, state):
                return WorkerOutcome(True, 1.0, ("receipt-A1",), ("next",))

            worker = PersistentFrontierWorker(
                state_store=store,
                propose=propose,
                handlers={"internal_test": handler},
                poll_seconds=0,
            )
            first = worker.run_cycle()
            self.assertEqual(first.generation, 1)
            self.assertEqual(first.last_status, "EXECUTED")

            recreated = PersistentFrontierWorker(
                state_store=store,
                propose=propose,
                handlers={"internal_test": handler},
                poll_seconds=0,
            )
            second = recreated.run_cycle()
            self.assertEqual(second.generation, 1)
            self.assertEqual(second.last_status, "DORMANT_SCAN")
            self.assertIn("receipt-A1", second.evidence_refs)

    def test_authority_boundary_never_executes_handler(self):
        with tempfile.TemporaryDirectory() as td:
            store = AtomicJSONStateStore(Path(td) / "state.json")

            def propose(state):
                return (
                    ActionProposal(
                        "DEPLOY", "external_deployment", {"target": "prod"}, True, True,
                        "rollback", ("ci",), 0.99, 10, 1, 0,
                    ),
                )

            def forbidden(*args):
                raise AssertionError("must not execute external action")

            worker = PersistentFrontierWorker(
                state_store=store,
                propose=propose,
                handlers={"external_deployment": forbidden},
                poll_seconds=0,
            )
            state = worker.run_cycle()
            self.assertEqual(state.last_status, "HOLD_AUTHORITY_BOUNDARY")

    def test_missing_handler_holds_without_losing_state(self):
        with tempfile.TemporaryDirectory() as td:
            store = AtomicJSONStateStore(Path(td) / "state.json")

            def propose(state):
                return (
                    ActionProposal(
                        "A", "unknown_internal_action", {"x": 1}, True, False,
                        "discard", ("e",), 0.99, 3, 0, 0,
                    ),
                )

            worker = PersistentFrontierWorker(
                state_store=store,
                propose=propose,
                handlers={},
                poll_seconds=0,
            )
            state = worker.run_cycle()
            self.assertEqual(state.last_status, "HOLD_NO_HANDLER")
            self.assertTrue(store.path.exists())

    def test_heartbeat_health(self):
        with tempfile.TemporaryDirectory() as td:
            store = AtomicJSONStateStore(Path(td) / "state.json")
            worker = PersistentFrontierWorker(
                state_store=store,
                propose=lambda state: (),
                handlers={},
                poll_seconds=0,
            )
            state = worker.run_cycle()
            health = state_health(state, stale_after_seconds=60)
            self.assertTrue(health["healthy"])
            self.assertEqual(health["status"], "HEALTHY")

    def test_bounded_run_forever_supports_watchdog_supervision(self):
        with tempfile.TemporaryDirectory() as td:
            store = AtomicJSONStateStore(Path(td) / "state.json")
            worker = PersistentFrontierWorker(
                state_store=store,
                propose=lambda state: (),
                handlers={},
                poll_seconds=0,
            )
            state = worker.run_forever(max_cycles=3)
            self.assertEqual(state.cycle_count, 3)


if __name__ == "__main__":
    unittest.main()
