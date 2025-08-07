import streamlit as st
import pandas as pd
from datetime import datetime, date
import calendar
import plotly.graph_objects as go
import plotly.express as px
from typing import Any
from database import load_data, save_data, load_data_from_source, save_data_to_source, enable_autosave, auto_save_data

# Utility function for consistent category key transformation
def get_category_key(category_name):
    """Convert category name to consistent key format"""
    return category_name.lower().replace(" ", "_").replace("&", "and").replace("/", "_")

# Configure page
st.set_page_config(
    page_title="KPIs",
    page_icon="📊",
    layout="wide"
)

# Check authentication
if "password_correct" not in st.session_state or not st.session_state.get("password_correct", False):
    st.error("🔒 Please login from the Home page first.")
    st.stop()

# Add logout functionality to sidebar
with st.sidebar:
    st.markdown("---")
    if st.button("🚪 Logout", key="logout_button"):
        # Clear all session state variables
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

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
    
    /* Light gray background for collapsible sections - match dropdown style */
    .streamlit-expander {
        background-color: #f0f2f6 !important;
        border-radius: 6px;
        margin-bottom: 10px;
        border: 1px solid #d1d5db;
    }
    
    .streamlit-expander .streamlit-expanderHeader {
        background-color: #f0f2f6 !important;
        border-radius: 6px;
        padding: 12px;
    }
    
    .streamlit-expander .streamlit-expanderContent {
        background-color: #f0f2f6 !important;
        padding: 12px;
        border-radius: 0 0 6px 6px;
    }
    
    /* Alternative targeting */
    div[data-testid="stExpander"] {
        background-color: #f0f2f6 !important;
        border-radius: 6px;
        border: 1px solid #d1d5db;
    }
    
    div[data-testid="stExpander"] > div {
        background-color: #f0f2f6 !important;
    }
    
    div[data-testid="stExpander"] button {
        background-color: #f0f2f6 !important;
        border-radius: 6px;
    }
    
    /* Make input boxes white inside expandable sections */
    div[data-testid="stExpander"] input[type="number"] {
        background-color: white !important;
        border: 1px solid #d1d5db !important;
        border-radius: 4px !important;
    }
    
    div[data-testid="stExpander"] .stNumberInput > div > div > input {
        background-color: white !important;
        border: 1px solid #d1d5db !important;
        border-radius: 4px !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #666;
        padding: 2rem;
        margin-top: 3rem;
        border-top: 1px solid #e0e0e0;
    }
    
    /* Green buttons for Data Management */
    .stButton > button,
    .stDownloadButton > button {
        background-color: #00D084 !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background-color: #00B574 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
    }
    
    .stButton > button:active,
    .stDownloadButton > button:active {
        transform: translateY(0) !important;
    }
</style>
""", unsafe_allow_html=True)

if 'model_data' not in st.session_state:
    st.session_state.model_data = load_data_from_source()

# Enable autosave functionality
enable_autosave()

# Auto-save data if changes detected
auto_save_data(st.session_state.model_data, "KPIs Dashboard")

# Header
st.markdown("""
<div class="main-header">
    <h1>📊 KPIs</h1>
