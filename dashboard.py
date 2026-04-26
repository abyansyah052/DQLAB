import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
import unicodedata

st.set_page_config(
    page_title="Northwind Traders Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D47A1 0%, #1565C0 100%);
    }
    section[data-testid="stSidebar"] * { color: #FFFFFF !important; }
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
        background: rgba(255,255,255,0.15) !important;
        border: 1px solid rgba(255,255,255,0.35) !important;
        color: white !important;
    }
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        background: rgba(255,255,255,0.08);
        border-radius: 6px;
        padding: 6px 10px;
        margin-bottom: 4px;
        cursor: pointer;
    }
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
        background: rgba(255,255,255,0.18);
    }
    section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.25) !important; }

    div[data-testid="stPlotlyChart"] {
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        background: #FFFFFF;
    }

    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

BASE = os.path.dirname(os.path.abspath(__file__))

def clean_str(s):
    if not isinstance(s, str):
        return s
    s = unicodedata.normalize("NFKC", s)
    s = ''.join(c for c in s if c.isprintable())
    return s.strip()

def kpi_card(label, value, cols):
    """Render KPI card pakai HTML murni — tidak terpengaruh versi Streamlit."""
    html = f"""
    <div style="
        background:#FFFFFF;
        border:1px solid #D1D5DB;
        border-top:3px solid #1565C0;
        border-radius:8px;
        box-shadow:0 1px 4px rgba(0,0,0,0.08);
        padding:16px 18px;
        min-height:80px;
    ">
        <div style="font-size:11px;font-weight:600;color:#6B7280;text-transform:uppercase;
                    letter-spacing:0.06em;margin-bottom:6px;">{label}</div>
        <div style="font-size:clamp(18px,1.8vw,26px);font-weight:800;color:#111827;
                    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{value}</div>
    </div>
    """
    cols.markdown(html, unsafe_allow_html=True)

@st.cache_data
def load_data():
    orders        = pd.read_csv(os.path.join(BASE, "orders.csv"),        encoding="latin-1")
    order_details = pd.read_csv(os.path.join(BASE, "order_details.csv"), encoding="latin-1")
    customers     = pd.read_csv(os.path.join(BASE, "customers.csv"),     encoding="latin-1")
    products      = pd.read_csv(os.path.join(BASE, "products.csv"),      encoding="latin-1")
    categories    = pd.read_csv(os.path.join(BASE, "categories.csv"),    encoding="latin-1")
    employees     = pd.read_csv(os.path.join(BASE, "employees.csv"),     encoding="latin-1")
    shippers      = pd.read_csv(os.path.join(BASE, "shippers.csv"),      encoding="latin-1")

    customers.columns  = customers.columns.str.strip()
    categories.columns = categories.columns.str.strip()
    categories["categoryName"] = categories["categoryName"].apply(clean_str)
    customers = customers.rename(columns={"city": "customer_city", "country": "customer_country"})

    orders["orderDate"]    = pd.to_datetime(orders["orderDate"])
    orders["shippedDate"]  = pd.to_datetime(orders["shippedDate"],  errors="coerce")
    orders["requiredDate"] = pd.to_datetime(orders["requiredDate"], errors="coerce")
    orders["year"]  = orders["orderDate"].dt.year
    orders["month"] = orders["orderDate"].dt.to_period("M").astype(str)

    order_details["revenue"] = (
        order_details["quantity"] * order_details["unitPrice"] * (1 - order_details["discount"])
    )

    df = (order_details
          .merge(orders,     on="orderID")
          .merge(customers,  on="customerID")
          .merge(products,   on="productID")
          .merge(categories, on="categoryID")
          .merge(employees,  on="employeeID"))

    return df, orders, shippers

df, orders, shippers = load_data()

C_BLUE_DARK  = "#0D47A1"
C_BLUE       = "#1565C0"
C_BLUE_MID   = "#1976D2"
C_BLUE_LIGHT = "#2196F3"
C_BLUE_SOFT  = "#42A5F5"
C_RED        = "#C62828"
C_GREEN      = "#2E7D32"
C_ORANGE     = "#E65100"
C_TEAL       = "#00695C"
C_PURPLE     = "#4527A0"
C_TEXT       = "#111827"
C_TEXT_MUTED = "#6B7280"

PALETTE_DIV = [C_BLUE_DARK, C_BLUE_MID, C_BLUE_LIGHT, C_TEAL, C_PURPLE, C_ORANGE, C_RED, "#37474F"]

