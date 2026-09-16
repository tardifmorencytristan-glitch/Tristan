# Architecture R0.1

## Mission

Keep the public root small enough to regenerate while federating larger historical/private/external sources by provenance.

## K*

`K* = minimum(source-of-truth + schemas + generators + tests + evidence + policies + provenance)` required to rebuild a bounded verified capability.

## Separation of roles

- **Generator** proposes.
- **Executor** performs an authorized operation.
- **Judge/validator** tests.
- **Reality anchor** supplies independent observations when required.
- **Authority** grants permission.
- **Registry** routes; it does not make claims true.

No role inherits another role's authority automatically.

## State transition

`INTENT -> Context* -> Residual -> Search -> Candidate -> Test -> Compete -> Evidence -> Crystal -> Regeneration`

Every transition may terminate in `NO_ACTION`, `HOLD`, `REJECTED`, or `RESIDUAL`.

## Federation

R0.1 records URLs and exact references when observed. It does not bulk-copy the historical repository, Drive, chat history, or web corpora.

## Promotion

R0.1 has no automatic scientific promotion mechanism. Repository checks validate structure and deterministic engineering contracts only.
