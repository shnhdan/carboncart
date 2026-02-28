# 🛒 CarbonCart — Know Your Footprint Before You Buy

> A data-driven product carbon calculator built for **Dev Season of Code 2026**

[![Deploy Status](https://img.shields.io/github/actions/workflow/status/YOUR_USERNAME/carboncart/pipeline.yml?label=pipeline&style=flat-square)](https://github.com/YOUR_USERNAME/carboncart/actions)
[![Live Demo](https://img.shields.io/badge/live-demo-3dff8f?style=flat-square)](https://YOUR_USERNAME.github.io/carboncart)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

---

## 🌍 What is CarbonCart?

CarbonCart is a web tool that lets you see the **CO₂ equivalent** of everyday products — electronics, clothing, food, transport, and home goods — before making a purchase decision.

Add items to your cart, get an instant carbon total, see how it compares to real-world equivalents (car km, tree months), and get eco-grades (A–F) with tips to reduce your impact.

**The goal:** make carbon data as intuitive as a price tag.

---

## 🔥 Features

| Feature | Description |
|---|---|
| 🗂 **44 Products, 5 Categories** | Electronics, clothing, food, transport, home |
| 📊 **Eco Grade (A–F)** | Instant visual grade per product |
| 🔢 **Data Pipeline** | Python pipeline enriches raw data with percentiles, grades, comparisons |
| 📉 **Cart Breakdown** | Bar chart showing your biggest offenders |
| 🌳 **Real Comparisons** | Car km, tree months, % of annual budget |
| 🔄 **Auto-deploy** | GitHub Actions runs pipeline + deploys to Pages on every push |
| ✅ **Tested** | Pipeline has unit tests |

---

## 🏗 Project Structure

```
carboncart/
├── data/
│   └── emissions.json          # Raw emissions database (source of truth)
├── pipeline/
│   └── enrich_data.py          # Data engineering pipeline
├── public/
│   ├── index.html              # Frontend app (zero dependencies)
│   └── emissions_enriched.json # Pipeline output (auto-generated)
├── tests/
│   └── test_pipeline.py        # Pipeline unit tests
├── .github/
│   └── workflows/
│       └── pipeline.yml        # CI/CD: run pipeline + deploy to Pages
└── README.md
```

---

## ⚙️ Data Pipeline (The DE Feature)

The raw `emissions.json` contains product labels and base CO₂ values. The **Python pipeline** enriches this into a production-ready dataset with:

- **Eco Grade (A–F):** based on a product's kg CO₂ relative to the worst in its category
- **Category Percentile:** where the item ranks within its category
- **Global Percentile:** where it ranks across all 44 products
- **Real-world comparisons:** car km, tree months, % of annual carbon budget
- **Category stats:** min, max, avg per category

```python
# Example: running the pipeline locally
python3 pipeline/enrich_data.py
# → Reads: data/emissions.json
# → Writes: public/emissions_enriched.json
```

This runs **automatically on GitHub Actions** on every push to `main` and on a weekly schedule.

---

## 🚀 Setup — 100% Free, No Local Install Needed

### Option A: Fork & Deploy (5 minutes)

1. **Fork this repo** on GitHub
2. Go to **Settings → Pages** → set source to `gh-pages` branch
3. Go to **Actions** → enable workflows
4. Push any change to trigger the pipeline
5. Your app is live at `https://YOUR_USERNAME.github.io/carboncart`

That's it. GitHub Actions handles everything else for free.

### Option B: Run Locally

```bash
git clone https://github.com/YOUR_USERNAME/carboncart
cd carboncart

# Run the data pipeline
python3 pipeline/enrich_data.py

# Run tests
python3 tests/test_pipeline.py

# Serve the app
cd public && python3 -m http.server 8080
# → Open http://localhost:8080
```

---

## 📡 GitHub Actions CI/CD

The workflow (`.github/workflows/pipeline.yml`) does:

```
Push to main
    ↓
Run Python pipeline (enrich_data.py)
    ↓
Verify output integrity
    ↓
Commit enriched JSON back to repo
    ↓
Deploy public/ folder to GitHub Pages
```

Triggers: push to `main`, weekly schedule (Sunday midnight), manual dispatch.

---

## 📊 Data Sources

| Source | Used For |
|---|---|
| [EPA Emission Factors](https://www.epa.gov/climateleadership/ghg-emission-factors-hub) | Transport, energy |
| [ADEME Base Carbone](https://www.bilans-ges.ademe.fr/) | Food, clothing, home goods |
| [MacroTrends Open LCA](https://www.openlca.org/) | Electronics lifecycle |
| [Our World in Data](https://ourworldindata.org/food-choice-vs-eating-local) | Food comparisons |

All data is compiled into `data/emissions.json` — a single source of truth with clear provenance.

---

## 🧪 Tests

```bash
python3 tests/test_pipeline.py
# ✅ test_eco_grade passed
# ✅ test_comparisons passed  
# ✅ test_percentile_rank passed
# ✅ test_full_pipeline passed (44 products)
# 🎉 All tests passed!
```

---

## 🗺 Roadmap (Post-Hackathon)

- [ ] Browser extension (detect products on Amazon/Tesco in real-time)
- [ ] More products via Open Food Facts API
- [ ] User accounts to track footprint over time
- [ ] Shareable cart links
- [ ] Country-specific electricity grid emissions

---

## 🤝 Contributing

PRs welcome. To add products, edit `data/emissions.json` and run the pipeline. Follow the existing schema exactly.

---

## 📄 License

MIT License — free to use, fork, and build on.

---

*Built with 💚 for [Dev Season of Code 2026](https://dev-season-of-code.devpost.com)*
