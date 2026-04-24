import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os

# ─── CONFIG ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Northwind Traders | Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Background */
    .stApp { background-color: #F0F4F8; }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D47A1 0%, #1565C0 50%, #1976D2 100%);
    }
    section[data-testid="stSidebar"] * { color: white !important; }
    section[data-testid="stSidebar"] .stSelectbox label { color: #BBDEFB !important; }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background: white;
        border: none;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #1A73E8;
    }
    div[data-testid="metric-container"] label { color: #5F6368 !important; font-size: 13px !important; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #1A73E8 !important; font-size: 28px !important; font-weight: 700 !important;
    }

    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, #1A73E8, #0D47A1);
        color: white;
        padding: 12px 20px;
        border-radius: 10px;
        margin: 20px 0 15px 0;
        font-size: 20px;
        font-weight: 700;
    }

    /* Chart containers */
    div[data-testid="stPlotlyChart"] {
        background: white;
        border-radius: 12px;
        padding: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }

    /* Hide hamburger */
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─── LOAD DATA ────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))

@st.cache_data
def load_data():
    orders        = pd.read_csv(os.path.join(BASE, "orders.csv"),        encoding='latin-1')
    order_details = pd.read_csv(os.path.join(BASE, "order_details.csv"), encoding='latin-1')
    customers     = pd.read_csv(os.path.join(BASE, "customers.csv"),     encoding='latin-1')
    products      = pd.read_csv(os.path.join(BASE, "products.csv"),      encoding='latin-1')
    categories    = pd.read_csv(os.path.join(BASE, "categories.csv"),    encoding='latin-1')
    employees     = pd.read_csv(os.path.join(BASE, "employees.csv"),     encoding='latin-1')
    shippers      = pd.read_csv(os.path.join(BASE, "shippers.csv"),      encoding='latin-1')

    customers.columns = customers.columns.str.strip()
    customers = customers.rename(columns={'city': 'customer_city', 'country': 'customer_country'})

    orders['orderDate']    = pd.to_datetime(orders['orderDate'])
    orders['shippedDate']  = pd.to_datetime(orders['shippedDate'],  errors='coerce')
    orders['requiredDate'] = pd.to_datetime(orders['requiredDate'], errors='coerce')
    orders['year']  = orders['orderDate'].dt.year
    orders['month'] = orders['orderDate'].dt.to_period('M').astype(str)

    order_details['revenue'] = (
        order_details['quantity'] * order_details['unitPrice'] * (1 - order_details['discount'])
    )

    df = (order_details
          .merge(orders,     on='orderID')
          .merge(customers,  on='customerID')
          .merge(products,   on='productID')
          .merge(categories, on='categoryID')
          .merge(employees,  on='employeeID'))

    return df, orders, shippers

df, orders, shippers = load_data()

# ─── CHART STYLE ──────────────────────────────────────────────────────────────
BLUE  = '#1A73E8'
BLUES = ['#0D47A1','#1565C0','#1976D2','#1E88E5','#42A5F5','#90CAF9','#BBDEFB']
RED   = '#EA4335'

def style(fig, height=380):
    fig.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Inter, Arial', size=12, color='#3C4043'),
        margin=dict(l=10, r=10, t=40, b=10),
        height=height,
        title_font=dict(size=14, color='#1A73E8', family='Inter, Arial'),
        legend=dict(bgcolor='rgba(0,0,0,0)', borderwidth=0)
    )
    fig.update_xaxes(showgrid=True, gridcolor='#F1F3F4', tickfont=dict(size=11))
    fig.update_yaxes(showgrid=True, gridcolor='#F1F3F4', tickfont=dict(size=11))
    return fig

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📦 Northwind Traders")
    st.markdown("*Analytics Dashboard*")
    st.markdown("---")

    st.markdown("### 🔍 Filters")

    # Page selector
    page = st.radio("📄 Navigate to", [
        "📊 Executive Summary",
        "🛍️ Product Analysis",
        "👥 Customer Analysis",
        "⚙️ Operations"
    ])

    st.markdown("---")

    # Year filter
    years = ["All"] + sorted(df['year'].dropna().unique().astype(str).tolist())
    sel_year = st.selectbox("📅 Year", years)

    # Country filter
    countries = ["All"] + sorted(df['customer_country'].dropna().unique().tolist())
    sel_country = st.selectbox("🌍 Country", countries)

    # Category filter
    cats = ["All"] + sorted(df['categoryName'].dropna().unique().tolist())
    sel_cat = st.selectbox("📦 Category", cats)

    st.markdown("---")
    st.markdown("**Data Period**")
    st.markdown(f"🗓️ {df['orderDate'].min().strftime('%b %Y')} – {df['orderDate'].max().strftime('%b %Y')}")
    st.markdown(f"📋 {df['orderID'].nunique():,} total orders")