LEGEND_STYLE = dict(bgcolor="rgba(0,0,0,0)", borderwidth=0, font=dict(size=11, color=C_TEXT))

def colorbar_cfg(title=""):
    return dict(title=title, tickfont=dict(color=C_TEXT_MUTED, size=11), title_font=dict(color=C_TEXT_MUTED, size=11))

def style(fig, height=360, showlegend=True, rotated_labels=False):
    bottom_margin = 60 if rotated_labels else 8
    fig.update_layout(
        plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
        font=dict(family="Inter, Arial, sans-serif", size=12, color=C_TEXT),
        height=height, margin=dict(l=8, r=8, t=44, b=bottom_margin),
        title_font=dict(size=13, color=C_TEXT, family="Inter, Arial, sans-serif"),
        showlegend=showlegend, legend=LEGEND_STYLE
    )
    fig.update_xaxes(showgrid=True, gridcolor="#F3F4F6", linecolor="#E5E7EB",
                     tickfont=dict(size=11, color=C_TEXT_MUTED), title_font=dict(color=C_TEXT_MUTED))
    fig.update_yaxes(showgrid=True, gridcolor="#F3F4F6", linecolor="#E5E7EB",
                     tickfont=dict(size=11, color=C_TEXT_MUTED), title_font=dict(color=C_TEXT_MUTED))
    fig.update_coloraxes(colorbar=dict(tickfont=dict(color=C_TEXT_MUTED, size=11), title_font=dict(color=C_TEXT_MUTED, size=11)))
    return fig

def page_header(title, subtitle=""):
    st.markdown(
        f'''<div style="border-left:4px solid #1565C0;padding:4px 0 4px 14px;margin-bottom:20px;">
        <div style="font-size:20px;font-weight:700;color:#111827;">{title}</div>
        <div style="font-size:13px;color:#6B7280;">{subtitle}</div></div>''',
        unsafe_allow_html=True
    )

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-size:16px;font-weight:700;letter-spacing:0.02em;margin-bottom:2px;">Northwind Traders</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:11px;opacity:0.75;margin-bottom:12px;">Business Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio("Navigation", [
        "Executive Summary",
        "Product Analysis",
        "Customer Analysis",
        "Operations Performance"
    ])

    st.markdown("---")
    st.markdown('<div style="font-size:11px;font-weight:600;letter-spacing:0.06em;opacity:0.8;margin-bottom:8px;">FILTERS</div>', unsafe_allow_html=True)

    years = ["All"] + sorted(df["year"].dropna().unique().astype(str).tolist())
    sel_year = st.selectbox("Year", years)

    countries = ["All"] + sorted(df["customer_country"].dropna().unique().tolist())
    sel_country = st.selectbox("Country", countries)

    cats = ["All"] + sorted(df["categoryName"].dropna().unique().tolist())
    sel_cat = st.selectbox("Category", cats)

    st.markdown("---")
    st.markdown(f'<div style="font-size:11px;opacity:0.8;">Period: {df["orderDate"].min().strftime("%b %Y")} - {df["orderDate"].max().strftime("%b %Y")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:11px;opacity:0.8;">Total Records: {len(df):,}</div>', unsafe_allow_html=True)

# ── FILTERS ───────────────────────────────────────────────────────────────────
dff = df.copy()
if sel_year    != "All": dff = dff[dff["year"].astype(str) == sel_year]
if sel_country != "All": dff = dff[dff["customer_country"] == sel_country]
if sel_cat     != "All": dff = dff[dff["categoryName"] == sel_cat]

