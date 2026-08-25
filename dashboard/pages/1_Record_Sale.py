import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import date

# -------------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------------
st.set_page_config(
    page_title="Record Sale — Nate Data",
    page_icon="🛒",
    layout="wide"
)

# -------------------------------------------------------
# STYLING
# -------------------------------------------------------
st.markdown("""
    <style>
    .main { background-color: #0F172A; color: #F1F5F9; }
    [data-testid="stSidebar"] { background-color: #1E293B; }
    .page-header {
        color: #38BDF8; font-size: 28px;
        font-weight: 700; margin-bottom: 4px;
    }
    .success-box {
        background-color: #14532D;
        border-radius: 8px;
        padding: 12px 16px;
        color: #86EFAC;
        font-weight: 500;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# DATABASE HELPERS
# Same get_connection() and run_query() pattern as app_v2.py
# Repeated here because each Streamlit page is independent
# -------------------------------------------------------
def get_connection():
    try:
        return mysql.connector.connect(
            host     = 'localhost',
            port     = 3306,
            user     = 'root',
            password = '4516Abaye@',
            database = 'nate_data'
        )
    except Error as e:
        st.error(f"Database connection failed: {e}")
        return None


def run_query(sql, params=None):
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        rows = cursor.fetchall()
        return pd.DataFrame(rows)
    except Error as e:
        st.error(f"Query failed: {e}")
        return pd.DataFrame()
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def run_insert(sql, params):
    """
    Executes an INSERT statement and returns the new row ID.
    Different from run_query() because INSERT does not return rows —
    it returns the ID of the newly created record (lastrowid).
    """
    conn = get_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        st.error(f"Insert failed: {e}")
        conn.rollback()
        return None
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# -------------------------------------------------------
# LOAD REFERENCE DATA
# Products and users are loaded fresh each time the page opens
# Workers need to see current products including new additions
# -------------------------------------------------------
@st.cache_data(ttl=300)
def load_products_for_sale():
    """Load all active products for the sale entry dropdowns."""
    sql = """
        SELECT
            p.product_id,
            CONCAT(p.product_name,
                   IF(p.specification IS NOT NULL
                      AND p.specification != 'N/A',
                      CONCAT(' (', p.specification, ')'), '')
            ) AS display_name,
            c.category_name
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        WHERE p.is_active = 1
        ORDER BY c.category_name, p.product_name
    """
    return run_query(sql)


@st.cache_data(ttl=600)
def load_users():
    """Load all active workers."""
    return run_query(
        "SELECT user_id, full_name, role FROM users WHERE is_active = 1"
    )


products_df = load_products_for_sale()
users_df    = load_users()

# -------------------------------------------------------
# PAGE HEADER
# -------------------------------------------------------
st.markdown("<div class='page-header'>🛒 Record Daily Sale</div>",
            unsafe_allow_html=True)
st.markdown("""
    <p style='color:#94A3B8; margin-bottom:20px;'>
    Workers enter the day's sales here at the end of each working day.
    Each sale is saved directly to the database and the dashboard
    updates automatically.
    </p>
""", unsafe_allow_html=True)

st.divider()

# -------------------------------------------------------
# INITIALIZE SESSION STATE
# Session state persists values between interactions
# without losing data when the user clicks a button.
# Think of it as a temporary memory for this page.
# -------------------------------------------------------
if 'sale_items' not in st.session_state:
    st.session_state.sale_items = []

if 'sale_submitted' not in st.session_state:
    st.session_state.sale_submitted = False

# -------------------------------------------------------
# STEP 1 — SALE DETAILS
# Who is selling, which shop, what date
# -------------------------------------------------------
st.subheader("Step 1 — Sale Details")

col1, col2, col3 = st.columns(3)

with col1:
    sale_date = st.date_input(
        "Sale Date",
        value=date.today(),
        help="The date the products were sold to the customer"
    )

with col2:
    if not users_df.empty:
        worker_options = {
            row['full_name']: row['user_id']
            for _, row in users_df.iterrows()
        }
        selected_worker_name = st.selectbox(
            "Worker (who is entering this sale?)",
            options=list(worker_options.keys())
        )
        selected_user_id = worker_options[selected_worker_name]
    else:
        st.error("No workers found in database.")
        selected_user_id = None

with col3:
    shop_options = {'Shop 1': 1, 'Shop 2': 2}
    selected_shop_name = st.selectbox(
        "Shop",
        options=list(shop_options.keys())
    )
    selected_location_id = shop_options[selected_shop_name]

st.divider()

# -------------------------------------------------------
# STEP 2 — ADD PRODUCTS TO THE SALE
# Workers add one product at a time to the sale list
# -------------------------------------------------------
st.subheader("Step 2 — Add Products Sold")

if not products_df.empty:
    # Build a dictionary: display_name → product_id
    product_options = {
        row['display_name']: row['product_id']
        for _, row in products_df.iterrows()
    }

    add_col1, add_col2, add_col3, add_col4 = st.columns([3, 1, 1, 1])

    with add_col1:
        selected_product_name = st.selectbox(
            "Product",
            options=list(product_options.keys()),
            key="product_select"
        )
        selected_product_id = product_options[selected_product_name]

    with add_col2:
        qty_sold = st.number_input(
            "Quantity Sold",
            min_value=1,
            max_value=9999,
            value=1,
            step=1,
            key="qty_input"
        )

    with add_col3:
        selling_price = st.number_input(
            "Selling Price (ETB)",
            min_value=1.0,
            max_value=999999.0,
            value=100.0,
            step=10.0,
            key="price_input"
        )

    with add_col4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Add Item", use_container_width=True):
            # Add this product to the sale items list
            st.session_state.sale_items.append({
                'product_id'       : selected_product_id,
                'product_name'     : selected_product_name,
                'quantity_sold'    : qty_sold,
                'selling_price_etb': selling_price,
                'line_total'       : qty_sold * selling_price
            })

else:
    st.error("No products found. Check database connection.")

# -------------------------------------------------------
# STEP 3 — REVIEW THE SALE BEFORE SUBMITTING
# -------------------------------------------------------
if st.session_state.sale_items:
    st.divider()
    st.subheader("Step 3 — Review Sale Items")

    sale_df = pd.DataFrame(st.session_state.sale_items)

    # Show the items table
    st.dataframe(
        sale_df[['product_name', 'quantity_sold',
                 'selling_price_etb', 'line_total']],
        use_container_width=True,
        hide_index=True
    )

    # Show totals
    total_units   = int(sale_df['quantity_sold'].sum())
    total_revenue = float(sale_df['line_total'].sum())

    metric1, metric2, metric3 = st.columns(3)
    with metric1:
        st.metric("Total Items", len(sale_df))
    with metric2:
        st.metric("Total Units", total_units)
    with metric3:
        st.metric("Total Revenue", f"{total_revenue:,.0f} ETB")

    st.divider()

    # -------------------------------------------------------
    # STEP 4 — SUBMIT OR CLEAR
    # -------------------------------------------------------
    st.subheader("Step 4 — Submit or Clear")

    btn1, btn2 = st.columns(2)

    with btn1:
        if st.button("✅ Submit Sale", use_container_width=True,
                     type="primary"):
            if selected_user_id is None:
                st.error("No worker selected.")
            else:
                # Insert the sale header first
                sale_id = run_insert(
                    """INSERT INTO sales
                       (location_id, user_id, sale_date, notes)
                       VALUES (%s, %s, %s, %s)""",
                    (selected_location_id, selected_user_id,
                     sale_date.strftime('%Y-%m-%d'),
                     'Daily sale entry via Nate Data app')
                )

                if sale_id:
                    # Insert all sale items linked to the header
                    all_inserted = True
                    for item in st.session_state.sale_items:
                        result = run_insert(
                            """INSERT INTO sale_items
                               (sale_id, product_id,
                                quantity_sold, selling_price_etb)
                               VALUES (%s, %s, %s, %s)""",
                            (sale_id,
                             item['product_id'],
                             item['quantity_sold'],
                             item['selling_price_etb'])
                        )
                        if result is None:
                            all_inserted = False
                            break

                    if all_inserted:
                        st.session_state.sale_submitted = True
                        st.session_state.sale_items = []
                        # Clear the cache so dashboard refreshes
                        st.cache_data.clear()
                        st.success(
                            f"Sale recorded successfully! "
                            f"Sale ID: {sale_id} | "
                            f"Revenue: {total_revenue:,.0f} ETB"
                        )
                        st.balloons()
                    else:
                        st.error(
                            "Some items failed to save. "
                            "Please check and try again."
                        )

    with btn2:
        if st.button("🗑️ Clear All Items", use_container_width=True):
            st.session_state.sale_items = []
            st.rerun()

else:
    st.info(
        "No items added yet. "
        "Use Step 2 above to add products to this sale."
    )

# -------------------------------------------------------
# SIDEBAR INFO
# -------------------------------------------------------
with st.sidebar:
    st.markdown("### 🛒 Record Sale")
    st.markdown("""
        <div style='font-size:13px; color:#94A3B8;'>
        <p><b>How to use:</b></p>
        <ol>
            <li>Set the sale date and worker</li>
            <li>Select each product sold</li>
            <li>Enter quantity and selling price</li>
            <li>Click Add Item</li>
            <li>Repeat for each product</li>
            <li>Review totals</li>
            <li>Click Submit Sale</li>
        </ol>
        <p style='color:#FCD34D;'>
        ⚠️ Submit only once per sale.<br>
        Check the review table before submitting.
        </p>
        </div>
    """, unsafe_allow_html=True)