</div>
""", unsafe_allow_html=True)



# Date range selector and filters - Default to previous month
today = date.today()
# Calculate previous month
if today.month == 1:
    prev_month = 12
    prev_year = today.year - 1
else:
    prev_month = today.month - 1
    prev_year = today.year

# Map month number to month name
month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
prev_month_name = month_names[prev_month - 1]

# Set default year index
year_options = ["2025", "2026", "2027", "2028", "2029", "2030", "All Years"]
try:
    default_year_index = year_options.index(str(prev_year))
except ValueError:
    default_year_index = 0  # Default to 2025 if previous year not in options

# Define all stakeholders from revenue assumptions (exact match)
all_stakeholders = [
    "Equipment Manufacturer", "Dealership", "Corporate", "Charging as a Service",
    "Charging Hardware", "Depot", "End User", "Infrastructure Partner",
    "Finance Partner", "Fleet Management Company", "Grants", "Logistics",
    "Non Customer", "OEM", "Service", "Technology Partner",
    "Upfitter/Distributor", "Utility/Energy Company", "Insurance Company", "Consultant"
]

col1, col2, col3, col4, col5 = st.columns([0.75, 0.75, 0.75, 0.75, 2.0])
with col1:
    selected_year = st.selectbox(
        "Select Year",
        year_options,
        index=default_year_index
    )

with col2:
    # Month selector - only show if specific year is selected
    if selected_year != "All Years":
        month_options = ["All Months"] + ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        # Set default month index (only if we're in the default year)
        if selected_year == str(prev_year):
            try:
                default_month_index = month_options.index(prev_month_name)
            except ValueError:
                default_month_index = 0
        else:
            default_month_index = 0
            
        selected_month = st.selectbox(
            "Select Month",
            month_options,
            index=default_month_index
        )
    else:
        selected_month = "All Months"

with col3:
    # MTD/YTD selector - only show if specific month is selected
    if selected_month != "All Months" and selected_year != "All Years":
        calculation_type = st.selectbox(
            "Calculation Type",
            ["MTD", "YTD"],
            index=1
        )
    else:
        calculation_type = "Full Period"

with col4:
    # Customer type filter dropdown
    customer_filter_options = ["All Customer Types"] + all_stakeholders
    selected_customer_filter = st.selectbox(
        "Filter Customer Type",
        options=customer_filter_options,
        index=0
    )
    
    # Set selected stakeholders based on dropdown selection
    if selected_customer_filter == "All Customer Types":
        selected_stakeholders = all_stakeholders
    else:
        selected_stakeholders = [selected_customer_filter]

# Generate months list based on selection and calculation type
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
        # Handle MTD vs YTD calculations
        if calculation_type == "MTD":
            # MTD = just the selected month
            months = [f"{selected_month} {year}"]
        elif calculation_type == "YTD":
            # YTD = all months from January through the selected month
            month_list = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            selected_month_index = month_list.index(selected_month)
            months = [f"{month} {year}" for month in month_list[:selected_month_index + 1]]
        else:
            # Full Period (fallback)
            months = [f"{selected_month} {year}"]



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

def calculate_gross_burn(month):
    """Calculate gross burn rate (total expenses)"""
    # Get cash flow data from liquidity model
    liquidity_data = st.session_state.model_data.get("liquidity_data", {})
    
    # Cash outflows - get all expense categories
    expense_categories = liquidity_data.get("category_order", [])
    expenses = liquidity_data.get("expenses", {})
    total_expenses = sum(expenses.get(cat, {}).get(month, 0) for cat in expense_categories)
    
    return total_expenses

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

def calculate_headcount_metrics(target_month=None):
    """Calculate total headcount from payroll data using date-based activation"""
    # Check if payroll_data exists
    if "payroll_data" not in st.session_state.model_data:
        return 0, 0
    
    payroll_data = st.session_state.model_data.get("payroll_data", {})
    
    # Use target month if provided, otherwise use current month
    if target_month:
        check_month = target_month
    else:
        check_month = datetime.now().strftime("%b %Y")
    
    # Count active employees using date-based logic
    employees = payroll_data.get("employees", {})
    total_employees = 0
    
    for emp_data in employees.values():
        if is_employee_active_for_month(emp_data, check_month):
            total_employees += 1
    
    # Count contractors using date-based logic
    contractors = payroll_data.get("contractors", {})
    total_contractors = 0
    
    for contractor_data in contractors.values():
        if is_contractor_active_for_month(contractor_data, check_month):
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
    # Use months list for "All Years" calculation
    total_revenue = sum(calculate_total_revenue(month) for month in months)
    avg_gross_margin = sum(calculate_gross_margin(month) for month in months) / len(months) if months else 0
    latest_arr = calculate_arr(months[-1]) if months else 0
    latest_cash_balance = calculate_cash_balance(months[-1]) if months else 0
    avg_burn_rate = sum(calculate_burn_rate(month) for month in months) / len(months) if months else 0
    total_customers, avg_arpc = calculate_customer_metrics(months[-1]) if months else (0, 0)
else:
    # Calculate for specific year using the months list (already handles MTD/YTD logic)
    total_revenue = sum(calculate_total_revenue(month) for month in months)
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
        if calculation_type == "MTD":
            period_label = f"MTD {selected_month} {selected_year}"
        elif calculation_type == "YTD":
            period_label = f"YTD {selected_month} {selected_year}"
        else:
            period_label = f"{selected_month} {selected_year}"
    
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
    subscription_total = sum(st.session_state.model_data.get("revenue", {}).get("Subscription", {}).get(month, 0) for month in months)
    if selected_year == "All Years":
        period_label = "All Years"
    elif selected_month == "All Months":
        period_label = f"{selected_year}"
    else:
        if calculation_type == "MTD":
            period_label = f"MTD {selected_month} {selected_year}"
        elif calculation_type == "YTD":
            period_label = f"YTD {selected_month} {selected_year}"
        else:
            period_label = f"{selected_month} {selected_year}"
    
    st.markdown(f"""
    <div class="metric-container">
        <h4>Subscription Revenue</h4>
        <h2>${subscription_total:,.0f}</h2>
        <p>Period: {period_label}</p>
    </div>
    """, unsafe_allow_html=True)

with rev_col2:
    transactional_total = sum(st.session_state.model_data.get("revenue", {}).get("Transactional", {}).get(month, 0) for month in months)
    st.markdown(f"""
    <div class="metric-container">
        <h4>Transactional Revenue</h4>
        <h2>${transactional_total:,.0f}</h2>
        <p>Period: {period_label}</p>
    </div>
    """, unsafe_allow_html=True)

with rev_col3:
    implementation_total = sum(st.session_state.model_data.get("revenue", {}).get("Implementation", {}).get(month, 0) for month in months)
    st.markdown(f"""
    <div class="metric-container">
        <h4>Implementation Revenue</h4>
        <h2>${implementation_total:,.0f}</h2>
        <p>Period: {period_label}</p>
    </div>
    """, unsafe_allow_html=True)

with rev_col4:
    maintenance_total = sum(st.session_state.model_data.get("revenue", {}).get("Maintenance", {}).get(month, 0) for month in months)
    st.markdown(f"""
    <div class="metric-container">
        <h4>Maintenance Revenue</h4>
        <h2>${maintenance_total:,.0f}</h2>
        <p>Period: {period_label}</p>
    </div>
    """, unsafe_allow_html=True)

# CUSTOMER METRICS
st.markdown('<div class="section-header">👥 Customer Metrics</div>', unsafe_allow_html=True)



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
    # Calculate simple average churn rate for selected stakeholders with subscription revenue
    total_churn_rates = 0
    total_months = 0
    
    for stakeholder in selected_stakeholders:
        # Check if this stakeholder has active subscribers based on calculation type
        customers = st.session_state.model_data.get("subscription_running_totals", {}).get(stakeholder, {})
        
        # Determine which months to check for active subscribers
        if calculation_type == "YTD" and selected_year != "All Years":
            # For YTD, check if there were subscribers in any month from January through the period
            if selected_month != "All Months":
                # YTD for specific month: Jan through selected month
                month_list = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                selected_month_index = month_list.index(selected_month)
                ytd_months = [f"{month} {selected_year}" for month in month_list[:selected_month_index + 1]]
            else:
                # YTD for "All Months": Jan through current month or all months
                current_month = datetime.now().strftime("%b")
                month_list = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                try:
                    current_month_index = month_list.index(current_month)
                    if selected_year == str(datetime.now().year):
                        ytd_months = [f"{month} {selected_year}" for month in month_list[:current_month_index + 1]]
                    else:
                        ytd_months = [f"{month} {selected_year}" for month in month_list]
                except ValueError:
                    ytd_months = [f"{month} {selected_year}" for month in month_list]
            
            has_active_subscribers = any(customers.get(month, 0) > 0 for month in ytd_months)
        else:
            # For MTD, Full Year, or All Years, check the actual analysis period
            has_active_subscribers = any(customers.get(month, 0) > 0 for month in months)
        
        # Only include stakeholders with active subscribers in churn calculation
        if has_active_subscribers:
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
    # Calculate total employees as of the selected month and year
    target_month = months[-1] if months else datetime.now().strftime("%b %Y")
    total_employees, total_contractors = calculate_headcount_metrics(target_month)
    total_headcount = total_employees + total_contractors
    
    st.markdown(f"""
    <div class="metric-container">
        <h4>Total Headcount</h4>
        <h2>{total_headcount}</h2>
        <p>{total_employees} FTE + {total_contractors} Contractors<br><small>As of {target_month}</small></p>
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
        fig.add_trace(go.Bar(name='Subscription', x=df_revenue['Month'], y=df_revenue['Subscription'], marker_color='#00D084', hovertemplate='<b>%{fullData.name}</b><br>%{y:,.0f}<extra></extra>'))
        fig.add_trace(go.Bar(name='Implementation', x=df_revenue['Month'], y=df_revenue['Implementation'], marker_color='#3498DB', hovertemplate='<b>%{fullData.name}</b><br>%{y:,.0f}<extra></extra>'))
        fig.add_trace(go.Bar(name='Transactional', x=df_revenue['Month'], y=df_revenue['Transactional'], marker_color='#F39C12', hovertemplate='<b>%{fullData.name}</b><br>%{y:,.0f}<extra></extra>'))
        fig.add_trace(go.Bar(name='Maintenance', x=df_revenue['Month'], y=df_revenue['Maintenance'], marker_color='#9B59B6', hovertemplate='<b>%{fullData.name}</b><br>%{y:,.0f}<extra></extra>'))
        
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
            'Net Burn': -calculate_burn_rate(month),
            'Gross Burn': -calculate_gross_burn(month)
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
            marker=dict(size=8),
            hovertemplate='<b>%{fullData.name}</b><br>%{y:,.0f}<extra></extra>'
        ))
        
        # Add net burn as bar
        fig.add_trace(go.Bar(
            x=df_cash['Month'],
            y=df_cash['Net Burn'],
            name='Net Burn',
            marker_color='#dc3545',
            yaxis='y2',
            opacity=0.7,
            hovertemplate='<b>%{fullData.name}</b><br>%{y:,.0f}<extra></extra>'
        ))
        
        # Add gross burn as bar
        fig.add_trace(go.Bar(
            x=df_cash['Month'],
            y=df_cash['Gross Burn'],
            name='Gross Burn',
            marker_color='#f8ac59',
            yaxis='y2',
            opacity=0.7,
            hovertemplate='<b>%{fullData.name}</b><br>%{y:,.0f}<extra></extra>'
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
            yaxis2=dict(title='Burn Rate ($)', side='right', overlaying='y'),
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
            marker=dict(size=8),
            hovertemplate='<b>%{fullData.name}</b><br>%{y:,.0f}<extra></extra>'
        ))
        
        # Add ARPC on secondary axis
        fig.add_trace(go.Scatter(
            x=df_customers['Month'],
            y=df_customers['ARPC'],
            mode='lines+markers',
            name='Avg Revenue per Customer',
            line=dict(color='#FFA500', width=2, dash='dot'),
            marker=dict(size=6),
            yaxis='y2',
            hovertemplate='<b>%{fullData.name}</b><br>%{y:,.0f}<extra></extra>'
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
            fig.add_trace(go.Bar(name=column, x=df_burn['Month'], y=df_burn[column], hovertemplate='<b>%{fullData.name}</b><br>%{y:,.0f}<extra></extra>'))
        
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

# BUDGET VARIANCE ANALYSIS
st.markdown('<div class="section-header">📊 Budget Variance Analysis</div>', unsafe_allow_html=True)

# Budget independence is handled by the system

# Initialize budget data if not exists (but don't override existing loaded data)
if "budget_data" not in st.session_state.model_data:
    # Initialize empty structure - data should already be loaded by load_data_from_source()
    st.session_state.model_data["budget_data"] = {
        "monthly_budgets": {},
        "ytd_budgets": {}
    }
elif st.session_state.model_data["budget_data"] is None:
    # Handle case where budget_data exists but is None
    st.session_state.model_data["budget_data"] = {
        "monthly_budgets": {},
        "ytd_budgets": {}
    }



# Budget filters - separate from main dashboard filters (independent of main filters)
budget_col1, budget_col2, budget_col3, budget_col4 = st.columns([1.2, 1.2, 1.2, 1.2])

with budget_col1:
    # All years from 2025-2030 (independent of main dashboard filters)
    all_budget_years = ["2025", "2026", "2027", "2028", "2029", "2030"]
    
    # Default to current year or 2025
    current_year = datetime.now().year
    try:
        default_year_index = all_budget_years.index(str(current_year))
    except ValueError:
        default_year_index = 0  # Default to 2025
    
    budget_selected_year = st.selectbox(
        "Budget Year",
        all_budget_years,
        index=default_year_index,
        key="budget_year_filter"
    )

with budget_col2:
    # All months for selected year (independent of main dashboard filters)
    all_month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    budget_year_months = [f"{month} {budget_selected_year}" for month in all_month_names]
    
    # Default to previous month
    current_date = datetime.now()
    if current_date.month == 1:
        default_month_name = calendar.month_abbr[12]
        default_year = current_date.year - 1
    else:
        default_month_name = calendar.month_abbr[current_date.month - 1]
        default_year = current_date.year
    
    default_month = f"{default_month_name} {default_year}"
    
    try:
        default_month_index = budget_year_months.index(default_month)
    except ValueError:
        default_month_index = 5  # Default to Jun if not found
    
    budget_selected_month = st.selectbox(
        "Budget Month",
        budget_year_months,
        index=default_month_index,
        key="budget_month_filter"
    )

with budget_col3:
    budget_calculation_type = st.selectbox(
        "Budget Analysis Type",
        ["MTD", "YTD"],
        index=1,  # Default to YTD
        help="MTD = Month-to-Date, YTD = Year-to-Date",
        key="budget_calculation_filter"
    )

with budget_col4:
    budget_input_method = st.selectbox(
        "Budget Input Method",
        ["Manual Entry", "Sync with Model"],
        index=0,
        help="Choose how to enter budget data",
        key="budget_input_method_filter"
    )

# Set budget variables based on new filters
budget_period = budget_calculation_type
if budget_period == "MTD":
    budget_month = budget_selected_month
else:
    budget_month = "YTD"

# Helper function to save budget data to Supabase
def save_budget_to_supabase():
    """Save budget data to Supabase database"""
    try:
        from database import save_budget_data_to_database
        success = save_budget_data_to_database(st.session_state.model_data)
        return success
    except Exception as e:
        st.error(f"❌ Error saving budget data: {str(e)}")
        return False

# Initialize liquidity data structure if not exists to ensure cash disbursements data is available
def initialize_liquidity_data_for_budget():
    """Initialize liquidity data structure if not exists to ensure budget analysis works"""
    # Default expense categories that should always exist (mirrors liquidity tab)
    default_categories = [
        "Payroll", "Contractors", "License Fees", "Travel", "Shows", "Associations", 
        "Marketing", "Company Vehicle", "Grant Writer", "Insurance", "Legal / Professional Fees",
        "Permitting/Fees/Licensing", "Shared Services", "Consultants/Audit/Tax", "Pritchard Amex", "Contingencies"
    ]
    
    # Initialize liquidity data structure if not exists
    if "liquidity_data" not in st.session_state.model_data:
        st.session_state.model_data["liquidity_data"] = {}
    
    # Initialize category order if not exists
    if "category_order" not in st.session_state.model_data["liquidity_data"]:
        st.session_state.model_data["liquidity_data"]["category_order"] = default_categories
    
    # Initialize expenses structure if not exists
    if "expenses" not in st.session_state.model_data["liquidity_data"]:
        st.session_state.model_data["liquidity_data"]["expenses"] = {}
        
        # Create default months
        months = []
        for year in range(2025, 2031):
            for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]:
                months.append(f"{month} {year}")
        
        # Initialize each category with zero values for all months
        for category in st.session_state.model_data["liquidity_data"]["category_order"]:
            if category not in st.session_state.model_data["liquidity_data"]["expenses"]:
                st.session_state.model_data["liquidity_data"]["expenses"][category] = {month: 0 for month in months}

# Function to get actual values from cash disbursements (liquidity tab)
def get_actual_values(period_type, month_or_period):
    """Get actual values for budget comparison from cash disbursements in liquidity tab"""
    
    # Initialize liquidity data structure if not exists
    initialize_liquidity_data_for_budget()
    
    # Get dynamic expense categories from liquidity tab
    expense_categories = st.session_state.model_data.get("liquidity_data", {}).get("category_order", [])
    
    if period_type == "MTD":
        # MTD actuals (single month)
        month = month_or_period
        actuals = {
            # Revenue - get from main revenue data
            "subscription_revenue": st.session_state.model_data.get("revenue", {}).get("Subscription", {}).get(month, 0),
            "transactional_revenue": st.session_state.model_data.get("revenue", {}).get("Transactional", {}).get(month, 0),
            "implementation_revenue": st.session_state.model_data.get("revenue", {}).get("Implementation", {}).get(month, 0),
            "maintenance_revenue": st.session_state.model_data.get("revenue", {}).get("Maintenance", {}).get(month, 0),
        }
        
        # Add dynamic expenses from cash disbursements (liquidity data)
        for category in expense_categories:
            category_key = get_category_key(category)
            # Pull from liquidity_data.expenses which mirrors the cash disbursements table
            actual_amount = st.session_state.model_data.get("liquidity_data", {}).get("expenses", {}).get(category, {}).get(month, 0)
            actuals[category_key] = actual_amount
        
        return actuals
    else:
        # YTD actuals - sum across ytd_months
        actuals = {
            "subscription_revenue": 0,
            "transactional_revenue": 0,
            "implementation_revenue": 0,
            "maintenance_revenue": 0,
        }
        
        # Initialize dynamic expense categories
        for category in expense_categories:
            category_key = get_category_key(category)
            actuals[category_key] = 0
        
        # Sum across all months in the period
        for month in month_or_period:
            # Sum revenue
            actuals["subscription_revenue"] += st.session_state.model_data.get("revenue", {}).get("Subscription", {}).get(month, 0)
            actuals["transactional_revenue"] += st.session_state.model_data.get("revenue", {}).get("Transactional", {}).get(month, 0)
            actuals["implementation_revenue"] += st.session_state.model_data.get("revenue", {}).get("Implementation", {}).get(month, 0)
            actuals["maintenance_revenue"] += st.session_state.model_data.get("revenue", {}).get("Maintenance", {}).get(month, 0)
            
            # Sum expenses from cash disbursements
            for category in expense_categories:
                category_key = get_category_key(category)
                actual_amount = st.session_state.model_data.get("liquidity_data", {}).get("expenses", {}).get(category, {}).get(month, 0)
                actuals[category_key] += actual_amount
        
        return actuals

# Get actual values using budget filters (independent of main dashboard filters)
if budget_period == "MTD":
    budget_months = [budget_selected_month]
else:
    # Get YTD months for the selected year (independent of main filters)
    budget_month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    selected_month_name = budget_selected_month.split(" ")[0]
    try:
        selected_month_index = budget_month_names.index(selected_month_name)
        budget_months = [f"{month} {budget_selected_year}" for month in budget_month_names[:selected_month_index + 1]]
    except ValueError:
        budget_months = [f"{month} {budget_selected_year}" for month in budget_month_names]

actuals = get_actual_values(budget_period, budget_selected_month if budget_period == "MTD" else budget_months)

# Get budget key based on period and handle YTD aggregation
if budget_period == "MTD":
    budget_key = f"{budget_selected_month}_budget"
else:
    # For YTD, we need to aggregate monthly data
    budget_key = f"{budget_selected_year}_ytd_budget"
    
    # Create YTD budget by aggregating monthly budgets
    budget_month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    selected_month_name = budget_selected_month.split(" ")[0]
    
    try:
        selected_month_index = budget_month_names.index(selected_month_name)
        ytd_months = [f"{month} {budget_selected_year}_budget" for month in budget_month_names[:selected_month_index + 1]]
        
        # Initialize YTD budget if it doesn't exist
        if budget_key not in st.session_state.model_data["budget_data"]["monthly_budgets"]:
            st.session_state.model_data["budget_data"]["monthly_budgets"][budget_key] = {}
        
        # Aggregate monthly budgets into YTD
        ytd_budget = {}
        for month_key in ytd_months:
            if month_key in st.session_state.model_data["budget_data"]["monthly_budgets"]:
                monthly_budget = st.session_state.model_data["budget_data"]["monthly_budgets"][month_key]
                for category, amount in monthly_budget.items():
                    if category not in ytd_budget:
                        ytd_budget[category] = 0
                    ytd_budget[category] += float(amount or 0)
        
        # Update the YTD budget with aggregated values
        st.session_state.model_data["budget_data"]["monthly_budgets"][budget_key] = ytd_budget
        
    except ValueError:
        # If month parsing fails, use current YTD budget or initialize empty
        if budget_key not in st.session_state.model_data["budget_data"]["monthly_budgets"]:
            st.session_state.model_data["budget_data"]["monthly_budgets"][budget_key] = {}

# Initialize liquidity data structure to ensure cash disbursements data is available
initialize_liquidity_data_for_budget()

# Get dynamic expense categories from liquidity tab (now guaranteed to exist)
expense_categories = st.session_state.model_data.get("liquidity_data", {}).get("category_order", [])

# Initialize budget if not exists OR ensure all current expense categories are included
if budget_key not in st.session_state.model_data["budget_data"]["monthly_budgets"]:
    # Initialize with revenue categories
    budget_dict = {
        "subscription_revenue": 0,
        "transactional_revenue": 0,
        "implementation_revenue": 0,
        "maintenance_revenue": 0,
    }
    
    # Add all expense categories from liquidity tab (cash disbursements)
    for category in expense_categories:
        # Convert category name to key (replace spaces with underscores, lowercase)
        category_key = get_category_key(category)
        budget_dict[category_key] = 0
    
    st.session_state.model_data["budget_data"]["monthly_budgets"][budget_key] = budget_dict
else:
    # Update existing budget with any new expense categories
    existing_budget = st.session_state.model_data["budget_data"]["monthly_budgets"][budget_key]
    
    # Ensure all revenue categories exist
    revenue_categories = ["subscription_revenue", "transactional_revenue", "implementation_revenue", "maintenance_revenue"]
    for rev_cat in revenue_categories:
        if rev_cat not in existing_budget:
            existing_budget[rev_cat] = 0
    
    # Ensure all current expense categories exist (from cash disbursements)
    for category in expense_categories:
        category_key = get_category_key(category)
        if category_key not in existing_budget:
            existing_budget[category_key] = 0



# Budget input section
st.markdown("Budget Input:")

# Budget input based on selected method
if budget_input_method == "Manual Entry":
    pass
    
elif budget_input_method == "Sync with Model":
    
    sync_col1, sync_col2, sync_col3 = st.columns([2, 2, 1])
    
    with sync_col1:
        # Effective month picker
        all_months = []
        for year in range(2025, 2031):
            for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]:
                all_months.append(f"{month} {year}")
        
        # Default to current month or closest available
        current_month = datetime.now().strftime("%b %Y")
        default_index = all_months.index(current_month) if current_month in all_months else 0
        
        effective_month = st.selectbox(
            "Effective Month",
            options=all_months,
            index=default_index,
            help="Budget will be updated from this month forward. Historical data remains unchanged. For YTD budgets, only months from effective date through selected month will be included."
        )
    
    with sync_col2:
        pass
    
    with sync_col3:
        st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
        if st.button("🔄 Sync Budget", type="primary"):
            try:
                # Sync budget data from selected month forward
                
                # Get all months from the model
                all_months = []
                for year in range(2025, 2031):
                    for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]:
                        all_months.append(f"{month} {year}")
                
                # Find the effective month index
                effective_month_idx = all_months.index(effective_month) if effective_month in all_months else 0
                
                # Sync budget for all months from effective date forward
                months_to_sync = all_months[effective_month_idx:effective_month_idx + 12]  # Limit to 12 months for testing
                

                
                synced_count = 0
                
                for month in months_to_sync:
                    # Get or create budget for this month
                    month_budget_key = f"{month}_budget"
                    if month_budget_key not in st.session_state.model_data["budget_data"]["monthly_budgets"]:
                        st.session_state.model_data["budget_data"]["monthly_budgets"][month_budget_key] = {}
                    
                    # Get actual values using the exact same working function
                    month_actuals = get_actual_values("MTD", month)
                    
                    # Calculate total actuals
                    total_actuals = sum(abs(v) for v in month_actuals.values() if isinstance(v, (int, float)))
                    
                    # Always sync data if we have any actual values, even if small
                    if month_actuals and len(month_actuals) > 0:
                        # Update budget with actual values
                        for key, value in month_actuals.items():
                            if value is not None and value != 0:  # Only update non-zero values
                                st.session_state.model_data["budget_data"]["monthly_budgets"][month_budget_key][key] = abs(float(value))
                        synced_count += 1
                        
                        pass  # Successfully synced month data
                
                # CRITICAL FIX: Update the display budget key with aggregated data
                # For YTD, we need to aggregate only the synced months (from effective date forward)
                if budget_period == "YTD":
                    # Calculate YTD months for the selected year, but only from effective month forward
                    budget_month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                    selected_month_name = budget_selected_month.split(" ")[0]
                    effective_month_name = effective_month.split(" ")[0]
                    
                    # Find indices
                    selected_month_index = budget_month_names.index(selected_month_name)
                    effective_month_index = budget_month_names.index(effective_month_name)
                    
                    # YTD should only include months from effective date through selected month
                    # If effective month is after selected month, use only selected month
                    start_index = max(effective_month_index, 0)
                    end_index = selected_month_index + 1
                    
                    if start_index <= selected_month_index:
                        ytd_budget_months = [f"{month} {budget_selected_year}" for month in budget_month_names[start_index:end_index]]
                        
                        # Get YTD actuals only for months from effective date forward
                        ytd_actuals = get_actual_values("YTD", ytd_budget_months)
                        
                        # Store aggregated YTD data in the YTD budget key that the display is looking for
                        if budget_key not in st.session_state.model_data["budget_data"]["monthly_budgets"]:
                            st.session_state.model_data["budget_data"]["monthly_budgets"][budget_key] = {}
                        
                        # Store the YTD data (only from effective month forward)
                        for key, value in ytd_actuals.items():
                            st.session_state.model_data["budget_data"]["monthly_budgets"][budget_key][key] = value
                    else:
                        # If effective month is after selected month, just clear the budget
                        if budget_key not in st.session_state.model_data["budget_data"]["monthly_budgets"]:
                            st.session_state.model_data["budget_data"]["monthly_budgets"][budget_key] = {}
                        
                        # Initialize with zeros since effective month is after selected display month
                        # Make sure to use the same expense categories from cash disbursements
                        default_categories = [
                            "Payroll", "Contractors", "License Fees", "Travel", "Shows", "Associations", 
                            "Marketing", "Company Vehicle", "Grant Writer", "Insurance", "Legal / Professional Fees",
                            "Permitting/Fees/Licensing", "Shared Services", "Consultants/Audit/Tax", "Pritchard Amex", "Contingencies"
                        ]
                        expense_categories = st.session_state.model_data.get("liquidity_data", {}).get("category_order", default_categories)
                        for category in expense_categories:
                            category_key = get_category_key(category)
                            st.session_state.model_data["budget_data"]["monthly_budgets"][budget_key][category_key] = 0
                        
                        # Also zero out revenue categories
                        revenue_categories = ["subscription_revenue", "transactional_revenue", "implementation_revenue", "maintenance_revenue"]
                        for rev_cat in revenue_categories:
                            st.session_state.model_data["budget_data"]["monthly_budgets"][budget_key][rev_cat] = 0
                
                elif budget_period == "MTD":
                    # For MTD, update the MTD budget key with the specific month's data
                    if budget_selected_month in months_to_sync:
                        current_actuals = get_actual_values("MTD", budget_selected_month)
                        for key, value in current_actuals.items():
                            if key in st.session_state.model_data["budget_data"]["monthly_budgets"][budget_key]:
                                st.session_state.model_data["budget_data"]["monthly_budgets"][budget_key][key] = value
                
                if synced_count > 0:
                    # Save the updated budget data to Supabase
                    save_budget_to_supabase()
                    save_data_to_source(st.session_state.model_data)
                    
                    # Create detailed success message
                    if budget_period == "YTD":
                        effective_month_name = effective_month.split(" ")[0]
                        selected_month_name = budget_selected_month.split(" ")[0]
                        st.success(f"✅ Budget synced with cash disbursements data for {synced_count} months starting from {effective_month}")
                        st.info(f"📊 YTD budget now includes actual cash flows from {effective_month_name} through {selected_month_name} {budget_selected_year} only (historical months before {effective_month_name} are excluded)")
                    else:
                        st.success(f"✅ Budget synced with cash disbursements data for {synced_count} months starting from {effective_month}")
                        
                    st.info(f"📝 You can now manually edit budget data for any month/year from the Budget Year/Month dropdowns above.")
                else:
                    st.warning("⚠️ No months were synced. This could mean there's no actual cash disbursement data for the selected period.")
                    st.info(f"🔍 Check that you have revenue and expense data in your liquidity model starting from {effective_month}")
                
                st.rerun()
                
            except Exception as e:
                st.error(f"Error syncing budget data. Please check your liquidity forecast data.")
    

    