if dff.empty:
    st.warning("⚠️ Tidak ada data untuk kombinasi filter yang dipilih. Coba ubah filter di sidebar.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — EXECUTIVE SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
if page == "Executive Summary":
    page_header("Executive Summary", "High-level business performance overview")

    total_rev    = dff["revenue"].sum()
    total_orders = dff["orderID"].nunique()
    total_cust   = dff["customerID"].nunique()
    avg_ov       = dff.groupby("orderID")["revenue"].sum().mean()
    total_qty    = dff["quantity"].sum()
    avg_freight  = dff.drop_duplicates("orderID")["freight"].mean()

    k1,k2,k3,k4,k5,k6 = st.columns(6)
    kpi_card("Total Revenue",    f"${total_rev:,.0f}",    k1)
    kpi_card("Total Orders",     f"{total_orders:,}",     k2)
    kpi_card("Active Customers", f"{total_cust:,}",       k3)
    kpi_card("Avg Order Value",  f"${avg_ov:,.0f}",       k4)
    kpi_card("Units Sold",       f"{total_qty:,}",        k5)
    kpi_card("Avg Freight Cost", f"${avg_freight:,.2f}",  k6)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])
    with col1:
        monthly = dff.groupby("month")["revenue"].sum().reset_index().sort_values("month")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly["month"], y=monthly["revenue"],
            mode="lines+markers",
            line=dict(color=C_BLUE, width=2.5),
            marker=dict(size=5, color=C_BLUE),
            fill="tozeroy", fillcolor="rgba(21,101,192,0.10)", name="Revenue"
        ))
        fig.update_layout(title="Monthly Revenue Trend", showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(style(fig, 320, False, rotated_labels=True), use_container_width=True)

    with col2:
        cat_rev = dff.groupby("categoryName")["revenue"].sum().reset_index().sort_values("revenue", ascending=False)
        fig = px.pie(cat_rev, names="categoryName", values="revenue",
                     title="Revenue by Category",
                     color_discrete_sequence=PALETTE_DIV, hole=0.42)
        fig.update_traces(
            textposition="auto", textinfo="percent+label",
            textfont=dict(size=10, color=C_TEXT), insidetextorientation="radial"
        )
        st.plotly_chart(style(fig, 320), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        country_rev = dff.groupby("customer_country")["revenue"].sum().reset_index().sort_values("revenue", ascending=True).tail(10)
        fig = px.bar(country_rev, x="revenue", y="customer_country", orientation="h",
                     title="Top 10 Countries by Revenue")
        fig.update_traces(marker_color=C_BLUE)
        fig.update_xaxes(tickprefix="$")
        st.plotly_chart(style(fig, 360, False), use_container_width=True)

    with col2:
        monthly_orders = dff.groupby("month")["orderID"].nunique().reset_index().sort_values("month")
        monthly_orders.columns = ["month", "order_count"]
        fig = px.bar(monthly_orders, x="month", y="order_count", title="Monthly Order Volume")
        fig.update_traces(marker_color=C_BLUE_MID)
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(style(fig, 360, False, rotated_labels=True), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — PRODUCT ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Product Analysis":
    page_header("Product & Category Analysis",
                "Identify best-performing products, high-discount items, and discontinued risk")

    k1,k2,k3,k4 = st.columns(4)
    kpi_card("Total Products",  f"{dff['productName'].nunique():,}",               k1)
    kpi_card("Categories",      f"{dff['categoryName'].nunique():,}",              k2)
    kpi_card("Avg Discount",    f"{dff['discount'].mean()*100:.1f}%",              k3)
    kpi_card("Active Products", f"{dff[dff['discontinued']==0]['productName'].nunique():,}", k4)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])
    with col1:
        prod_rev = dff.groupby("productName")["revenue"].sum().reset_index().sort_values("revenue", ascending=True).tail(10)
        fig = px.bar(prod_rev, x="revenue", y="productName", orientation="h",
                     title="Top 10 Products by Revenue")
        fig.update_traces(marker_color=C_BLUE)
        fig.update_xaxes(tickprefix="$")
        st.plotly_chart(style(fig, 400, False), use_container_width=True)

    with col2:
        cat_qty = dff.groupby("categoryName")["quantity"].sum().reset_index().sort_values("quantity", ascending=False)
        fig = px.bar(cat_qty, x="categoryName", y="quantity",
                     title="Units Sold by Category",
                     color="categoryName", color_discrete_sequence=PALETTE_DIV)
        fig.update_layout(showlegend=False, xaxis_tickangle=-30)
        st.plotly_chart(style(fig, 400, False, rotated_labels=True), use_container_width=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        prod_an = dff.groupby(["productName","categoryName"]).agg(
            revenue=("revenue","sum"), avg_discount=("discount","mean"), qty=("quantity","sum")
        ).reset_index()
        fig = px.scatter(prod_an, x="avg_discount", y="revenue",
                         hover_name="productName", size="qty", color="categoryName",
                         title="Discount Rate vs Revenue — Spot Overpriced Discounts",
                         labels={"avg_discount":"Avg Discount Rate","revenue":"Total Revenue"},
                         color_discrete_sequence=PALETTE_DIV, size_max=40)
        fig.update_traces(marker=dict(opacity=0.80, line=dict(width=1.2, color="rgba(55,65,81,0.4)")))
        fig.update_xaxes(tickformat=".0%")
        fig.update_yaxes(tickprefix="$")
        st.plotly_chart(style(fig, 380), use_container_width=True)

    with col2:
        disc = dff.groupby("discontinued")["revenue"].sum().reset_index()
        disc["status"] = disc["discontinued"].map({0: "Active", 1: "Discontinued"})
        fig = px.pie(disc, names="status", values="revenue",
                     title="Active vs Discontinued Revenue",
                     color_discrete_sequence=[C_BLUE, C_RED], hole=0.45)
        fig.update_traces(
            textposition="auto", textinfo="percent+label",
            textfont=dict(size=11, color=C_TEXT), insidetextorientation="radial"
        )
        st.plotly_chart(style(fig, 380), use_container_width=True)

    cat_monthly = dff.groupby(["month","categoryName"])["revenue"].sum().reset_index().sort_values("month")
    fig = px.line(cat_monthly, x="month", y="revenue", color="categoryName",
                  title="Monthly Revenue Trend by Category",
                  color_discrete_sequence=PALETTE_DIV,
                  labels={"revenue":"Revenue","month":"Month"})
    fig.update_layout(xaxis_tickangle=-45)
    fig.update_yaxes(tickprefix="$")
    st.plotly_chart(style(fig, 300, True, rotated_labels=True), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — CUSTOMER ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Customer Analysis":
    page_header("Customer Analysis",
                "Identify most valuable customers and high-potential markets")

    k1,k2,k3 = st.columns(3)
    kpi_card("Total Customers",     f"{dff['customerID'].nunique():,}",                                  k1)
    kpi_card("Countries Served",    f"{dff['customer_country'].nunique():,}",                            k2)
    kpi_card("Avg Orders/Customer", f"{dff.groupby('customerID')['orderID'].nunique().mean():.1f}", k3)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])
    with col1:
        top_cust = (dff.groupby(["companyName","customer_country"])["revenue"]
                    .sum().reset_index()
                    .sort_values("revenue", ascending=True).tail(10))
        fig = px.bar(top_cust, x="revenue", y="companyName", orientation="h",
                     title="Top 10 Customers by Revenue",
                     color="customer_country", color_discrete_sequence=PALETTE_DIV)
        fig.update_xaxes(tickprefix="$")
        st.plotly_chart(style(fig, 400), use_container_width=True)

    with col2:
        cr = (dff.groupby("customer_country")
              .agg(total_revenue=("revenue","sum"), total_orders=("orderID","nunique"))
              .reset_index().sort_values("total_revenue", ascending=False).head(8))
        fig = px.bar(cr, x="customer_country", y="total_revenue",
                     title="Revenue by Country (Top 8)",
                     color="total_orders",
                     color_continuous_scale=[[0, C_BLUE_SOFT],[0.5, C_BLUE],[1, C_BLUE_DARK]])
        fig.update_yaxes(tickprefix="$")
        fig.update_layout(xaxis_tickangle=-30, coloraxis_colorbar=colorbar_cfg("Orders"))
        st.plotly_chart(style(fig, 400, True, rotated_labels=True), use_container_width=True)

    col1, col2 = st.columns([3, 2])
    with col1:
        geo = dff.groupby("customer_country")["revenue"].sum().reset_index()
        fig = px.choropleth(geo, locations="customer_country", locationmode="country names",
                            color="revenue", title="Revenue Distribution by Country (Geographic)",
                            color_continuous_scale=[[0,"#90CAF9"],[0.5,C_BLUE_MID],[1,C_BLUE_DARK]])
        fig.update_layout(
            geo=dict(showframe=False, showcoastlines=True, coastlinecolor="#D1D5DB", bgcolor="white"),
            coloraxis_colorbar=colorbar_cfg("Revenue")
        )
        fig.update_coloraxes(colorbar_tickprefix="$")
        st.plotly_chart(style(fig, 360), use_container_width=True)

    with col2:
        cust_freq = dff.groupby("customerID")["orderID"].nunique().reset_index()
        cust_freq.columns = ["customerID","order_count"]
        bins  = pd.cut(cust_freq["order_count"], bins=[0,3,7,12,20,50], labels=["1-3","4-7","8-12","13-20","20+"])
        fdist = bins.value_counts().sort_index().reset_index()
        fdist.columns = ["Range","Count"]
        n = len(fdist)
        bar_colors = [C_BLUE_DARK, C_BLUE, C_BLUE_MID, C_BLUE_LIGHT, C_BLUE_SOFT][:n]
        fig = px.bar(fdist, x="Range", y="Count", title="Customer Order Frequency Segmentation")
        fig.update_traces(marker_color=bar_colors)
        st.plotly_chart(style(fig, 360, False), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — OPERATIONS PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Operations Performance":
    page_header("Operations Performance",
                "Evaluate employee contribution, shipper reliability, and delivery efficiency")

    ship_df = orders.merge(shippers, on="shipperID")
    ship_df = ship_df[ship_df["shippedDate"].notna()].copy()
    ship_df["delay_days"] = (ship_df["shippedDate"] - ship_df["requiredDate"]).dt.days
    ship_df["status"]     = ship_df["delay_days"].apply(lambda x: "On Time" if x <= 0 else "Late")
    on_time_pct = (ship_df["delay_days"] <= 0).mean() * 100
    late_count  = (ship_df["delay_days"] > 0).sum()

    k1,k2,k3,k4 = st.columns(4)
    kpi_card("Total Employees",  f"{dff['employeeID'].nunique():,}", k1)
    kpi_card("Shippers",         "3",                                k2)
    kpi_card("On-Time Delivery", f"{on_time_pct:.1f}%",             k3)
    kpi_card("Late Deliveries",  f"{late_count:,}",                 k4)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        emp = dff.groupby("employeeName").agg(
            revenue=("revenue","sum"), orders=("orderID","nunique")
        ).reset_index().sort_values("revenue", ascending=False)
        fig = px.bar(emp, x="employeeName", y="revenue",
                     title="Revenue Generated by Employee",
                     color="revenue",
                     color_continuous_scale=[[0, C_BLUE_SOFT],[0.5, C_BLUE],[1, C_BLUE_DARK]])
        fig.update_yaxes(tickprefix="$")
        fig.update_layout(xaxis_tickangle=-15, coloraxis_showscale=False)
        st.plotly_chart(style(fig, 340, False, rotated_labels=True), use_container_width=True)

    with col2:
        fig = px.bar(emp.sort_values("orders", ascending=False),
                     x="employeeName", y="orders",
                     title="Orders Handled by Employee",
                     color="orders",
                     color_continuous_scale=[[0, C_BLUE_SOFT],[0.5, C_BLUE_MID],[1, C_BLUE_DARK]])
        fig.update_layout(xaxis_tickangle=-15, coloraxis_showscale=False)
        st.plotly_chart(style(fig, 340, False, rotated_labels=True), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        ss = ship_df.groupby(["companyName","status"]).size().reset_index(name="count")
        fig = px.bar(ss, x="companyName", y="count", color="status", barmode="group",
                     title="On-Time vs Late Deliveries by Shipper",
                     color_discrete_map={"On Time": C_BLUE, "Late": C_RED})
        st.plotly_chart(style(fig, 320), use_container_width=True)

    with col2:
        ad = ship_df.groupby("companyName")["delay_days"].mean().reset_index()
        ad.columns = ["Shipper", "Avg Delay (days)"]
        bar_colors_delay = [C_GREEN if x <= 0 else C_RED for x in ad["Avg Delay (days)"]]
        fig = go.Figure(go.Bar(
            x=ad["Shipper"], y=ad["Avg Delay (days)"],
            marker_color=bar_colors_delay,
            text=ad["Avg Delay (days)"].round(1),
            textposition="outside",
            textfont=dict(color=C_TEXT, size=12)
        ))
        fig.add_hline(y=0, line_dash="dash", line_color="#9CA3AF", opacity=0.6)
        fig.update_layout(
            title="Average Delivery Delay by Shipper (days)",
            yaxis=dict(range=[
                min(ad["Avg Delay (days)"].min() * 1.3, -1),
                ad["Avg Delay (days)"].max() * 1.4
            ])
        )
        st.plotly_chart(style(fig, 320, False), use_container_width=True)

    emp_time = dff.groupby(["month","employeeName"])["revenue"].sum().reset_index().sort_values("month")
    fig = px.line(emp_time, x="month", y="revenue", color="employeeName",
                  title="Monthly Revenue per Employee — Performance Trend",
                  color_discrete_sequence=PALETTE_DIV)
    fig.update_layout(xaxis_tickangle=-45)
    fig.update_yaxes(tickprefix="$")
    st.plotly_chart(style(fig, 300, True, rotated_labels=True), use_container_width=True)

st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#9CA3AF;font-size:11px;padding:6px 0;'>"
    "Northwind Traders Analytics Dashboard | Streamlit + Plotly | Data: 2013-2015"
    "</div>",
    unsafe_allow_html=True
)
