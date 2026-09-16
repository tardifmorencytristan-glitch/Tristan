from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sqlite3
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Callable

from .context import score_object
from .model import TristanObject
from .registry import Registry

CAMEL_BOUNDARY = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")
NON_ALNUM = re.compile(r"[^a-z0-9]+")


def normalized_terms(text: str) -> tuple[str, ...]:
    raw = unicodedata.normalize("NFKD", str(text))
    raw = "".join(ch for ch in raw if not unicodedata.combining(ch))
    raw = CAMEL_BOUNDARY.sub(" ", raw).replace("_", " ")
    return tuple(term for term in NON_ALNUM.split(raw.lower()) if len(term) >= 2)


def core_text(obj: TristanObject) -> str:
    return " ".join((obj.title, " ".join(obj.tags), obj.summary))


def full_public_text(obj: TristanObject) -> str:
    return " ".join(
        (
            obj.id,
            obj.kind,
            obj.title,
            obj.status,
            obj.summary,
            " ".join(obj.tags),
            " ".join(obj.dependencies),
            " ".join(obj.failures),
            " ".join(obj.frontiers),
            json.dumps(obj.metadata, sort_keys=True, separators=(",", ":")),
        )
    )


def rank_current(query: str, registry: Registry) -> list[str]:
    rows: list[tuple[str, float]] = []
    for obj in registry.all():
        score = score_object(query, obj)
        if score > 0:
            rows.append((obj.id, score))
    rows.sort(key=lambda row: (-row[1], row[0]))
    return [object_id for object_id, _ in rows]


def _bm25_rank(
    query: str,
    registry: Registry,
    text_fn: Callable[[TristanObject], str],
) -> list[str]:
    objects = registry.all()
    docs = [normalized_terms(text_fn(obj)) for obj in objects]
    query_terms = normalized_terms(query)
    if not query_terms or not docs:
        return []
    n = len(docs)
    average_length = sum(len(doc) for doc in docs) / n
    document_frequency = {
        term: sum(term in doc for doc in docs) for term in set(query_terms)
    }
    rows: list[tuple[str, float]] = []
    for obj, doc in zip(objects, docs):
        term_frequency = Counter(doc)
        score = 0.0
        for term in query_terms:
            frequency = term_frequency.get(term, 0)
            if not frequency:
                continue
            inverse_document_frequency = math.log(
                1.0 + (n - document_frequency[term] + 0.5) / (document_frequency[term] + 0.5)
            )
            denominator = frequency + 1.5 * (
                0.25 + 0.75 * len(doc) / max(average_length, 1e-12)
            )
            score += inverse_document_frequency * frequency * 2.5 / denominator
        if score > 0:
            rows.append((obj.id, score))
    rows.sort(key=lambda row: (-row[1], row[0]))
    return [object_id for object_id, _ in rows]


def rank_bm25_core(query: str, registry: Registry) -> list[str]:
    return _bm25_rank(query, registry, core_text)


def rank_bm25_full(query: str, registry: Registry) -> list[str]:
    return _bm25_rank(query, registry, full_public_text)


def rank_tfidf_full(query: str, registry: Registry) -> list[str]:
    objects = registry.all()
    docs = [normalized_terms(full_public_text(obj)) for obj in objects]
    query_terms = normalized_terms(query)
    if not query_terms or not docs:
        return []
    vocabulary = set(query_terms)
    for doc in docs:
        vocabulary.update(doc)
    n = len(docs)
    document_frequency = {
        term: sum(term in set(doc) for doc in docs) for term in vocabulary
    }

    def vector(tokens: tuple[str, ...]) -> dict[str, float]:
        counts = Counter(tokens)
        return {
            term: (1.0 + math.log(frequency))
            * (math.log((n + 1.0) / (document_frequency[term] + 1.0)) + 1.0)
            for term, frequency in counts.items()
        }

    query_vector = vector(query_terms)
    query_norm = math.sqrt(sum(value * value for value in query_vector.values()))
    rows: list[tuple[str, float]] = []
    for obj, doc in zip(objects, docs):
        doc_vector = vector(doc)
        doc_norm = math.sqrt(sum(value * value for value in doc_vector.values()))
        if not query_norm or not doc_norm:
            continue
        dot = sum(
            query_vector.get(term, 0.0) * doc_vector.get(term, 0.0)
            for term in query_vector
        )
        score = dot / (query_norm * doc_norm)
        if score > 0:
            rows.append((obj.id, score))
    rows.sort(key=lambda row: (-row[1], row[0]))
    return [object_id for object_id, _ in rows]


def rank_fts5_full(query: str, registry: Registry) -> list[str]:
    terms = normalized_terms(query)
    if not terms:
        return []
    connection = sqlite3.connect(":memory:")
    try:
        connection.execute(
            "CREATE VIRTUAL TABLE docs USING fts5(id UNINDEXED, body, tokenize='unicode61')"
        )
        connection.executemany(
            "INSERT INTO docs(id, body) VALUES (?, ?)",
            [
                (obj.id, full_public_text(obj).replace("_", " "))
                for obj in registry.all()
            ],
        )
        expression = " OR ".join(f'"{term}"' for term in terms)
        rows = connection.execute(
            "SELECT id, bm25(docs) AS score FROM docs WHERE docs MATCH ? ORDER BY score, id",
            (expression,),
        ).fetchall()
        return [row[0] for row in rows]
    finally:
        connection.close()