# Show current budget values and allow editing
# Get budget values for display
budget_values = st.session_state.model_data["budget_data"]["monthly_budgets"][budget_key]

if budget_input_method == "Manual Entry":
    # Show budget inputs for both MTD and YTD (YTD will be read-only)
    is_readonly = (budget_period == "YTD")
    
    # Revenue Inputs (Collapsible)
    with st.expander("💰 Revenue Inputs", expanded=False):
        rev_col1, rev_col2 = st.columns(2)
        
        with rev_col1:
            # Subscription Revenue with auto-save (disabled for YTD)
            old_sub_value = st.session_state.model_data["budget_data"]["monthly_budgets"][budget_key].get("subscription_revenue", 0)
            new_sub_value = st.number_input(
                "Subscription Revenue",
                value=float(old_sub_value),
                min_value=0.0,
                step=1000.0,
                format="%.0f",
                key=f"budget_sub_{budget_key}",
                disabled=is_readonly
            )
            if not is_readonly and new_sub_value != old_sub_value:
                st.session_state.model_data["budget_data"]["monthly_budgets"][budget_key]["subscription_revenue"] = new_sub_value
                save_budget_to_supabase()
            
            # Transactional Revenue with auto-save (disabled for YTD)
            old_trans_value = st.session_state.model_data["budget_data"]["monthly_budgets"][budget_key].get("transactional_revenue", 0)
            new_trans_value = st.number_input(
                "Transactional Revenue",
                value=float(old_trans_value),
                min_value=0.0,
                step=1000.0,
                format="%.0f",
                key=f"budget_trans_{budget_key}",
                disabled=is_readonly
            )
            if not is_readonly and new_trans_value != old_trans_value:
                st.session_state.model_data["budget_data"]["monthly_budgets"][budget_key]["transactional_revenue"] = new_trans_value
                save_budget_to_supabase()
        
        with rev_col2:
            # Implementation Revenue with auto-save (disabled for YTD)
            old_impl_value = st.session_state.model_data["budget_data"]["monthly_budgets"][budget_key].get("implementation_revenue", 0)
            new_impl_value = st.number_input(
                "Implementation Revenue",
                value=float(old_impl_value),
                min_value=0.0,
                step=1000.0,
                format="%.0f",
                key=f"budget_impl_{budget_key}",
                disabled=is_readonly
            )
            if not is_readonly and new_impl_value != old_impl_value:
                st.session_state.model_data["budget_data"]["monthly_budgets"][budget_key]["implementation_revenue"] = new_impl_value
                save_budget_to_supabase()
            
            # Maintenance Revenue with auto-save (disabled for YTD)
            old_maint_value = st.session_state.model_data["budget_data"]["monthly_budgets"][budget_key].get("maintenance_revenue", 0)
            new_maint_value = st.number_input(
                "Maintenance Revenue",
                value=float(old_maint_value),
                min_value=0.0,
                step=1000.0,
                format="%.0f",
                key=f"budget_maint_{budget_key}",
                disabled=is_readonly
            )
            if not is_readonly and new_maint_value != old_maint_value:
                st.session_state.model_data["budget_data"]["monthly_budgets"][budget_key]["maintenance_revenue"] = new_maint_value
                save_budget_to_supabase()

    # Expense Inputs (Collapsible) - Dynamic from Liquidity Tab Cash Disbursements
    with st.expander("💸 Expense Inputs", expanded=False):
        # Get expense categories from liquidity data
        default_categories = [
            "Payroll", "Contractors", "License Fees", "Travel", "Shows", "Associations", 
            "Marketing", "Company Vehicle", "Grant Writer", "Insurance", "Legal / Professional Fees",
            "Permitting/Fees/Licensing", "Shared Services", "Consultants/Audit/Tax", "Pritchard Amex", "Contingencies"
        ]
        expense_categories = st.session_state.model_data.get("liquidity_data", {}).get("category_order", default_categories)
        
        # Ensure categories are unique to prevent duplicate keys
        expense_categories = list(dict.fromkeys(expense_categories)) if expense_categories else default_categories
        
        # Create columns for expense inputs
        num_cols = 2
        expense_cols = st.columns(num_cols)
        
        # Dynamic expense inputs based on liquidity tab categories with auto-save (disabled for YTD)
        for i, category in enumerate(expense_categories):
            category_key = get_category_key(category)
            col_idx = i % num_cols
            
            with expense_cols[col_idx]:
                # Ensure the category exists in the budget dict
                if category_key not in st.session_state.model_data["budget_data"]["monthly_budgets"][budget_key]:
                    st.session_state.model_data["budget_data"]["monthly_budgets"][budget_key][category_key] = 0
                
                # Get old value and create input with auto-save (disabled for YTD)
                old_expense_value = st.session_state.model_data["budget_data"]["monthly_budgets"][budget_key].get(category_key, 0)
                new_expense_value = st.number_input(
                    category,
                    value=float(old_expense_value),
                    min_value=0.0,
                    step=1000.0,
                    format="%.0f",
                    key=f"budget_{category_key}_{budget_key}_{i}",
                    disabled=is_readonly
                )
                if not is_readonly and new_expense_value != old_expense_value:
                    st.session_state.model_data["budget_data"]["monthly_budgets"][budget_key][category_key] = new_expense_value
                    save_budget_to_supabase()

