# Data Analyst: Convexity & Sensitivity AI Agent

**Advanced Fixed Income Risk Analytics Platform**
A 15-day quantitative analytics project for Indian G-Sec bond portfolios.

---

## Project Overview

This project builds a complete fixed income risk analytics engine from first principles.
It covers bond pricing, Key Rate Duration (KRD), Monte Carlo simulation, machine learning pricing models, yield curve fitting, and a gamified training platform design.

| Field | Detail |
|---|---|
| Domain | Fixed Income / Quantitative Finance |
| Portfolio | 301 Indian G-Sec & Corporate Bonds |
| Valuation Date | October 31, 2024 |
| Total Market Value | INR 32,059,345.97 |
| Modified Duration | 4.2031 years |
| Convexity | 176.2455 |
| DV01 | INR 8,948.25 |

---

## Project Structure

```
Data-Analyst-Convexity-Sensitivity-AI-Agent/
│
├── README.md
├── requirements.txt
├── Dockerfile
│
├── Python Scripts
│   ├── bond_pricing.py              # Day 2: Bond pricing engine
│   ├── portfolio_analytics.py       # Day 3: Portfolio aggregation & charts
│   ├── key_rate_duration.py         # Day 4: KRD vectors & heatmap
│   ├── monte_carlo.py               # Day 5-6: Parallel + 3-Factor MC simulation
│   ├── ml_models.py                 # Day 8: Random Forest, XGBoost, Neural Network
│   ├── shap_explainability.py       # Day 8: SHAP feature importance
│   ├── sensitivity_analysis.py      # Day 9: ML vs Analytical comparison
│   ├── yield_curve.py               # Day 10: Nelson-Siegel & Svensson fitting
│   ├── generate_excel_workbook.py   # Day 14: Excel validation workbook
│   └── var_backtest.py              # Day 14: Kupiec POF backtesting
│
├── R Scripts
│   ├── duration_convexity_analysis.R
│   └── sensitivity_visualization.R
│
├── Documentation
│   ├── dax_measures_dictionary.md
│   ├── Bond_Risk_Lab_Design_Document.md
│   ├── yield_curve_interpretation.md
│   └── ml_sensitivity_analysis_notes.md
│
├── Data Files
│   ├── bond_portfolio_data.csv
│   ├── bond_portfolio_recalc.csv
│   ├── bond_portfolio_krd.csv
│   ├── yield_curve_history.csv
│   ├── monte_carlo_results.csv
│   ├── yield_curve_fit_results.csv
│   └── ml_model_comparison.csv
│
└── Excel Validation
    └── VikashKumar_ExcelValidation.xlsx
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
git clone https://github.com/vikashkr20/Data-Analyst-Convexity-Sensitivity-AI-Agent.git
cd Data-Analyst-Convexity-Sensitivity-AI-Agent
pip install -r requirements.txt
```

### Run the Full Pipeline

```bash
python bond_pricing.py           # Day 2: Reprice all 301 bonds
python portfolio_analytics.py    # Day 3: Portfolio aggregation & charts
python key_rate_duration.py      # Day 4: KRD vectors & heatmap
python monte_carlo.py            # Day 5-6: Monte Carlo VaR/CVaR
python ml_models.py              # Day 8: Train ML models
python shap_explainability.py    # Day 8: SHAP analysis
python sensitivity_analysis.py   # Day 9: ML vs Analytical sensitivity
python yield_curve.py            # Day 10: Yield curve fitting
python generate_excel_workbook.py  # Day 14: Excel workbook
python var_backtest.py           # Day 14: VaR backtesting
```

### Docker

```bash
docker build -t matrisk-platform .
docker run --rm matrisk-platform
```

---

## Core Formulas

**Bond Price (Semi-Annual Coupon)**

$$P = \sum_{t=1}^{N} \frac{C/2}{(1 + y/2)^{t}} + \frac{F}{(1 + y/2)^{N}}$$

**Modified Duration**

$$D_{mod} = \frac{D_{mac}}{1 + y/2}$$

**P&L Approximation (Duration + Convexity)**

$$\Delta P \approx -D_{mod} \cdot \Delta y + \frac{1}{2} \cdot C_{conv} \cdot (\Delta y)^2$$

**Nelson-Siegel Yield Curve**

$$y(t) = \beta_0 + \beta_1 \frac{1-e^{-t/\lambda}}{t/\lambda} + \beta_2\left[\frac{1-e^{-t/\lambda}}{t/\lambda} - e^{-t/\lambda}\right]$$

---

## Key Results

### Portfolio Risk Metrics

