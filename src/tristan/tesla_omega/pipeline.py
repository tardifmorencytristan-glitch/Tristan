from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json

from .models import Claim, Evidence, OAKVector, Status
from .topology import binary_tree, chain, star


SOURCES: tuple[Evidence, ...] = (
    Evidence("S001", "patent", "US454622A - System of Electric Lighting", "https://patents.google.com/patent/US454622A/en", 1891, True),
    Evidence("S002", "patent", "US613809A - Remote control of moving vessels or vehicles", "https://patents.google.com/patent/US613809A/en", 1898, True),
    Evidence("S003", "patent", "US645576A - System of transmission of electrical energy", "https://patents.google.com/patent/US645576A/en", 1900, True),
    Evidence("S004", "archive", "Nikola Tesla Museum - Activity archive", "https://tesla-museum.org/en/legacy/archive/activity/", None, True),
    Evidence("S005", "archive", "Nikola Tesla Museum - Patents", "https://tesla-museum.org/en/nikola-tesla-2/patents/", None, True),
    Evidence("S006", "review", "Magnetically coupled resonant WPT for IoT perception layer: review", "https://doi.org/10.1016/j.rser.2025.116013", 2025, False),
    Evidence("S007", "study", "Coil structures with misalignments for WPT", "https://doi.org/10.1016/j.prime.2025.100959", 2025, False),
)


CLAIMS: tuple[Claim, ...] = (
    Claim("T001", "Tesla patented a high-frequency, high-potential electric lighting system in US454622A.", "historical", ("S001",), oak=OAKVector(documentary=Status.DOCUMENTED)),
    Claim("T002", "Tesla patented remote control of mechanisms in moving vessels or vehicles in US613809A.", "historical", ("S002",), oak=OAKVector(documentary=Status.DOCUMENTED)),
    Claim("T003", "Tesla patented a system of transmission of electrical energy in US645576A.", "historical", ("S003",), oak=OAKVector(documentary=Status.DOCUMENTED)),
    Claim("T004", "A multi-resonator reconstruction should reproduce its analytically predicted normal-mode splitting before physical interpretation.", "computational", (), prediction="mode splitting agrees with ideal coupled-resonator equations within declared numerical tolerance", observable="normal-mode frequencies", falsifier="simulation disagrees with analytic baseline outside tolerance"),
    Claim("T005", "A fractal or hierarchical LC topology may produce a distinguishable modal-density signature relative to cost-matched controls.", "conjecture", (), prediction="rho_fractal(omega) differs from rho_control(omega)", observable="modal density and spectral spacing", falsifier="no reproducible difference under matched constraints"),
    Claim("T006", "Any topology claimed to improve wireless power transfer must be tested under misalignment and load variation, not only at its nominal optimum.", "method", ("S006", "S007"), oak=OAKVector(documentary=Status.DOCUMENTED)),
)


def _digest() -> str:
    canonical = json.dumps(
        {"sources": [s.to_dict() for s in SOURCES], "claims": [c.to_dict() for c in CLAIMS]},
        sort_keys=True,
        separators=(",", ":"),
    )
    return sha256(canonical.encode("utf-8")).hexdigest()


def compile_tesla_omega_status() -> dict[str, object]:
    documentary = Counter(c.oak.documentary.value for c in CLAIMS)
    topologies = [chain(4), star(5), binary_tree(3)]
    return {
        "status": "PROVISIONAL_RESEARCH_KERNEL",
        "authority_granted": False,
        "historical_truth_claimed": False,
        "physical_validation_claimed": False,
        "sources": len(SOURCES),
        "primary_sources": sum(1 for s in SOURCES if s.primary),
        "claims": len(CLAIMS),
        "documentary_status": dict(sorted(documentary.items())),
        "candidate_topologies": [
            {"name": t.name, "signature": t.signature()} for t in topologies
        ],
        "next_gates": [
            "extract parameterized circuits from primary sources",
            "cross-check historical claims against independent primary records",
            "build analytic vs simulation closure tests",
            "compare fractal/hierarchical topologies to cost-matched controls",
            "record negative results in FailureSynth",
        ],
        "corpus_digest_sha256": _digest(),
    }