# Budget vs Actual Analysis
st.markdown("Budget vs Actual Analysis:")

# Budget values are already defined above

# Ensure we have consistent expense categories for comparison
default_categories = [
    "Payroll", "Contractors", "License Fees", "Travel", "Shows", "Associations", 
    "Marketing", "Company Vehicle", "Grant Writer", "Insurance", "Legal / Professional Fees",
    "Permitting/Fees/Licensing", "Shared Services", "Consultants/Audit/Tax", "Pritchard Amex", "Contingencies"
]
expense_categories = st.session_state.model_data.get("liquidity_data", {}).get("category_order", default_categories)

# Ensure categories are unique to prevent duplicates
expense_categories = list(dict.fromkeys(expense_categories)) if expense_categories else default_categories

# Create comparison data
comparison_data = []

# Cash Receipts (Revenue)
comparison_data.append({
    "Category": "Cash Receipts",
    "Item": "Subscription Revenue",
    "Budget": budget_values["subscription_revenue"],
    "Actual": actuals["subscription_revenue"],
    "Variance": actuals["subscription_revenue"] - budget_values["subscription_revenue"],
    "Variance %": ((actuals["subscription_revenue"] - budget_values["subscription_revenue"]) / budget_values["subscription_revenue"] * 100) if budget_values["subscription_revenue"] != 0 else 0
})

