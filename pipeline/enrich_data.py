"""
CarbonCart — Core Enrichment Pipeline
======================================
Reads raw emissions.json → outputs enriched emissions_enriched.json
"""

import json
from pathlib import Path
from datetime import datetime

ROOT   = Path(__file__).parent.parent
INPUT  = ROOT / "data" / "emissions.json"
OUTPUT = ROOT / "public" / "emissions_enriched.json"

KM_PER_KG     = 1 / 0.21
TREE_YEARS_PER_KG = 1 / 21.77
AVG_ANNUAL_KG = 4000


def eco_grade(kg: float, cat_max: float) -> str:
    r = kg / max(cat_max, 1)
    if r <= 0.10: return "A"
    if r <= 0.25: return "B"
    if r <= 0.45: return "C"
    if r <= 0.65: return "D"
    if r <= 0.85: return "E"
    return "F"


def comparisons(kg: float) -> dict:
    return {
        "car_km":      round(kg * KM_PER_KG, 1),
        "tree_months": round(kg * TREE_YEARS_PER_KG * 12, 1),
        "pct_annual":  round((kg / AVG_ANNUAL_KG) * 100, 2),
    }


def percentile_rank(value: float, values: list) -> int:
    below = sum(1 for v in values if v < value)
    return round((below / len(values)) * 100) if values else 0


def enrich(data: dict) -> dict:
    all_values = [i["kg_co2"] for c in data["categories"].values() for i in c["items"].values()]

    enriched = {
        "meta": {"pipeline_version": "2.0.0", "avg_person_annual_kg": AVG_ANNUAL_KG,
                 "generated_at": datetime.utcnow().isoformat() + "Z"},
        "version": data["version"],
        "last_updated": data["last_updated"],
        "source": data["source"],
        "categories": {}
    }

    for cat_key, cat in data["categories"].items():
        items = cat["items"]
        vals  = [i["kg_co2"] for i in items.values()]
        cat_max = max(vals)

        enriched_items = {}
        for ik, item in items.items():
            kg = item["kg_co2"]
            enriched_items[ik] = {
                **item,
                "eco_grade": eco_grade(kg, cat_max),
                "comparisons": comparisons(kg),
                "category_percentile": percentile_rank(kg, vals),
                "global_percentile":   percentile_rank(kg, all_values),
                "lineage": {
                    "source": data["source"],
                    "pipeline_version": "2.0.0",
                    "generated_at": datetime.utcnow().isoformat() + "Z",
                    "confidence": "high" if kg > 0.5 else "medium",
                }
            }

        enriched["categories"][cat_key] = {
            **{k: v for k, v in cat.items() if k != "items"},
            "stats": {
                "max_kg": max(vals), "min_kg": min(vals),
                "avg_kg": round(sum(vals)/len(vals), 2), "item_count": len(items)
            },
            "items": enriched_items,
        }

    enriched["summary"] = {
        "total_products": len(all_values),
        "global_max_kg": max(all_values),
        "global_min_kg": min(all_values),
        "global_avg_kg": round(sum(all_values)/len(all_values), 2),
        "category_count": len(data["categories"]),
    }
    return enriched


def main():
    print(f"⚙️  Enriching {INPUT.name}...")
    with open(INPUT) as f:
        raw = json.load(f)

    result = enrich(raw)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(result, f, indent=2)

    print(f"✅ Enriched → {OUTPUT.name} ({result['summary']['total_products']} products)")


if __name__ == "__main__":
    main()
