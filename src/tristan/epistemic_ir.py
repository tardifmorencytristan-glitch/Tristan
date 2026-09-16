from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ScientificContract:
    subject: str
    operation: str
    expected: Any = None
    scope: str = ""
    evidence: str = ""
    units: str | None = None


@dataclass(frozen=True)
class ImplementationFact:
    kind: str
    value: Any
    path: str = ""


@dataclass
class ConsistencyFinding:
    status: str
    family: str
    contract: ScientificContract
    observed: list[ImplementationFact] = field(default_factory=list)
    note: str = ""


def _canon(node: ast.AST) -> Any:
    if isinstance(node, ast.Expression):
        return _canon(node.body)
    if isinstance(node, ast.Constant):
        return ("const", node.value)
    if isinstance(node, ast.Name):
        return ("name", node.id)
    if isinstance(node, ast.UnaryOp):
        return (type(node.op).__name__, _canon(node.operand))
    if isinstance(node, ast.Call):
        fn = _canon(node.func)
        return ("call", fn, tuple(_canon(a) for a in node.args))
    if isinstance(node, ast.Attribute):
        return ("attr", _canon(node.value), node.attr)
    if isinstance(node, ast.BinOp):
        op = type(node.op).__name__
        left, right = _canon(node.left), _canon(node.right)
        if op in {"Add", "Mult"}:
            pair = tuple(sorted((left, right), key=repr))
            return (op,) + pair
        return (op, left, right)
    if isinstance(node, ast.Subscript):
        return ("subscript", _canon(node.value), _canon(node.slice))
    return (type(node).__name__, ast.dump(node, include_attributes=False))


def formula_ir(expr: str) -> Any:
    """Canonical, syntax-aware IR for a bounded Python expression."""
    return _canon(ast.parse(expr, mode="eval"))


def formulas_equivalent_syntax(expr_a: str, expr_b: str) -> bool:
    """Conservative structural equivalence; symbolic algebra is a later backend."""
    return formula_ir(expr_a) == formula_ir(expr_b)


def implementation_ir(source: str) -> list[ImplementationFact]:
    tree = ast.parse(source)
    facts: list[ImplementationFact] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = _call_name(node.func)
            facts.append(ImplementationFact("call", name))
            if name.endswith("clamp") or name in {"min", "max"}:
                facts.append(ImplementationFact("bound", name))
            if any(k in name.lower() for k in ("relu", "sigmoid", "tanh", "softmax")):
                facts.append(ImplementationFact("nonlinearity", name))
            if "norm" in name.lower() or "normalize" in name.lower():
                facts.append(ImplementationFact("normalization", name))
            if "loss" in name.lower() or name.lower().endswith("cross_entropy"):
                facts.append(ImplementationFact("loss_term", name))
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    facts.append(ImplementationFact("assignment", t.id))
        elif isinstance(node, ast.Constant) and isinstance(node.value, (int, float, str)):
            facts.append(ImplementationFact("constant", node.value))
    return facts


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _call_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def evaluate_contract(contract: ScientificContract, facts: list[ImplementationFact]) -> ConsistencyFinding:
    op = contract.operation.lower()
    values = [f for f in facts if f.kind == op]
    if op in {"normalization", "nonlinearity", "bound", "loss_term"}:
        if not values:
            return ConsistencyFinding("POTENTIAL_MISMATCH", op.upper(), contract, [], "required operation not observed")
        if contract.expected is None:
            return ConsistencyFinding("SUPPORTED", op.upper(), contract, values)
        hits = [f for f in values if str(contract.expected).lower() in str(f.value).lower()]
        return ConsistencyFinding("SUPPORTED" if hits else "POTENTIAL_MISMATCH", op.upper(), contract, hits or values)
    if op == "constant":
        hits = [f for f in facts if f.kind == "constant" and f.value == contract.expected]
        return ConsistencyFinding("SUPPORTED" if hits else "POTENTIAL_MISMATCH", "CONSTANT", contract, hits)
    if op == "dataset":
        needle = str(contract.expected).lower()
        hits = [f for f in facts if f.kind in {"call", "constant"} and needle in str(f.value).lower()]
        return ConsistencyFinding("SUPPORTED" if hits else "POTENTIAL_MISMATCH", "DATASET_IDENTITY", contract, hits)
    return ConsistencyFinding("UNKNOWN", "UNSUPPORTED_CONTRACT", contract, [], "no verifier backend for operation")
