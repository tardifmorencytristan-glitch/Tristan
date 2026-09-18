from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time
from typing import Callable

from .autonomous_decision import ActionProposal, decide_action


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class WorkerState:
    schema_version: str = "tristan-frontier-worker-r3"
    worker_id: str = "jarvis-frontier-worker"
    generation: int = 0
    cycle_count: int = 0
    last_started_at: str | None = None
    last_heartbeat_at: str | None = None
    last_completed_at: str | None = None
    last_action_id: str | None = None
    last_status: str = "NEW"
    evidence_refs: list[str] = field(default_factory=list)
    residuals: list[str] = field(default_factory=list)
    pending: list[dict] = field(default_factory=list)
    history: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "WorkerState":
        return cls(**data)


class AtomicJSONStateStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def load(self) -> WorkerState:
        if not self.path.exists():
            return WorkerState()
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return WorkerState.from_dict(data)

    def save(self, state: WorkerState) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(
            json.dumps(state.to_dict(), ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        os.replace(tmp, self.path)


@dataclass(frozen=True)
class WorkerOutcome:
    success: bool
    verified_gain: float
    evidence_refs: tuple[str, ...] = ()
    residuals: tuple[str, ...] = ()
    note: str = ""

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.verified_gain < 0:
            errors.append("verified_gain must be non-negative")
        if self.success and not self.evidence_refs:
            errors.append("successful outcome requires evidence_refs")
        return errors


ActionHandler = Callable[[ActionProposal, WorkerState], WorkerOutcome]
ProposalGenerator = Callable[[WorkerState], tuple[ActionProposal, ...]]


class PersistentFrontierWorker:
    def __init__(
        self,
        *,
        state_store: AtomicJSONStateStore,
        propose: ProposalGenerator,
        handlers: dict[str, ActionHandler],
        worker_id: str = "jarvis-frontier-worker",
        poll_seconds: float = 30.0,
        max_history: int = 256,
    ) -> None:
        if poll_seconds < 0:
            raise ValueError("poll_seconds must be non-negative")
        self.state_store = state_store
        self.propose = propose
        self.handlers = dict(handlers)
        self.worker_id = worker_id
        self.poll_seconds = poll_seconds
        self.max_history = max_history

    def _heartbeat(self, state: WorkerState) -> None:
        state.last_heartbeat_at = _utcnow()
        self.state_store.save(state)

    def run_cycle(self) -> WorkerState:
        state = self.state_store.load()
        state.worker_id = self.worker_id
        state.last_started_at = _utcnow()
        state.cycle_count += 1
        self._heartbeat(state)

        proposals = self.propose(state)
        if not proposals:
            state.last_status = "DORMANT_SCAN"
            state.residuals = list(dict.fromkeys(state.residuals + ["no-current-proposal"]))
            state.last_completed_at = _utcnow()
            self.state_store.save(state)
            return state

        decisions = [(proposal, decide_action(proposal, executor_id=self.worker_id)) for proposal in proposals]
        executable = [(p, d) for p, d in decisions if d.decision == "EXECUTE_AUTONOMOUSLY"]

        if not executable:
            boundary = [(p, d) for p, d in decisions if d.decision == "REQUIRE_AUTHORIZATION"]
            if boundary:
                proposal, decision = max(boundary, key=lambda row: (row[1].utility, row[0].action_id))
                state.last_action_id = proposal.action_id
                state.last_status = "HOLD_AUTHORITY_BOUNDARY"
                state.residuals = list(dict.fromkeys(state.residuals + [f"authorization:{proposal.action_id}"]))
            else:
                proposal, decision = max(decisions, key=lambda row: (row[1].utility, row[0].action_id))
                state.last_action_id = proposal.action_id
                state.last_status = decision.decision
                state.residuals = list(dict.fromkeys(state.residuals + [decision.reason]))
            state.last_completed_at = _utcnow()
            self.state_store.save(state)
            return state

        proposal, decision = max(executable, key=lambda row: (row[1].utility, row[0].action_id))
        handler = self.handlers.get(proposal.action_kind)
        if handler is None:
            state.last_action_id = proposal.action_id
            state.last_status = "HOLD_NO_HANDLER"
            state.residuals = list(dict.fromkeys(state.residuals + [f"missing-handler:{proposal.action_kind}"]))
            state.last_completed_at = _utcnow()
            self.state_store.save(state)
            return state

        outcome = handler(proposal, state)
        errors = outcome.validate()
        if errors:
            raise ValueError("; ".join(errors))

        state.last_action_id = proposal.action_id
        state.last_status = "EXECUTED" if outcome.success else "FAILURE_ANALYSIS"
        state.generation += 1
        state.evidence_refs = list(dict.fromkeys(state.evidence_refs + list(outcome.evidence_refs)))
        state.residuals = list(dict.fromkeys(outcome.residuals))
        state.history.append({
            "generation": state.generation,
            "action_id": proposal.action_id,
            "action_kind": proposal.action_kind,
            "decision": decision.to_dict(),
            "outcome": asdict(outcome),
            "completed_at": _utcnow(),
        })
        if len(state.history) > self.max_history:
            state.history = state.history[-self.max_history:]
        state.last_completed_at = _utcnow()
        self.state_store.save(state)
        return state

    def run_forever(self, *, max_cycles: int | None = None) -> WorkerState:
        cycles = 0
        state = self.state_store.load()
        while max_cycles is None or cycles < max_cycles:
            state = self.run_cycle()
            cycles += 1
            if max_cycles is not None and cycles >= max_cycles:
                break
            time.sleep(self.poll_seconds)
        return state


def state_health(state: WorkerState, *, stale_after_seconds: float = 180.0) -> dict:
    if state.last_heartbeat_at is None:
        return {"status": "NEVER_STARTED", "healthy": False}
    heartbeat = datetime.fromisoformat(state.last_heartbeat_at)
    age = (datetime.now(timezone.utc) - heartbeat).total_seconds()
    return {
        "status": "HEALTHY" if age <= stale_after_seconds else "STALE",
        "healthy": age <= stale_after_seconds,
        "heartbeat_age_seconds": max(0.0, age),
        "worker_id": state.worker_id,
        "cycle_count": state.cycle_count,
        "generation": state.generation,
        "last_status": state.last_status,
    }
