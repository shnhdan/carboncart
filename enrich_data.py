"""
CarbonCart Data Pipeline
========================
Reads raw emissions.json, enriches it with:
- Percentile rankings per category
- Eco-score (A-F grade)
- Comparison benchmarks (e.g., "equivalent to driving X km")
- Summary stats for dashboard

Outputs enriched JSON to public/emissions_enriched.json
Runs on GitHub Actions on schedule or on push.
"""

import json
import os
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
INPUT = ROOT / "data" / "emissions.json"
OUTPUT = ROOT / "public" / "emissions_enriched.json"

# ── Benchmarks ────────────────────────────────────────────────────────────────
# 1 km petrol car = 0.21 kg CO2
# 1 hour avg electricity = 0.43 kg CO2
# 1 plastic bag = 0.008 kg CO2
KM_CAR_PER_KG   = 1 / 0.21       # km per 1 kg CO2
TREE_YEARS_PER_KG = 1 / 21.77    # one tree absorbs ~21.77 kg/year
AVG_PERSON_ANNUAL_KG = 4000       # global average annual footprint (consumer goods only)


def eco_grade(kg_co2: float, category_max: float) -> str:
    """Return A–F eco grade based on how bad this item is relative to category."""
    ratio = kg_co2 / max(category_max, 1)
    if ratio <= 0.1:  return "A"
    if ratio <= 0.25: return "B"
    if ratio <= 0.45: return "C"
    if ratio <= 0.65: return "D"
    if ratio <= 0.85: return "E"
    return "F"


def comparisons(kg_co2: float) -> dict:
    return {
        "car_km":       round(kg_co2 * KM_CAR_PER_KG, 1),
        "tree_months":  round(kg_co2 * TREE_YEARS_PER_KG * 12, 1),
        "pct_annual":   round((kg_co2 / AVG_PERSON_ANNUAL_KG) * 100, 2),
    }


def percentile_rank(value: float, all_values: list[float]) -> int:
    """Return 0–100 percentile rank (higher = worse/more carbon)."""
    below = sum(1 for v in all_values if v < value)
    return round((below / len(all_values)) * 100) if all_values else 0


def enrich(data: dict) -> dict:
    enriched = {
        "meta": {
            **data.get("meta", {}),
            "pipeline_version": "1.1.0",
            "avg_person_annual_kg": AVG_PERSON_ANNUAL_KG,
        },
        "version": data["version"],
        "last_updated": data["last_updated"],
        "source": data["source"],
        "categories": {}
    }

    # Gather all values across ALL categories for global percentile
    all_values = []
    for cat in data["categories"].values():
        for item in cat["items"].values():
            all_values.append(item["kg_co2"])

    for cat_key, cat in data["categories"].items():
        items = cat["items"]
        category_values = [i["kg_co2"] for i in items.values()]
        cat_max = max(category_values)
        cat_min = min(category_values)
        cat_avg = sum(category_values) / len(category_values)

        enriched_items = {}
        for item_key, item in items.items():
            kg = item["kg_co2"]
            enriched_items[item_key] = {
                **item,
                "eco_grade": eco_grade(kg, cat_max),
                "comparisons": comparisons(kg),
                "category_percentile": percentile_rank(kg, category_values),
                "global_percentile": percentile_rank(kg, all_values),
            }

        enriched["categories"][cat_key] = {
            **{k: v for k, v in cat.items() if k != "items"},
            "stats": {
                "max_kg": cat_max,
                "min_kg": cat_min,
                "avg_kg": round(cat_avg, 2),
                "item_count": len(items),
            },
            "items": enriched_items,
        }

    # Global summary
    enriched["summary"] = {
        "total_products": len(all_values),
        "global_max_kg": max(all_values),
        "global_min_kg": min(all_values),
        "global_avg_kg": round(sum(all_values) / len(all_values), 2),
        "category_count": len(data["categories"]),
    }

    return enriched


def main():
    print(f"📂 Reading {INPUT}")
    with open(INPUT) as f:
        raw = json.load(f)

    print("⚙️  Enriching data...")
    result = enrich(raw)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(result, f, indent=2)

    print(f"✅ Written to {OUTPUT}")
    print(f"   {result['summary']['total_products']} products across {result['summary']['category_count']} categories")
    print(f"   Global avg: {result['summary']['global_avg_kg']} kg CO₂")


if __name__ == "__main__":
    main()