| Metric | Value |
|---|---|
| Total Market Value | INR 32,059,345.97 |
| Modified Duration | 4.2031 years |
| Convexity | 176.2455 |
| Total DV01 | INR 8,948.25 |
| KRD Sum vs ModDur Error | 0.03% |

### KRD Portfolio Profile (Barbell)

| Zone | KRD | Weight |
|---|---|---|
| Short-end (3M–2Y) | 0.5871 | 13.97% |
| Belly (3Y–7Y) | 1.1250 | 26.78% |
| Long-end (10Y–30Y) | 2.4895 | 59.25% |

### Monte Carlo VaR / CVaR

| Model | 95% VaR | 99% VaR |
|---|---|---|
| Parallel Shift | INR -1,462,165 | INR -1,596,023 |
| 3-Factor Cholesky | INR -1,432,496 | INR -1,670,865 |

### ML Model Comparison

| Model | RMSE | MAE | R² |
|---|---|---|---|
| Random Forest | 4.0631 | 1.9342 | 58.23% |
| XGBoost | 4.2333 | 1.9202 | 54.66% |
| **Neural Network** | **1.6035** | **0.6757** | **93.49%** |

### Yield Curve Fitting (2024-10-30)

| Model | RMSE | R² |
|---|---|---|
| Nelson-Siegel | 0.000843 | 94.64% |
| **Svensson** | **0.000747** | **95.79%** |

### Implied Forward Rates

| Tenor | Forward Rate |
|---|---|
| 1Y–2Y | 7.0671% |
| 2Y–5Y | 7.7943% |
| 5Y–10Y | 8.2898% |

---

## Bond Risk Lab (Gamified Platform)

A gamified training simulation for fixed income analysts:

- 1,000-point scoring rubric across 6 risk dimensions
- 20 progressive scenarios (Foundational to Master level)
- 10 achievement badges (Convexity King, KRD Sniper, SVB Survivor, etc.)
- 5-year revenue model targeting INR 47.5 Crores by Year 5

---

## Power BI Dashboard

An 8-page Power BI dashboard featuring:

- 40+ DAX measures for portfolio analytics, KRD, VaR/CVaR, and NS curve diagnostics
- Star schema data model across 7 tables
- What-If parameter slicer for real-time yield shift P&L analysis
- Bookmarks for RBI rate cut, hawkish shock, and stress test scenarios

See [`dax_measures_dictionary.md`](dax_measures_dictionary.md) for full DAX code.

---

## 15-Day Methodology

| Day | Deliverable | Status |
|---|---|---|
| Day 1 | Domain Orientation & Indian Fixed Income Market | ✅ |
| Day 2 | `bond_pricing.py` — 5 core analytical functions | ✅ |
| Day 3 | `portfolio_analytics.py` — Aggregation & charts | ✅ |
| Day 4 | `key_rate_duration.py` — KRD vectors & heatmap | ✅ |
| Day 5 | `monte_carlo.py` — Parallel shift VaR/CVaR | ✅ |
| Day 6 | `monte_carlo.py` — 3-Factor Cholesky simulation | ✅ |
| Day 7 | Case Studies: RBI Hike, SVB, Gilt Rally | ✅ |
| Day 8 | `ml_models.py` + `shap_explainability.py` | ✅ |
| Day 9 | `sensitivity_analysis.py` — ML vs Analytical | ✅ |
| Day 10 | `yield_curve.py` — NS & Svensson fitting | ✅ |
| Day 11 | R scripts: caret, XGBoost, H2O, ggplot2 | ✅ |
| Day 12 | Power BI DAX measures dictionary | ✅ |
| Day 13 | Gamified Bond Risk Lab design document | ✅ |
| Day 14 | Excel workbook + Kupiec VaR backtesting | ✅ |
| Day 15 | Final report, presentation, Dockerfile, Git tag | ✅ |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Pricing Engine | Python, NumPy, SciPy |
| Machine Learning | scikit-learn (RF, MLP), XGBoost, SHAP |
| Experiment Tracking | MLflow (SQLite backend) |
| Visualization | Matplotlib, Seaborn |
| Curve Fitting | scipy.optimize.minimize |
| Excel Generation | openpyxl |
| R Modeling | caret, xgboost, h2o, ggplot2 |
| DevOps | Docker, Git |
| BI | Power BI (DAX, Star Schema) |

---

## Author

**Vikash Kumar** — Fixed Income Quantitative Analyst

Repository: [Data-Analyst-Convexity-Sensitivity-AI-Agent](https://github.com/vikashkr20/Data-Analyst-Convexity-Sensitivity-AI-Agent)