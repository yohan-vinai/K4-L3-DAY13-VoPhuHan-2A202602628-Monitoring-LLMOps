from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from statistics import mean
from typing import Any

from .logging_config import LOG_PATH
from .metrics import percentile


def _read_recent_logs(now: datetime) -> tuple[list[dict[str, Any]], list[datetime]]:
    if not LOG_PATH.exists():
        return [], []
    cutoff = now - timedelta(minutes=60)
    records: list[dict[str, Any]] = []
    times: list[datetime] = []
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
            timestamp = datetime.fromisoformat(str(record["ts"]).replace("Z", "+00:00"))
        except (KeyError, ValueError, json.JSONDecodeError):
            continue
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        if cutoff <= timestamp <= now:
            records.append(record)
            times.append(timestamp)
    return records, times


def dashboard_data(now: datetime | None = None) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    records, timestamps = _read_recent_logs(now)
    start = now.replace(second=0, microsecond=0) - timedelta(minutes=59)
    buckets: list[list[dict[str, Any]]] = [[] for _ in range(60)]
    for record, timestamp in zip(records, timestamps):
        index = int((timestamp.replace(second=0, microsecond=0) - start).total_seconds() // 60)
        if 0 <= index < 60:
            buckets[index].append(record)

    received = [r for r in records if r.get("event") == "request_received"]
    responses = [r for r in records if r.get("event") == "response_sent"]
    failures = [r for r in records if r.get("event") == "request_failed"]
    error_breakdown = dict(
        Counter(str(r.get("error_type", "unknown")) for r in failures)
    )
    latency = [int(r["latency_ms"]) for r in responses if isinstance(r.get("latency_ms"), (int, float))]
    ttft = [int(r["ttft_ms"]) for r in responses if isinstance(r.get("ttft_ms"), (int, float))]
    retrieval = [r["tool_success"] for r in records if isinstance(r.get("tool_success"), bool)]

    def series(value_fn):
        return [value_fn(items) for items in buckets]

    def cumulative_series(value_fn):
        total = 0.0
        result = []
        for items in buckets:
            total += value_fn(items)
            result.append(round(total, 6))
        return result

    error_rate = (len(failures) / len(received) * 100) if received else 0.0
    retrieval_success = (sum(retrieval) / len(retrieval) * 100) if retrieval else 0.0
    costs = [float(r.get("cost_usd", 0) or 0) for r in responses]
    tokens_in = sum(int(r.get("tokens_in", 0) or 0) for r in responses)
    tokens_out = sum(int(r.get("tokens_out", 0) or 0) for r in responses)
    qualities = [float(r["quality_score"]) for r in responses if isinstance(r.get("quality_score"), (int, float))]

    return {
        "generated_at": now.isoformat(),
        "time_range_minutes": 60,
        "panels": [
            {"id": "latency", "title": "Latency percentiles and TTFT", "unit": "ms",
             "threshold": "P95 ≤ 3000 ms", "threshold_value": 3000, "values": {"P50": percentile(latency, 50), "P95": percentile(latency, 95), "P99": percentile(latency, 99), "TTFT P95": percentile(ttft, 95)},
             "series": series(lambda rows: percentile([int(r["latency_ms"]) for r in rows if r.get("event") == "response_sent" and isinstance(r.get("latency_ms"), (int, float))], 95))},
            {"id": "traffic", "title": "Request traffic", "unit": "requests/minute",
             "threshold": "At least 1 request/minute", "threshold_value": 1, "values": {"Requests": len(received), "Rate": round(len(received) / 60, 2)},
             "series": series(lambda rows: sum(r.get("event") == "request_received" for r in rows))},
            {"id": "errors", "title": "Error rate and retrieval success", "unit": "%",
             "threshold": "Errors ≤ 2%; retrieval ≥ 90%", "threshold_value": 2, "values": {"Error rate": round(error_rate, 2), "Retrieval success": round(retrieval_success, 2)},
             "breakdown": error_breakdown,
             "series": series(lambda rows: (sum(r.get("event") == "request_failed" for r in rows) / max(1, sum(r.get("event") == "request_received" for r in rows))) * 100)},
            {"id": "cost", "title": "Cost over time", "unit": "USD",
             "threshold": "≤ $2.50 in 60m", "threshold_value": 2.5, "values": {"Total": round(sum(costs), 6)},
             "series": cumulative_series(lambda rows: sum(float(r.get("cost_usd", 0) or 0) for r in rows if r.get("event") == "response_sent"))},
            {"id": "tokens", "title": "Input and output tokens", "unit": "tokens",
             "threshold": "≤ 50,000 tokens", "threshold_value": 50000, "values": {"Input": tokens_in, "Output": tokens_out},
             "series": cumulative_series(lambda rows: sum(int(r.get("tokens_in", 0) or 0) + int(r.get("tokens_out", 0) or 0) for r in rows if r.get("event") == "response_sent"))},
            {"id": "quality", "title": "Quality proxy", "unit": "score (0–1)",
             "threshold": "Mean ≥ 0.75", "threshold_value": 0.75, "values": {"Mean": round(mean(qualities), 3) if qualities else 0.0},
             "series": series(lambda rows: round(mean([float(r["quality_score"]) for r in rows if r.get("event") == "response_sent" and isinstance(r.get("quality_score"), (int, float))]), 3) if any(r.get("event") == "response_sent" and isinstance(r.get("quality_score"), (int, float)) for r in rows) else 0.0)},
        ],
    }


def dashboard_html() -> str:
    return """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Day 13 Monitoring Dashboard</title>
<style>
:root{color-scheme:dark;--bg:#0b1020;--card:#131b2e;--line:#273550;--text:#edf3ff;--muted:#91a3bf;--accent:#68d5c2}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:14px system-ui,-apple-system,sans-serif}.wrap{max-width:1320px;margin:auto;padding:28px}.top{display:flex;justify-content:space-between;align-items:center;gap:20px;margin-bottom:22px}h1{font-size:24px;margin:0 0 5px}.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;min-height:235px}.card h2{font-size:16px;margin:0 0 5px}.threshold{color:var(--muted);font-size:12px}.values{display:flex;flex-wrap:wrap;gap:16px;margin:16px 0 8px}.metric b{display:block;font-size:20px;color:var(--accent)}.metric span{font-size:11px;color:var(--muted)}.breakdown{color:var(--muted);font-size:12px;margin:6px 0}svg{width:100%;height:88px;overflow:visible}.axis{stroke:var(--line);stroke-width:1}.plot{fill:none;stroke:var(--accent);stroke-width:2}.empty{color:var(--muted);font-size:13px;padding-top:22px}@media(max-width:760px){.wrap{padding:16px}.grid{grid-template-columns:1fr}.top{align-items:flex-start;flex-direction:column}}
</style></head><body><main class="wrap"><header class="top"><div><h1>K4-L3A Day 13 · Monitoring &amp; LLMOps</h1><div class="muted">Source: scrubbed data/logs.jsonl · rolling 60 minutes · refresh 30 seconds</div></div><div id="updated" class="muted">Loading…</div></header><section id="panels" class="grid"></section></main>
<script>
function lineSvg(values,threshold){if(!values.length)return '<div class="empty">No data in this time range</div>';const w=600,h=88,p=4,max=Math.max(...values,threshold,1);const points=values.map((v,i)=>`${p+i*(w-2*p)/(values.length-1)},${h-p-(v/max)*(h-2*p)}`).join(' ');const ty=h-p-(threshold/max)*(h-2*p);return `<svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="none"><path class="axis" d="M0 ${h-1}H${w}"/><path d="M0 ${ty}H${w}" stroke="#e2a95d" stroke-dasharray="6 5"/><polyline class="plot" points="${points}"/></svg>`}
function escapeHtml(value){return String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function render(data){document.getElementById('updated').textContent='Updated '+new Date(data.generated_at).toLocaleTimeString();document.getElementById('panels').innerHTML=data.panels.map(p=>{const vals=Object.entries(p.values).map(([k,v])=>`<div class="metric"><b>${v}</b><span>${k} · ${p.unit}</span></div>`).join('');const breakdown=p.breakdown?`<div class="breakdown">Error types: ${Object.entries(p.breakdown).map(([k,v])=>`${escapeHtml(k)} (${v})`).join(', ')||'none in this time range'}</div>`:'';return `<article class="card"><h2>${p.title}</h2><div class="threshold">Threshold: ${p.threshold}</div><div class="values">${vals}</div>${breakdown}${lineSvg(p.series,p.threshold_value)}</article>`}).join('')}
async function refresh(){try{const r=await fetch('/dashboard/data',{cache:'no-store'});render(await r.json())}catch(e){document.getElementById('updated').textContent='Dashboard data unavailable'}}refresh();setInterval(refresh,30000);
</script></body></html>"""
