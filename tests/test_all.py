"""
CarbonCart — Full Test Suite
Run: python3 tests/test_all.py
"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pipeline.enrich_data import enrich, eco_grade, comparisons, percentile_rank
from pipeline.validate    import validate, iqr_bounds
from pipeline.aggregate   import build_stats

# ── enrich_data tests ──────────────────────────────────────────
def test_eco_grade():
    assert eco_grade(0,100)   == "A"
    assert eco_grade(10,100)  == "A"
    assert eco_grade(30,100)  == "C"
    assert eco_grade(100,100) == "F"
    print("✅ test_eco_grade")

def test_comparisons():
    c = comparisons(21)
    assert abs(c["car_km"] - 100) < 2
    assert c["pct_annual"] > 0
    print("✅ test_comparisons")

def test_percentile_rank():
    vals = [10,20,30,40,50]
    assert percentile_rank(10,vals) == 0
    assert percentile_rank(50,vals) == 80
    print("✅ test_percentile_rank")

def test_enrich_pipeline():
    with open("data/emissions.json") as f: raw=json.load(f)
    result = enrich(raw)
    assert result["summary"]["total_products"] > 0
    for ck,cat in result["categories"].items():
        for ik,item in cat["items"].items():
            assert "eco_grade"  in item, f"Missing eco_grade on {ck}/{ik}"
            assert "comparisons" in item
            assert "lineage"     in item
            assert item["eco_grade"] in "ABCDEF"
    print(f"✅ test_enrich_pipeline ({result['summary']['total_products']} products)")

# ── validate tests ─────────────────────────────────────────────
def test_iqr_bounds():
    lo, hi = iqr_bounds([10,20,30,40,50])
    assert lo < 10
    assert hi > 50
    print("✅ test_iqr_bounds")

def test_validate_schema():
    with open("data/emissions.json") as f: raw=json.load(f)
    report = validate(raw)
    assert report["overall_score"] > 0
    assert report["overall_status"] in ("PASS","FAIL")
    assert "categories" in report
    print(f"✅ test_validate_schema (score={report['overall_score']})")

def test_validate_catches_bad_data():
    bad = {
        "version":"1.0","last_updated":"2026","source":"test","categories":{
            "test":{"label":"Test","icon":"🔬","default_kg_co2":1,"items":{
                "bad_item":{"label":"Bad","kg_co2":-1,"tip":"x"}
            }}
        }
    }
    report = validate(bad)
    assert report["failures"] > 0
    print("✅ test_validate_catches_bad_data")

# ── aggregate tests ────────────────────────────────────────────
def test_aggregate():
    with open("public/emissions_enriched.json") as f: data=json.load(f)
    stats = build_stats(data)
    assert len(stats["leaderboard"]["greenest"]) > 0
    assert len(stats["substitutions"]) > 0
    assert len(stats["cross_category_ratios"]) > 0
    assert stats["summary"]["greenest_kg"] < stats["summary"]["worst_kg"]
    print(f"✅ test_aggregate ({len(stats['substitutions'])} substitutions)")

def test_grade_distribution():
    with open("public/emissions_enriched.json") as f: data=json.load(f)
    stats = build_stats(data)
    total = sum(v["count"] for v in stats["grade_distribution"].values())
    assert total == data["summary"]["total_products"]
    print(f"✅ test_grade_distribution (total={total})")

if __name__=="__main__":
    print("Running CarbonCart test suite...\n")
    test_eco_grade()
    test_comparisons()
    test_percentile_rank()
    test_enrich_pipeline()
    test_iqr_bounds()
    test_validate_schema()
    test_validate_catches_bad_data()
    test_aggregate()
    test_grade_distribution()
    print("\n🎉 All 9 tests passed!")
