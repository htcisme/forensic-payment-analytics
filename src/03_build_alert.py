"""Run SQL summaries, R1/R2/R3, sensitivity comparisons and the review queue."""
from pathlib import Path
import argparse
import json
from rule_engine import run_pipeline

ROOT = Path(__file__).resolve().parent.parent

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=ROOT / "data/processed/forensic.sqlite")
    parser.add_argument("--output", type=Path, default=ROOT / "reports")
    args = parser.parse_args()
    result = run_pipeline(args.db, args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"Saved reports to: {args.output.resolve()}")
