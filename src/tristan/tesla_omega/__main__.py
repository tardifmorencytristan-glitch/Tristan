from __future__ import annotations

import json

from .pipeline import compile_tesla_omega_status


if __name__ == "__main__":
    print(json.dumps(compile_tesla_omega_status(), ensure_ascii=False, indent=2, sort_keys=True))
