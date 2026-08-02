---
inclusion: always
---

# Nate Data — Project Steering File

This file is automatically loaded in every session.
It gives Kiro full context about this project so Natnael never has to re-explain it.

---

## Who Is Building This

**Name:** Natnael Haile
**University:** Bahir Dar University, Ethiopia (3rd Year, Data Science student)
**Business:** His brother's electrical shop in Dessie, Ethiopia
**Brand Name:** Nate Data
**Goal:** Build a complete, real-world Business Intelligence system as a portfolio project

---

## What This Project Is

The shop previously had no digital system — everything was recorded in paper notebooks.
Natnael personally spent one month physically counting every product in the shop
and converting it into a structured Excel dataset.

This is **real data from a real business**, not a practice dataset.

The project transforms that data into a full Business Intelligence and AI system,
covering everything from raw data cleaning to deployed machine learning models.

---

## Project Phases and Status

| Phase | Title                           | Status      |
|-------|---------------------------------|-------------|
| 1     | Data Collection                 | COMPLETE    |
| 2     | Data Cleaning                   | COMPLETE    |
| 3     | Exploratory Data Analysis (EDA) | COMPLETE    |
| 4     | Artificial Store Dataset        | COMPLETE    |
| 5     | Interactive Dashboard           | pending     |
| 6     | Sales Dataset                   | pending     |
| 7     | Sales Analytics                 | pending     |
| 8     | Machine Learning                | pending     |
| 9     | Deploy Final Portfolio Project  | pending     |

---

## Dataset: Inventory — Real Facts (from Phase 2 audit)

**Raw file (never modify):** `data/raw/inventory_raw.xlsx`
**Cleaned Excel:**           `data/cleaned/inventory_cleaned.xlsx`
**Cleaned CSV:**             `data/cleaned/inventory_cleaned.csv`

### Size
- **201 rows** (products), **10 columns** after cleaning
- Data collected by hand from the physical shop floor
- Count date: **2026-06-19** (stored as Excel serial 46192 in the raw file)

### Columns in the CLEANED dataset

| Column                | Type     | Notes                                                       |
|-----------------------|----------|-------------------------------------------------------------|
| Product_ID            | text     | Unique identifier, P0001–P0201                              |
| Product_Name          | text     | Standardized to Title Case, typos corrected                 |
| Category              | text     | 13 categories after cleaning (see list below)               |
| Specification         | text     | Technical spec; `'N/A'` where not applicable                |
| Quantity              | integer  | Units in stock; 0 means out of stock or count not completed |
| Purchase_Price_ETB    | float    | Cost price in Ethiopian Birr (NOT selling price)            |
| Location              | text     | All values = `'Shop'` (warehouse data to be added later)    |
| Count_Date            | datetime | 2026-06-19 for all rows                                     |
| Needs_Review          | boolean  | True for products with flagged data quality issues          |
| Total_Stock_Value_ETB | float    | Derived: Quantity × Purchase_Price_ETB                      |

### Key Business Numbers (from cleaned data)
- **Total inventory value:** 989,360 ETB
- **Total products:** 201
- **Categories:** 13
- **Out of stock / uncounted products:** 12
- **Products flagged for price review:** 2 (P0107, P0123)

### 13 Product Categories (after cleaning)

| Category             | Notes                                                      |
|----------------------|------------------------------------------------------------|
| Panel Light          | LED panel ceiling lights (various wattages)                |
| Lamp                 | General LED lamps and bulbs                                |
| Spot Light           | Directional spot lights                                    |
| Breaker              | Circuit breakers, contactors, change-overs                 |
| Pawza                | Rechargeable / emergency lights (Amharic: ፓዋዛ)            |
| Plastic Globe        | Globe-shaped plastic lamp covers (merged from Globe+Plastic Globe) |
| Magnetic Light       | Magnetic track lighting and fixtures                       |
| Grand                | Switches and sockets — Grand brand                         |
| Haud                 | Switches and sockets — Haud brand                         |
| Vegas                | Switches and sockets — Vegas brand                         |
| Mirror Light         | Decorative mirror lights                                   |
| Strip Light          | LED strip lights and accessories                           |
| Electrical Component | Phase bars, power supplies (re-categorized from Magnetic Light) |

