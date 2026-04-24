
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ============================================
# CONFIG
# ============================================
st.set_page_config(
    page_title="Northwind Traders Dashboard",
    page_icon="📦",
    layout="wide"
)

# ============================================
# LOAD DATA (dari CSV langsung)
# ============================================
orders       = pd.read_csv("orders-5.csv")
order_details= pd.read_csv("order_details.csv")
customers    = pd.read_csv("customers-2.csv")
products     = pd.read_csv("products-6.csv")
categories   = pd.read_csv("categories.csv")
employees    = pd.read_csv("employees-3.csv")
shippers     = pd.read_csv("shippers-7.csv")

# Fix kolom tanggal
orders['orderDate']    = pd.to_datetime(orders['orderDate'])
orders['shippedDate']  = pd.to_datetime(orders['shippedDate'])
orders['requiredDate'] = pd.to_datetime(orders['requiredDate'])

# Hitung revenue
order_details['revenue'] = (
    order_details['quantity'] *
    order_details['unitPrice'] *
    (1 - order_details['discount'])
)

# Master join
df = order_details \
    .merge(orders, on='orderID') \
    .merge(customers, on='customerID') \
    .merge(products, on='productID') \
    .merge(categories, on='categoryID') \
    .merge(employees, on='employeeID')

# ============================================
# SIDEBAR FILTER
# ============================================
st.sidebar.image("https://img.icons8.com/color/96/shop.png", width=80)
st.sidebar.title("Northwind Traders")
st.sidebar.markdown("---")

countries = ["All"] + sorted(df['country'].dropna().unique().tolist())
selected_country = st.sidebar.selectbox("Filter by Country", countries)

if selected_country != "All":
    df = df[df['country'] == selected_country]

# ============================================
# PAGE 1: EXECUTIVE SUMMARY
# ============================================
st.title("📊 Executive Summary")
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Revenue",    f"${df['revenue'].sum():,.0f}")
col2.metric("📦 Total Orders",     f"{df['orderID'].nunique():,}")
col3.metric("👥 Total Customers",  f"{df['customerID'].nunique():,}")
col4.metric("🛒 Avg Order Value",  f"${df.groupby('orderID')['revenue'].sum().mean():,.0f}")

st.markdown("---")

# Revenue Trend
monthly = df.groupby(df['orderDate'].dt.to_period('M'))['revenue'].sum().reset_index()
monthly['orderDate'] = monthly['orderDate'].astype(str)
fig1 = px.line(monthly, x='orderDate', y='revenue',
               title='📈 Monthly Revenue Trend',
               color_discrete_sequence=['#1A73E8'])
fig1.update_layout(plot_bgcolor='white', paper_bgcolor='white')
st.plotly_chart(fig1, use_container_width=True)

# Revenue by Country
country_rev = df.groupby('country')['revenue'].sum().reset_index().sort_values('revenue', ascending=False).head(10)
fig2 = px.bar(country_rev, x='revenue', y='country', orientation='h',
              title='🌍 Top 10 Countries by Revenue',
              color='revenue', color_continuous_scale='Blues')
fig2.update_layout(plot_bgcolor='white', paper_bgcolor='white')
st.plotly_chart(fig2, use_container_width=True)

# ============================================
# PAGE 2: PRODUCT ANALYSIS
# ============================================
st.markdown("---")
st.title("🛍️ Product & Category Analysis")
st.markdown("---")

col1, col2 = st.columns(2)

# Pie chart by category
with col1:
    cat_rev = df.groupby('categoryName')['revenue'].sum().reset_index()
    fig3 = px.pie(cat_rev, names='categoryName', values='revenue',
                  title='Revenue by Category',
                  color_discrete_sequence=px.colors.sequential.Blues_r)
    st.plotly_chart(fig3, use_container_width=True)

# Top products
with col2:
    prod_rev = df.groupby('productName')['revenue'].sum().reset_index().sort_values('revenue', ascending=False).head(10)
    fig4 = px.bar(prod_rev, x='revenue', y='productName', orientation='h',
                  title='Top 10 Products by Revenue',
                  color='revenue', color_continuous_scale='Blues')
    fig4.update_layout(plot_bgcolor='white', paper_bgcolor='white')
    st.plotly_chart(fig4, use_container_width=True)

# Scatter: Discount vs Revenue
prod_analysis = df.groupby('productName').agg(
    revenue=('revenue','sum'),
    avg_discount=('discount','mean')
).reset_index()
fig5 = px.scatter(prod_analysis, x='avg_discount', y='revenue',
                  hover_name='productName', size='revenue',
                  title='💡 Discount vs Revenue per Product',
                  color='revenue', color_continuous_scale='Blues',
                  labels={'avg_discount': 'Avg Discount', 'revenue': 'Total Revenue'})
fig5.update_layout(plot_bgcolor='white', paper_bgcolor='white')
st.plotly_chart(fig5, use_container_width=True)

# ============================================
# PAGE 3: CUSTOMER ANALYSIS
# ============================================
st.markdown("---")
st.title("👥 Customer Analysis")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    top_customers = df.groupby('companyName')['revenue'].sum().reset_index().sort_values('revenue', ascending=False).head(10)
    fig6 = px.bar(top_customers, x='revenue', y='companyName', orientation='h',
                  title='Top 10 Customers by Revenue',
                  color='revenue', color_continuous_scale='Blues')
    fig6.update_layout(plot_bgcolor='white', paper_bgcolor='white')
    st.plotly_chart(fig6, use_container_width=True)

with col2:
    country_orders = df.groupby('country')['orderID'].nunique().reset_index()
    country_orders.columns = ['country', 'total_orders']
    fig7 = px.choropleth(country_orders, locations='country',
                         locationmode='country names',
                         color='total_orders',
                         title='🗺️ Orders by Country',
                         color_continuous_scale='Blues')
    st.plotly_chart(fig7, use_container_width=True)

# ============================================
# PAGE 4: OPERATIONS PERFORMANCE
# ============================================
st.markdown("---")
st.title("⚙️ Operations Performance")
st.markdown("---")

col1, col2 = st.columns(2)

# Employee performance
with col1:
    emp_rev = df.groupby('employeeName')['revenue'].sum().reset_index().sort_values('revenue', ascending=False)
    fig8 = px.bar(emp_rev, x='employeeName', y='revenue',
                  title='👨‍💼 Revenue by Employee',
                  color='revenue', color_continuous_scale='Blues')
    fig8.update_layout(plot_bgcolor='white', paper_bgcolor='white')
    st.plotly_chart(fig8, use_container_width=True)

# Shipper delay
with col2:
    ship_df = orders.merge(shippers, on='shipperID')
    ship_df = ship_df[ship_df['shippedDate'].notna()]
    ship_df['delay_days'] = (ship_df['shippedDate'] - ship_df['requiredDate']).dt.days
    ship_df['status'] = ship_df['delay_days'].apply(lambda x: 'Late 🔴' if x > 0 else 'On Time 🟢')
    ship_summary = ship_df.groupby(['companyName','status']).size().reset_index(name='count')
    fig9 = px.bar(ship_summary, x='companyName', y='count', color='status',
                  title='🚚 Shipper: On Time vs Late',
                  color_discrete_map={'On Time 🟢': '#1A73E8', 'Late 🔴': '#EA4335'},
                  barmode='group')
    fig9.update_layout(plot_bgcolor='white', paper_bgcolor='white')
    st.plotly_chart(fig9, use_container_width=True)

st.markdown("---")
st.caption("📦 Northwind Traders Analytics Dashboard | Built with Streamlit & Plotly")
