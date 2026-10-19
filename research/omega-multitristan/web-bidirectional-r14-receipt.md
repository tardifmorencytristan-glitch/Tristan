# Omega Web R14 - Distributed public round-trip receipt

Status: **VERIFIED BOUNDED ROUND-TRIP**, not production autonomy, not scientific certification.

## Test scope
Source: `research/omega-multitristan/web-bidirectional-r14-canary.md` on the branch `research/omega-web-bidir-r14-20261019` in the public GitHub repository `tardifmorencytristan-glitch/Tristan`.
GitHub source commit: `e8e8000caa0a875a9c147ec6105159dd434ddd2f`.
GitHub authenticated write: succeeded. GitHub connector read-back: succeeded.
All three independently connected user devices fetched **that exact commit** via HTTPS.

## Results
| Independent machine role | HTTP response | Required marker found | SHA-256 of UTF-8 response text |
| --- | --- | --- | --- |
| FORGE | 200 | true | `7dbc3082d598b339e163d05e0bf075dc5dcd7278dc97c9ff51482dd3e47d7312` |
| OAK | 200 | true | `7dbc3082d598b339e163d05e0bf075dc5dcd7278dc97c9ff51482dd3e47d7312` |
| VERIFIER | 200 | true | `7dbc3082d598b339e163d05e0bf075dc5dcd7278dc97c9ff51482dd3e47d7312` |

The three HTTPS downloads agreed in digest and in the required arithmetic marker. This is a platform-relayed receipt, not machine-cryptographically-signed attestation.

## Important boundaries
- **Proven:** public GitHub connector authenticated write -> publication -> HTTPS reads on each machine -> local SHA-256/marker read-back, then result reporting via the authorized remote bridge.
- **Not proven:** locally authenticated PC-to-GitHub Git writes, an always-on controller, inbound listener exposure, GitHub CI, unattended deployment, auto-merge, full scientific validation, or irreversible availability.
- The existing CLI GitHub authentication test was not successful on FORGE and `gh` was not available on OAK/VERIFIER. No credential installation, copying or printing was performed.
- Public documentation contains no confidential corpus or credentials. It is inert; retrieved Web content is never executable authority.
- Access rights must remain scoped, inspectable and revocable. Durable historical proof is separate from irreversible network permissions.
- Never auto-publish from private sources without checking licensing, rights, secrets, privacy, and scientific claim status.
- `PUBLISHED` != `VERIFIED` != `DEPLOYED`; `NO_ACTION` is allowed.

## Intended future workflow
For a verified locally-owned claim: locate prior work -> specify testable statement -> cross-check mathematical / software validity -> independently replicate -> scan source rights and secrets -> publish to permitted destination -> fetch after publish -> use only within the intended scope -> retain receipt and possible rollback. Start from local-first components; do not install competing controllers.
