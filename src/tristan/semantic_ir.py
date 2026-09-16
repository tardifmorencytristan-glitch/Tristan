from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DataflowEdge:
    source: str
    target: str
    operation: str


@dataclass(frozen=True)
class ArchitectureNode:
    name: str
    kind: str
    args: tuple[Any, ...] = ()


@dataclass
class ProtocolIR:
    datasets: set[str] = field(default_factory=set)
    transforms: set[str] = field(default_factory=set)
    optimizers: set[str] = field(default_factory=set)
    seeds: set[Any] = field(default_factory=set)
    constants: set[Any] = field(default_factory=set)


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        p = _call_name(node.value)
        return f"{p}.{node.attr}" if p else node.attr
    return ""


def _expr_names(node: ast.AST) -> set[str]:
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def dataflow_ir(source: str) -> list[DataflowEdge]:
    tree = ast.parse(source)
    edges: list[DataflowEdge] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            value = node.value
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            op = _call_name(value.func) if isinstance(value, ast.Call) else type(value).__name__
            srcs = _expr_names(value)
            for t in targets:
                if isinstance(t, ast.Name):
                    for s in sorted(srcs):
                        if s != t.id:
                            edges.append(DataflowEdge(s, t.id, op))
        elif isinstance(node, ast.Return):
            for s in sorted(_expr_names(node.value) if node.value else set()):
                edges.append(DataflowEdge(s, "<return>", "return"))
    return edges


def architecture_ir(source: str) -> list[ArchitectureNode]:
    tree = ast.parse(source)
    nodes: list[ArchitectureNode] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = _call_name(node.func)
            low = name.lower()
            if any(k in low for k in ("linear", "conv", "pool", "norm", "relu", "sigmoid", "tanh", "resnet", "transformer")):
                args = tuple(a.value for a in node.args if isinstance(a, ast.Constant))
                nodes.append(ArchitectureNode(name, "module", args))
    return nodes


def protocol_ir(source: str) -> ProtocolIR:
    tree = ast.parse(source)
    out = ProtocolIR()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = _call_name(node.func)
            low = name.lower()
            if any(k in low for k in ("cifar", "mnist", "imagenet", "dataset", "dataloader")):
                out.datasets.add(name)
            if any(k in low for k in ("crop", "flip", "rotate", "resize", "normalize")):
                out.transforms.add(name)
            if any(k in low for k in ("adam", "sgd", "optimizer")):
                out.optimizers.add(name)
            if "seed" in low:
                for a in node.args:
                    if isinstance(a, ast.Constant): out.seeds.add(a.value)
        elif isinstance(node, ast.Constant) and isinstance(node.value, (int, float, str)):
            out.constants.add(node.value)
    return out


def has_path(edges: list[DataflowEdge], source: str, target: str, required_operation: str | None = None) -> bool:
    graph: dict[str, list[DataflowEdge]] = {}
    for e in edges: graph.setdefault(e.source, []).append(e)
    stack=[source]; seen=set()
    while stack:
        cur=stack.pop()
        if cur in seen: continue
        seen.add(cur)
        for e in graph.get(cur, []):
            if e.target == target and (required_operation is None or required_operation.lower() in e.operation.lower()): return True
            stack.append(e.target)
    return False