# ─── APPLY FILTERS ────────────────────────────────────────────────────────────
dff = df.copy()
if sel_year    != "All": dff = dff[dff['year'].astype(str) == sel_year]
if sel_country != "All": dff = dff[dff['customer_country'] == sel_country]
if sel_cat     != "All": dff = dff[dff['categoryName'] == sel_cat]

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — EXECUTIVE SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Executive Summary":
    st.markdown('<div class="section-header">📊 Executive Summary</div>', unsafe_allow_html=True)

    # KPI Cards
    total_rev   = dff['revenue'].sum()
    total_orders= dff['orderID'].nunique()
    total_cust  = dff['customerID'].nunique()
    avg_ov      = dff.groupby('orderID')['revenue'].sum().mean()
    total_qty   = dff['quantity'].sum()

    k1,k2,k3,k4,k5 = st.columns(5)
    k1.metric("💰 Total Revenue",    f"${total_rev:,.0f}")
    k2.metric("📦 Total Orders",     f"{total_orders:,}")
    k3.metric("👥 Active Customers", f"{total_cust:,}")
    k4.metric("🛒 Avg Order Value",  f"${avg_ov:,.0f}")
    k5.metric("📮 Units Sold",       f"{total_qty:,}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 1: Revenue Trend + Revenue by Category
    col1, col2 = st.columns([2,1])
    with col1:
        monthly = dff.groupby('month')['revenue'].sum().reset_index().sort_values('month')
        fig = px.area(monthly, x='month', y='revenue',
                      title='📈 Monthly Revenue Trend',
                      color_discrete_sequence=[BLUE])
        fig.update_traces(fill='tozeroy', fillcolor='rgba(26,115,232,0.1)', line_color=BLUE, line_width=2.5)
        st.plotly_chart(style(fig, 360), use_container_width=True)
    with col2:
        cat_rev = dff.groupby('categoryName')['revenue'].sum().reset_index()
        fig = px.pie(cat_rev, names='categoryName', values='revenue',
                     title='🏷️ Revenue by Category',
                     color_discrete_sequence=BLUES, hole=0.4)
        fig.update_traces(textposition='inside', textinfo='percent+label',
                          textfont_size=10)
        st.plotly_chart(style(fig, 360), use_container_width=True)

    # Row 2: Top Countries + Monthly Orders
    col1, col2 = st.columns(2)
    with col1:
        country_rev = dff.groupby('customer_country')['revenue'].sum().reset_index().sort_values('revenue', ascending=True).tail(10)
        fig = px.bar(country_rev, x='revenue', y='customer_country', orientation='h',
                     title='🌍 Top 10 Countries by Revenue',
                     color='revenue', color_continuous_scale='Blues',
                     text='revenue')
        fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside', textfont_size=10)
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(style(fig, 380), use_container_width=True)
    with col2:
        monthly_orders = dff.groupby('month')['orderID'].nunique().reset_index().sort_values('month')
        fig = px.bar(monthly_orders, x='month', y='orderID',
                     title='📦 Monthly Order Volume',
                     color_discrete_sequence=[BLUE])
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(style(fig, 380), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — PRODUCT ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🛍️ Product Analysis":
    st.markdown('<div class="section-header">🛍️ Product & Category Analysis</div>', unsafe_allow_html=True)

    # KPI
    k1,k2,k3 = st.columns(3)
    k1.metric("🏷️ Total Products",    f"{dff['productName'].nunique():,}")
    k2.metric("📂 Categories",         f"{dff['categoryName'].nunique():,}")
    k3.metric("💸 Avg Discount",       f"{dff['discount'].mean()*100:.1f}%")
    st.markdown("<br>", unsafe_allow_html=True)

    # Row 1: Top Products + Category Revenue
    col1, col2 = st.columns([3,2])
    with col1:
        prod_rev = dff.groupby('productName')['revenue'].sum().reset_index().sort_values('revenue', ascending=True).tail(10)
        fig = px.bar(prod_rev, x='revenue', y='productName', orientation='h',
                     title='🥇 Top 10 Products by Revenue',
                     color='revenue', color_continuous_scale='Blues', text='revenue')
        fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside', textfont_size=9)
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(style(fig, 400), use_container_width=True)
    with col2:
        cat_qty = dff.groupby('categoryName')['quantity'].sum().reset_index().sort_values('quantity', ascending=False)
        fig = px.bar(cat_qty, x='categoryName', y='quantity',
                     title='📦 Units Sold by Category',
                     color='quantity', color_continuous_scale='Blues')
        fig.update_layout(xaxis_tickangle=-30)
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(style(fig, 400), use_container_width=True)

    # Row 2: Discount vs Revenue Scatter + Discontinued
    col1, col2 = st.columns([2,1])
    with col1:
        prod_analysis = dff.groupby(['productName','categoryName']).agg(
            revenue=('revenue','sum'), avg_discount=('discount','mean'), qty=('quantity','sum')
        ).reset_index()
        fig = px.scatter(prod_analysis, x='avg_discount', y='revenue',
                         hover_name='productName', size='qty', color='categoryName',
                         title='💡 Discount Rate vs Revenue per Product',
                         labels={'avg_discount':'Avg Discount Rate','revenue':'Total Revenue'},
                         color_discrete_sequence=BLUES)
        fig.update_traces(marker=dict(opacity=0.8, line=dict(width=1, color='white')))
        st.plotly_chart(style(fig, 380), use_container_width=True)
    with col2:
        disc_status = dff.groupby('discontinued')['revenue'].sum().reset_index()
        disc_status['status'] = disc_status['discontinued'].map({0:'Active 🟢', 1:'Discontinued 🔴'})
        fig = px.pie(disc_status, names='status', values='revenue',
                     title='⚠️ Active vs Discontinued Revenue',
                     color_discrete_sequence=[BLUE, RED], hole=0.45)
        st.plotly_chart(style(fig, 380), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — CUSTOMER ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "👥 Customer Analysis":
    st.markdown('<div class="section-header">👥 Customer Analysis</div>', unsafe_allow_html=True)

    k1,k2,k3 = st.columns(3)
    k1.metric("👥 Total Customers",    f"{dff['customerID'].nunique():,}")
    k2.metric("🌍 Countries Served",   f"{dff['customer_country'].nunique():,}")
    k3.metric("📦 Avg Orders/Customer",f"{dff.groupby('customerID')['orderID'].nunique().mean():.1f}")
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([3,2])
    with col1:
        top_cust = dff.groupby(['companyName','customer_country'])['revenue'].sum().reset_index()
        top_cust = top_cust.sort_values('revenue', ascending=True).tail(10)
        fig = px.bar(top_cust, x='revenue', y='companyName', orientation='h',
                     title='🏆 Top 10 Customers by Revenue',
                     color='customer_country',
                     color_discrete_sequence=BLUES, text='revenue')
        fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside', textfont_size=9)
        st.plotly_chart(style(fig, 400), use_container_width=True)
    with col2:
        country_orders = dff.groupby('customer_country').agg(
            total_orders=('orderID','nunique'), total_revenue=('revenue','sum')
        ).reset_index().sort_values('total_revenue', ascending=False).head(8)
        fig = px.bar(country_orders, x='customer_country', y='total_revenue',
                     title='🌍 Revenue by Country',
                     color='total_revenue', color_continuous_scale='Blues')
        fig.update_layout(xaxis_tickangle=-30)
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(style(fig, 400), use_container_width=True)

    # Geo map + Customer order frequency
    col1, col2 = st.columns([3,2])
    with col1:
        geo = dff.groupby('customer_country')['revenue'].sum().reset_index()
        fig = px.choropleth(geo, locations='customer_country', locationmode='country names',
                            color='revenue', title='🗺️ Revenue Heatmap by Country',
                            color_continuous_scale='Blues')
        fig.update_layout(geo=dict(showframe=False, showcoastlines=True, bgcolor='white'))
        st.plotly_chart(style(fig, 400), use_container_width=True)
    with col2:
        cust_freq = dff.groupby('customerID')['orderID'].nunique().reset_index()
        cust_freq.columns = ['customerID','order_count']
        freq_bins = pd.cut(cust_freq['order_count'], bins=[0,3,7,12,20,50], labels=['1-3','4-7','8-12','13-20','20+'])
        freq_dist = freq_bins.value_counts().sort_index().reset_index()
        freq_dist.columns = ['frequency','count']
        fig = px.bar(freq_dist, x='frequency', y='count',
                     title='📊 Customer Order Frequency',
                     color_discrete_sequence=[BLUE])
        st.plotly_chart(style(fig, 400), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — OPERATIONS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⚙️ Operations":
    st.markdown('<div class="section-header">⚙️ Operations Performance</div>', unsafe_allow_html=True)

    # Employee KPIs
    k1,k2,k3 = st.columns(3)
    k1.metric("👨‍💼 Employees",          f"{dff['employeeID'].nunique():,}")
    k2.metric("🚚 Shippers",            "3")
    on_time_pct = 0
    ship_df = orders.merge(shippers, on='shipperID')
    ship_df = ship_df[ship_df['shippedDate'].notna()].copy()
    ship_df['delay'] = (ship_df['shippedDate'] - ship_df['requiredDate']).dt.days
    on_time_pct = (ship_df['delay'] <= 0).mean() * 100
    k3.metric("✅ On-Time Delivery",    f"{on_time_pct:.1f}%")
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        emp_rev = dff.groupby('employeeName').agg(
            revenue=('revenue','sum'), orders=('orderID','nunique')
        ).reset_index().sort_values('revenue', ascending=False)
        fig = px.bar(emp_rev, x='employeeName', y='revenue',
                     title='👨‍💼 Revenue Generated by Employee',
                     color='revenue', color_continuous_scale='Blues', text='revenue')
        fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside', textfont_size=9)
        fig.update_coloraxes(showscale=False)
        fig.update_layout(xaxis_tickangle=-20)
        st.plotly_chart(style(fig, 380), use_container_width=True)
    with col2:
        emp_orders = emp_rev.sort_values('orders', ascending=False)
        fig = px.bar(emp_orders, x='employeeName', y='orders',
                     title='📦 Orders Handled by Employee',
                     color='orders', color_continuous_scale='Blues')
        fig.update_coloraxes(showscale=False)
        fig.update_layout(xaxis_tickangle=-20)
        st.plotly_chart(style(fig, 380), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        ship_df['status'] = ship_df['delay'].apply(lambda x: 'On Time 🟢' if x <= 0 else 'Late 🔴')
        ship_summary = ship_df.groupby(['companyName','status']).size().reset_index(name='count')
        fig = px.bar(ship_summary, x='companyName', y='count', color='status', barmode='group',
                     title='🚚 Shipper: On Time vs Late Deliveries',
                     color_discrete_map={'On Time 🟢': BLUE, 'Late 🔴': RED})
        st.plotly_chart(style(fig, 360), use_container_width=True)
    with col2:
        avg_delay = ship_df.groupby('companyName')['delay'].mean().reset_index()
        avg_delay.columns = ['Shipper','Avg Delay (days)']
        fig = px.bar(avg_delay, x='Shipper', y='Avg Delay (days)',
                     title='⏱️ Avg Delivery Delay by Shipper',
                     color='Avg Delay (days)',
                     color_continuous_scale=[[0,'#1A73E8'],[0.5,'#FFA726'],[1,'#EA4335']])
        fig.update_coloraxes(showscale=False)
        fig.add_hline(y=0, line_dash='dash', line_color='gray', opacity=0.5)
        st.plotly_chart(style(fig, 360), use_container_width=True)

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#9AA0A6; font-size:12px;'>"
    "📦 Northwind Traders Analytics Dashboard &nbsp;|&nbsp; Built with Streamlit & Plotly &nbsp;|&nbsp; Data: 2013–2015"
    "</div>", unsafe_allow_html=True
)
