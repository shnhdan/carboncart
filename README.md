

# 🛒 CarbonCart — Know Your Footprint Before You Buy

> Built for **Dev Season of Code 2026** | Themes: Sustainability · Data Engineering · Social Good

[![Pipeline](https://img.shields.io/github/actions/workflow/status/shnhdan/carboncart/pipeline.yml?label=pipeline\&style=flat-square)](https://github.com/shnhdan/carboncart/actions)
[![Live Demo](https://img.shields.io/badge/live-demo-00ff7f?style=flat-square)](https://shnhdan.github.io/carboncart)

---

## 🌍 What is CarbonCart?

CarbonCart shows the **CO₂ cost of everyday products** before you buy.
Add items to your cart, see your total emissions, eco-grades (A–F), real-world comparisons, and smarter alternatives — instantly.

---

## 🏗 Architecture

```
emissions.json (raw data)
        ↓
[1] validate.py      → data_quality_report.json
        ↓
[2] enrich_data.py   → emissions_enriched.json
        ↓
[3] snapshot.py      → snapshots/YYYY-MM-DD.json
                     → trends.json
        ↓
[4] aggregate.py     → stats_table.json
        ↓
GitHub Pages → index.html (3-tab UI)
```

---

## ⚙️ Key Data Engineering Features

### ✅ Data Validation

* IQR-based outlier detection per category
* Schema checks (required fields + positive values)
* Confidence scoring per item
* CI fails if overall quality score < 80

### 📈 Historical Snapshots

* Saves `snapshots/YYYY-MM-DD.json` on each run
* Tracks average CO₂, product count, grade distribution
* Generates `trends.json` for time-series charts
* Runs weekly via GitHub Actions

### 📊 Pre-computed Aggregations

* Top 10 greenest & worst products
* Smart substitution table (“swap X for Y, save Z kg”)
* Grade distribution (A–F)
* Category comparison metrics
* All served as static JSON for fast performance

---

## 📁 Project Structure

```
carboncart/
├── data/                 # Raw emissions dataset
├── pipeline/             # Validation, enrichment, snapshot, aggregation
├── public/               # UI + generated JSON outputs
├── snapshots/            # Historical data
├── tests/                # Automated pipeline tests
└── .github/workflows/    # CI/CD pipeline
```

---

## 💻 Local Development

```bash
python3 pipeline/validate.py
python3 pipeline/enrich_data.py
python3 pipeline/snapshot.py
python3 pipeline/aggregate.py
python3 tests/test_all.py
cd public && python3 -m http.server 8080
```

---

## 📊 UI Tabs

| Tab              | Description                                       |
| ---------------- | ------------------------------------------------- |
| 🛒 Shop          | Cart, eco-grades, comparisons, emission breakdown |
| 📊 Data Explorer | Leaderboards, substitutions, grade distribution   |
| ✅ Quality Report | Validation scores, outlier flags, CI status       |

---

MIT License · Data sources: EPA · ADEME · OpenLCA

---

If you want a more aggressive, recruiter-optimized README (less explanation, more impact), I can rewrite it sharper.
