# 🛒 CarbonCart — Know Your Footprint Before You Buy

> Built for **Dev Season of Code 2026** | Themes: AI/ML · Data Science · Sustainability · Social Good

[![Pipeline](https://img.shields.io/github/actions/workflow/status/shnhdan/carboncart/pipeline.yml?label=pipeline&style=flat-square)](https://github.com/shnhdan/carboncart/actions)
[![Live Demo](https://img.shields.io/badge/live-demo-00ff7f?style=flat-square)](https://shnhdan.github.io/carboncart)

---

## 🌍 What is CarbonCart?

CarbonCart shows you the **CO₂ cost** of everyday purchases — before you buy. Add products to your cart, see your total carbon footprint, get eco-grades (A–F), real-world comparisons, and smarter alternatives.

---

## 🏗 Architecture

```
emissions.json (raw data)
        ↓
[1] validate.py      → data_quality_report.json   (DE Feature 1)
        ↓
[2] enrich_data.py   → emissions_enriched.json    (Core Pipeline)
        ↓
[3] snapshot.py      → snapshots/YYYY-MM-DD.json  (DE Feature 2)
                     → trends.json
        ↓
[4] aggregate.py     → stats_table.json            (DE Feature 3)
        ↓
GitHub Pages → index.html (3-tab UI)
```

---

## ⚙️ Data Engineering Features

### DE Feature 1 — Data Quality Validation
- IQR-based outlier detection per category
- Schema completeness checks (required fields, positive values)
- Confidence scoring per item (high / medium / low)
- CI **fails the build** if overall quality score < 80
- Output: `public/data_quality_report.json` → visualised in **Quality Report** tab

### DE Feature 2 — Historical Snapshots & Trends
- Every pipeline run saves `snapshots/YYYY-MM-DD.json`
- Tracks: avg CO₂, product count, grade distribution over time
- Generates `trends.json` with chart-ready time series data
- Runs weekly on schedule via GitHub Actions cron

### DE Feature 3 — Pre-computed Aggregations
- Global leaderboard: top 10 greenest & worst products
- Substitution table: "swap X for Y, save Z kg" per category
- Category vs category CO₂ comparison matrix
- Grade band distribution (A–F counts)
- All served as static JSON — fast, no runtime compute
- Output: `public/stats_table.json` → visualised in **Data Explorer** tab

---

## 📁 Project Structure

```
carboncart/
├── data/
│   └── emissions.json              # Raw source of truth (44 products)
├── pipeline/
│   ├── validate.py                 # DE1: Quality & validation
│   ├── enrich_data.py              # Core: Enrichment pipeline
│   ├── snapshot.py                 # DE2: Historical snapshots
│   └── aggregate.py                # DE3: Pre-computed stats
├── public/
│   ├── index.html                  # Full 3-tab UI
│   ├── emissions_enriched.json     # Pipeline output
│   ├── stats_table.json            # Aggregation output
│   ├── data_quality_report.json    # Validation output
│   └── trends.json                 # Trend tracker output
├── snapshots/
│   └── YYYY-MM-DD.json             # Historical snapshots
├── tests/
│   └── test_all.py                 # 9 tests covering all pipelines
└── .github/workflows/
    └── pipeline.yml                # CI/CD: all 4 steps + deploy
```

---

## 🚀 Deploy (100% Free)

1. Fork this repo
2. Settings → Pages → source: `gh-pages` branch
3. Actions tab → enable workflows → Run workflow
4. Live at: `https://YOUR_USERNAME.github.io/carboncart`

### Local Dev

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

| Tab | What it shows |
|---|---|
| 🛒 Shop | Product grid, eco-grades, cart, comparisons, breakdown |
| 📊 Data Explorer | Leaderboard, substitutions, grade dist, cross-category ratios |
| ✅ Quality Report | Per-item validation scores, IQR outlier flags, CI status |

---

*MIT License · Data: EPA · ADEME · Open LCA*
