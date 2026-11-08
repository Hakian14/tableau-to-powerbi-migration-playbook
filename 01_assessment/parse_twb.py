"""
Count complexity drivers in Tableau workbook files (.twb, or .twbx which is a zip).

    python 01_assessment/parse_twb.py path/to/workbooks/*.twb* > inventory_counts.csv

Output columns match templates/inventory.csv so the result can be pasted in.
Counting is heuristic (regexes over the workbook XML); it is meant to size the
work, not to be a parser.
"""

from __future__ import annotations

import csv
import glob
import re
import sys
import zipfile
import xml.etree.ElementTree as ET


def read_twb(path: str) -> str:
    if path.lower().endswith(".twbx"):
        with zipfile.ZipFile(path) as z:
            name = next(n for n in z.namelist() if n.lower().endswith(".twb"))
            return z.read(name).decode("utf-8", errors="ignore")
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read()


TABLE_CALC_RE = re.compile(r"\b(WINDOW_\w+|RUNNING_\w+|LOOKUP|RANK\w*|INDEX|FIRST|LAST|PREVIOUS_VALUE|TOTAL)\s*\(", re.I)
LOD_RE = re.compile(r"\{\s*(FIXED|INCLUDE|EXCLUDE)\b", re.I)


def analyse(path: str) -> dict:
    xml = read_twb(path)
    root = ET.fromstring(xml)
    datasources = [d for d in root.iter("datasource") if d.get("name") not in (None, "Parameters")]
    calcs = [c.get("formula", "") for c in root.iter("calculation") if c.get("formula")]
    return {
        "workbook": path.rsplit("/", 1)[-1],
        "data_sources": len(datasources),
        "extract_or_live": "extract" if any(d.find(".//extract") is not None for d in datasources) else "live",
        "blends": sum(1 for _ in root.iter("relationship")) if root.find(".//blend") is not None else 0,
        "custom_sql": sum(1 for r in root.iter("relation") if (r.get("type") or "") == "text"),
        "n_sheets": sum(1 for _ in root.iter("worksheet")),
        "n_dashboards": sum(1 for _ in root.iter("dashboard")),
        "n_calc_fields": len(calcs),
        "n_lod": sum(1 for f in calcs if LOD_RE.search(f)),
        "n_table_calcs": sum(1 for f in calcs if TABLE_CALC_RE.search(f)),
        "n_parameters": sum(1 for c in root.iter("column") if (c.get("param-domain-type") or "")),
        "n_sets": sum(1 for _ in root.iter("group") if _.get("user:ui-builder") == "set"),
        "dashboard_actions": sum(1 for _ in root.iter("action")),
        "rls": "yes" if root.find(".//user-filter") is not None or any("USERNAME()" in f.upper() for f in calcs) else "no",
    }


def main(patterns: list[str]) -> int:
    paths = [p for pat in patterns for p in glob.glob(pat)]
    if not paths:
        print("no workbooks matched", file=sys.stderr)
        return 1
    rows = [analyse(p) for p in paths]
    w = csv.DictWriter(sys.stdout, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
