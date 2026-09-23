import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error

# -------------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------------
st.set_page_config(
    page_title="Manage Products — Nate Data",
    page_icon="🛠️",
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
        db = st.secrets["mysql"]
        return mysql.connector.connect(
            host                = db["host"],
            port                = int(db["port"]),
            user                = db["user"],
            password            = db["password"],
            database            = db["database"],
            ssl_disabled        = False,
            ssl_verify_cert     = False,
            ssl_verify_identity = False
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


def run_update(sql, params):
    """
    Executes an UPDATE statement.
    Returns True if successful, False if failed.
    Different from run_insert because UPDATE does not
    return a new ID — it just modifies existing rows.
    """
    conn = get_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return True
    except Error as e:
        st.error(f"Update failed: {e}")
        conn.rollback()
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# -------------------------------------------------------
# LOAD REFERENCE DATA
# -------------------------------------------------------
@st.cache_data(ttl=60)
def load_products():
    sql = """
        SELECT
            p.product_id, p.product_name,
            c.category_name, c.category_id,
            p.specification, p.is_active,
            p.created_at
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        ORDER BY c.category_name, p.product_name
    """
    return run_query(sql)


@st.cache_data(ttl=300)
def load_categories():
    return run_query(
        "SELECT category_id, category_name FROM categories "
        "WHERE is_active = 1 ORDER BY category_name"
    )


products_df   = load_products()
categories_df = load_categories()

# -------------------------------------------------------
# PAGE HEADER
# -------------------------------------------------------
st.markdown("<div class='page-header'>🛠️ Manage Products</div>",
            unsafe_allow_html=True)
st.markdown("""
    <p style='color:#94A3B8; margin-bottom:20px;'>
    Add new products, update existing ones, or deactivate
    discontinued products. Never delete a product that has
    sales history — use deactivate instead.
    </p>
""", unsafe_allow_html=True)

st.divider()

# -------------------------------------------------------
# TABS — three separate operations on one page
# Tabs keep the page organized without needing
# separate pages for each small operation
# -------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "➕ Add New Product",
    "✏️ Update Product",
    "🔴 Deactivate / Reactivate"
])

