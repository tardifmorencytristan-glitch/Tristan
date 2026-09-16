from __future__ import annotations

from dataclasses import dataclass, field, asdict
from decimal import Decimal, InvalidOperation
import re
from typing import Any, Iterable

from .loss_tensor import LossObservation, LossTensor


CITATION_SUPPORT_STATES = {"UNKNOWN", "PRESENT", "RESOLVED", "SUPPORTS", "CONTRADICTS"}
NUMERIC_COURT_STATES = {
    "CONSISTENT",
    "HOLD_MISSING_QUANTITY",
    "HOLD_UNIT_DISAGREEMENT",
    "HOLD_VALUE_DISAGREEMENT",
}

_QUANTITY_PATTERN = re.compile(
    r"(?P<label>[A-Za-z][A-Za-z0-9_\- ]{0,39}?)\s*=\s*"
    r"(?P<value>[+-]?(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][+-]?\d+)?)"
    r"(?:\s*(?P<unit>[A-Za-zµμΩ%°]+(?:/[A-Za-z]+)?))?"
)
_SYMBOL_PATTERN = re.compile(r"[A-Za-zµμΩ][A-Za-z0-9_µμΩ]*")


@dataclass(frozen=True)
class QuantityIR:
    id: str
    label: str
    value_text: str
    unit: str = ""
    source_node_id: str = ""
    provenance_ids: tuple[str, ...] = ()
    status: str = "OBSERVED_CANDIDATE"

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.id:
            errors.append("QuantityIR.id required")
        if not self.label:
            errors.append("QuantityIR.label required")
        if not self.value_text:
            errors.append("QuantityIR.value_text required")
        try:
            Decimal(self.value_text)
        except InvalidOperation:
            errors.append("QuantityIR.value_text must be decimal-parsable")
        if not self.source_node_id:
            errors.append("QuantityIR.source_node_id required")
        return errors

    @property
    def decimal_value(self) -> Decimal:
        errors = self.validate()
        if errors:
            raise ValueError(errors)
        return Decimal(self.value_text)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["decimal_value"] = str(self.decimal_value)
        return payload


@dataclass(frozen=True)
class EquationIR:
    id: str
    raw_text: str
    lhs: str
    rhs: str
    symbols: tuple[str, ...]
    source_node_id: str
    provenance_ids: tuple[str, ...] = ()
    status: str = "CANDIDATE_UNVERIFIED"

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.id or not self.source_node_id:
            errors.append("EquationIR id/source_node_id required")
        if not self.raw_text or not self.lhs.strip() or not self.rhs.strip():
            errors.append("EquationIR requires non-empty lhs/rhs")
        if "=" not in self.raw_text:
            errors.append("EquationIR.raw_text must contain '='")
        return errors


@dataclass(frozen=True)
class TableCellIR:
    row: int
    column: int
    text: str
    source_node_id: str
    rowspan: int = 1
    colspan: int = 1
    is_header: bool = False

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.row < 0 or self.column < 0:
            errors.append("TableCellIR row/column must be >= 0")
        if self.rowspan < 1 or self.colspan < 1:
            errors.append("TableCellIR row/colspan must be >= 1")
        if not self.source_node_id:
            errors.append("TableCellIR.source_node_id required")
        return errors


@dataclass(frozen=True)
class TableIR:
    id: str
    cells: tuple[TableCellIR, ...]
    source_node_id: str
    provenance_ids: tuple[str, ...] = ()
    status: str = "STRUCTURE_CANDIDATE_UNVERIFIED"

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.id or not self.source_node_id:
            errors.append("TableIR id/source_node_id required")
        if not self.cells:
            errors.append("TableIR.cells required")
        coordinates: set[tuple[int, int]] = set()
        for cell in self.cells:
            errors.extend(cell.validate())
            coordinate = (cell.row, cell.column)
            if coordinate in coordinates:
                errors.append(f"duplicate table coordinate: {coordinate}")
            coordinates.add(coordinate)
        return errors


@dataclass(frozen=True)
class CitationIR:
    id: str
    raw_marker: str
    source_node_id: str
    target_text: str = ""
    resolved_source_id: str = ""
    support_status: str = "UNKNOWN"
    provenance_ids: tuple[str, ...] = ()

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.id or not self.raw_marker or not self.source_node_id:
            errors.append("CitationIR id/raw_marker/source_node_id required")
        if self.support_status not in CITATION_SUPPORT_STATES:
            errors.append(f"invalid CitationIR.support_status: {self.support_status}")
        if self.support_status in {"SUPPORTS", "CONTRADICTS"} and not self.resolved_source_id:
            errors.append("support/contradiction claim requires resolved_source_id")
        return errors