def fts5_available() -> bool:
    connection = sqlite3.connect(":memory:")
    try:
        connection.execute("CREATE VIRTUAL TABLE probe USING fts5(body)")
        return True
    except sqlite3.OperationalError:
        return False
    finally:
        connection.close()


def evaluate(
    ranker: Callable[[str, Registry], list[str]],
    registry: Registry,
    rows: list[dict],
) -> dict[str, float]:
    if not rows:
        raise ValueError("benchmark split must not be empty")
    hit_at_1 = 0
    reciprocal_ranks: list[float] = []
    recalls_at_3: list[float] = []
    for row in rows:
        relevant = set(row["relevant"])
        ranking = ranker(row["query"], registry)
        hit_at_1 += int(bool(ranking) and ranking[0] in relevant)
        ranks = [ranking.index(item) + 1 for item in relevant if item in ranking]
        reciprocal_ranks.append(0.0 if not ranks else 1.0 / min(ranks))
        recalls_at_3.append(len(set(ranking[:3]) & relevant) / len(relevant))
    count = len(rows)
    return {
        "hit_at_1": round(hit_at_1 / count, 6),
        "mrr": round(sum(reciprocal_ranks) / count, 6),
        "recall_at_3": round(sum(recalls_at_3) / count, 6),
    }


def run_court(registry_path: str | Path, benchmark_path: str | Path) -> dict:
    registry_path = Path(registry_path)
    benchmark_path = Path(benchmark_path)
    registry = Registry.load(registry_path)
    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
    rows = benchmark["queries"]
    splits = {
        name: [row for row in rows if row["split"] == name]
        for name in ("dev", "holdout")
    }
    arms: dict[str, Callable[[str, Registry], list[str]]] = {
        "CURRENT_R0_1": rank_current,
        "BM25_CORE": rank_bm25_core,
        "BM25_FULL": rank_bm25_full,
        "TFIDF_FULL_NORMALIZED": rank_tfidf_full,
    }
    unavailable: list[str] = []
    if fts5_available():
        arms["SQLITE_FTS5_FULL"] = rank_fts5_full
    else:
        unavailable.append("SQLITE_FTS5_FULL")

    results = {
        arm: {
            split: evaluate(ranker, registry, split_rows)
            for split, split_rows in splits.items()
        }
        for arm, ranker in arms.items()
    }
    holdout_best_mrr = max(value["holdout"]["mrr"] for value in results.values())
    best_by_mrr = sorted(
        arm
        for arm, value in results.items()
        if value["holdout"]["mrr"] == holdout_best_mrr
    )
    current = results["CURRENT_R0_1"]["holdout"]
    candidate_gain = round(holdout_best_mrr - current["mrr"], 6)
    if candidate_gain <= 0:
        decision = "NO_ACTION"
    elif len(best_by_mrr) > 1:
        decision = "TIE_KEEP_RUNTIME_UNCHANGED_SHADOW_CHALLENGERS"
    else:
        decision = "SHADOW_CANDIDATE_ONLY_NEEDS_LARGER_INDEPENDENT_COURT"

    return {
        "protocol": "TRISTAN-CONTEXT-RETRIEVAL-COURT-R0.2",
        "source": {
            "registry_sha256": hashlib.sha256(registry_path.read_bytes()).hexdigest(),
            "benchmark_sha256": hashlib.sha256(benchmark_path.read_bytes()).hexdigest(),
        },
        "counts": {
            "objects": len(registry.all()),
            "queries": len(rows),
            "dev": len(splits["dev"]),
            "holdout": len(splits["holdout"]),
        },
        "results": results,
        "unavailable_arms": unavailable,
        "holdout_best_mrr": holdout_best_mrr,
        "best_by_holdout_mrr": best_by_mrr,
        "holdout_mrr_gain_vs_current": candidate_gain,
        "decision": decision,
        "runtime_mutation_authorized": False,
        "boundaries": benchmark["boundaries"]
        + [
            "BM25PriorArtReused!=NewTristanInvention",
            "SQLiteFTSAvailableHere!=AvailableEverywhere",
            "Tie!=Winner",
            "BenchmarkVictory!=UniversalRetrievalSuperiority",
            "NoRuntimeMutationWithoutLargerIndependentCourt",
        ],
        "prior_art": {
            "historical_bm25_adapter_sha": "3dc0f2cc769ca3fa75a175493fe58249e8847e73",
            "historical_context_r2_doc_sha": "e7b4193d2af681819ec5859c347c1c5dc7156b9b",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default="registry/objects.jsonl")
    parser.add_argument(
        "--benchmark", default="benchmarks/context_retrieval_r0_2.json"
    )
    args = parser.parse_args()
    print(json.dumps(run_court(args.registry, args.benchmark), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
