# Autonomy R3 - Persistent Frontier Worker

R3 turns the R2 continuation protocol into a restartable worker process.

Properties:

- atomic JSON state persistence;
- restart/resume from the last durable state;
- heartbeat on every cycle;
- health/staleness reporting for a watchdog;
- bounded history retention;
- fresh Autonomy R1 decision before every action;
- handler allow-list;
- external/irreversible/scientific authority boundaries remain fail-closed;
- dormant scans preserve context instead of terminating.

A process supervisor may run the worker continuously. If the process crashes, a replacement worker loads the same state file and continues from the last completed cycle.

Persistence of the file itself is the responsibility of the runtime. Local machines can use a normal durable filesystem. Cloud deployments should place the state on a persistent volume or a durable key/value/database backend.

PersistentExecution != InfiniteAuthority.
Restart != Forget.
Heartbeat != ScientificEvidence.
