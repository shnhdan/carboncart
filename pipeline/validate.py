"""
CarbonCart — DE Feature 1: Data Quality & Validation Layer
===========================================================
Validates emissions.json before it enters the pipeline.
- Outlier detection using IQR per category
- Schema completeness checks
- Confidence scoring per item
- Outputs: data_quality_report.json
- CI fails if overall score < 80
"""

import json
import statistics
from pathlib import Path
from datetime import datetime

ROOT   = Path(__file__).parent.parent
INPUT  = ROOT / "data" / "emissions.json"
OUTPUT = ROOT / "public" / "data_quality_report.json"


def iqr_bounds(values: list[float]) -> tuple[float, float]:
    s = sorted(values)
    n = len(s)
    q1 = s[n // 4]
    q3 = s[(3 * n) // 4]
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr


REQUIRED_FIELDS = {"label", "kg_co2", "tip"}


def validate(data: dict) -> dict:
    results = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "schema_version": data.get("version", "unknown"),
        "overall_score": 0,
        "total_items": 0,
        "passed": 0,
        "warnings": 0,
        "failures": 0,
        "categories": {}
    }

    all_issues = []

    for cat_key, cat in data["categories"].items():
        items = cat["items"]
        values = [item["kg_co2"] for item in items.values()]
        lo, hi = iqr_bounds(values)
        cat_avg = statistics.mean(values)
        cat_std = statistics.stdev(values) if len(values) > 1 else 0

        cat_result = {
            "label": cat["label"],
            "item_count": len(items),
            "avg_kg": round(cat_avg, 2),
            "std_kg": round(cat_std, 2),
            "iqr_lower": round(lo, 2),
            "iqr_upper": round(hi, 2),
            "items": {}
        }

        for item_key, item in items.items():
            checks = []
            score = 100

            # 1. Schema completeness
            missing = REQUIRED_FIELDS - set(item.keys())
            if missing:
                checks.append({"level": "FAIL", "msg": f"Missing fields: {missing}"})
                score -= 40
            else:
                checks.append({"level": "PASS", "msg": "All required fields present"})

            # 2. CO2 value sanity
            kg = item.get("kg_co2", 0)
            if kg <= 0:
                checks.append({"level": "FAIL", "msg": "kg_co2 must be positive"})
                score -= 30
            elif kg < 0.1:
                checks.append({"level": "WARN", "msg": "Suspiciously low value (<0.1 kg)"})
                score -= 10
            else:
                checks.append({"level": "PASS", "msg": "CO₂ value in valid range"})

            # 3. Outlier detection (IQR)
            if kg > hi:
                checks.append({"level": "WARN", "msg": f"Outlier: {kg} kg > upper fence {round(hi,1)} kg"})
                score -= 10
            elif kg < lo and lo > 0:
                checks.append({"level": "WARN", "msg": f"Outlier: {kg} kg < lower fence {round(lo,1)} kg"})
                score -= 10
            else:
                checks.append({"level": "PASS", "msg": "Value within IQR bounds"})

            # 4. Tip quality
            tip = item.get("tip", "")
            if len(tip) < 20:
                checks.append({"level": "WARN", "msg": "Tip is too short (<20 chars)"})
                score -= 10
            else:
                checks.append({"level": "PASS", "msg": "Tip meets length requirement"})

            # 5. Confidence level
            if score >= 90:   confidence = "high"
            elif score >= 70: confidence = "medium"
            else:             confidence = "low"

            status = "PASS" if score >= 70 else "FAIL"

            item_result = {
                "label": item.get("label", item_key),
                "kg_co2": kg,
                "score": max(score, 0),
                "status": status,
                "confidence": confidence,
                "checks": checks
            }

            cat_result["items"][item_key] = item_result
            results["total_items"] += 1

            if status == "PASS":
                results["passed"] += 1
            else:
                results["failures"] += 1
                all_issues.append(f"{cat_key}/{item_key}: score={score}")

            warn_count = sum(1 for c in checks if c["level"] == "WARN")
            results["warnings"] += warn_count

        results["categories"][cat_key] = cat_result

    # Overall score = % items passing
    total = results["total_items"]
    results["overall_score"] = round((results["passed"] / total) * 100, 1) if total else 0
    results["overall_status"] = "PASS" if results["overall_score"] >= 80 else "FAIL"
    results["issues_summary"] = all_issues

    return results


def main():
    print(f"🔍 Validating {INPUT}")
    with open(INPUT) as f:
        raw = json.load(f)

    report = validate(raw)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(report, f, indent=2)

    score = report["overall_score"]
    status = report["overall_status"]
    print(f"{'✅' if status == 'PASS' else '❌'} Quality Score: {score}/100 [{status}]")
    print(f"   Items: {report['passed']} passed · {report['failures']} failed · {report['warnings']} warnings")

    if status == "FAIL":
        print("\n🚨 Issues found:")
        for issue in report["issues_summary"]:
            print(f"   → {issue}")
        raise SystemExit(1)  # Fail the CI build

    print(f"✅ Written to {OUTPUT}")


if __name__ == "__main__":
    main()
