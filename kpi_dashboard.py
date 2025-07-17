import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date
import plotly.graph_objects as go
import plotly.express as px
from typing import Any

# Configure page
st.set_page_config(
    page_title="SHAED Finance Dashboard - KPIs",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for SHAED branding
st.markdown("""
<style>
    /* Main background and colors */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #00D084 0%, #00B574 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header h2 {
        margin: 0.5rem 0 0 0;
        font-size: 1.5rem;
        font-weight: 400;
        opacity: 0.9;
    }
    
    /* Section headers */
    .section-header {
        background-color: #00D084;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1.5rem 0 1rem 0;
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    /* Metric containers */
    .metric-container {
        background-color: white;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #00D084;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin: 0.5rem 0;
        height: 100%;
    }
    
    .metric-container h4 {
        color: #00D084;
        margin: 0;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    .metric-container h2 {
        margin: 0.5rem 0 0 0;
        font-size: 2rem;
        font-weight: 700;
    }
    
    .metric-container p {
        margin: 0.25rem 0 0 0;
        font-size: 0.85rem;
        color: #666;
    }
    
    /* KPI cards */
    .kpi-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin: 0.5rem 0;
        height: 100%;
        text-align: center;
        transition: transform 0.2s;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    .kpi-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .kpi-label {
        color: #666;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .kpi-change {
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    .positive {
        color: #00D084;
    }
    
    .negative {
        color: #dc3545;
    }
    
    /* Table styling */
    .stDataFrame {
        font-size: 0.9rem;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 8px;
        border-left: 4px solid #00D084;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'model_data' not in st.session_state:
    st.session_state.model_data = {}

# Load data
data_file = 'financial_model_data.json'
if os.path.exists(data_file):
    with open(data_file, 'r') as f:
        st.session_state.model_data = json.load(f)

# Header
st.markdown("""
<div class="main-header">
    <h1>📊 KPI Dashboard</h1>
    <h2>Key Performance Indicators & Metrics</h2>
</div>
""", unsafe_allow_html=True)

# Unified Navigation Bar
st.markdown('<div class="section-header">🧭 Dashboard Navigation</div>', unsafe_allow_html=True)

nav_col1, nav_col2, nav_col3, nav_col4, nav_col5, nav_col6, nav_col7, nav_col8 = st.columns(8)

with nav_col1:
    if st.button("🏠 Home", key="nav_home", use_container_width=True):
        st.info("Run: streamlit run home.py")

with nav_col2:
    if st.button("📊 KPIs", key="nav_kpi", use_container_width=True):
        st.info("Run: streamlit run kpi_dashboard.py")

with nav_col3:
    if st.button("📈 Income", key="nav_income", use_container_width=True):
        st.info("Run: streamlit run financial_model.py")

with nav_col4:
    if st.button("💰 Liquidity", key="nav_liquidity", use_container_width=True):
        st.info("Run: streamlit run liquidity_model.py")

with nav_col5:
    if st.button("💵 Revenue", key="nav_revenue", use_container_width=True):
        st.info("Run: streamlit run revenue_assumptions.py")

with nav_col6:
    if st.button("👥 Headcount", key="nav_headcount", use_container_width=True):
        st.info("Run: streamlit run payroll_model.py")

with nav_col7:
    if st.button("📊 Gross Profit", key="nav_gross", use_container_width=True):
        st.info("Run: streamlit run gross_profit_model.py")

with nav_col8:
    if st.button("☁️ Hosting", key="nav_hosting", use_container_width=True):
        st.info("Run: streamlit run hosting_costs_model.py")

# Add visual separator after navigation
st.markdown("---")

# Date range selector and filters
col1, col2, col3, col4 = st.columns([2, 2, 3, 3])
with col1:
    selected_year = st.selectbox(
        "Select Year",
        ["2025", "2026", "2027", "2028", "2029", "2030", "All Years"],
        index=6
    )

with col2:
    # Month selector - only show if specific year is selected
    if selected_year != "All Years":
        month_options = ["All Months"] + ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        selected_month = st.selectbox(
            "Select Month",
            month_options,
            index=0
        )
    else:
        selected_month = "All Months"

# Define all stakeholders from revenue assumptions (exact match)
all_stakeholders = [
    "Equipment Manufacturer", "Dealership", "Corporate", "Charging as a Service",
    "Charging Hardware", "Depot", "End User", "Infrastructure Partner",
    "Finance Partner", "Fleet Management Company", "Grants", "Logistics",
    "Non Customer", "OEM", "Service", "Technology Partner",
    "Upfitter/Distributor", "Utility/Energy Company", "Insurance Company", "Consultant"
]

with col3:
    # Customer type filter dropdown
    customer_filter_options = ["All Customer Types"] + all_stakeholders
    selected_customer_filter = st.selectbox(
        "Filter Customer Type",
        options=customer_filter_options,
        index=0,
        help="Select a specific customer type or view all types"
    )
    
    # Set selected stakeholders based on dropdown selection
    if selected_customer_filter == "All Customer Types":
        selected_stakeholders = all_stakeholders
    else:
        selected_stakeholders = [selected_customer_filter]

# Generate months list based on selection
if selected_year == "All Years":
    months = []
    for year in range(2025, 2031):
        for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]:
            months.append(f"{month} {year}")
else:
    year = selected_year
    if selected_month == "All Months":
        months = [f"{month} {year}" for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]]
    else:
        # Single month selected
        months = [f"{selected_month} {year}"]

# Display current filter selection
with col4:
    if selected_year == "All Years":
        st.info(f"📅 **Period**: All Years (2025-2030)")
    elif selected_month == "All Months":
        st.info(f"📅 **Period**: All months in {selected_year}")
    else:
        st.info(f"📅 **Period**: {selected_month} {selected_year}")

# Helper functions
def calculate_total_revenue(month):
    """Calculate total revenue for a given month"""
    revenue_streams = ["Subscription", "Transactional", "Implementation", "Maintenance"]
    total = 0
    revenue_data = st.session_state.model_data.get("revenue", {})
    for stream in revenue_streams:
        total += revenue_data.get(stream, {}).get(month, 0)
    return total

def calculate_arr(month):
    """Calculate Annual Recurring Revenue based on subscription revenue"""
    subscription_revenue = st.session_state.model_data.get("revenue", {}).get("Subscription", {}).get(month, 0)
    return subscription_revenue * 12

def calculate_gross_margin(month):
    """Calculate gross margin percentage"""
    revenue = calculate_total_revenue(month)
    cogs = calculate_total_cogs(month)
    if revenue > 0:
        return ((revenue - cogs) / revenue) * 100
    return 0

def calculate_total_cogs(month):
    """Calculate total cost of goods sold"""
    cogs_streams = ["Subscription", "Transactional", "Implementation", "Maintenance"]
    total_direct_costs = 0
    total_hosting_costs = 0
    
    # Get direct costs
    for stream in cogs_streams:
        total_direct_costs += st.session_state.model_data.get("direct_costs", {}).get(stream, {}).get(month, 0)
    
    # Get hosting costs (if available)
    hosting_data = st.session_state.model_data.get("hosting_monthly_expensed", {})
    if hosting_data:
        # Sum all hosting cost categories for the month
        for category in hosting_data:
            total_hosting_costs += hosting_data.get(category, {}).get(month, 0)
    
    return total_direct_costs + total_hosting_costs

def calculate_burn_rate(month):
    """Calculate monthly burn rate (negative cash flow)"""
    # Get cash flow data from liquidity model
    liquidity_data = st.session_state.model_data.get("liquidity_data", {})
    
    # Cash inflows
    revenue = liquidity_data.get("revenue", {}).get(month, 0)
    other_cash_receipts = liquidity_data.get("other_cash_receipts", {}).get(month, 0)
    investment = liquidity_data.get("investment", {}).get(month, 0)
    
    # Cash outflows - get all expense categories
    expense_categories = liquidity_data.get("category_order", [])
    expenses = liquidity_data.get("expenses", {})
    total_expenses = sum(expenses.get(cat, {}).get(month, 0) for cat in expense_categories)
    
    # Net cash flow (positive means burning cash)
    net_flow = total_expenses - (revenue + other_cash_receipts + investment)
    
    return net_flow

def calculate_cash_balance(month):
    """Calculate cumulative cash balance up to a month"""
    liquidity_data = st.session_state.model_data.get("liquidity_data", {})
    
    # Get initial cash balance
    initial_cash = liquidity_data.get("starting_balance", 0)
    
    # Calculate cumulative cash flow
    cumulative_flow = initial_cash
    
    # Get all months up to the specified month
    all_months = []
    for year in range(2025, 2031):
        for m in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]:
            all_months.append(f"{m} {year}")
    
    for m in all_months:
        # Cash inflows
        revenue = liquidity_data.get("revenue", {}).get(m, 0)
        other_cash_receipts = liquidity_data.get("other_cash_receipts", {}).get(m, 0)
        investment = liquidity_data.get("investment", {}).get(m, 0)
        
        # Cash outflows
        expense_categories = liquidity_data.get("category_order", [])
        expenses = liquidity_data.get("expenses", {})
        total_expenses = sum(expenses.get(cat, {}).get(m, 0) for cat in expense_categories)
        
        cumulative_flow += revenue + other_cash_receipts + investment - total_expenses
        
        if m == month:
            break
    
    return cumulative_flow

def calculate_customer_metrics(month):
    """Calculate customer-related metrics for selected stakeholders"""
    # Get subscription running totals (active customers after churn)
    subscription_totals = st.session_state.model_data.get("subscription_running_totals", {})
    
    total_customers = 0
    for stakeholder in selected_stakeholders:  # Use selected stakeholders instead of all
        total_customers += subscription_totals.get(stakeholder, {}).get(month, 0)
    
    # Calculate average revenue per customer
    subscription_revenue = st.session_state.model_data.get("revenue", {}).get("Subscription", {}).get(month, 0)
    arpc = subscription_revenue / total_customers if total_customers > 0 else 0
    
    return total_customers, arpc

def calculate_new_customers_in_period(months_list):
    """Calculate total new customers added during a period"""
    new_customers_data = st.session_state.model_data.get("subscription_new_customers", {})
    
    total_new = 0
    for stakeholder in selected_stakeholders:
        for month in months_list:
            total_new += new_customers_data.get(stakeholder, {}).get(month, 0)
    
    return total_new

def calculate_runway_month():
    """Calculate the month when cash runs out based on liquidity data - consistent across all filters"""
    # Always check all months to find when cash goes negative
    all_months = []
    for year in range(2025, 2031):
        for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]:
            all_months.append(f"{month} {year}")
    
    # Find the first month where cash balance goes negative
    for month in all_months:
        balance = calculate_cash_balance(month)
        if balance <= 0:
            return month
    
    # If we never go negative, check if we're profitable (positive cash flow in recent months)
    # Check the last few months with data to see if we're generating positive cash flow
    recent_months = all_months[-12:]  # Last 12 months
    positive_flow_count = 0
    
    for month in reversed(recent_months):
        burn_rate = calculate_burn_rate(month)
        if burn_rate <= 0:  # Negative burn rate means generating cash
            positive_flow_count += 1
        
        # If we have 3+ months of positive cash flow, consider it profitable
        if positive_flow_count >= 3:
            return "Profitable"
    
    # If we never go negative and don't have consistent positive flow, return far future
    return "Beyond 2030"

def calculate_headcount_metrics():
    """Calculate total headcount from payroll data using date-based activation"""
    # Check if payroll_data exists
    if "payroll_data" not in st.session_state.model_data:
        return 0, 0
    
    payroll_data = st.session_state.model_data.get("payroll_data", {})
    
    # Get current month for active check
    current_month = datetime.now().strftime("%b %Y")
    
    # Count active employees using date-based logic
    employees = payroll_data.get("employees", {})
    total_employees = 0
    
    for emp_data in employees.values():
        if is_employee_active_for_month(emp_data, current_month):
            total_employees += 1
    
    # Count contractors using date-based logic
    contractors = payroll_data.get("contractors", {})
    total_contractors = 0
    
    for contractor_data in contractors.values():
        if is_contractor_active_for_month(contractor_data, current_month):
            total_contractors += contractor_data.get("resources", 0)
    
    return total_employees, int(total_contractors)

def is_employee_active_for_month(emp_data, month_str):
    """Check if employee is active for a specific month"""
    try:
        # Convert month string (e.g., "Jan 2025") to date (first day of month)
        month_date = datetime.strptime(month_str, "%b %Y")
        
        # Check hire date
        hire_date_str = emp_data.get("hire_date")
        if hire_date_str:
            hire_date = datetime.strptime(hire_date_str, "%Y-%m-%d")
            # Employee must be hired by the first day of the month
            if month_date < hire_date:
                return False
        
        # Check termination date
        termination_date_str = emp_data.get("termination_date")
        if termination_date_str:
            termination_date = datetime.strptime(termination_date_str, "%Y-%m-%d")
            # Employee is active until the month AFTER their termination date
            # Calculate the first day of the month after termination
            if termination_date.month == 12:
                next_month_start = datetime(termination_date.year + 1, 1, 1)
            else:
                next_month_start = datetime(termination_date.year, termination_date.month + 1, 1)
            
            # Employee is inactive starting from the month after termination
            if month_date >= next_month_start:
                return False
        
        return True
    except (ValueError, TypeError):
        # If there's any error parsing dates, fall back to active field
        return emp_data.get("active", True)

def is_contractor_active_for_month(contractor_data, month_str):
    """Check if contractor is active for a specific month"""
    try:
        # Convert month string (e.g., "Jan 2025") to date (first day of month)
        month_date = datetime.strptime(month_str, "%b %Y")
        
        # Check start date
        start_date_str = contractor_data.get("start_date")
        if start_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            if month_date < start_date:
                return False
        
        # Check end date
        end_date_str = contractor_data.get("end_date")
        if end_date_str:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            # Contractor is active until the month AFTER their end date
            # Calculate the first day of the month after end date
            if end_date.month == 12:
                next_month_start = datetime(end_date.year + 1, 1, 1)
            else:
                next_month_start = datetime(end_date.year, end_date.month + 1, 1)
            
            # Contractor is inactive starting from the month after end date
            if month_date >= next_month_start:
                return False
        
        return True
    except (ValueError, TypeError):
        # If there's any error parsing dates, assume active
        return True

# EXECUTIVE SUMMARY
st.markdown('<div class="section-header">🎯 Executive Summary</div>', unsafe_allow_html=True)

# Calculate key metrics for the selected period
if selected_year == "All Years":
    # Calculate totals for all years
    ytd_months = months  # Use all months for "All Years"
    total_revenue = sum(calculate_total_revenue(month) for month in ytd_months)
    avg_gross_margin = sum(calculate_gross_margin(month) for month in months) / len(months) if months else 0
    latest_arr = calculate_arr(months[-1]) if months else 0
    latest_cash_balance = calculate_cash_balance(months[-1]) if months else 0
    avg_burn_rate = sum(calculate_burn_rate(month) for month in months) / len(months) if months else 0
    total_customers, avg_arpc = calculate_customer_metrics(months[-1]) if months else (0, 0)
else:
    # Calculate for specific year
    if selected_month == "All Months":
        ytd_months = months  # Use all months for full year
    else:
        # Create YTD months list (January through selected month)
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        selected_month_index = month_names.index(selected_month)
        ytd_months = [f"{month_names[i]} {selected_year}" for i in range(selected_month_index + 1)]
    
    total_revenue = sum(calculate_total_revenue(month) for month in ytd_months)
    avg_gross_margin = sum(calculate_gross_margin(month) for month in months) / len(months) if months else 0
    latest_arr = calculate_arr(months[-1]) if months else 0
    latest_cash_balance = calculate_cash_balance(months[-1]) if months else 0
    avg_burn_rate = sum(calculate_burn_rate(month) for month in months) / len(months) if months else 0
    total_customers, avg_arpc = calculate_customer_metrics(months[-1]) if months else (0, 0)

# Display executive metrics
exec_col1, exec_col2, exec_col3, exec_col4 = st.columns(4)

with exec_col1:
    if selected_year == "All Years":
        period_label = "All Years"
    elif selected_month == "All Months":
        period_label = f"{selected_year}"
    else:
        period_label = f"YTD {selected_month} {selected_year}"
    
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Revenue</div>
        <div class="kpi-value" style="color: #00D084;">${total_revenue:,.0f}</div>
        <div class="kpi-change positive">Period: {period_label}</div>
    </div>
    """, unsafe_allow_html=True)

with exec_col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">ARR (Latest)</div>
        <div class="kpi-value" style="color: #00B574;">${latest_arr:,.0f}</div>
        <div class="kpi-change">Annual Recurring Revenue</div>
    </div>
    """, unsafe_allow_html=True)

with exec_col3:
    cash_color = "#00D084" if latest_cash_balance > 0 else "#dc3545"
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Cash Balance</div>
        <div class="kpi-value" style="color: {cash_color};">${latest_cash_balance:,.0f}</div>
        <div class="kpi-change">Latest Balance</div>
    </div>
    """, unsafe_allow_html=True)

