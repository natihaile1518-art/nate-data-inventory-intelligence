import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import mysql.connector
from mysql.connector import Error

# -------------------------------------------------------
# PAGE CONFIGURATION
# Identical to Version 1 — same brand, same layout
# -------------------------------------------------------
st.set_page_config(
    page_title="Nate Data v2 — Live Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)
# -------------------------------------------------------
# DATABASE CONNECTION
# VERSION 1 used: pd.read_csv(file_path)
# VERSION 2 uses: mysql.connector.connect(host, user, password)
# The rest of the app works with DataFrames in both versions
# The only difference is WHERE the data comes from
# -------------------------------------------------------

def get_connection():
    """
    Establishes and returns a MySQL connection.
    Credentials are read from Streamlit Secrets — never hardcoded.
    Locally: reads from .streamlit/secrets.toml
    Deployed: reads from Streamlit Cloud secret settings
    """
    try:
        db = st.secrets["mysql"]
        connection = mysql.connector.connect(
            host                = db["host"],
            port                = int(db["port"]),
            user                = db["user"],
            password            = db["password"],
            database            = db["database"],
            ssl_disabled        = False,
            ssl_verify_cert     = False,
            ssl_verify_identity = False
        )
        return connection
    except Error as e:
        st.error(f"Database connection failed: {e}")
        return None

def run_query(sql, params=None):
    """
    Executes a SQL query and returns a pandas DataFrame.

    Parameters:
        sql    — the SQL query string
        params — optional tuple of parameters for the query

    Returns:
        pandas DataFrame with the query results
        Empty DataFrame if query fails
    """
    connection = get_connection()
    if connection is None:
        return pd.DataFrame()

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        rows    = cursor.fetchall()
        df      = pd.DataFrame(rows)
        return df
    except Error as e:
        st.error(f"Query failed: {e}")
        return pd.DataFrame()
    finally:
        # Always close the connection when done
        # 'finally' runs whether the query succeeded or failed
        if connection.is_connected():
            cursor.close()
            connection.close()
# -------------------------------------------------------
# CUSTOM STYLING
# Same dark theme as Version 1
# New additions: metric-positive and metric-negative
# for profit/loss color coding
# -------------------------------------------------------
st.markdown("""
    <style>
    .main {
        background-color: #0F172A;
        color: #F1F5F9;
    }
    [data-testid="stSidebar"] {
        background-color: #1E293B;
    }
    .kpi-card {
        background-color: #1E293B;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid #334155;
        margin-bottom: 10px;
    }
    .kpi-value {
        font-size: 26px;
        font-weight: 700;
        color: #38BDF8;
    }
    .kpi-label {
        font-size: 12px;
        color: #94A3B8;
        margin-top: 4px;
    }
    .metric-positive {
        font-size: 26px;
        font-weight: 700;
        color: #22C55E;
    }
    .metric-negative {
        font-size: 26px;
        font-weight: 700;
        color: #EF4444;
    }
    .section-header {
        color: #38BDF8;
        font-size: 17px;
        font-weight: 600;
        margin-bottom: 8px;
        padding-bottom: 6px;
        border-bottom: 1px solid #334155;
    }
    .version-badge {
        background-color: #22C55E;
        color: white;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)
# -------------------------------------------------------
# DATA LOADING
# -------------------------------------------------------
# DATA LOADING
# VERSION 1: pd.read_csv() — reads static files
# VERSION 2: run_query()   — reads live MySQL database
#
# @st.cache_data(ttl=300) means:
#   - cache the result for 300 seconds (5 minutes)
#   - after 5 minutes, re-query MySQL for fresh data
#   - Version 1 used cache_data with no ttl (never refreshed)
# -------------------------------------------------------

@st.cache_data(ttl=300)
def load_products():
    """Load all active products with category names."""
    sql = """
        SELECT
            p.product_id,
            p.product_name,
            c.category_name,
            p.specification,
            p.is_active
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        WHERE p.is_active = 1
        ORDER BY c.category_name, p.product_name
    """
    return run_query(sql)

@st.cache_data(ttl=300)
def load_current_inventory():
    """
    Calculate current stock for every product.
    Formula: opening_snapshot + purchases - sales
    This query did NOT exist in Version 1.
    Version 1 just read the quantity column from a CSV.
    Version 2 calculates quantity dynamically from transactions.
    """
    sql = """
        SELECT
            p.product_id,
            p.product_name,
            c.category_name,
            p.specification,
            pi.purchase_price_etb                  AS unit_cost_etb,
            COALESCE(snap.opening_qty, 0)
            + COALESCE(purch.purchased_qty, 0)
            - COALESCE(sold.sold_qty, 0)            AS current_stock,
            COALESCE(snap.opening_qty, 0)           AS opening_stock,
            COALESCE(purch.purchased_qty, 0)        AS total_purchased,
            COALESCE(sold.sold_qty, 0)              AS total_sold,
            (COALESCE(snap.opening_qty, 0)
            + COALESCE(purch.purchased_qty, 0)
            - COALESCE(sold.sold_qty, 0))
            * pi.purchase_price_etb                 AS stock_value_etb
        FROM products p
        JOIN categories c      ON p.category_id  = c.category_id
        JOIN purchase_items pi ON p.product_id   = pi.product_id
        JOIN purchases pu      ON pi.purchase_id = pu.purchase_id
        LEFT JOIN (
            SELECT product_id, SUM(quantity) AS opening_qty
            FROM inventory_snapshots
            WHERE location_id = 1
            GROUP BY product_id
        ) snap  ON p.product_id = snap.product_id
        LEFT JOIN (
            SELECT pi2.product_id, SUM(pi2.quantity) AS purchased_qty
            FROM purchase_items pi2
            JOIN purchases pu2 ON pi2.purchase_id = pu2.purchase_id
            WHERE pu2.location_id = 1
              AND pu2.supplier_name != 'Opening Stock'
            GROUP BY pi2.product_id
        ) purch ON p.product_id = purch.product_id
        LEFT JOIN (
            SELECT si.product_id, SUM(si.quantity_sold) AS sold_qty
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.sale_id
            WHERE s.location_id = 1
            GROUP BY si.product_id
        ) sold  ON p.product_id = sold.product_id
        WHERE pu.supplier_name = 'Opening Stock'
          AND p.is_active = 1
        ORDER BY c.category_name, p.product_name
    """
    return run_query(sql)

@st.cache_data(ttl=300)
def load_sales_summary():
    """
    Load daily sales summary with revenue, cost, profit.
    This entire function has NO equivalent in Version 1.
    Version 1 had no sales data at all.
    """
    sql = """
        SELECT
            s.sale_date,
            l.location_name                                AS shop,
            COUNT(DISTINCT s.sale_id)                      AS transactions,
            SUM(si.quantity_sold)                          AS units_sold,
            SUM(si.quantity_sold * si.selling_price_etb)   AS revenue_etb,
            SUM(si.quantity_sold * pi.purchase_price_etb)  AS cost_etb,
            SUM(si.quantity_sold * si.selling_price_etb)
            - SUM(si.quantity_sold * pi.purchase_price_etb) AS profit_etb
        FROM sales s
        JOIN sale_items si     ON s.sale_id      = si.sale_id
        JOIN locations l       ON s.location_id  = l.location_id
        JOIN purchase_items pi ON si.product_id  = pi.product_id
        JOIN purchases pu      ON pi.purchase_id = pu.purchase_id
        WHERE pu.supplier_name = 'Opening Stock'
        GROUP BY s.sale_date, l.location_name
        ORDER BY s.sale_date DESC
    """
    return run_query(sql)

@st.cache_data(ttl=300)
def load_locations():
    """Load all active shop locations."""
    sql = """
        SELECT location_id, location_name, location_type
        FROM locations
        WHERE is_active = 1
        ORDER BY location_id
    """
    return run_query(sql)

# Load all data when the app starts
df_products   = load_products()
df_inventory  = load_current_inventory()
df_sales      = load_sales_summary()
df_locations  = load_locations()
# -------------------------------------------------------
# SIDEBAR
# Version 1: showed Location filter (Shop/Warehouse/All)
# Version 2: removes location filter — focuses on live
#            Shop 1 transactions. Adds LIVE database badge.
# -------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style='text-align:center; padding: 10px 0;'>
            <h2 style='color:#38BDF8; margin:0;'>⚡ Nate Data</h2>
            <p style='color:#94A3B8; font-size:12px; margin:4px 0;'>
                Business Intelligence v2
            </p>
            <span class='version-badge'>● LIVE DATABASE</span>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Category filter
    st.subheader("📦 Category")
    if not df_inventory.empty:
        all_categories = sorted(
            df_inventory['category_name'].unique().tolist()
        )
        selected_categories = st.multiselect(
            "Filter by category",
            options=all_categories,
            default=all_categories
        )
    else:
        selected_categories = []

    st.divider()

    # Product search
    st.subheader("🔍 Search")
    search_term = st.text_input(
        "Search product name",
        placeholder="e.g. Tesla, Breaker, Spot..."
    )

    st.divider()

    # Low stock threshold
    st.subheader("⚠️ Stock Alert Threshold")
    low_stock_threshold = st.slider(
        "Flag products below this quantity",
        min_value=1,
        max_value=20,
        value=5,
        step=1
    )

    st.divider()

    # Database status
    st.subheader("🗄️ Data Source")
    st.markdown("""
        <div style='font-size:12px; color:#94A3B8;'>
            <p>📡 Connected to MySQL</p>
            <p>🏪 Database: nate_data</p>
            <p>🔄 Refreshes every 5 minutes</p>
        </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.caption("© 2026 Nate Data")
    st.caption("Bahir Dar University")
# -------------------------------------------------------
# APPLY FILTERS
# Same filtering logic as Version 1
# Applied to df_inventory instead of combined_df
# -------------------------------------------------------
filtered_inventory = df_inventory.copy() if not df_inventory.empty \
    else pd.DataFrame()

if not filtered_inventory.empty:
    # Apply category filter
    if selected_categories:
        filtered_inventory = filtered_inventory[
            filtered_inventory['category_name'].isin(selected_categories)
        ]
    # Apply search filter
    if search_term:
        filtered_inventory = filtered_inventory[
            filtered_inventory['product_name'].str.contains(
                search_term, case=False, na=False
            )
        ]

# -------------------------------------------------------
# HEADER
# Version 1: simple title
# Version 2: adds subtitle showing it reads from MySQL
# -------------------------------------------------------
st.markdown("""
    <div style='text-align:center; padding:20px 0 10px 0;'>
        <h1 style='color:#38BDF8; font-size:34px; margin-bottom:4px;'>
            ⚡ Nate Data
        </h1>
        <p style='color:#94A3B8; font-size:15px; margin:0;'>
            Small Business Intelligence System — Version 2
        </p>
        <p style='color:#475569; font-size:12px; margin-top:4px;'>
            Dessie, Ethiopia ● Live MySQL Database ● Real Transactions
        </p>
    </div>
""", unsafe_allow_html=True)

st.divider()

# -------------------------------------------------------
# KPI CALCULATIONS
# Version 1: read directly from CSV columns
# Version 2: calculated from live transaction data
# -------------------------------------------------------

# Inventory KPIs — from current stock calculation
total_products  = len(filtered_inventory)
total_units     = int(filtered_inventory['current_stock'].sum()) \
    if not filtered_inventory.empty else 0
total_value     = filtered_inventory['stock_value_etb'].sum() \
    if not filtered_inventory.empty else 0
total_cats      = filtered_inventory['category_name'].nunique() \
    if not filtered_inventory.empty else 0
out_of_stock    = int((filtered_inventory['current_stock'] == 0).sum()) \
    if not filtered_inventory.empty else 0
low_stock_count = int(
    ((filtered_inventory['current_stock'] > 0) &
     (filtered_inventory['current_stock'] <= low_stock_threshold)).sum()
) if not filtered_inventory.empty else 0

# Sales KPIs — NEW in Version 2, did not exist in Version 1
total_revenue = df_sales['revenue_etb'].sum() \
    if not df_sales.empty else 0
total_profit  = df_sales['profit_etb'].sum() \
    if not df_sales.empty else 0
profit_margin = round(
    (total_profit / total_revenue * 100), 1
) if total_revenue > 0 else 0

# -------------------------------------------------------
# KPI CARDS — ROW 1: Inventory metrics
# -------------------------------------------------------
st.markdown("<div class='section-header'>📦 Inventory Overview</div>",
            unsafe_allow_html=True)

c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:
    st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-value'>{total_products:,}</div>
            <div class='kpi-label'>Products</div>
        </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-value'>{total_units:,}</div>
            <div class='kpi-label'>Units in Stock</div>
        </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-value'>{total_value:,.0f}</div>
            <div class='kpi-label'>Stock Value (ETB)</div>
        </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-value'>{total_cats}</div>
            <div class='kpi-label'>Categories</div>
        </div>""", unsafe_allow_html=True)

with c5:
    st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-value' style='color:#EF4444;'>
                {out_of_stock}
            </div>
            <div class='kpi-label'>Out of Stock</div>
        </div>""", unsafe_allow_html=True)

with c6:
    st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-value' style='color:#FCD34D;'>
                {low_stock_count}
            </div>
            <div class='kpi-label'>Low Stock (≤{low_stock_threshold})</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------------
# KPI CARDS — ROW 2: Sales metrics
# NEW in Version 2 — Version 1 had no sales data at all
# -------------------------------------------------------
st.markdown("<div class='section-header'>💰 Sales Performance</div>",
            unsafe_allow_html=True)

s1, s2, s3, s4 = st.columns(4)

with s1:
    st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-value'>{total_revenue:,.0f}</div>
            <div class='kpi-label'>Total Revenue (ETB)</div>
        </div>""", unsafe_allow_html=True)

with s2:
    profit_class = 'metric-positive' if total_profit >= 0 \
        else 'metric-negative'
    st.markdown(f"""
        <div class='kpi-card'>
            <div class='{profit_class}'>{total_profit:,.0f}</div>
            <div class='kpi-label'>Total Profit (ETB)</div>
        </div>""", unsafe_allow_html=True)

with s3:
    st.markdown(f"""
        <div class='kpi-card'>
            <div class='metric-positive'>{profit_margin}%</div>
            <div class='kpi-label'>Profit Margin</div>
        </div>""", unsafe_allow_html=True)

with s4:
    total_transactions = int(df_sales['transactions'].sum()) \
        if not df_sales.empty else 0
    st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-value'>{total_transactions:,}</div>
            <div class='kpi-label'>Total Transactions</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
