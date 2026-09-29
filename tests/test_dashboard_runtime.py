from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from app import dashboard


def test_dashboard_aggregates_error_breakdown_and_runtime_metrics(
    monkeypatch, tmp_path: Path
) -> None:
    log_path = tmp_path / "logs.jsonl"
    now = datetime(2026, 9, 29, 3, 0, tzinfo=timezone.utc)
    records = [
        {
            "ts": "2026-09-29T02:59:00Z",
            "event": "request_received",
        },
        {
            "ts": "2026-09-29T02:59:02Z",
            "event": "request_failed",
            "error_type": "RuntimeError",
            "tool_success": False,
        },
        {
            "ts": "2026-09-29T02:59:10Z",
            "event": "request_received",
        },
        {
            "ts": "2026-09-29T02:59:11Z",
            "event": "response_sent",
            "latency_ms": 1000,
            "ttft_ms": 100,
            "cost_usd": 0.01,
            "tokens_in": 20,
            "tokens_out": 30,
            "quality_score": 0.8,
            "tool_success": True,
        },
    ]
    log_path.write_text(
        "\n".join(json.dumps(record) for record in records) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(dashboard, "LOG_PATH", log_path)

    result = dashboard.dashboard_data(now)
    panels = {panel["id"]: panel for panel in result["panels"]}

    assert panels["errors"]["values"] == {
        "Error rate": 50.0,
        "Retrieval success": 50.0,
    }
    assert panels["errors"]["breakdown"] == {"RuntimeError": 1}
    assert panels["latency"]["values"]["P95"] == 1000.0
    assert panels["cost"]["values"]["Total"] == 0.01
    assert panels["tokens"]["values"] == {"Input": 20, "Output": 30}
    assert panels["quality"]["values"]["Mean"] == 0.8