comparison_data.append({
    "Category": "Cash Receipts",
    "Item": "Transactional Revenue",
    "Budget": budget_values["transactional_revenue"],
    "Actual": actuals["transactional_revenue"],
    "Variance": actuals["transactional_revenue"] - budget_values["transactional_revenue"],
    "Variance %": ((actuals["transactional_revenue"] - budget_values["transactional_revenue"]) / budget_values["transactional_revenue"] * 100) if budget_values["transactional_revenue"] != 0 else 0
})

comparison_data.append({
    "Category": "Cash Receipts",
    "Item": "Implementation Revenue",
    "Budget": budget_values["implementation_revenue"],
    "Actual": actuals["implementation_revenue"],
    "Variance": actuals["implementation_revenue"] - budget_values["implementation_revenue"],
    "Variance %": ((actuals["implementation_revenue"] - budget_values["implementation_revenue"]) / budget_values["implementation_revenue"] * 100) if budget_values["implementation_revenue"] != 0 else 0
})

comparison_data.append({
    "Category": "Cash Receipts",
    "Item": "Maintenance Revenue",
    "Budget": budget_values["maintenance_revenue"],
    "Actual": actuals["maintenance_revenue"],
    "Variance": actuals["maintenance_revenue"] - budget_values["maintenance_revenue"],
    "Variance %": ((actuals["maintenance_revenue"] - budget_values["maintenance_revenue"]) / budget_values["maintenance_revenue"] * 100) if budget_values["maintenance_revenue"] != 0 else 0
})

