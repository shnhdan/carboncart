"""
CarbonCart — DE Feature 3: Pre-computed Stats & Aggregations Table
==================================================================
Generates a rich stats_table.json consumed by the UI's Data Explorer.
Includes:
 - Category vs category comparison matrix
 - Top 5 worst offenders per category
 - Product substitution table (if you swapped X for Y, save Z kg)
 - Grade band distribution
 - Eco score leaderboard
"""

import json
from pathlib import Path
from datetime import datetime
from itertools import combinations

ROOT     = Path(__file__).parent.parent
ENRICHED = ROOT / "public" / "emissions_enriched.json"
OUTPUT   = ROOT / "public" / "stats_table.json"


def build_stats(data: dict) -> dict:
    cats = data["categories"]

    # ── 1. Category comparison matrix ─────────────────────────────────────
    cat_matrix = {}
    for ck, cat in cats.items():
        vals = [i["kg_co2"] for i in cat["items"].values()]
        cat_matrix[ck] = {
            "label": cat["label"],
            "icon":  cat["icon"],
            "avg_kg": cat["stats"]["avg_kg"],
            "max_kg": cat["stats"]["max_kg"],
            "min_kg": cat["stats"]["min_kg"],
            "item_count": cat["stats"]["item_count"],
        }

    # Cross-category ratios: how much worse is cat A vs cat B?
    cat_keys = list(cat_matrix.keys())
    cross_ratios = []
    for a, b in combinations(cat_keys, 2):
        avg_a = cat_matrix[a]["avg_kg"]
        avg_b = cat_matrix[b]["avg_kg"]
        if avg_b > 0:
            ratio = round(avg_a / avg_b, 2)
            if ratio >= 1:
                cross_ratios.append({
                    "higher": a, "lower": b,
                    "ratio": ratio,
                    "label": f"{cat_matrix[a]['label']} avg is {ratio}× higher than {cat_matrix[b]['label']}"
                })
            else:
                inv = round(1 / ratio, 2)
                cross_ratios.append({
                    "higher": b, "lower": a,
                    "ratio": inv,
                    "label": f"{cat_matrix[b]['label']} avg is {inv}× higher than {cat_matrix[a]['label']}"
                })

    cross_ratios.sort(key=lambda x: x["ratio"], reverse=True)

    # ── 2. Top 5 worst offenders per category ──────────────────────────────
    worst_by_cat = {}
    for ck, cat in cats.items():
        sorted_items = sorted(cat["items"].items(), key=lambda x: x[1]["kg_co2"], reverse=True)
        worst_by_cat[ck] = [
            {
                "key": k,
                "label": v["label"],
                "kg_co2": v["kg_co2"],
                "eco_grade": v["eco_grade"],
                "tip": v["tip"],
            }
            for k, v in sorted_items[:5]
        ]

    # ── 3. Global leaderboard (best & worst 10) ────────────────────────────
    all_items = []
    for ck, cat in cats.items():
        for ik, item in cat["items"].items():
            all_items.append({
                "id": f"{ck}/{ik}",
                "label": item["label"],
                "category": cat["label"],
                "category_key": ck,
                "kg_co2": item["kg_co2"],
                "eco_grade": item["eco_grade"],
            })

    all_items.sort(key=lambda x: x["kg_co2"])
    leaderboard = {
        "greenest": all_items[:10],
        "worst":    list(reversed(all_items[-10:])),
    }

    # ── 4. Substitution table ──────────────────────────────────────────────
    # For each category, find "if you swap worst for best, you save X kg"
    substitutions = []
    for ck, cat in cats.items():
        items = list(cat["items"].items())
        if len(items) < 2:
            continue
        worst = max(items, key=lambda x: x[1]["kg_co2"])
        best  = min(items, key=lambda x: x[1]["kg_co2"])
        saving = round(worst[1]["kg_co2"] - best[1]["kg_co2"], 1)
        if saving > 0:
            substitutions.append({
                "category": cat["label"],
                "from_label": worst[1]["label"],
                "from_kg":    worst[1]["kg_co2"],
                "to_label":   best[1]["label"],
                "to_kg":      best[1]["kg_co2"],
                "saving_kg":  saving,
                "saving_pct": round((saving / worst[1]["kg_co2"]) * 100, 1),
                "tip":        best[1]["tip"],
            })

    substitutions.sort(key=lambda x: x["saving_kg"], reverse=True)

    # ── 5. Grade distribution ──────────────────────────────────────────────
    grade_dist = {"A": [], "B": [], "C": [], "D": [], "E": [], "F": []}
    for ck, cat in cats.items():
        for ik, item in cat["items"].items():
            g = item["eco_grade"]
            if g in grade_dist:
                grade_dist[g].append({
                    "id": f"{ck}/{ik}",
                    "label": item["label"],
                    "category": cat["label"],
                    "kg_co2": item["kg_co2"],
                })

    grade_summary = {
        g: {"count": len(items), "items": items}
        for g, items in grade_dist.items()
    }

    # ── 6. CO2 per-category breakdown (for pie chart) ──────────────────────
    category_totals = {
        ck: {
            "label": cat["label"],
            "icon":  cat["icon"],
            "total_kg": round(sum(i["kg_co2"] for i in cat["items"].values()), 1),
            "avg_kg":   cat["stats"]["avg_kg"],
        }
        for ck, cat in cats.items()
    }

    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "category_matrix": cat_matrix,
        "cross_category_ratios": cross_ratios[:8],
        "worst_by_category": worst_by_cat,
        "leaderboard": leaderboard,
        "substitutions": substitutions,
        "grade_distribution": grade_summary,
        "category_totals": category_totals,
        "summary": {
            "total_items": len(all_items),
            "greenest_item": all_items[0]["label"] if all_items else "",
            "greenest_kg":   all_items[0]["kg_co2"] if all_items else 0,
            "worst_item":    all_items[-1]["label"] if all_items else "",
            "worst_kg":      all_items[-1]["kg_co2"] if all_items else 0,
        }
    }


def main():
    print(f"📊 Building stats table from {ENRICHED.name}")

    if not ENRICHED.exists():
        print("⚠️  Run enrich_data.py first")
        raise SystemExit(1)

    with open(ENRICHED) as f:
        data = json.load(f)

    stats = build_stats(data)

    with open(OUTPUT, "w") as f:
        json.dump(stats, f, indent=2)

    print(f"✅ Stats table written → {OUTPUT.name}")
    print(f"   {len(stats['leaderboard']['greenest'])} greenest · {len(stats['substitutions'])} substitutions · {len(stats['cross_category_ratios'])} cross-ratios")
    best = stats['summary']['greenest_item']
    worst = stats['summary']['worst_item']
    print(f"   🌿 Greenest: {best} | ⚠️ Worst: {worst}")


if __name__ == "__main__":
    main()