### Data Quality Issues Found and Fixed in Phase 2

| Issue | Fix Applied |
|-------|-------------|
| Column named `Sell_Price_ETB` | Renamed to `Purchase_Price_ETB` |
| `Count_Date` as Excel serial (46192) | Converted to proper date (2026-06-19) |
| `'NULL'` text in Specification | Replaced with `'N/A'` |
| 10 rows with missing Quantity | Filled with 0, type cast to integer |
| Extra spaces and inconsistent capitalization | `.strip()` + `.title()` applied |
| `Globe` and `Plastic Globe` were same category split in two | Merged into `Plastic Globe` |
| Typos: `Contractor`, `Cheng Over`, `Haveles`, `Chargable` | Corrected to proper spelling |
| `Phase Bar` and `Power Supply` misclassified as `Magnetic Light` | Moved to `Electrical Component` |
| P0107 price anomaly (2,500 ETB vs 300 ETB for same product) | Flagged in `Needs_Review` column |
| P0123 price anomaly (2,500 ETB vs 120 ETB for same product) | Flagged in `Needs_Review` column |

### Known Open Issues (require shop owner verification)
- **P0107** — Chint 1 Phase 10A priced at 2,500 ETB. Identical product P0108 is 300 ETB. Likely a typo.
- **P0123** — Fuse Holder Andeli priced at 2,500 ETB. Identical product P0093 is 120 ETB. Likely a typo.
- **P0174 / P0175** — Both are "4 Way Switch" Vegas at 460 ETB. Quantities are 1 and 4. May be one row entered twice — needs confirmation from shop owner.
- **12 products with Quantity = 0** — Either out of stock or count was not completed. Needs recount.

---

## Folder Structure

```
Summer_Projects/
├── data/
│   ├── raw/                         # Original data — NEVER modify
│   │   └── inventory_raw.xlsx       # 201 rows, 8 columns, as collected
│   └── cleaned/                     # Output of Phase 2
│       ├── inventory_cleaned.xlsx   # 201 rows, 10 columns, human-readable
│       └── inventory_cleaned.csv    # Same data, fast-loading for Python
├── notebook/
│   └── inventory_cleaning.ipynb    # Phase 2: 40 cells (17 steps)
├── dashboard/
│   └── reports/
└── .kiro/steering/
    └── nate-data-project.md        # This file
```

---

## Technology Stack

- **Python** — core language
- **Pandas** — data manipulation and cleaning
- **NumPy** — numerical operations
- **Matplotlib** — static charts
- **Plotly** — interactive charts
- **Streamlit** — interactive dashboard (Phase 5)
- **Excel** — raw data storage
- **Jupyter Notebook** — analysis and documentation
- **GitHub** — version control and portfolio showcase

---

## Coding Standards for This Project

1. **Explain every important line** — Natnael is learning, not just copying code
2. **Use meaningful variable names** — `df_clean` not `df2`, `missing_count` not `mc`
3. **Never modify the raw data file** — always work on `.copy()` and save to `data/cleaned/`
4. **Use `os.path.join()`** for file paths — never hardcode absolute paths
5. **Separate concerns** — each step gets its own markdown explanation cell in notebooks
6. **Validate business logic** — always check if values make sense in a real shop context
7. **Save in both Excel and CSV** — Excel for humans, CSV for Python performance
8. **Add a `# comment`** above every non-obvious line of code
9. **Always load from `inventory_cleaned.csv`** in Phase 3 and beyond — never from raw

---

## Phase 3: EDA — What to Explore (upcoming)