# Total Receipts
total_budget_receipts = sum([budget_values["subscription_revenue"], budget_values["transactional_revenue"], budget_values["implementation_revenue"], budget_values["maintenance_revenue"]])
total_actual_receipts = sum([actuals["subscription_revenue"], actuals["transactional_revenue"], actuals["implementation_revenue"], actuals["maintenance_revenue"]])

comparison_data.append({
    "Category": "Cash Receipts",
    "Item": "Total Receipts",
    "Budget": total_budget_receipts,
    "Actual": total_actual_receipts,
    "Variance": total_actual_receipts - total_budget_receipts,
    "Variance %": ((total_actual_receipts - total_budget_receipts) / total_budget_receipts * 100) if total_budget_receipts != 0 else 0
})

# Cash Payments (Expenses) - Dynamic from Liquidity Tab Cash Disbursements
for category in expense_categories:
    category_key = get_category_key(category)
    comparison_data.append({
        "Category": "Cash Payments",
        "Item": category,  # Expense category name from cash disbursements
        "Budget": budget_values.get(category_key, 0),  # Budget amount you entered
        "Actual": actuals.get(category_key, 0),  # Actual amount from liquidity tab cash disbursements
        "Variance": actuals.get(category_key, 0) - budget_values.get(category_key, 0),
        "Variance %": ((actuals.get(category_key, 0) - budget_values.get(category_key, 0)) / budget_values.get(category_key, 0) * 100) if budget_values.get(category_key, 0) != 0 else 0
    })

# Total Payments
total_budget_payments = sum([budget_values.get(get_category_key(category), 0) for category in expense_categories])
total_actual_payments = sum([actuals.get(get_category_key(category), 0) for category in expense_categories])

comparison_data.append({
    "Category": "Cash Payments",
    "Item": "Total Payments",
    "Budget": total_budget_payments,
    "Actual": total_actual_payments,
    "Variance": total_actual_payments - total_budget_payments,
    "Variance %": ((total_actual_payments - total_budget_payments) / total_budget_payments * 100) if total_budget_payments != 0 else 0
})