with exec_col4:
    runway_month = calculate_runway_month()
    # Color based on how far out the runway month is
    if runway_month in ["Profitable", "Beyond 2030"]:
        runway_color = "#00D084"  # Green
    elif "2025" in runway_month:
        runway_color = "#dc3545"  # Red for 2025 (critical)
    elif "2026" in runway_month:
        runway_color = "#FFA500"  # Orange for 2026 (concerning)
    else:
        # 2027+ or other cases
        runway_color = "#00D084"  # Green for far out
    
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Cash Runway</div>
        <div class="kpi-value" style="color: {runway_color};">{runway_month}</div>
        <div class="kpi-change">Run Out Month</div>
    </div>
    """, unsafe_allow_html=True)

# REVENUE METRICS
st.markdown('<div class="section-header">💰 Revenue Metrics</div>', unsafe_allow_html=True)

rev_col1, rev_col2, rev_col3, rev_col4 = st.columns(4)

with rev_col1:
    subscription_total = sum(st.session_state.model_data.get("revenue", {}).get("Subscription", {}).get(month, 0) for month in ytd_months)
    if selected_year == "All Years":
        period_label = "All Years"
    elif selected_month == "All Months":
        period_label = f"{selected_year}"
    else:
        period_label = f"YTD {selected_month} {selected_year}"
    
    st.markdown(f"""
    <div class="metric-container">
        <h4>Subscription Revenue</h4>
        <h2>${subscription_total:,.0f}</h2>
        <p>Period: {period_label}</p>
    </div>
    """, unsafe_allow_html=True)

with rev_col2:
    transactional_total = sum(st.session_state.model_data.get("revenue", {}).get("Transactional", {}).get(month, 0) for month in ytd_months)
    st.markdown(f"""
    <div class="metric-container">
        <h4>Transactional Revenue</h4>
        <h2>${transactional_total:,.0f}</h2>
        <p>Period: {period_label}</p>
    </div>
    """, unsafe_allow_html=True)

with rev_col3:
    implementation_total = sum(st.session_state.model_data.get("revenue", {}).get("Implementation", {}).get(month, 0) for month in ytd_months)
    st.markdown(f"""
    <div class="metric-container">
        <h4>Implementation Revenue</h4>
        <h2>${implementation_total:,.0f}</h2>
        <p>Period: {period_label}</p>
    </div>
    """, unsafe_allow_html=True)

with rev_col4:
    maintenance_total = sum(st.session_state.model_data.get("revenue", {}).get("Maintenance", {}).get(month, 0) for month in ytd_months)
    st.markdown(f"""
    <div class="metric-container">
        <h4>Maintenance Revenue</h4>
        <h2>${maintenance_total:,.0f}</h2>
        <p>Period: {period_label}</p>
    </div>
    """, unsafe_allow_html=True)

# CUSTOMER METRICS
st.markdown('<div class="section-header">👥 Customer Metrics</div>', unsafe_allow_html=True)

# Show which customer type and period is selected
period_display = f"{selected_month} {selected_year}" if selected_month != "All Months" and selected_year != "All Years" else selected_year
if selected_customer_filter != "All Customer Types":
    st.info(f"📊 Showing metrics for: {selected_customer_filter} | Period: {period_display}")
else:
    st.info(f"📊 Showing metrics for: All customer types | Period: {period_display}")

cust_col1, cust_col2, cust_col3, cust_col4 = st.columns(4)

with cust_col1:
    st.markdown(f"""
    <div class="metric-container">
        <h4>Total Customers</h4>
        <h2>{int(total_customers)}</h2>
        <p>Active subscriptions</p>
    </div>
    """, unsafe_allow_html=True)

# Calculate customer acquisition metrics
new_customers_period = calculate_new_customers_in_period(months)

with cust_col2:
    st.markdown(f"""
    <div class="metric-container">
        <h4>New Customers</h4>
        <h2>{int(new_customers_period)}</h2>
        <p>Added in period</p>
    </div>
    """, unsafe_allow_html=True)

with cust_col3:
    # Get average subscription price for selected stakeholders only
    subscription_prices = []
    for stakeholder in selected_stakeholders:  # Use selected stakeholders
        prices = st.session_state.model_data.get("subscription_pricing", {}).get(stakeholder, {})
        for month in months:
            price = prices.get(month, 0)
            if price > 0:
                subscription_prices.append(price)
    
    avg_subscription_price = sum(subscription_prices) / len(subscription_prices) if subscription_prices else 0
    
    st.markdown(f"""
    <div class="metric-container">
        <h4>Avg Subscription Price</h4>
        <h2>${avg_subscription_price:,.0f}</h2>
        <p>Monthly subscription</p>
    </div>
    """, unsafe_allow_html=True)

with cust_col4:
    # Calculate simple average churn rate for selected stakeholders
    total_churn_rates = 0
    total_months = 0
    
    for stakeholder in selected_stakeholders:
        churns = st.session_state.model_data.get("subscription_churn_rates", {}).get(stakeholder, {})
        
        for month in months:
            churn_rate = churns.get(month, 0)
            total_churn_rates += churn_rate
            total_months += 1
    
    # Calculate simple average churn
    if total_months > 0:
        avg_churn = total_churn_rates / total_months
    else:
        avg_churn = 0.0
    
    # Format the display with color coding
    if avg_churn == 0:
        churn_color = "#666"  # Gray for no data
    elif avg_churn < 3:
        churn_color = "#00D084"  # Green
    elif avg_churn < 5:
        churn_color = "#FFA500"  # Orange
    else:
        churn_color = "#dc3545"  # Red
    
    st.markdown(f"""
    <div class="metric-container">
        <h4>Churn Rate</h4>
        <h2 style="color: {churn_color};">{avg_churn:.1f}%</h2>
        <p>Average monthly</p>
    </div>
    """, unsafe_allow_html=True)

# OPERATIONAL METRICS
st.markdown('<div class="section-header">⚙️ Operational Metrics</div>', unsafe_allow_html=True)

ops_col1, ops_col2, ops_col3, ops_col4, ops_col5 = st.columns(5)

with ops_col1:
    # Calculate average monthly burn
    burn_color = "#dc3545" if avg_burn_rate > 0 else "#00D084"
    st.markdown(f"""
    <div class="metric-container">
        <h4>Monthly Burn Rate</h4>
        <h2 style="color: {burn_color};">${abs(avg_burn_rate):,.0f}</h2>
        <p>Average net cash burn</p>
    </div>
    """, unsafe_allow_html=True)

with ops_col2:
    # Calculate average gross burn (total expenses without revenue offset)
    liquidity_data = st.session_state.model_data.get("liquidity_data", {})
    expense_categories = liquidity_data.get("category_order", [])
    expenses = liquidity_data.get("expenses", {})
    
    total_gross_burn = 0
    for month in months:
        monthly_expenses = sum(expenses.get(cat, {}).get(month, 0) for cat in expense_categories)
        total_gross_burn += monthly_expenses
    
    avg_gross_burn = total_gross_burn / len(months) if months else 0
    
    st.markdown(f"""
    <div class="metric-container">
        <h4>Avg Gross Burn</h4>
        <h2 style="color: #dc3545;">${abs(avg_gross_burn):,.0f}</h2>
        <p>Total expenses/month</p>
    </div>
    """, unsafe_allow_html=True)

with ops_col3:
    # Calculate total employees
    total_employees, total_contractors = calculate_headcount_metrics()
    total_headcount = total_employees + total_contractors
    
    st.markdown(f"""
    <div class="metric-container">
        <h4>Total Headcount</h4>
        <h2>{total_headcount}</h2>
        <p>{total_employees} FTE + {total_contractors} Contractors</p>
    </div>
    """, unsafe_allow_html=True)

with ops_col4:
    # Calculate revenue per employee
    revenue_per_employee = total_revenue / total_headcount if total_headcount > 0 else 0
    
    st.markdown(f"""
    <div class="metric-container">
        <h4>Revenue per Employee</h4>
        <h2>${revenue_per_employee:,.0f}</h2>
        <p>Productivity metric</p>
    </div>
    """, unsafe_allow_html=True)

with ops_col5:
    # Calculate payroll as % of revenue
    payroll_total = sum(st.session_state.model_data.get("liquidity_data", {}).get("expenses", {}).get("Payroll", {}).get(month, 0) for month in months)
    payroll_percentage = (payroll_total / total_revenue * 100) if total_revenue > 0 else 0
    
    st.markdown(f"""
    <div class="metric-container">
        <h4>Payroll % of Revenue</h4>
        <h2>{payroll_percentage:.1f}%</h2>
        <p>Efficiency metric</p>
    </div>
    """, unsafe_allow_html=True)

# CUSTOMER BREAKDOWN
if selected_customer_filter == "All Customer Types":
    # Show breakdown by type when viewing all
    st.markdown('<div class="section-header">📊 Customer Breakdown by Type</div>', unsafe_allow_html=True)
    
    # Create breakdown data
    customer_breakdown_data = []
    for stakeholder in all_stakeholders:
        count = st.session_state.model_data.get("subscription_running_totals", {}).get(stakeholder, {}).get(months[-1] if months else "", 0)
        if count > 0:
            customer_breakdown_data.append({
                'Customer Type': stakeholder,
                'Active Customers': int(count),
                'Percentage': (count / total_customers * 100) if total_customers > 0 else 0
            })
    
    if customer_breakdown_data:
        # Sort by customer count
        customer_breakdown_data.sort(key=lambda x: x['Active Customers'], reverse=True)
        
        # Create columns for top customer types
        breakdown_cols = st.columns(min(4, len(customer_breakdown_data)))
        for idx, data in enumerate(customer_breakdown_data[:4]):
            with breakdown_cols[idx]:
                st.markdown(f"""
                <div class="metric-container">
                    <h4>{data['Customer Type']}</h4>
                    <h2>{data['Active Customers']}</h2>
                    <p>{data['Percentage']:.1f}% of total</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Show full breakdown in expander if more than 4 types
        if len(customer_breakdown_data) > 4:
            with st.expander("View all customer types"):
                df_breakdown = pd.DataFrame(customer_breakdown_data)
                st.dataframe(
                    df_breakdown.style.format({
                        'Active Customers': '{:,.0f}',
                        'Percentage': '{:.1f}%'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
else:
    # Show detailed metrics for selected customer type
    st.markdown(f'<div class="section-header">📊 {selected_customer_filter} - Detailed Metrics</div>', unsafe_allow_html=True)
    
    detail_col1, detail_col2, detail_col3, detail_col4 = st.columns(4)
    
    # Get specific data for this customer type
    customer_data = st.session_state.model_data.get("subscription_running_totals", {}).get(selected_customer_filter, {})
    new_customer_data = st.session_state.model_data.get("subscription_new_customers", {}).get(selected_customer_filter, {})
    pricing_data = st.session_state.model_data.get("subscription_pricing", {}).get(selected_customer_filter, {})
    churn_data = st.session_state.model_data.get("subscription_churn_rates", {}).get(selected_customer_filter, {})
    
    with detail_col1:
        # Calculate growth rate
        if len(months) >= 2:
            start_customers = customer_data.get(months[0], 0)
            end_customers = customer_data.get(months[-1], 0)
            if start_customers > 0:
                growth_rate = ((end_customers - start_customers) / start_customers) * 100
            else:
                growth_rate = 100 if end_customers > 0 else 0
        else:
            growth_rate = 0
            
        color = "#00D084" if growth_rate > 0 else "#dc3545" if growth_rate < 0 else "#666"
        st.markdown(f"""
        <div class="metric-container">
            <h4>Growth Rate</h4>
            <h2 style="color: {color};">{growth_rate:.1f}%</h2>
            <p>Period growth</p>
        </div>
        """, unsafe_allow_html=True)
    
    with detail_col2:
        # Latest monthly price
        latest_price = pricing_data.get(months[-1] if months else "", 0)
        st.markdown(f"""
        <div class="metric-container">
            <h4>Current Price</h4>
            <h2>${latest_price:,.0f}</h2>
            <p>Monthly subscription</p>
        </div>
        """, unsafe_allow_html=True)
    
    with detail_col3:
        # Latest churn rate
        latest_churn = churn_data.get(months[-1] if months else "", 0)
        churn_color = "#00D084" if latest_churn < 3 else "#FFA500" if latest_churn < 5 else "#dc3545"
        st.markdown(f"""
        <div class="metric-container">
            <h4>Current Churn</h4>
            <h2 style="color: {churn_color};">{latest_churn:.1f}%</h2>
            <p>Monthly rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    with detail_col4:
        # Customer lifetime value (simple calculation)
        if latest_churn > 0:
            avg_lifetime_months = 100 / latest_churn  # Simplified LTV calculation
            ltv = latest_price * avg_lifetime_months
        else:
            ltv = 0
        
        st.markdown(f"""
        <div class="metric-container">
            <h4>Est. LTV</h4>
            <h2>${ltv:,.0f}</h2>
            <p>Lifetime value</p>
        </div>
        """, unsafe_allow_html=True)

# TREND ANALYSIS
st.markdown('<div class="section-header">📈 Trend Analysis</div>', unsafe_allow_html=True)

# Always use 12 months for trend analysis based on selected year
if selected_year == "All Years":
    # For all years, use the last 12 months of available data
    trend_months = months[-12:] if len(months) >= 12 else months
else:
    # For specific year, use all 12 months of that year
    trend_months = [f"{month} {selected_year}" for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]]

# Create tabs for different charts
chart_tab1, chart_tab2, chart_tab3, chart_tab4 = st.tabs(["Revenue Trend", "Cash Flow", "Customer Growth", "Burn Analysis"])

with chart_tab1:
    # Revenue trend chart
    revenue_data = []
    for month in trend_months:
        revenue_data.append({
            'Month': month,
            'Subscription': st.session_state.model_data.get("revenue", {}).get("Subscription", {}).get(month, 0),
            'Implementation': st.session_state.model_data.get("revenue", {}).get("Implementation", {}).get(month, 0),
            'Transactional': st.session_state.model_data.get("revenue", {}).get("Transactional", {}).get(month, 0),
            'Maintenance': st.session_state.model_data.get("revenue", {}).get("Maintenance", {}).get(month, 0)
        })
    
    if revenue_data:
        df_revenue = pd.DataFrame(revenue_data)
        
        fig = go.Figure()
        
        # Add traces for each revenue stream
        fig.add_trace(go.Bar(name='Subscription', x=df_revenue['Month'], y=df_revenue['Subscription'], marker_color='#00D084'))
        fig.add_trace(go.Bar(name='Implementation', x=df_revenue['Month'], y=df_revenue['Implementation'], marker_color='#00B574'))
        fig.add_trace(go.Bar(name='Transactional', x=df_revenue['Month'], y=df_revenue['Transactional'], marker_color='#009564'))
        fig.add_trace(go.Bar(name='Maintenance', x=df_revenue['Month'], y=df_revenue['Maintenance'], marker_color='#007554'))
        
        # Dynamic title based on selection
        if selected_year == "All Years":
            chart_title = 'Revenue by Stream (Last 12 Months)'
        else:
            chart_title = f'Revenue by Stream ({selected_year})'
        
        fig.update_layout(
            barmode='stack',
            title=chart_title,
            xaxis_title='Month',
            yaxis_title='Revenue ($)',
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)

with chart_tab2:
    # Cash flow trend
    cash_flow_data = []
    for month in trend_months:
        cash_flow_data.append({
            'Month': month,
            'Cash Balance': calculate_cash_balance(month),
            'Monthly Burn': -calculate_burn_rate(month)
        })
    
    if cash_flow_data:
        df_cash = pd.DataFrame(cash_flow_data)
        
        fig = go.Figure()
        
        # Add cash balance line
        fig.add_trace(go.Scatter(
            x=df_cash['Month'],
            y=df_cash['Cash Balance'],
            mode='lines+markers',
            name='Cash Balance',
            line=dict(color='#00D084', width=3),
            marker=dict(size=8)
        ))
        
        # Add monthly burn as bar
        fig.add_trace(go.Bar(
            x=df_cash['Month'],
            y=df_cash['Monthly Burn'],
            name='Monthly Burn',
            marker_color='#dc3545',
            yaxis='y2',
            opacity=0.7
        ))
        
        # Dynamic title based on selection
        if selected_year == "All Years":
            chart_title = 'Cash Balance & Burn Rate (Last 12 Months)'
        else:
            chart_title = f'Cash Balance & Burn Rate ({selected_year})'
        
        fig.update_layout(
            title=chart_title,
            xaxis_title='Month',
            yaxis=dict(title='Cash Balance ($)', side='left'),
            yaxis2=dict(title='Monthly Burn ($)', side='right', overlaying='y'),
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)

with chart_tab3:
    # Customer growth
    customer_data = []
    for month in trend_months:
        total_cust, arpc = calculate_customer_metrics(month)
        customer_data.append({
            'Month': month,
            'Total Customers': total_cust,
            'ARPC': arpc
        })
    
    if customer_data:
        df_customers = pd.DataFrame(customer_data)
        
        fig = go.Figure()
        
        # Add customer count
        fig.add_trace(go.Scatter(
            x=df_customers['Month'],
            y=df_customers['Total Customers'],
            mode='lines+markers',
            name='Total Customers',
            line=dict(color='#00D084', width=3),
            marker=dict(size=8)
        ))
        
        # Add ARPC on secondary axis
        fig.add_trace(go.Scatter(
            x=df_customers['Month'],
            y=df_customers['ARPC'],
            mode='lines+markers',
            name='Avg Revenue per Customer',
            line=dict(color='#FFA500', width=2, dash='dot'),
            marker=dict(size=6),
            yaxis='y2'
        ))
        
        # Dynamic title based on selection
        if selected_year == "All Years":
            chart_title = 'Customer Growth & ARPC (Last 12 Months)'
        else:
            chart_title = f'Customer Growth & ARPC ({selected_year})'
        
        fig.update_layout(
            title=chart_title,
            xaxis_title='Month',
            yaxis=dict(title='Total Customers', side='left'),
            yaxis2=dict(title='ARPC ($)', side='right', overlaying='y'),
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)

with chart_tab4:
    # Burn analysis breakdown
    burn_breakdown = []
    expense_categories = st.session_state.model_data.get("liquidity_data", {}).get("category_order", [])
    
    for month in trend_months:
        month_data: dict[str, Any] = {'Month': month}
        expenses = st.session_state.model_data.get("liquidity_data", {}).get("expenses", {})
        
        # Get top expense categories
        for category in expense_categories[:5]:  # Top 5 categories
            month_data[category] = expenses.get(category, {}).get(month, 0)
        
        # Other expenses
        other_expenses = sum(expenses.get(cat, {}).get(month, 0) for cat in expense_categories[5:])
        month_data['Other'] = other_expenses
        
        burn_breakdown.append(month_data)
    
    if burn_breakdown:
        df_burn = pd.DataFrame(burn_breakdown)
        
        fig = go.Figure()
        
        # Add stacked bars for each expense category
        for column in df_burn.columns[1:]:
            fig.add_trace(go.Bar(name=column, x=df_burn['Month'], y=df_burn[column]))
        
        # Dynamic title based on selection
        if selected_year == "All Years":
            chart_title = 'Expense Breakdown (Last 12 Months)'
        else:
            chart_title = f'Expense Breakdown ({selected_year})'
        
        fig.update_layout(
            barmode='stack',
            title=chart_title,
            xaxis_title='Month',
            yaxis_title='Expenses ($)',
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)

# KEY INSIGHTS
st.markdown('<div class="section-header">💡 Key Insights & Alerts</div>', unsafe_allow_html=True)

insights_col1, insights_col2 = st.columns(2)

with insights_col1:
    st.markdown("### 🟢 Positive Indicators")
    
    # Check for positive trends
    if latest_arr > 0:
        st.success(f"✓ ARR reached ${latest_arr:,.0f}")
    
    if avg_gross_margin > 70:
        st.success(f"✓ Strong gross margin at {avg_gross_margin:.1f}%")
    
    if total_customers > 100:
        st.success(f"✓ Achieved {int(total_customers)} dealer milestone")
    
    if runway_month in ["Profitable", "Beyond 2030"]:
        st.success("✓ Healthy cash flow - excellent runway")
    elif "2027" in runway_month or "2028" in runway_month or "2029" in runway_month or "2030" in runway_month:
        st.success(f"✓ Healthy cash runway until {runway_month}")

with insights_col2:
    st.markdown("### 🔴 Areas of Attention")
    
    # Check for areas needing attention
    if "2025" in runway_month:
        st.error(f"⚠️ Critical: Cash runs out in {runway_month}")
    elif "2026" in runway_month:
        st.warning(f"⚠️ Concerning: Cash runs out in {runway_month}")
    
    if avg_burn_rate > 500000:
        st.warning(f"⚠️ High burn rate: ${abs(avg_burn_rate):,.0f}/month")
    
    if avg_churn > 5:
        st.warning(f"⚠️ Churn rate above target: {avg_churn:.1f}%")
    
    if latest_cash_balance < 0:
        st.error(f"⚠️ Negative cash balance: ${latest_cash_balance:,.0f}")

# MILESTONE TRACKING
st.markdown('<div class="section-header">🎯 Milestone Tracking</div>', unsafe_allow_html=True)

# Define key milestones
milestones = [
    {"name": "First 10 Dealers", "target": 10, "actual": total_customers, "type": "customers"},
    {"name": "First $100K MRR", "target": 100000, "actual": latest_arr/12, "type": "revenue"},
    {"name": "Breakeven", "target": 0, "actual": -avg_burn_rate, "type": "profitability"},
    {"name": "$1M ARR", "target": 1000000, "actual": latest_arr, "type": "revenue"},
    {"name": "100 Dealers", "target": 100, "actual": total_customers, "type": "customers"},
    {"name": "Series A Ready", "target": 2000000, "actual": latest_arr, "type": "revenue"}
]

# Display milestones
milestone_cols = st.columns(len(milestones))
for idx, milestone in enumerate(milestones):
    with milestone_cols[idx]:
        progress = (milestone["actual"] / milestone["target"] * 100) if milestone["target"] > 0 else 0
        progress = min(progress, 100)  # Cap at 100%
        
        achieved = progress >= 100
        color = "#00D084" if achieved else "#FFA500" if progress > 50 else "#dc3545"
        
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 4px solid {color};">
            <div class="kpi-label">{milestone["name"]}</div>
            <div style="font-size: 1.2rem; font-weight: 600; color: {color};">
                {progress:.0f}%
            </div>
            <div style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">
                {milestone["actual"]:,.0f} / {milestone["target"]:,.0f}
            </div>
        </div>
        """, unsafe_allow_html=True)

# SAVE AND LOAD DATA
st.markdown("---")
st.markdown('<div class="section-header">💾 Save and Load Data</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 3])

with col1:
    if st.button("💾 Save All Data", type="primary", use_container_width=True):
        try:
            with open(data_file, 'w') as f:
                json.dump(st.session_state.model_data, f, indent=2)
            st.success("✅ All data saved successfully!")
        except Exception as e:
            st.error(f"❌ Error saving data: {str(e)}")

with col2:
    if st.button("📂 Load Data", type="secondary", use_container_width=True):
        try:
            if os.path.exists(data_file):
                with open(data_file, 'r') as f:
                    st.session_state.model_data = json.load(f)
                st.success("✅ Data loaded successfully!")
                st.rerun()
            else:
                st.warning("⚠️ No saved data file found.")
        except Exception as e:
            st.error(f"❌ Error loading data: {str(e)}")

# Download/Upload functionality
st.markdown("### 📤 Export/Import Data")

col1, col2 = st.columns(2)

with col1:
    # Download button
    if st.session_state.model_data:
        json_str = json.dumps(st.session_state.model_data, indent=2)
        st.download_button(
            label="⬇️ Download Data as JSON",
            data=json_str,
            file_name=f"shaed_financial_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

with col2:
    # Upload functionality
    uploaded_file = st.file_uploader("⬆️ Upload Data JSON", type=['json'])
    if uploaded_file is not None:
        try:
            data = json.load(uploaded_file)
            st.session_state.model_data = data
            with open(data_file, 'w') as f:
                json.dump(data, f, indent=2)
            st.success("✅ Data uploaded and saved successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error uploading file: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    💡 <strong>Tip:</strong> Use the year selector to filter metrics for specific periods. 
    All metrics are automatically calculated based on data from other dashboard tabs.
</div>
""", unsafe_allow_html=True)