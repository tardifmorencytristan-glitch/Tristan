from __future__ import annotations

_LATEX_ESCAPES = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def escape_latex(text: str) -> str:
    return "".join(_LATEX_ESCAPES.get(ch, ch) for ch in str(text))


def _require(packet: dict, key: str):
    value = packet.get(key)
    if value in (None, "", [], {}):
        raise ValueError(f"missing required manuscript field: {key}")
    return value


def render_battery_manuscript(packet: dict) -> str:
    """Render a bounded Battery-T manuscript projection.

    This renderer is deliberately conservative: it preserves source scope,
    measurements and explicit limitations and does not infer novelty,
    ScientificPASS, causality or universal superiority.
    """
    title = escape_latex(_require(packet, "title"))
    scope = escape_latex(_require(packet, "scope"))
    source = str(_require(packet, "source_anchor"))
    results = _require(packet, "results")
    limitations = _require(packet, "limitations")

    dfn = float(results["DFN_mean_shape_rmse_v"])
    spm = float(results["SPM_mean_shape_rmse_v"])
    spme = float(results["SPMe_mean_shape_rmse_v"])
    cap_low = float(results["capacity_overprediction_low_pct"])
    cap_high = float(results["capacity_overprediction_high_pct"])

    if not (dfn < spm < spme):
        raise ValueError("frozen observed ordering DFN < SPM < SPMe not preserved")
    if cap_low <= 0 or cap_high < cap_low:
        raise ValueError("invalid capacity-overprediction bounds")

    limitation_items = "\n".join(
        rf"\item {escape_latex(item)}" for item in limitations
    )

    return rf"""\documentclass[11pt]{{article}}
\usepackage[T1]{{fontenc}}
\usepackage[utf8]{{inputenc}}
\usepackage{{lmodern}}
\usepackage{{microtype}}
\usepackage{{geometry}}
\usepackage{{booktabs}}
\usepackage{{xurl}}
\usepackage{{hyperref}}
\geometry{{margin=1in}}
\title{{{title}}}
\author{{Tristan Tardif-Morency}}
\date{{Evidence-bounded draft}}
\begin{{document}}
\maketitle

\begin{{abstract}}
Within {scope}, three public CALCE first-cycle discharge slices were compared against zero-fit PyBaMM SPM, SPMe, and DFN simulations. Mean voltage-shape RMSE was {dfn:.5f}~V for DFN, {spm:.5f}~V for SPM, and {spme:.5f}~V for SPMe. The same court recorded approximately {cap_low:.0f}--{cap_high:.0f}\% absolute-capacity overprediction. These observations are bounded to the stated protocol and do not establish universal model superiority or ScientificPASS.
\end{{abstract}}

\section{{Evidence anchor}}
The manuscript projection is tied to the exact source receipt:\\
\url{{{source}}}

Generated text is not an independent evidence source.

\section{{Methods}}
The court uses the public CALCE cells CS2\_33, CS2\_34, and CS2\_35 and the PyBaMM 26.8.0.0 Ramadass2004 parameter set without cell-specific parameter calibration. Comparison is performed on normalized discharged-capacity coordinates for the stated first-cycle slices.

\section{{Results}}
\begin{{table}}[ht]
\centering
\caption{{Mean voltage-shape RMSE over the frozen three-cell court.}}
\begin{{tabular}}{{lr}}
\toprule
Model & Mean RMSE (V) \\
\midrule
DFN & {dfn:.5f} \\
SPM & {spm:.5f} \\
SPMe & {spme:.5f} \\
\bottomrule
\end{{tabular}}
\end{{table}}

Within {scope}, DFN has the lowest observed mean voltage-shape RMSE among the three evaluated models. This comparison is descriptive for the frozen court; it is not a claim of universal superiority.

\section{{Limitations}}
\begin{{itemize}}
{limitation_items}
\end{{itemize}}

\section{{Conclusion}}
The frozen Battery-T court supports a bounded comparative statement about voltage-shape error under the stated protocol while simultaneously revealing a substantial capacity mismatch. The appropriate next step is independent replication and identifiable recalibration under a preregistered protocol, not stronger wording.

\end{{document}}
"""


def extract_required_tokens(tex: str) -> set[str]:
    """Small deterministic readback contract used before PDF compilation."""
    return {
        token for token in [
            "CALCE",
            "DFN",
            "SPM",
            "SPMe",
            "ScientificPASS",
            "universal superiority",
            "capacity mismatch",
        ] if token.lower() in tex.lower()
    }