# Net Position
net_budget = total_budget_receipts - total_budget_payments
net_actual = total_actual_receipts - total_actual_payments

comparison_data.append({
    "Category": "Net Position",
    "Item": "Net Cash Flow",
    "Budget": net_budget,
    "Actual": net_actual,
    "Variance": net_actual - net_budget,
    "Variance %": ((net_actual - net_budget) / abs(net_budget) * 100) if net_budget != 0 else 0
})

# Create DataFrame
df_comparison = pd.DataFrame(comparison_data)

# Display the comparison table with formatting

# Custom function to create income statement style tables
def create_budget_variance_table(comparison_data):
    """Create a professionally formatted budget variance table matching income statement style"""
    
    # Separate data by category
    receipts_data = [item for item in comparison_data if item['Category'] == 'Cash Receipts']
    payments_data = [item for item in comparison_data if item['Category'] == 'Cash Payments']
    net_data = [item for item in comparison_data if item['Category'] == 'Net Position']
    
    # Create DataFrame for better rendering
    import pandas as pd
    
    # Create a simplified table structure
    table_data = []
    
    # Add section headers and data
    table_data.append({
        'Item': '💰 Cash Receipts',
        'Budget': '',
        'Actual': '',
        'Variance': '',
        'Variance %': '',
        'Type': 'header'
    })
    
    # Add receipts data
    for item in receipts_data:
        if item['Item'] == 'Total Receipts':
            continue
        table_data.append({
            'Item': f"   {item['Item']}",
            'Budget': f"${item['Budget']:,.0f}",
            'Actual': f"${item['Actual']:,.0f}",
            'Variance': f"${item['Variance']:,.0f}",
            'Variance %': f"{item['Variance %']:.1f}%",
            'Type': 'line_item'
        })
    
    # Add total receipts
    total_receipts = next(item for item in receipts_data if item['Item'] == 'Total Receipts')
    table_data.append({
        'Item': 'Total Receipts',
        'Budget': f"${total_receipts['Budget']:,.0f}",
        'Actual': f"${total_receipts['Actual']:,.0f}",
        'Variance': f"${total_receipts['Variance']:,.0f}",
        'Variance %': f"{total_receipts['Variance %']:.1f}%",
        'Type': 'subtotal'
    })
    
    # Add payments header
    table_data.append({
        'Item': '💸 Cash Payments',
        'Budget': '',
        'Actual': '',
        'Variance': '',
        'Variance %': '',
        'Type': 'header'
    })
    
    # Add payments data
    for item in payments_data:
        if item['Item'] == 'Total Payments':
            continue
        table_data.append({
            'Item': f"   {item['Item']}",
            'Budget': f"${item['Budget']:,.0f}",
            'Actual': f"${item['Actual']:,.0f}",
            'Variance': f"${item['Variance']:,.0f}",
            'Variance %': f"{item['Variance %']:.1f}%",
            'Type': 'line_item'
        })
    
    # Add total payments
    total_payments = next(item for item in payments_data if item['Item'] == 'Total Payments')
    table_data.append({
        'Item': 'Total Payments',
        'Budget': f"${total_payments['Budget']:,.0f}",
        'Actual': f"${total_payments['Actual']:,.0f}",
        'Variance': f"${total_payments['Variance']:,.0f}",
        'Variance %': f"{total_payments['Variance %']:.1f}%",
        'Type': 'subtotal'
    })
    
    # Add net position
    for item in net_data:
        table_data.append({
            'Item': f"📊 {item['Item']}",
            'Budget': f"${item['Budget']:,.0f}",
            'Actual': f"${item['Actual']:,.0f}",
            'Variance': f"${item['Variance']:,.0f}",
            'Variance %': f"{item['Variance %']:.1f}%",
            'Type': 'net'
        })
    
    # Create DataFrame without the Type column for display
    display_df = pd.DataFrame(table_data).drop('Type', axis=1)
    
    # Custom styling function
    def style_budget_table(df, type_data):
        def highlight_rows(row):
            idx = row.name
            if idx < len(type_data):
                row_type = type_data[idx]['Type']
                if row_type == 'header':
                    return ['background-color: #00D084; color: white; font-weight: bold; padding: 8px'] * len(row)
                elif row_type == 'subtotal':
                    return ['background-color: #f0f8ff; font-weight: bold; border-top: 1px solid #ccc; padding: 6px'] * len(row)
                elif row_type == 'net':
                    return ['background-color: #e8f5e8; font-weight: bold; border-top: 2px solid #00D084; border-bottom: 2px solid #00D084; padding: 6px'] * len(row)
                else:
                    return ['padding: 4px'] * len(row)
            return ['padding: 4px'] * len(row)
        
        # Apply row styling and ensure clean formatting
        styled_df = df.style.apply(highlight_rows, axis=1)
        styled_df = styled_df.set_table_styles([
            {'selector': 'table', 'props': [('border-collapse', 'collapse'), ('width', '100%')]},
            {'selector': 'th, td', 'props': [('text-align', 'left'), ('border', 'none')]},
            {'selector': 'tbody tr:last-child', 'props': [('border-bottom', '2px solid #00D084')]}
        ])
        
        return styled_df
    
    return style_budget_table(display_df, table_data)



# Budget vs Actual Table (Collapsible)
with st.expander("📊 Budget vs Actual Table", expanded=False):
    # Display the professionally formatted table
    styled_table = create_budget_variance_table(comparison_data)

    # Calculate precise height based on actual table content
    # Count actual rows in the formatted table (headers + line items + totals + net)
    receipts_items = len([item for item in comparison_data if item['Category'] == 'Cash Receipts' and item['Item'] != 'Total Receipts'])
    payments_items = len([item for item in comparison_data if item['Category'] == 'Cash Payments' and item['Item'] != 'Total Payments'])
    
    # Actual rows: 2 headers + receipt items + 1 total receipts + payment items + 1 total payments + 1 net cash flow
    actual_rows = 2 + receipts_items + 1 + payments_items + 1 + 1
    table_height = actual_rows * 35 + 50  # 35px per row + minimal buffer

    st.dataframe(styled_table, use_container_width=True, hide_index=True, height=table_height)

# Summary metrics
summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)

with summary_col1:
    revenue_variance = total_actual_receipts - total_budget_receipts
    revenue_variance_pct = (revenue_variance / total_budget_receipts * 100) if total_budget_receipts != 0 else 0
    color = "#00D084" if revenue_variance >= 0 else "#dc3545"
    
    st.markdown(f"""
    <div class="metric-container">
        <h4>Revenue Variance</h4>
        <h2 style="color: {color};">${revenue_variance:,.0f}</h2>
        <p style="color: {color};">{revenue_variance_pct:.1f}% vs budget</p>
    </div>
    """, unsafe_allow_html=True)

with summary_col2:
    expense_variance = total_actual_payments - total_budget_payments
    expense_variance_pct = (expense_variance / total_budget_payments * 100) if total_budget_payments != 0 else 0
    color = "#dc3545" if expense_variance > 0 else "#00D084"
    
    st.markdown(f"""
    <div class="metric-container">
        <h4>Expense Variance</h4>
        <h2 style="color: {color};">${expense_variance:,.0f}</h2>
        <p style="color: {color};">{expense_variance_pct:.1f}% vs budget</p>
    </div>
    """, unsafe_allow_html=True)

