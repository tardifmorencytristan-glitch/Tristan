from __future__ import annotations

import json
from pathlib import Path
from .model import TristanObject


class Registry:
    def __init__(self, objects: list[TristanObject]):
        ids = [obj.id for obj in objects]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate TristanObject ids")
        self._objects = tuple(objects)
        self._by_id = {obj.id: obj for obj in objects}

    @classmethod
    def load(cls, path: str | Path) -> "Registry":
        objects: list[TristanObject] = []
        with Path(path).open("r", encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, 1):
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                try:
                    data = json.loads(stripped)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"invalid JSONL at line {line_no}: {exc}") from exc
                objects.append(TristanObject.from_dict(data))
        return cls(objects)

    def all(self) -> tuple[TristanObject, ...]:
        return self._objects

    def get(self, object_id: str) -> TristanObject | None:
        return self._by_id.get(object_id)

    def require(self, object_id: str) -> TristanObject:
        obj = self.get(object_id)
        if obj is None:
            raise KeyError(object_id)
        return obj
