import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# -------------------------------------------------------
# PAGE CONFIGURATION
# This must be the first Streamlit command in the file
# -------------------------------------------------------
st.set_page_config(
    page_title="Nate Data — Inventory Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------
# CUSTOM STYLING
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
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #38BDF8;
    }
    .kpi-label {
        font-size: 13px;
        color: #94A3B8;
        margin-top: 4px;
    }
    .section-header {
        color: #38BDF8;
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 10px;
        padding-bottom: 6px;
        border-bottom: 1px solid #334155;
    }
    .alert-box {
        background-color: #7F1D1D;
        border-radius: 8px;
        padding: 12px 16px;
        color: #FCA5A5;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# LOAD DATA
# -------------------------------------------------------
@st.cache_data
def load_data():
    dashboard_dir = os.path.dirname(os.path.abspath(__file__))
    project_root  = os.path.dirname(dashboard_dir)
    cleaned_dir   = os.path.join(project_root, 'data', 'cleaned')

    shop_path = os.path.join(cleaned_dir, 'inventory_cleaned.csv')
    shop      = pd.read_csv(shop_path)
    shop['Count_Date'] = pd.to_datetime(shop['Count_Date'])

    wh_path   = os.path.join(cleaned_dir, 'warehouse_inventory.csv')
    warehouse = pd.read_csv(wh_path)
    warehouse['Count_Date'] = pd.to_datetime(warehouse['Count_Date'])

    combined  = pd.concat([shop, warehouse], ignore_index=True)

    return shop, warehouse, combined

shop_df, warehouse_df, combined_df = load_data()

# -------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/lightning-bolt.png", width=60)
    st.title("Nate Data")
    st.caption("Electrical Shop Intelligence")
    st.divider()

    # Location filter
    st.subheader("📍 Location")
    location_options = ["All", "Shop", "Warehouse"]
    selected_location = st.selectbox("Select Location", location_options)

    st.divider()

    # Category filter
    st.subheader("📦 Category")
    all_categories = sorted(combined_df['Category'].unique().tolist())
    selected_categories = st.multiselect(
        "Select Categories",
        options=all_categories,
        default=all_categories
    )

    st.divider()

    # Search
    st.subheader("🔍 Search")
    search_term = st.text_input("Search product name", placeholder="e.g. Tesla, Breaker...")

    st.divider()

    # Low stock threshold
    st.subheader("⚠️ Low Stock Alert")
    low_stock_threshold = st.slider(
        "Low stock threshold",
        min_value=1,
        max_value=20,
        value=5,
        step=1
    )

    st.divider()
    st.caption("© 2026 Nate Data")
    st.caption("Bahir Dar University")

# -------------------------------------------------------
# FILTER DATA BASED ON SIDEBAR SELECTIONS
# -------------------------------------------------------
# Start with the right location dataset
if selected_location == "Shop":
    filtered_df = shop_df.copy()
elif selected_location == "Warehouse":
    filtered_df = warehouse_df.copy()
else:
    filtered_df = combined_df.copy()

# Apply category filter
if selected_categories:
    filtered_df = filtered_df[filtered_df['Category'].isin(selected_categories)]

# Apply search filter
if search_term:
    filtered_df = filtered_df[
        filtered_df['Product_Name'].str.contains(search_term, case=False, na=False)
    ]

# -------------------------------------------------------
# HEADER
# -------------------------------------------------------
st.markdown("""
    <div style='text-align:center; padding: 20px 0 10px 0;'>
        <h1 style='color:#38BDF8; font-size:36px; margin-bottom:4px;'>
            ⚡ Nate Data
        </h1>
        <p style='color:#94A3B8; font-size:16px;'>
            Electrical Shop Inventory Intelligence System
        </p>
        <p style='color:#475569; font-size:13px;'>
            Dessie, Ethiopia — Real Inventory Data
        </p>
    </div>
""", unsafe_allow_html=True)

st.divider()

# -------------------------------------------------------
# KPI CARDS
# -------------------------------------------------------
total_products = len(filtered_df)
total_value    = filtered_df['Total_Stock_Value_ETB'].sum()
total_cats     = filtered_df['Category'].nunique()
total_units    = filtered_df['Quantity'].sum()
out_of_stock   = (filtered_df['Quantity'] == 0).sum()
low_stock      = ((filtered_df['Quantity'] > 0) &
                  (filtered_df['Quantity'] <= low_stock_threshold)).sum()

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-value'>{total_products:,}</div>
            <div class='kpi-label'>Total Products</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-value'>{total_value:,.0f}</div>
            <div class='kpi-label'>Total Value (ETB)</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-value'>{total_cats}</div>
            <div class='kpi-label'>Categories</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-value'>{total_units:,}</div>
            <div class='kpi-label'>Total Units</div>
        </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-value' style='color:#FCA5A5;'>{out_of_stock}</div>
            <div class='kpi-label'>Out of Stock</div>
        </div>
    """, unsafe_allow_html=True)

with col6:
    st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-value' style='color:#FCD34D;'>{low_stock}</div>
            <div class='kpi-label'>Low Stock (≤{low_stock_threshold})</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------------
# CHARTS — ROW 1
# -------------------------------------------------------
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("<div class='section-header'>📊 Inventory Value by Category</div>",
                unsafe_allow_html=True)

    value_by_cat = (
        filtered_df.groupby('Category')['Total_Stock_Value_ETB']
        .sum()
        .reset_index()
        .sort_values('Total_Stock_Value_ETB', ascending=False)
    )

    fig1 = px.bar(
        value_by_cat,
        x='Category',
        y='Total_Stock_Value_ETB',
        color='Category',
        text_auto='.2s',
        template='plotly_dark',
        labels={'Total_Stock_Value_ETB': 'Total Value (ETB)', 'Category': ''}
    )
    fig1.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=20, b=40),
        xaxis_tickangle=-35
    )
    st.plotly_chart(fig1, use_container_width=True)

with chart_col2:
    st.markdown("<div class='section-header'>📦 Total Quantity by Category</div>",
                unsafe_allow_html=True)

    qty_by_cat = (
        filtered_df.groupby('Category')['Quantity']
        .sum()
        .reset_index()
        .sort_values('Quantity', ascending=False)
    )

    fig2 = px.bar(
        qty_by_cat,
        x='Category',
        y='Quantity',
        color='Category',
        text_auto=True,
        template='plotly_dark',
        labels={'Quantity': 'Total Units', 'Category': ''}
    )
    fig2.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=20, b=40),
        xaxis_tickangle=-35
    )
    st.plotly_chart(fig2, use_container_width=True)

# -------------------------------------------------------
# CHARTS — ROW 2
# -------------------------------------------------------
chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    st.markdown("<div class='section-header'>🍩 Value Distribution by Category</div>",
                unsafe_allow_html=True)

    fig3 = px.pie(
        value_by_cat,
        names='Category',
        values='Total_Stock_Value_ETB',
        hole=0.5,
        template='plotly_dark'
    )
    fig3.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=20, b=20),
        legend=dict(font=dict(size=10))
    )
    st.plotly_chart(fig3, use_container_width=True)

with chart_col4:
    st.markdown("<div class='section-header'>💰 Top 10 Most Expensive Products</div>",
                unsafe_allow_html=True)

    top_expensive = (
        filtered_df[['Product_Name', 'Category', 'Purchase_Price_ETB']]
        .drop_duplicates(subset=['Product_Name', 'Purchase_Price_ETB'])
        .sort_values('Purchase_Price_ETB', ascending=True)
        .tail(10)
    )

    fig4 = px.bar(
        top_expensive,
        x='Purchase_Price_ETB',
        y='Product_Name',
        orientation='h',
        color='Purchase_Price_ETB',
        color_continuous_scale='Blues',
        template='plotly_dark',
        labels={'Purchase_Price_ETB': 'Price (ETB)', 'Product_Name': ''}
    )
    fig4.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=20, b=20),
        coloraxis_showscale=False
    )
    st.plotly_chart(fig4, use_container_width=True)

# -------------------------------------------------------
# LOW STOCK ALERT
# -------------------------------------------------------
st.markdown("<div class='section-header'>🚨 Stock Alerts</div>",
            unsafe_allow_html=True)

alert_col1, alert_col2 = st.columns(2)

with alert_col1:
    st.markdown("**Out of Stock Products**")
    oos = filtered_df[filtered_df['Quantity'] == 0][
        ['Product_ID', 'Product_Name', 'Category', 'Purchase_Price_ETB', 'Location']
    ].reset_index(drop=True)

    if oos.empty:
        st.success("No out of stock products.")
    else:
        st.error(f"{len(oos)} product(s) are out of stock.")
        st.dataframe(oos, use_container_width=True, height=250)

with alert_col2:
    st.markdown(f"**Low Stock Products (Quantity ≤ {low_stock_threshold})**")
    low = filtered_df[
        (filtered_df['Quantity'] > 0) &
        (filtered_df['Quantity'] <= low_stock_threshold)
    ][['Product_ID', 'Product_Name', 'Category',
       'Quantity', 'Purchase_Price_ETB', 'Location']].sort_values('Quantity').reset_index(drop=True)

    if low.empty:
        st.success("No low stock products.")
    else:
        st.warning(f"{len(low)} product(s) are running low.")
        st.dataframe(low, use_container_width=True, height=250)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------------
# FULL PRODUCT TABLE
# -------------------------------------------------------
st.markdown("<div class='section-header'>📋 Full Product Inventory</div>",
            unsafe_allow_html=True)

display_df = filtered_df[[
    'Product_ID', 'Product_Name', 'Category', 'Specification',
    'Quantity', 'Purchase_Price_ETB', 'Total_Stock_Value_ETB',
    'Location', 'Count_Date'
]].reset_index(drop=True)

st.dataframe(
    display_df,
    use_container_width=True,
    height=400
)

# Summary below table
st.caption(
    f"Showing {len(display_df)} products | "
    f"Total Value: {display_df['Total_Stock_Value_ETB'].sum():,.0f} ETB | "
    f"Total Units: {display_df['Quantity'].sum():,}"
)
