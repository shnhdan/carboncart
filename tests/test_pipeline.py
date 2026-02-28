"""
Tests for the CarbonCart data pipeline.
Run: python3 tests/test_pipeline.py
"""
import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pipeline.enrich_data import enrich, eco_grade, comparisons, percentile_rank

def test_eco_grade():
    assert eco_grade(0, 100) == "A"
    assert eco_grade(10, 100) == "A"
    assert eco_grade(26, 100) == "C"
    assert eco_grade(100, 100) == "F"
    print("✅ test_eco_grade passed")

def test_comparisons():
    c = comparisons(21)  # 21 kg CO2 = 100km petrol car
    assert abs(c["car_km"] - 100) < 2
    assert c["pct_annual"] > 0
    print("✅ test_comparisons passed")

def test_percentile_rank():
    vals = [10, 20, 30, 40, 50]
    assert percentile_rank(10, vals) == 0
    assert percentile_rank(50, vals) == 80
    assert percentile_rank(30, vals) == 40
    print("✅ test_percentile_rank passed")

def test_full_pipeline():
    with open("data/emissions.json") as f:
        raw = json.load(f)
    result = enrich(raw)

    assert "categories" in result
    assert "summary" in result
    assert result["summary"]["total_products"] > 0

    # Every item must have eco_grade and comparisons
    for cat_key, cat in result["categories"].items():
        for item_key, item in cat["items"].items():
            assert "eco_grade" in item, f"Missing eco_grade on {cat_key}/{item_key}"
            assert "comparisons" in item, f"Missing comparisons on {cat_key}/{item_key}"
            assert "category_percentile" in item
            assert "global_percentile" in item
            assert item["eco_grade"] in "ABCDEF"

    print(f"✅ test_full_pipeline passed ({result['summary']['total_products']} products)")

if __name__ == "__main__":
    test_eco_grade()
    test_comparisons()
    test_percentile_rank()
    test_full_pipeline()
    print("\n🎉 All tests passed!")
