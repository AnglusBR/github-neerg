from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .activity import fetch_public_events
from .ai import review_with_github_models
from .report import fallback_review, render_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gera relatórios a partir de atividade GitHub real")
    parser.add_argument("--username", required=True)
    parser.add_argument("--period", choices=("daily", "weekly"), default="daily")
    parser.add_argument("--output", type=Path, default=Path("."))
    parser.add_argument("--ai-token", default=os.getenv("GITHUB_TOKEN", ""))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    days = 1 if args.period == "daily" else 7
    date_key = datetime.now(ZoneInfo("America/Sao_Paulo")).date().isoformat()
    events = fetch_public_events(args.username, days=days, token=args.ai_token or None)

    data_dir = args.output / "data"
    report_dir = args.output / "reports" / args.period
    ai_dir = args.output / "reports" / "ai"
    data_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    ai_dir.mkdir(parents=True, exist_ok=True)

    snapshot = {
        "username": args.username,
        "period": args.period,
        "date": date_key,
        "events": events,
    }
    serialized = json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    (data_dir / f"{args.period}-latest.json").write_text(serialized, encoding="utf-8")

    report = render_report(args.username, events, args.period, date_key)
    report_path = report_dir / f"{date_key}.md"
    report_path.write_text(report, encoding="utf-8")

    fingerprint = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    state_path = data_dir / "ai-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
    state_key = f"{args.period}:{date_key}"

    if state.get(state_key) != fingerprint:
        review = fallback_review(events)
        if args.ai_token and events:
            try:
                review = review_with_github_models(report, args.ai_token)
            except Exception as exc:  # o relatório factual não deve falhar se a IA estiver indisponível
                print(f"GitHub Models indisponível: {exc}")
        (ai_dir / f"{args.period}-{date_key}.md").write_text(
            f"# Revisão de engenharia — {date_key}\n\n{review}", encoding="utf-8"
        )
        state[state_key] = fingerprint
        state_path.write_text(
            json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    print(f"Relatório atualizado: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

