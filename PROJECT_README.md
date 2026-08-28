# ⚡ Nate Data — Small Business Intelligence System

**Built by:** Natnael Haile  
**University:** Bahir Dar University, Ethiopia (3rd Year, Data Science)  
**Business:** Brother's electrical shop in Dessie, Ethiopia  
**Status:** Actively developed — collecting real sales data

---

## What This Project Is

A complete, real-world Business Intelligence system built for an actual electrical shop in Dessie, Ethiopia.

The shop previously recorded everything in paper notebooks with no digital system. I personally spent one month counting every product by hand, then built this system from scratch — from raw data collection to a live MySQL-powered web application.

This is not a tutorial project or a Kaggle dataset. Every number in this system came from a real shop floor.

---

## Project Evolution

### Version 1 — Inventory Intelligence Dashboard
A static inventory analysis dashboard built from the physical count data.

**Live:** https://nate-data-inventory-intelligence-k8tcrz4fzcby5nmgcxzaur.streamlit.app/

What it answers:
- What products does the shop carry?
- What is the total inventory value?
- Which categories hold the most stock?
- Which products are low or out of stock?

### Version 2 — Live Business Intelligence System
A transaction-based system connected to a MySQL database.

What it answers:
- What did the shop sell today?
- What is today's revenue and profit?
- Which products are selling fastest?
- Which shop is performing better?
- What stock needs to be reordered?

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python | Core language |
| Pandas | Data cleaning and analysis |
| MySQL 8.0 | Live transaction database |
| mysql-connector-python | Python-MySQL connection |
| Streamlit | Web application framework |
| Plotly | Interactive charts |
| Git + GitHub | Version control |
| Jupyter Notebook | Analysis and documentation |

---

## Project Phases

| Phase | Title | Status |
|-------|-------|--------|
| 1 | Data Collection (manual shop count) | ✅ Complete |
| 2 | Data Cleaning | ✅ Complete |
| 3 | Exploratory Data Analysis | ✅ Complete |
| 4 | Artificial Warehouse Dataset | ✅ Complete |
| 5 | Static Inventory Dashboard (v1) | ✅ Complete |
| 6 | Sales Dataset Design | ✅ Complete |
| 7–12 | MySQL Database + Business Analytics | ✅ Complete |
| 13–14 | Live Streamlit App (v2) | ✅ Complete |
| 15 | Real Sales Data Collection | 🔄 In Progress |
| 16 | Machine Learning Investigation | ⏳ Pending |
| 17 | Demand Forecasting + Reorder Intelligence | ⏳ Pending |
| 18 | Final Deployment | ⏳ Pending |

---

## Database Schema

```
nate_data (MySQL)
├── locations          — Shop 1, Shop 2, Warehouse
├── categories         — 13 product categories
├── products           — 195 real products
├── users              — Owner + 2 workers
├── inventory_snapshots— Opening stock (June 2026)
├── purchases          — Stock received from suppliers
├── purchase_items     — Purchase line items
├── sales              — Customer transactions
├── sale_items         — Sale line items
└── inventory_adjustments — Damaged, lost, transferred stock
```

**Inventory formula:**
```
Current Stock = Opening Snapshot + Purchases - Sales + Adjustments
```

---

## Application Pages

| Page | Who Uses It | Purpose |
|------|------------|---------|
| Dashboard | Owner | Live KPIs, charts, stock alerts |
| Record Sale | Workers | Enter daily sales at end of day |
| Record Purchase | Owner | Record new stock arrivals |
| Manage Products | Owner | Add, update, deactivate products |

---

## Key Business Numbers (as of June 2026 inventory count)

- **195 products** across **13 categories**
- **874,960 ETB** total inventory value
- **Spot Light** — highest value category (19.7% of total)
- **Breaker** — most product variety (44 types)
- **Profit margin** — approximately 29–31% per transaction

---

## Folder Structure

```
Summer_Projects/
├── data/
│   ├── raw/                    # Original inventory count
│   └── cleaned/                # Cleaned data files
├── notebook/                   # Jupyter notebooks (all phases)
├── sql/                        # MySQL schema and query files
├── dashboard/
│   ├── app.py                  # Version 1 — static dashboard
│   ├── app_v2.py               # Version 2 — live MySQL dashboard
│   └── pages/                  # Multi-page app pages
│       ├── 1_Record_Sale.py
│       ├── 2_Record_Purchase.py
│       └── 3_Manage_Products.py
└── requirements.txt
```

---

## How to Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set up MySQL
# Create database: nate_data
# Run: sql/01_create_database.sql
# Run: sql/02_create_tables.sql
# Run: sql/03_seed_data.sql

# Update password in dashboard/app_v2.py

# Run Version 1 (static)
streamlit run dashboard/app.py

# Run Version 2 (live MySQL)
streamlit run dashboard/app_v2.py
```

---

## Future Machine Learning (Phase 16-17)

Once sufficient sales history is collected:
- **Demand Forecasting** — predict future product demand
- **Reorder Prediction** — predict when stock will run out
- **Slow-Moving Product Detection** — identify products not selling
- **Sales Pattern Analysis** — weekly and seasonal trends

---

## About the Developer

Natnael Haile is a 3rd-year Data Science student at Bahir Dar University, Ethiopia.
Available for freelance data science and business intelligence projects.

**GitHub:** https://github.com/natihaile1518-art  
**Project:** https://github.com/natihaile1518-art/nate-data-inventory-intelligence