with summary_col3:
    net_variance = net_actual - net_budget
    net_variance_pct = (net_variance / abs(net_budget) * 100) if net_budget != 0 else 0
    color = "#00D084" if net_variance >= 0 else "#dc3545"
    
    st.markdown(f"""
    <div class="metric-container">
        <h4>Net Variance</h4>
        <h2 style="color: {color};">${net_variance:,.0f}</h2>
        <p style="color: {color};">{net_variance_pct:.1f}% vs budget</p>
    </div>
    """, unsafe_allow_html=True)

with summary_col4:
    # Budget accuracy - percentage of items within 10% of budget
    items_within_10_percent = sum(1 for item in comparison_data if abs(item['Variance %']) <= 10 and item['Item'] not in ['Total Receipts', 'Total Payments', 'Net Cash Flow'])
    total_line_items = len(comparison_data) - 3  # Exclude totals
    accuracy = (items_within_10_percent / total_line_items * 100) if total_line_items > 0 else 0
    
    color = "#00D084" if accuracy >= 80 else "#FFA500" if accuracy >= 60 else "#dc3545"
    
    st.markdown(f"""
    <div class="metric-container">
        <h4>Budget Accuracy</h4>
        <h2 style="color: {color};">{accuracy:.0f}%</h2>
        <p>Items within 10% of budget</p>
    </div>
    """, unsafe_allow_html=True)

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

# DATA MANAGEMENT
st.markdown("---")
st.markdown('<div class="section-header">💾 Data Management</div>', unsafe_allow_html=True)

data_col1, data_col2, data_col3, data_col4, data_col5, data_col6 = st.columns([1, 1, 1, 1, 0.75, 1.25])

with data_col1:
    if st.button("💾 Save Data", type="primary", use_container_width=True):
        try:
            # Save regular model data
            save_data_to_source(st.session_state.model_data)
            
            # Save budget data specifically from KPI tab (only if budget data exists)
            if "budget_data" in st.session_state.model_data and st.session_state.model_data["budget_data"].get("monthly_budgets"):
                try:
                    from database import save_budget_data_to_database
                    save_budget_data_to_database(st.session_state.model_data)
                except Exception as e:
                    st.warning(f"⚠️ Budget data save failed: {str(e)}")
            
            st.success("✅ Data saved successfully!")
        except Exception as e:
            st.error(f"❌ Error saving data: {str(e)}")

with data_col2:
    if st.button("📂 Load Data", type="secondary", use_container_width=True):
        st.session_state.model_data = load_data_from_source()
        st.success("✅ Data loaded successfully!")
        st.rerun()

with data_col3:
    # Create Excel export data
    try:
        import tempfile
        import os
        from datetime import datetime
        
        # Generate timestamp and filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"SHAED_Financial_Data_{timestamp}.xlsx"
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            temp_path = tmp_file.name
        
        # Create Excel writer
        with pd.ExcelWriter(temp_path, engine='openpyxl') as writer:
            # Export Revenue Data
            revenue_data = st.session_state.model_data.get("revenue", {})
            if revenue_data:
                revenue_df = pd.DataFrame(revenue_data).T
                revenue_df.index.name = 'Month'
                revenue_df.to_excel(writer, sheet_name='Revenue')
            
            # Export Customer Data
            customer_data = st.session_state.model_data.get("subscription_running_totals", {})
            if customer_data:
                customer_df = pd.DataFrame(customer_data).T
                customer_df.index.name = 'Month'
                customer_df.to_excel(writer, sheet_name='Customers')
            
            # Export Pricing Data
            pricing_data = st.session_state.model_data.get("subscription_pricing", {})
            if pricing_data:
                pricing_df = pd.DataFrame(pricing_data).T
                pricing_df.index.name = 'Month'
                pricing_df.to_excel(writer, sheet_name='Pricing')
            
            # Export Churn Rates
            churn_data = st.session_state.model_data.get("subscription_churn_rates", {})
            if churn_data:
                churn_df = pd.DataFrame(churn_data).T
                churn_df.index.name = 'Month'
                churn_df.to_excel(writer, sheet_name='Churn Rates')
            
            # Export Liquidity Data
            liquidity_data = st.session_state.model_data.get("liquidity_data", {})
            if liquidity_data:
                # Revenue sheet in liquidity
                if 'revenue' in liquidity_data:
                    liq_revenue_df = pd.DataFrame({'Revenue': liquidity_data['revenue']})
                    liq_revenue_df.index.name = 'Month'
                    liq_revenue_df.to_excel(writer, sheet_name='Liquidity Revenue')
                
                # Expenses sheet
                if 'expenses' in liquidity_data:
                    expenses_df = pd.DataFrame(liquidity_data['expenses']).T
                    expenses_df.index.name = 'Month'
                    expenses_df.to_excel(writer, sheet_name='Expenses')
                
                # Other cash items
                cash_items_data = {}
                for key in ['other_cash_receipts', 'investment']:
                    if key in liquidity_data:
                        cash_items_data[key.replace('_', ' ').title()] = liquidity_data[key]
                
                if cash_items_data:
                    cash_items_df = pd.DataFrame(cash_items_data).T
                    cash_items_df.index.name = 'Month'
                    cash_items_df.to_excel(writer, sheet_name='Other Cash Items')
            
            # Export KPI Summary for current selection
            kpi_summary_data = []
            for month in months[:12]:  # Last 12 months for summary
                total_rev = calculate_total_revenue(month)
                arr = calculate_arr(month)
                cash_bal = calculate_cash_balance(month)
                burn = calculate_burn_rate(month)
                customers, arpc = calculate_customer_metrics(month)
                
                kpi_summary_data.append({
                    'Month': month,
                    'Total Revenue': total_rev,
                    'ARR': arr,
                    'Cash Balance': cash_bal,
                    'Burn Rate': burn,
                    'Total Customers': customers,
                    'ARPC': arpc,
                    'Gross Margin %': calculate_gross_margin(month)
                })
            
            if kpi_summary_data:
                kpi_df = pd.DataFrame(kpi_summary_data)
                kpi_df.to_excel(writer, sheet_name='KPI Summary', index=False)
            
            # Export Budget vs Actual Analysis if available
            if comparison_data:
                budget_df = pd.DataFrame(comparison_data)
                budget_df.to_excel(writer, sheet_name='Budget vs Actual', index=False)
        
        # Read the file data for download
        with open(temp_path, 'rb') as f:
            excel_data = f.read()
        
        # Clean up temp file
        os.unlink(temp_path)
        
        # Direct download button that triggers immediately
        st.download_button(
            label="📊 Export Excel",
            data=excel_data,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True
        )
        
    except ImportError:
        # Fallback button if openpyxl not available
        if st.button("📊 Export Excel", type="primary", use_container_width=True):
            st.error("❌ Excel export requires openpyxl. Please install: pip install openpyxl")
    except Exception as e:
        # Fallback button if there's an error
        if st.button("📊 Export Excel", type="primary", use_container_width=True):
            st.error(f"❌ Error creating Excel file: {str(e)}")

# Footer
st.markdown("""
<div class="footer">
    <strong>SHAED Finance Dashboard - KPIs</strong> | Powering the future of mobility<br>
    <small>© 2025 SHAED - All rights reserved</small>
</div>
""", unsafe_allow_html=True)