# -------------------------------------------------------
# TAB 1 — ADD NEW PRODUCT
# -------------------------------------------------------
with tab1:
    st.subheader("Add a New Product")
    st.markdown("""
        <p style='color:#94A3B8; font-size:13px;'>
        Use this when the shop starts selling a product
        that does not exist in the database yet.
        </p>
    """, unsafe_allow_html=True)

    # Find the next available Product ID automatically
    next_id_df = run_query("""
        SELECT CONCAT('P', LPAD(
            CAST(SUBSTRING(MAX(product_id), 2) AS UNSIGNED) + 1,
            4, '0')) AS next_id
        FROM products
    """)
    suggested_id = next_id_df['next_id'].iloc[0] \
        if not next_id_df.empty else 'P0202'

    col1, col2 = st.columns(2)

    with col1:
        new_product_id = st.text_input(
            "Product ID",
            value=suggested_id,
            help="Auto-suggested. Change only if needed."
        )
        new_product_name = st.text_input(
            "Product Name",
            placeholder="e.g. Bright Star Lamp"
        )

    with col2:
        if not categories_df.empty:
            cat_options = {
                row['category_name']: row['category_id']
                for _, row in categories_df.iterrows()
            }
            selected_cat_name = st.selectbox(
                "Category",
                options=list(cat_options.keys())
            )
            selected_cat_id = cat_options[selected_cat_name]
        else:
            st.error("No categories found.")
            selected_cat_id = None

        new_spec = st.text_input(
            "Specification (optional)",
            placeholder="e.g. 7W, 10A, 25A — leave blank if not applicable"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("➕ Add Product", type="primary",
                 use_container_width=True, key="add_btn"):
        if not new_product_id.strip():
            st.error("Product ID is required.")
        elif not new_product_name.strip():
            st.error("Product Name is required.")
        elif selected_cat_id is None:
            st.error("Category is required.")
        else:
            spec_value = new_spec.strip() if new_spec.strip() else None
            result = run_insert(
                """INSERT INTO products
                   (product_id, product_name, category_id, specification)
                   VALUES (%s, %s, %s, %s)""",
                (new_product_id.strip(),
                 new_product_name.strip(),
                 selected_cat_id,
                 spec_value)
            )
            if result is not None:
                st.cache_data.clear()
                st.success(
                    f"Product added: {new_product_id} — "
                    f"{new_product_name} ({selected_cat_name})"
                )
            else:
                st.error(
                    "Failed to add product. "
                    "The Product ID may already exist."
                )

# -------------------------------------------------------
# TAB 2 — UPDATE PRODUCT
# -------------------------------------------------------
with tab2:
    st.subheader("Update an Existing Product")
    st.markdown("""
        <p style='color:#94A3B8; font-size:13px;'>
        Fix a typo in a product name or update its specification.
        The product's sales history is not affected.
        </p>
    """, unsafe_allow_html=True)

    if not products_df.empty:
        active_products = products_df[products_df['is_active'] == 1]
        product_options = {
            f"{row['product_id']} — {row['product_name']} "
            f"({row['category_name']})": row['product_id']
            for _, row in active_products.iterrows()
        }

        selected_display = st.selectbox(
            "Select product to update",
            options=list(product_options.keys()),
            key="update_select"
        )
        selected_pid = product_options[selected_display]

        # Load current values for the selected product
        current = products_df[
            products_df['product_id'] == selected_pid
        ].iloc[0]

        col1, col2 = st.columns(2)

        with col1:
            updated_name = st.text_input(
                "Product Name",
                value=current['product_name'],
                key="update_name"
            )

        with col2:
            current_spec = current['specification'] \
                if current['specification'] and \
                current['specification'] != 'None' else ''
            updated_spec = st.text_input(
                "Specification",
                value=current_spec,
                key="update_spec"
            )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("✏️ Save Changes", type="primary",
                     use_container_width=True, key="update_btn"):
            spec_value = updated_spec.strip() \
                if updated_spec.strip() else None
            success = run_update(
                """UPDATE products
                   SET product_name = %s, specification = %s
                   WHERE product_id = %s""",
                (updated_name.strip(), spec_value, selected_pid)
            )
            if success:
                st.cache_data.clear()
                st.success(
                    f"Updated: {selected_pid} — {updated_name}"
                )
            else:
                st.error("Update failed. Please try again.")
    else:
        st.warning("No products found.")

# -------------------------------------------------------
# TAB 3 — DEACTIVATE / REACTIVATE
# -------------------------------------------------------
with tab3:
    st.subheader("Deactivate or Reactivate a Product")
    st.markdown("""
        <p style='color:#94A3B8; font-size:13px;'>
        Deactivating a product hides it from sale entry forms
        and active reports. All historical sales data is preserved.
        Never delete a product — deactivate it instead.
        </p>
    """, unsafe_allow_html=True)

    if not products_df.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**🔴 Deactivate an Active Product**")
            active_products = products_df[products_df['is_active'] == 1]
            if not active_products.empty:
                deact_options = {
                    f"{row['product_id']} — {row['product_name']}":
                    row['product_id']
                    for _, row in active_products.iterrows()
                }
                deact_selection = st.selectbox(
                    "Select product to deactivate",
                    options=list(deact_options.keys()),
                    key="deact_select"
                )
                deact_pid = deact_options[deact_selection]

                if st.button("🔴 Deactivate", use_container_width=True,
                             key="deact_btn"):
                    success = run_update(
                        "UPDATE products SET is_active = 0 "
                        "WHERE product_id = %s",
                        (deact_pid,)
                    )
                    if success:
                        st.cache_data.clear()
                        st.success(
                            f"{deact_pid} deactivated. "
                            f"Historical data preserved."
                        )
            else:
                st.info("No active products.")

        with col2:
            st.markdown("**🟢 Reactivate an Inactive Product**")
            inactive_products = products_df[products_df['is_active'] == 0]
            if not inactive_products.empty:
                react_options = {
                    f"{row['product_id']} — {row['product_name']}":
                    row['product_id']
                    for _, row in inactive_products.iterrows()
                }
                react_selection = st.selectbox(
                    "Select product to reactivate",
                    options=list(react_options.keys()),
                    key="react_select"
                )
                react_pid = react_options[react_selection]

                if st.button("🟢 Reactivate", use_container_width=True,
                             key="react_btn"):
                    success = run_update(
                        "UPDATE products SET is_active = 1 "
                        "WHERE product_id = %s",
                        (react_pid,)
                    )
                    if success:
                        st.cache_data.clear()
                        st.success(f"{react_pid} reactivated.")
            else:
                st.info("No inactive products.")

# -------------------------------------------------------
# PRODUCT TABLE — full view at the bottom
# -------------------------------------------------------
st.divider()
st.subheader("Current Product Catalogue")

if not products_df.empty:
    status_filter = st.radio(
        "Show",
        options=["Active only", "All products"],
        horizontal=True
    )
    display_df = products_df if status_filter == "All products" \
        else products_df[products_df['is_active'] == 1]

    st.dataframe(
        display_df[[
            'product_id', 'product_name', 'category_name',
            'specification', 'is_active', 'created_at'
        ]],
        use_container_width=True,
        height=400,
        hide_index=True
    )
    st.caption(f"Showing {len(display_df)} products")

# -------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------
with st.sidebar:
    st.markdown("### 🛠️ Manage Products")
    st.markdown("""
        <div style='font-size:13px; color:#94A3B8;'>
        <p><b>Three operations:</b></p>
        <p>➕ <b>Add</b> — new product the shop sells</p>
        <p>✏️ <b>Update</b> — fix a name or specification</p>
        <p>🔴 <b>Deactivate</b> — discontinued products</p>
        <hr style='border-color:#334155;'>
        <p style='color:#FCD34D;'>
        ⚠️ Never delete a product.<br>
        Deactivate it instead to preserve sales history.
        </p>
        </div>
    """, unsafe_allow_html=True)
