from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BLOCK_RE = re.compile(
    r"(?ms)^D(?P<index>\d+)\s*-\s*(?P<title>[^\r\n]+)\s*\r?\n"
    r"Commit exact\s*:\s*(?P<commit>[0-9a-f]{40})\s*\r?\n"
    r"Statut\s*:\s*(?P<status>[^\r\n]+)\s*\r?\n"
    r"Delta\s*:\s*(?P<delta>.*?)\r?\n"
    r"Preuve bornée\s*:\s*(?P<evidence>.*?)\r?\n"
    r"Frontière OAK\s*:\s*(?P<boundary>.*?)(?=\r?\nD\d+\s*-|\r?\n3\. Corrections|\Z)"
)


def parse_delta(text: str) -> dict:
    items = []
    for m in BLOCK_RE.finditer(text):
        items.append(
            {
                "id": f"D{m.group('index')}",
                "title": m.group("title").strip(),
                "commit": m.group("commit"),
                "status": " ".join(m.group("status").split()),
                "delta": " ".join(m.group("delta").split()),
                "bounded_evidence": " ".join(m.group("evidence").split()),
                "oak_boundary": " ".join(m.group("boundary").split()),
            }
        )
    return {"schema_version": "r1", "kind": "living_thesis_delta", "items": items}


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: r4_delta_parser.py <r4_text.txt> <output.json>", file=sys.stderr)
        return 2
    src = Path(sys.argv[1])
    out = Path(sys.argv[2])
    parsed = parse_delta(src.read_text(encoding="utf-8"))
    out.write_text(json.dumps(parsed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"items": len(parsed["items"]), "output": str(out)}, ensure_ascii=False))
    return 0 if parsed["items"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
