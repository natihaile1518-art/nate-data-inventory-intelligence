import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import date

# -------------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------------
st.set_page_config(
    page_title="Record Purchase — Nate Data",
    page_icon="📦",
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
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# DATABASE HELPERS
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
# -------------------------------------------------------
@st.cache_data(ttl=300)
def load_products_for_purchase():
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
    return run_query(
        "SELECT user_id, full_name, role FROM users WHERE is_active = 1"
    )


products_df = load_products_for_purchase()
users_df    = load_users()

# -------------------------------------------------------
# PAGE HEADER
# -------------------------------------------------------
st.markdown("<div class='page-header'>📦 Record Stock Purchase</div>",
            unsafe_allow_html=True)
st.markdown("""
    <p style='color:#94A3B8; margin-bottom:20px;'>
    Use this form when new stock arrives at the shop.
    Recording purchases keeps inventory counts accurate
    and preserves supplier price history.
    </p>
""", unsafe_allow_html=True)

st.divider()

# -------------------------------------------------------
# INITIALIZE SESSION STATE
# -------------------------------------------------------
if 'purchase_items' not in st.session_state:
    st.session_state.purchase_items = []

# -------------------------------------------------------
# STEP 1 — PURCHASE DETAILS
# -------------------------------------------------------
st.subheader("Step 1 — Purchase Details")

col1, col2, col3, col4 = st.columns(4)

with col1:
    purchase_date = st.date_input(
        "Purchase Date",
        value=date.today(),
        help="The date the stock was received"
    )

with col2:
    if not users_df.empty:
        worker_options = {
            row['full_name']: row['user_id']
            for _, row in users_df.iterrows()
        }
        selected_worker = st.selectbox(
            "Received by",
            options=list(worker_options.keys())
        )
        selected_user_id = worker_options[selected_worker]
    else:
        st.error("No workers found.")
        selected_user_id = None

with col3:
    shop_options = {'Shop 1': 1, 'Shop 2': 2, 'Warehouse': 3}
    selected_shop = st.selectbox(
        "Received at",
        options=list(shop_options.keys())
    )
    selected_location_id = shop_options[selected_shop]

with col4:
    supplier_name = st.text_input(
        "Supplier Name",
        placeholder="e.g. Addis Trading",
        help="The name of the supplier you bought from"
    )

st.divider()

# -------------------------------------------------------
# STEP 2 — ADD PRODUCTS PURCHASED
# -------------------------------------------------------
st.subheader("Step 2 — Add Products Purchased")

if not products_df.empty:
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
        qty_purchased = st.number_input(
            "Quantity",
            min_value=1,
            max_value=99999,
            value=1,
            step=1,
            key="qty_input"
        )

    with add_col3:
        purchase_price = st.number_input(
            "Purchase Price (ETB)",
            min_value=1.0,
            max_value=999999.0,
            value=100.0,
            step=10.0,
            key="price_input",
            help="The price you paid per unit to the supplier"
        )

    with add_col4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Add Item", use_container_width=True):
            st.session_state.purchase_items.append({
                'product_id'        : selected_product_id,
                'product_name'      : selected_product_name,
                'quantity'          : qty_purchased,
                'purchase_price_etb': purchase_price,
                'line_total'        : qty_purchased * purchase_price
            })

# -------------------------------------------------------
# STEP 3 — REVIEW
# -------------------------------------------------------
if st.session_state.purchase_items:
    st.divider()
    st.subheader("Step 3 — Review Purchase Items")

    purchase_df = pd.DataFrame(st.session_state.purchase_items)

    st.dataframe(
        purchase_df[['product_name', 'quantity',
                     'purchase_price_etb', 'line_total']],
        use_container_width=True,
        hide_index=True
    )

    total_units = int(purchase_df['quantity'].sum())
    total_cost  = float(purchase_df['line_total'].sum())

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Total Items", len(purchase_df))
    with m2:
        st.metric("Total Units", total_units)
    with m3:
        st.metric("Total Cost", f"{total_cost:,.0f} ETB")

    st.divider()

    # -------------------------------------------------------
    # STEP 4 — SUBMIT OR CLEAR
    # -------------------------------------------------------
    st.subheader("Step 4 — Submit or Clear")

    btn1, btn2 = st.columns(2)

    with btn1:
        if st.button("✅ Submit Purchase", use_container_width=True,
                     type="primary"):
            if selected_user_id is None:
                st.error("No worker selected.")
            elif not supplier_name.strip():
                st.error("Please enter the supplier name.")
            else:
                # Insert purchase header
                purchase_id = run_insert(
                    """INSERT INTO purchases
                       (location_id, user_id, purchase_date,
                        supplier_name, notes)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (selected_location_id,
                     selected_user_id,
                     purchase_date.strftime('%Y-%m-%d'),
                     supplier_name.strip(),
                     'Purchase recorded via Nate Data app')
                )

                if purchase_id:
                    all_inserted = True
                    for item in st.session_state.purchase_items:
                        result = run_insert(
                            """INSERT INTO purchase_items
                               (purchase_id, product_id,
                                quantity, purchase_price_etb)
                               VALUES (%s, %s, %s, %s)""",
                            (purchase_id,
                             item['product_id'],
                             item['quantity'],
                             item['purchase_price_etb'])
                        )
                        if result is None:
                            all_inserted = False
                            break

                    if all_inserted:
                        st.session_state.purchase_items = []
                        st.cache_data.clear()
                        st.success(
                            f"Purchase recorded successfully! "
                            f"Purchase ID: {purchase_id} | "
                            f"Total Cost: {total_cost:,.0f} ETB | "
                            f"Supplier: {supplier_name}"
                        )
                        st.balloons()
                    else:
                        st.error(
                            "Some items failed to save. "
                            "Please try again."
                        )

    with btn2:
        if st.button("🗑️ Clear All Items", use_container_width=True):
            st.session_state.purchase_items = []
            st.rerun()

else:
    st.info(
        "No items added yet. "
        "Use Step 2 above to add products to this purchase."
    )

# -------------------------------------------------------
# SIDEBAR INFO
# -------------------------------------------------------
with st.sidebar:
    st.markdown("### 📦 Record Purchase")
    st.markdown("""
        <div style='font-size:13px; color:#94A3B8;'>
        <p><b>How to use:</b></p>
        <ol>
            <li>Set the purchase date</li>
            <li>Select who received the stock</li>
            <li>Select which location received it</li>
            <li>Enter the supplier name</li>
            <li>Add each product purchased</li>
            <li>Enter quantity and price paid</li>
            <li>Review totals</li>
            <li>Click Submit Purchase</li>
        </ol>
        <p style='color:#FCD34D;'>
        ⚠️ The purchase price here is what YOU<br>
        paid the supplier — not the selling price.
        </p>
        </div>
    """, unsafe_allow_html=True)
