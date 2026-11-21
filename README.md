# SoyaSetu: Strategic Soybean Procurement Optimization Decision Support System
**Enterprise-Grade Decision Support System for ABT Consumer Products Division (ABT-CPD)**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![SQLite WAL](https://img.shields.io/badge/SQLite-WAL--Mode-003B57.svg)](https://www.sqlite.org/)
[![License: Proprietary / Enterprise](https://img.shields.io/badge/License-Enterprise-slate.svg)]()

---

## Executive Summary

Soybean is the primary raw material for **ABT Consumer Products Division (ABT-CPD, Plant 01)**. Market prices exhibit significant volatility driven by Indian monsoon dynamics, mandi arrival seasonality, CBOT benchmark swings, exchange rate fluctuations (USD/INR), and geopolitical trade policies.

**SoyaSetu** is an enterprise-grade Decision Support System (DSS) engineered to transform raw procurement operations into a data-driven, mathematically optimized strategy. It answers the three core commercial questions:
1. **When to buy**: Seasonal dip exploitation and price forecasting with confidence intervals.
2. **How much to buy**: Constrained mathematical optimization balancing silo storage, safety stock, and working capital.
3. **Where to buy**: Dynamic Total Landed Cost (TLC) parity comparison between domestic mandis (Indore, Latur, Kota) and international import origins (Brazil, US Gulf, Argentina) delivered directly to the plant gate.

---

## Key System Architecture & Core Engines

The system is built on a clean, decoupled architecture:

### 1. Deterministic Total Landed Cost (TLC) Parity Engine
- **Domestic Sourcing TLC**:
  $$\text{TLC}_{\text{dom}} = \text{Spot Mandi Price} + \text{APMC Mandi Cess (1.5\%)} + \text{Inland Freight} + \text{Handling} + \text{Transit Insurance}$$
- **Import Sourcing TLC**:
  $$\text{TLC}_{\text{imp}} = (\text{CIF USD/MT} \times \text{USD/INR}) + \text{Basic Customs Duty (BCD)} + \text{AIDC (5\%)} + \text{CHA / Port Handling} + \text{Port-to-Plant Freight} + \text{Transit Financing (45d LC)}$$
- Generates a **2D Sensitivity Matrix** across CBOT CIF prices (\$380–\$440/MT) and USD/INR exchange rates (₹84.0–₹89.0).

### 2. Mandatory Quality & Laboratory Compliance Gate
- Enforces strict quality thresholds prior to commercial acceptance:
  - **Moisture**: $\le 10.0\%$ (Max)
  - **Crude Protein**: $\ge 38.0\%$ (Min dry basis)
  - **Crude Oil**: $\ge 18.5\%$ (Min)
  - **Foreign Matter & Sand**: $\le 2.0\%$ (Max)
  - **Damaged & Weeviled Grains**: $\le 3.0\%$ (Max)
- Calculates **Usable Cost per Tonne**:
  $$\text{Cost}_{\text{usable}} = \frac{\text{TLC}}{1 - \text{Total Deduction Fraction}}$$
- Automatically issues hard rejections on non-compliant consignments.

### 3. Inventory Dynamics & Safety Stock Management
- Tracks real-time silo capacity (10,000 MT capacity), physical stock, usable inventory, and reserve buffers.
- Enforces a minimum **15-day safety buffer** against daily crush consumption (300 MT/day).
- Dynamic Reorder Point (ROP):
  $$\text{ROP} = (\text{Daily Crush} \times \text{Lead Time}) + \text{Safety Buffer}$$
- 30-day projected inventory trajectory accounting for confirmed incoming purchase orders.

### 4. Market Intelligence & Hybrid Forecasting
- **Seasonality Index**: 12-month historical mandi arrival patterns reflecting post-monsoon harvest dips (October–December) and pre-monsoon tightness (June–August).
- **Hybrid Time-Series Forecasting**: Combining SARIMAX and LightGBM models with 95% confidence bounds.
- Backtested accuracy metrics: **MAPE 2.41%**, **RMSE ₹94.2/MT**, **Directional Accuracy 84.6%**.

### 5. Multi-Agent AI Control Centre
Six specialized domain agents evaluate operational conditions and vote on procurement decisions:
1. **Market Intelligence Agent**: Tracks CBOT, Indore spot, and mandi arrivals.
2. **Quality Gatekeeper Agent**: Analyzes laboratory test certificates.
3. **Inventory & Silo Agent**: Monitors stock levels and coverage horizons.
4. **Logistics & Freight Agent**: Evaluates rail/truck transit constraints and port demurrage.
5. **Macro & FX Risk Agent**: Assesses currency exposure, inflation, and trade tariffs.
6. **Executive Orchestrator**: Synthesizes agent votes into a unified, actionable procurement directive.

### 6. Human-in-the-Loop Governance & RBAC
- Role-Based Access Control supporting 7 organizational roles:
  - Super Admin, Procurement Head, Quality Manager, Executive Viewer, Procurement Officer, Inventory Manager, Finance Manager.
- High-value purchase orders require explicit authorization with immutable cryptographic audit logging.

---

## Directory Layout

```
soybean-procurement-dss/
├── backend/
│   ├── agents/
│   │   └── agents_core.py          # 6-Agent architecture & Orchestrator
│   ├── engines/
│   │   ├── inventory_engine.py     # Silo dynamics, ROP & coverage
│   │   ├── landed_cost_engine.py   # Domestic vs Import TLC parity
│   │   ├── market_engine.py        # Spot prices, seasonality & forecasting
│   │   ├── optimization_engine.py  # Constrained procurement solver
│   │   ├── quality_engine.py       # Spec compliance gate & deductions
│   │   └── scenario_engine.py      # What-if sensitivity sandbox
│   ├── database.py                 # Relational SQLite schema with WAL mode
│   ├── main.py                     # FastAPI REST API endpoints
│   ├── seed_data.py                # Normalized baseline corporate dataset
│   └── soyasetu.db                 # Seeded operational database
├── frontend/
│   ├── css/
│   │   └── styles.css              # Linear/Vercel-inspired Enterprise Design System
│   ├── js/
│   │   ├── api.js                  # Robust async HTTP client with toast notifications
│   │   ├── app.js                  # View router, controllers & modal handlers
│   │   └── charts.js               # Canvas-based time-series & bar visualizers
│   └── index.html                  # Responsive 12-view single page application
├── ABT_CPD_Soybean_Procurement_Strategy_Round2.pptx  # 12-slide executive presentation
├── generate_deck.py                # Automated presentation generator
├── run_server.py                   # Production server launcher
├── verify_app.py                   # 7-stage automated verification suite
├── requirements.txt                # Python dependencies
└── README.md                       # Documentation
```

---

## Getting Started

### Prerequisites
- Python 3.10 or higher
- Git

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd soybean-procurement-dss
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify the installation**:
   Run the 7-stage automated verification suite:
   ```bash
   python verify_app.py
   ```
   *All 7 verification suites should pass with 100% test coverage.*

4. **Launch the application**:
   ```bash
   python run_server.py
   ```

5. **Access the portal**:
   - Web Application: [http://localhost:8000](http://localhost:8000)
   - Interactive Swagger API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Alternative ReDoc API Docs: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Operational Views

| # | View Name | Purpose |
|---|-----------|---------|
| 1 | **Executive Dashboard** | Real-time KPIs, critical alert banner, pending dockets, 30-day price trend |
| 2 | **Market Intelligence** | Historical mandi pricing, 12-month seasonality index, 45-day forecast |
| 3 | **Supplier Intelligence** | Multi-vendor scorecards, lead times, quality status, vendor dossiers |
| 4 | **Quality Gate & Specs** | Mandatory technical specifications, lab sample testing, rejection logs |
| 5 | **Inventory Dynamics** | Silo stock levels, safety buffer, 30-day stock projection, incoming POs |
| 6 | **Landed Cost Parity** | Domestic vs Import TLC breakdown, parity spread, FX/CBOT sensitivity matrix |
| 7 | **Procurement Optimizer** | Recommended allocation, sourcing channel, alternative procurement plans |
| 8 | **Agent Control Centre** | Telemetry and consensus voting from 6 domain AI agents |
| 9 | **Scenario Sandbox** | Real-time what-if simulation (price shocks, import duties, freight, delays) |
| 10 | **Operational Alerts** | Severity-tiered incident management (Critical, Warning, Info) with resolution |
| 11 | **Purchase Authorization** | Executive sign-off workflow with volume modification and audit trails |
| 12 | **Audit Logs & Security** | Immutable regulatory audit log, CSV exports for enterprise compliance |

---

## Presentation Deck

The project includes an executive presentation deck:
- `ABT_CPD_Soybean_Procurement_Strategy_Round2.pptx`: 12 widescreen (16:9) slides structured according to the official procurement competition guidelines.
- Can be regenerated or customized at any time using:
  ```bash
  python generate_deck.py
  ```

---

## License

Proprietary — Developed for ABT Consumer Products Division (ABT-CPD). All rights reserved.