When Phase 3 begins, these are the questions to answer with charts and statistics:

**Inventory composition**
- How many products per category? (bar chart)
- Which category holds the most total stock value? (bar chart)
- Which category has the highest average product price? (bar chart)

**Price analysis**
- What is the price distribution across all products? (histogram)
- What are the top 10 most expensive products? (horizontal bar)
- What are the top 10 products by total stock value?

**Stock health**
- Which products are out of stock (Quantity = 0)?
- Which products are low stock (Quantity ≤ 5)?
- How many products are in each stock level bucket?

**Category deep-dives**
- Breakers: how many phases, how many brands?
- Lamps vs Spot Lights: price and quantity comparison

---

## Dashboard Requirements (Phase 5)

The Streamlit dashboard must include:
- Total Products (KPI card)
- Total Inventory Value in ETB (KPI card)
- Total Categories (KPI card)
- Total Quantity (KPI card)
- Product Search
- Category Filter
- Low Stock Alert (configurable threshold, default = 5)
- Out of Stock Products list
- Most Expensive Products table
- Inventory Value by Category (bar chart)
- Quantity by Category (bar chart)
- Product Details table
- Interactive Charts (Plotly)

Visual style: modern, professional. Brand "Nate Data" in header.

---

## Artificial Store Dataset Rules (Phase 4)

The artificial data must follow realistic business rules:
- High-demand products (cables, bulbs, switches) → higher stock quantity
- Expensive products → lower stock quantity
- Decorative or specialty products → smaller stock
- Some products must be out of stock (realistic)
- Price distributions should follow realistic electrical shop patterns
- The data should be indistinguishable from real warehouse data

---

## Future Sales Dataset Schema (Phase 6)

| Column            | Description                         |
|-------------------|-------------------------------------|
| Date              | Date of the sale                    |
| Product_ID        | Links to inventory dataset          |
| Quantity_Sold     | Number of units sold                |
| Selling_Price_ETB | Price sold at (to calculate profit) |

Enables: Revenue, Profit, Profit Margin, Best Sellers, Monthly/Daily trends.

---

## Machine Learning Plans (Phase 8)

| Model                         | Type         | Why                                           |
|-------------------------------|--------------|-----------------------------------------------|
| Demand Forecasting            | Supervised   | Predict future sales from historical patterns |
| Reorder Prediction            | Supervised   | Predict when stock will run out               |
| Slow-Moving Product Detection | Unsupervised | Cluster products by sales velocity            |
| Inventory Recommendation      | Hybrid       | Recommend optimal reorder quantities          |

---

## Tone and Teaching Style

- Natnael is a beginner in Python but understands Data Science concepts
- Always explain WHY before HOW
- Use real-world analogies when explaining technical concepts
- Build step by step — never dump everything at once
- Treat this like a real software engineering project, not a tutorial exercise
- Point out when something is a real industry best practice

## How to Teach Code — STRICT RULES

These rules apply to every piece of code written for this project, forever.

1. **Never give a complete script at once.** Teach one step at a time.
2. **Each step must follow this exact structure:**
   - What is the purpose of this step? (1–2 sentences)
   - Why does this matter for the brother's electrical shop? (business connection)
   - The code for this step only (not the next step)
   - Line-by-line explanation of every important line
   - What output should appear after running it
   - How to read and interpret that output
3. **Always connect code to the business problem.**
   - Don't just explain what the code does technically.
   - Explain: Why does this matter for the shop? What insight does it give us?
   - Explain: How will this be useful in the dashboard or ML models later?
4. **Show Natnael what his own real data looks like** at each step.
   - Don't use generic examples. Reference his actual categories, products, and numbers.
5. **End every step with a transition** — one sentence explaining what the next step will cover and why it logically follows.
6. **Never skip steps** even if the fix seems minor. Every line is a learning opportunity.
7. **If Natnael asks a question mid-step**, answer it fully before continuing.