@dataclass(frozen=True)
class NumericCourtDecision:
    status: str
    label: str
    parser_ids: tuple[str, ...]
    values: tuple[str, ...]
    units: tuple[str, ...]
    reason: str

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.status not in NUMERIC_COURT_STATES:
            errors.append(f"invalid numeric court status: {self.status}")
        if not self.label or len(self.parser_ids) < 2:
            errors.append("numeric court requires label and >=2 parser ids")
        return errors

    def to_loss_tensor(self, transform_id: str = "numeric_integrity_court") -> LossTensor:
        tensor = LossTensor()
        if self.status == "CONSISTENT":
            tensor.add(LossObservation(transform_id, self.label, "NUMERIC", "PRESERVED", severity=0.0, recoverability=1.0, cause=self.reason))
            return tensor
        dimension = "UNITS" if self.status == "HOLD_UNIT_DISAGREEMENT" else "NUMERIC"
        tensor.add(LossObservation(transform_id, self.label, dimension, "UNKNOWN", severity=1.0, recoverability=0.0, cause=self.reason))
        return tensor


def extract_explicit_quantities(text: str, source_node_id: str, provenance_ids: tuple[str, ...] = ()) -> list[QuantityIR]:
    results: list[QuantityIR] = []
    for index, match in enumerate(_QUANTITY_PATTERN.finditer(text)):
        label = match.group("label").strip()
        value = match.group("value")
        unit = (match.group("unit") or "").strip()
        quantity = QuantityIR(
            id=f"{source_node_id}:quantity:{index}",
            label=label,
            value_text=value,
            unit=unit,
            source_node_id=source_node_id,
            provenance_ids=provenance_ids,
        )
        errors = quantity.validate()
        if errors:
            raise ValueError(errors)
        results.append(quantity)
    return results


def equation_candidate(raw_text: str, source_node_id: str, provenance_ids: tuple[str, ...] = (), candidate_id: str = "") -> EquationIR:
    if raw_text.count("=") != 1:
        raise ValueError("bounded EquationIR candidate requires exactly one '='")
    lhs, rhs = raw_text.split("=", 1)
    symbols = tuple(dict.fromkeys(_SYMBOL_PATTERN.findall(raw_text)))
    equation = EquationIR(
        id=candidate_id or f"{source_node_id}:equation",
        raw_text=raw_text,
        lhs=lhs.strip(),
        rhs=rhs.strip(),
        symbols=symbols,
        source_node_id=source_node_id,
        provenance_ids=provenance_ids,
    )
    errors = equation.validate()
    if errors:
        raise ValueError(errors)
    return equation


def compare_quantities(parser_quantities: dict[str, Iterable[QuantityIR]], label: str) -> NumericCourtDecision:
    parser_ids = tuple(sorted(parser_quantities))
    if len(parser_ids) < 2:
        raise ValueError("numeric court requires at least two parsers")
    matches: dict[str, QuantityIR] = {}
    for parser_id in parser_ids:
        candidates = [q for q in parser_quantities[parser_id] if q.label == label]
        if len(candidates) != 1:
            return NumericCourtDecision(
                "HOLD_MISSING_QUANTITY",
                label,
                parser_ids,
                tuple(q.value_text for q in matches.values()),
                tuple(q.unit for q in matches.values()),
                f"parser {parser_id} has {len(candidates)} candidates for label {label!r}",
            )
        matches[parser_id] = candidates[0]

    units = tuple(matches[p].unit for p in parser_ids)
    values = tuple(matches[p].value_text for p in parser_ids)
    if len(set(units)) != 1:
        return NumericCourtDecision("HOLD_UNIT_DISAGREEMENT", label, parser_ids, values, units, "units disagree across parser observations")
    decimals = tuple(matches[p].decimal_value for p in parser_ids)
    if len(set(decimals)) != 1:
        return NumericCourtDecision("HOLD_VALUE_DISAGREEMENT", label, parser_ids, values, units, "numeric values disagree across parser observations")
    return NumericCourtDecision("CONSISTENT", label, parser_ids, values, units, "numeric value and unit agree exactly across parser observations")
