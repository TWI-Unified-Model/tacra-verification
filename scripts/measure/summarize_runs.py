#!/usr/bin/env python3
"""Recompute every figure of the measurement tables from the runs in docs/measurements/evidence,
with burst_stats.py, into docs/measurements/summary.json; or check that the committed summary is
what the runs give.

    python3 scripts/measure/summarize_runs.py            # write docs/measurements/summary.json
    python3 scripts/measure/summarize_runs.py --check    # exit 1 if the committed file differs

A run is a directory under evidence/; its modes are the JSON files burst_stats.py reads (the ones
that carry "drills"); instance-*.json and the other records are not statistics and are skipped.
"""
import importlib.util
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
EVIDENCE = ROOT / "docs" / "measurements" / "evidence"
SUMMARY = ROOT / "docs" / "measurements" / "summary.json"


def load_burst_stats():
    spec = importlib.util.spec_from_file_location("burst_stats", HERE / "burst_stats.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def summarize():
    burst_stats = load_burst_stats()
    summary = {}
    for run_dir in sorted(p for p in EVIDENCE.iterdir() if p.is_dir()):
        modes = {}
        for path in sorted(run_dir.glob("*.json")):
            with open(path) as f:
                if "drills" not in json.load(f):
                    continue
            modes[path.stem] = burst_stats.stats(str(path))
        summary[run_dir.name] = modes
    return summary


def main():
    summary = summarize()
    text = json.dumps(summary, indent=1, sort_keys=True) + "\n"
    if "--check" in sys.argv[1:]:
        current = SUMMARY.read_text(encoding="utf-8") if SUMMARY.exists() else ""
        if current != text:
            print(f"{SUMMARY.relative_to(ROOT)} differs from what the runs give; run summarize_runs.py and look at the diff")
            return 1
        runs = len(summary)
        modes = sum(len(m) for m in summary.values())
        print(f"summary.json is what the runs give: {runs} runs, {modes} modes")
        return 0
    SUMMARY.write_text(text, encoding="utf-8")
    print("written", SUMMARY.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
