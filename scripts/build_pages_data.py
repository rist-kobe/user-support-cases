#!/usr/bin/env python3
"""Build the aggregated JSON data file used by the GitHub Pages viewer.

This script walks ``cases/**/*.json`` and combines every case document into a
single ``docs/data/cases.json`` file. GitHub Pages serves only the contents of
``docs/`` (or the branch root), so the site cannot ``fetch()`` files that live
outside of that directory. Aggregating the case data ahead of time lets the
static site load everything with a single request.

Usage:
    python scripts/build_pages_data.py

Re-run this script (and commit the resulting ``docs/data/cases.json``)
whenever files under ``cases/`` are added, removed, or modified.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = REPO_ROOT / "cases"
OUTPUT_PATH = REPO_ROOT / "docs" / "data" / "cases.json"

CASE_TYPE_NAME = {
    "performance_analysis": "性能分析",
    "performance_improvement": "性能改善",
    "porting": "移植",
}


def load_cases() -> list[dict]:
    cases = []

    for json_file in sorted(CASES_DIR.rglob("*.json")):
        with json_file.open(encoding="utf-8") as f:
            data = json.load(f)

        case_type = data.get("case_type", "")
        data.setdefault("case_type_name", CASE_TYPE_NAME.get(case_type, case_type))
        data["source_path"] = str(json_file.relative_to(REPO_ROOT))

        cases.append(data)

    cases.sort(key=lambda c: (c.get("case_type", ""), c.get("case_id", 0)))
    return cases


def build_tag_index(cases: list[dict]) -> dict:
    support_tags: set[str] = set()
    technical_tags: set[str] = set()

    for case in cases:
        support_tags.update(case.get("support_tags") or [])
        technical_tags.update(case.get("technical_tags") or [])

    return {
        "support_tags": sorted(support_tags),
        "technical_tags": sorted(technical_tags),
    }


def main() -> None:
    cases = load_cases()

    payload = {
        "generated_from": "cases/",
        "case_count": len(cases),
        "case_types": CASE_TYPE_NAME,
        "tags": build_tag_index(cases),
        "cases": cases,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")

    print(f"Wrote {len(cases)} cases to {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
