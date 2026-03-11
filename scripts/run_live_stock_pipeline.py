from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STEPS = [
    "scripts/fetch_alpaca_stock_snapshot.py",
    "scripts/build_stock_signal_report.py",
    "scripts/risk_gate_and_position_sizing.py",
    "scripts/execute_alpaca_orders.py",
    "scripts/export_submission_artifacts.py",
    "scripts/compute_eval_metrics.py",
]


def main() -> None:
    for step in STEPS:
        print(f"[run] {step}")
        cp = subprocess.run([sys.executable, str(ROOT / step)], cwd=ROOT)
        if cp.returncode != 0:
            raise SystemExit(f"step failed: {step}")
    print("[ok] live stock pipeline done")


if __name__ == "__main__":
    main()
