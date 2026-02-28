"""
CarbonCart — DE Feature 2: Historical Snapshots & Trend Tracking
================================================================
Every pipeline run saves a timestamped snapshot of the enriched data.
Generates trends.json showing dataset evolution over time.
Outputs: public/trends.json, snapshots/YYYY-MM-DD.json
"""

import json
import shutil
from pathlib import Path
from datetime import datetime, date

ROOT      = Path(__file__).parent.parent
ENRICHED  = ROOT / "public" / "emissions_enriched.json"
SNAPSHOTS = ROOT / "snapshots"
TRENDS    = ROOT / "public" / "trends.json"


def save_snapshot() -> str:
    """Save today's enriched data as a dated snapshot."""
    today = date.today().isoformat()
    snap_path = SNAPSHOTS / f"{today}.json"
    SNAPSHOTS.mkdir(exist_ok=True)

    with open(ENRICHED) as f:
        data = json.load(f)

    # Lightweight snapshot — just the stats, not every item detail
    snap = {
        "date": today,
        "schema_version": data.get("version"),
        "pipeline_version": data.get("meta", {}).get("pipeline_version"),
        "total_products": data["summary"]["total_products"],
        "category_count": data["summary"]["category_count"],
        "global_avg_kg": data["summary"]["global_avg_kg"],
        "global_max_kg": data["summary"]["global_max_kg"],
        "global_min_kg": data["summary"]["global_min_kg"],
        "category_avgs": {
            k: v["stats"]["avg_kg"]
            for k, v in data["categories"].items()
        },
        "grade_distribution": _grade_distribution(data),
    }

    with open(snap_path, "w") as f:
        json.dump(snap, f, indent=2)

    print(f"📸 Snapshot saved: {snap_path.name}")
    return today


def _grade_distribution(data: dict) -> dict:
    """Count how many items fall in each grade band A-F."""
    dist = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0}
    for cat in data["categories"].values():
        for item in cat["items"].values():
            g = item.get("eco_grade", "F")
            if g in dist:
                dist[g] += 1
    return dist


def build_trends() -> dict:
    """Read all snapshots and build a trends timeline."""
    SNAPSHOTS.mkdir(exist_ok=True)
    snap_files = sorted(SNAPSHOTS.glob("*.json"))

    if not snap_files:
        return {"generated_at": datetime.utcnow().isoformat() + "Z", "snapshots": [], "insights": {}}

    timeline = []
    for f in snap_files:
        with open(f) as fp:
            timeline.append(json.load(fp))

    # Insights: compare latest vs earliest
    first, last = timeline[0], timeline[-1]
    insights = {}

    if len(timeline) >= 2:
        avg_delta = round(last["global_avg_kg"] - first["global_avg_kg"], 2)
        prod_delta = last["total_products"] - first["total_products"]
        insights = {
            "avg_co2_change": avg_delta,
            "avg_co2_trend": "increased" if avg_delta > 0 else "decreased" if avg_delta < 0 else "stable",
            "products_added": prod_delta,
            "tracked_since": first["date"],
            "latest_update": last["date"],
            "total_snapshots": len(timeline),
        }
    else:
        insights = {
            "tracked_since": first["date"],
            "latest_update": last["date"],
            "total_snapshots": len(timeline),
            "note": "Need 2+ snapshots for trend analysis"
        }

    trends = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "insights": insights,
        "snapshots": timeline,
        "chart_data": {
            "labels": [s["date"] for s in timeline],
            "global_avg": [s["global_avg_kg"] for s in timeline],
            "total_products": [s["total_products"] for s in timeline],
            "grade_A_count": [s["grade_distribution"].get("A", 0) for s in timeline],
            "grade_F_count": [s["grade_distribution"].get("F", 0) for s in timeline],
        }
    }

    return trends


def main():
    print("📊 Running snapshot & trend tracker...")

    if not ENRICHED.exists():
        print("⚠️  emissions_enriched.json not found — run enrich_data.py first")
        raise SystemExit(1)

    today = save_snapshot()
    trends = build_trends()

    with open(TRENDS, "w") as f:
        json.dump(trends, f, indent=2)

    snaps = len(trends["snapshots"])
    print(f"✅ Trends written → {TRENDS.name} ({snaps} snapshot{'s' if snaps != 1 else ''})")
    if "avg_co2_change" in trends["insights"]:
        d = trends["insights"]["avg_co2_change"]
        print(f"   Avg CO₂ {'▲' if d > 0 else '▼'} {abs(d)} kg since {trends['insights']['tracked_since']}")


if __name__ == "__main__":
    main()
